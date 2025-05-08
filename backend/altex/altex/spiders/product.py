import scrapy
import json


class ProductSpider(scrapy.Spider):
    name = "product"
    allowed_domains = ["altex.ro"]

    def start_requests(self):
        """Enter the main website.

        Yields:
            url: URL of the site itself.
            callback: procesing function to get articles.
        """
        start_urls_dummy = [
            "https://fenrir.altex.ro/catalog/category/trepiede-camere-foto-video?page=1&size=1000",
        ]
        start_urls = {
            "Tripod":("https://altex.ro/trepiede-camere-foto-video/cpl/","trepiede-camere-foto-video"),
            "VacuumCleaner":("https://altex.ro/aspiratoare/cpl/","aspiratoare"),
            "GamingHeadset": ("https://altex.ro/casti-calculator/cpl/","casti-calculator"),
            "FitnessBike" : ("https://altex.ro/biciclete-fitness/cpl/","biciclete-fitness"),
            "TV":("https://altex.ro/televizoare/cpl/","televizoare"),
            "Scooter":("https://altex.ro/trotinete-electrice/cpl/","trotinete-electrice"),
            "ControllerAndSteeringWheel":("https://altex.ro/volane-gaming/cpl/","volane-gaming")
            }
        
        for category, url in start_urls.items():
            url = "https://fenrir.altex.ro/catalog/category/"+url[1]+"?page=1&size=1000"
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta = {'category':category}
            )

    def parse(self, response):
        products = json.loads(response.body)
        for product in products["products"]:
            item_id = product["id"]
            title = product["name"]
            if product["reviews_value"] == 0 or product["reviews_count"] == 0:
                average_rating = 0
            else:
                average_rating = product["reviews_value"] / product["reviews_count"]

            yield scrapy.Request(
                url=f"https://fenrir.altex.ro/review/reviews/?limit=100&productId={item_id}&page=0&sortBy=date&orderBy=desc",
                headers={"User-Agent": "Mozilla/5.0"},
                callback=self.parse_product_review,
                meta={"title": title, "id": item_id, "average_rating": average_rating,'category':response.meta['category']},
            )

    def parse_product_review(self, response):
        reviews = json.loads(response.body)
        for review in reviews["items"]:
            yield {
                "product_code": response.meta["id"],
                "product_title": response.meta["title"],
                "average_rating": response.meta["average_rating"],
                "text": review["body"],
                "rating": review["rating"],
                "author": review["customer"]["name"],
                "country": "RO",
                "most_inner_category": response.meta['category']
            }
