import scrapy
from altex.spiders.product import ProductSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


process = CrawlerProcess(settings=get_project_settings())
process.crawl(ProductSpider)
process.start()
