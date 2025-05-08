import scrapy
import re
from scrapy.linkextractors import LinkExtractor
import requests
import json
import time

# https://stackoverflow.com/questions/67610949/crawling-through-multiple-links-on-scrapy

class ChocolatespiderSpider(scrapy.Spider):
    name = "chocolatespider"
    allowed_domains = ["www.emag.ro"]
    start_urls = {"TV": "https://www.emag.ro/televizoare/c?ref=hp_menu_quick-nav_190_1&type=category",
                 "Microphone" :"https://www.emag.ro/microfoane-pc/c?ref=hp_menu_quick-nav_23_28&type=category",
                 "GamingHeadset" : "https://www.emag.ro/casti-pc/c?ref=hp_menu_quick-nav_23_27&type=category",
                 "DeskChair" :  "https://www.emag.ro/scaune-gaming/c?ref=hp_menu_quick-nav_463_9&type=link",
                 "ControllerAndSteeringWheel" :"https://www.emag.ro/controlere-volane-casti-gaming/c?ref=hp_menu_quick-nav_463_7&type=link",
                 "FitnessBike" :"https://www.emag.ro/biciclete-fitness/c?ref=hp_menu_quick-nav_651_2&type=category"
                }
    
    def start_requests(self):
        for category, url in self.start_urls.items():
            yield scrapy.Request(url=url, callback=self.parse, meta={'category':category})
    
    def parse(self, response):
        nb_of_products = response.xpath("//div[contains(@class, $classname)]/strong/text()",classname='js-listing-pagination')[1].get() 
        
        nb_of_pages = int(int(nb_of_products) / 60) + 1
        for idx in range(nb_of_pages):
            found_next_button_link =  response.css('a[aria-label]')[0].attrib['href']
            if found_next_button_link:
                next_button_link = 'https://www.emag.ro' + found_next_button_link
                yield scrapy.Request(next_button_link, callback=self.parse_next_page, meta={'category':response.meta['category']} )
            else:
                break
            
    
    def parse_next_page(self, response):
        products_urls = response.css('a.card-v2-title.semibold.mrg-btm-xxs.js-product-url')
        
        for product in products_urls:
            page_link = product.attrib['href']
            if page_link:
                yield scrapy.Request(page_link, callback=self.parse_product_page, meta={'category':response.meta['category']})
    
    
    def parse_product_page(self, response):
        base_link = response.url
        # base link : 'https://www.emag.ro/scaun-gaming-pentru-calculator-deus-extreme-hero-piele-sintetica-negru-albastru-boc-777extremezeroblack-blue/pd/DTBPWRBBM/'
        nr_reviews = response.css('p.text-muted::text').get()
        if nr_reviews is not None:
            nr_reviews = re.sub('\\n            ','', nr_reviews)
            nr_reviews = re.sub(' de review-uri\n        ','',nr_reviews)
            offset = 0
            aspects = response.css('td.col-xs-4.text-muted::text')
            aspects = [aspect.get() for aspect in aspects]
            
            if int(nr_reviews) >= 1:
                
                while  offset < int(nr_reviews):
                    base_link = re.sub("https://www.emag.ro/","",base_link)       
                    base_link = "https://www.emag.ro/product-feedback/" + base_link + "reviews/list"
                    print(f"Dowloading reviews from offset {offset}...")
                    params = {
                    'page[limit]': '100',
                    'page[offset]': str(offset),
                    'sort[created]': 'desc',
                    }
                    offset += 100
                    yield scrapy.FormRequest(url = base_link,method="GET", formdata=params, callback=self.parse_reviews, meta={'category':response.meta['category'],'aspects': aspects})
            
        
                
    def parse_reviews(self, response):
        jsonresponse = json.loads(response.body)
        jsonresponse = jsonresponse["reviews"]
        product_id = jsonresponse["first_item"]["product"]["id"]
        product_title = jsonresponse["first_item"]["product"]["name"]
        average_rating = 0
        count = int(jsonresponse["count"])
        rating_distirbution = jsonresponse["rating_distribution"]
        aspects = response.meta['aspects']
        aspects = ' | '.join(aspects)
        
        for item in rating_distirbution.items():
            average_rating += int(item[0]) *int(item[1])
        average_rating = average_rating/count
        
        reviews_items = jsonresponse["items"]
        for item in reviews_items:
            text_review = item["content"]
            rating = item["rating"]
            author = item["user"]["name"]
            yield {
                'product_code': product_id,
                'product_title':product_title,
                'average_rating': average_rating,
                'text': text_review,
                'rating': rating,
                'author': author,
                'country':'RO',
                'most_inner_category': response.meta['category'],
                'aspects' : aspects
                }
    