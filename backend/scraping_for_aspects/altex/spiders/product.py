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
            "TV": ("https://altex.ro/televizoare/cpl/","televizoare"),
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
        # https://altex.ro/trepied-hama-4613-26-cm-negru/cpd/TRP4613/#additional
        for product in products["products"]:
            item_id = product["id"]
            title = product["name"]
            sku = product['sku']
            url_key = product['url_key']
            
            yield scrapy.Request(
                url=f"https://altex.ro/{url_key}/cpd/{sku}/#additional",
                headers={"User-Agent": "Mozilla/5.0"},
                callback=self.parse_specs,
                meta={"title": title, "id": item_id},
            )
            

    def parse_specs(self, response):
        aspects = response.css('th.text-gray-1200 ::text')
        aspects = [a.get() for a in aspects]
        aspects = ' | '.join(aspects)
        yield {
            "product_code": response.meta["id"],
            "product_title": response.meta["title"],
            "aspects": aspects
        }
