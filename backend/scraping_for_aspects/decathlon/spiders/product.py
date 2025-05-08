import scrapy
import json
import re

class ProductSpider(scrapy.Spider):
    name = "product"
    allowed_domains = ["www.decathlon.ro"]

    def start_requests(self):
        """Enter the main website.

        Yields:
            url: URL of the site itself.
            callback: procesing function to get articles.
        """
        start_urls = {
            "Boots":"https://www.decathlon.ro/browse/c0-barbati/c1-incaltaminte-barbati/c2-ghete-si-bocanci-barbati/_/N-1m4zxfp",
            "Ski":"https://www.decathlon.ro/browse/c0-barbati/c1-echipament-sportiv-barbati/c2-schi-barbati/_/N-1j769xy",
            "Scooters":"https://www.decathlon.ro/browse/c0-barbati/c1-echipament-sportiv-barbati/c2-trotinete-barbati/_/N-113nkgu",
            "Squash_Racket":"https://www.decathlon.ro/browse/c0-toate-sporturile/c1-squash/c2-rachete-si-huse-squash/_/N-d9dy9s ",
            "Fitness_Bike":"https://www.decathlon.ro/browse/c0-toate-sporturile/c1-fitness/c3-biciclete-fitness/_/N-iocek4"
        }
        
        for category, url in start_urls.items():
            for i in range(0, 374, 34):
                yield scrapy.Request(
                    url=f"{url}?from={i}&size={34}",
                    callback=self.parse,
                    meta={"category":category}
                )

    def parse(self, response):
        products = response.xpath(
            "//div[contains(@class, 'product-list')]/div[contains(@role, 'listitem')]/div/a[contains(@class, 'dpb-product-model-link')]/@href"
        ).getall()
        titles = response.xpath(
            "//div[contains(@class, 'product-list')]/div[contains(@role, 'listitem')]/div/a[contains(@class, 'dpb-product-model-link')]/span/text()"
        ).getall()
        nbOfReviews =  response.xpath(
            "//div[contains(@class, 'product-list')]/div[contains(@role, 'listitem')]/div/a[contains(@class, 'dpb-reviews')]/div/span[contains(@class,'vtmn-rating_comment--secondary')]/text()"
        ).getall()
        if nbOfReviews:
            for product, title, nb in zip(products, titles, nbOfReviews):
                item_id = product.split("?mc=")[1]
                item_id = item_id[:8]
                # https://www.decathlon.ro/r/bocanci-mid-impermeabili-drumetie-la-munte-mh100-negru-barbati/_/R-p-307814?mc=8553119&c=NEGRU
                # https://www.decathlon.ro/p/bocanci-mid-impermeabili-drumetie-la-munte-mh100-negru-barbati/_/R-p-307814?mc=8553119&c=NEGRU
                yield scrapy.Request(
                        url=f"https://www.decathlon.ro/p/{product}",
                        headers={"User-Agent": "Mozilla/5.0"},
                        callback=self.parse_product_page,
                        meta={"title": title, "id": item_id,"category":response.meta['category']},
                    )

    def parse_product_page(self,response):
        aspects =  response.css('h3.svelte-102uyjc::text')
        if len(aspects)>0:
            aspects = [a.get() for a in aspects]
            aspects = ' | '.join(aspects)
            yield {
                "product_code": response.meta["id"],
                "product_title": response.meta["title"],
                "most_inner_category": response.meta["category"],
                "aspects": aspects
            }
                       