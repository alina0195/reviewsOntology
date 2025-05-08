import scrapy
from chocolatescraper.spiders.chocolatespider import ChocolatespiderSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


process = CrawlerProcess(settings=get_project_settings())
process.crawl(ChocolatespiderSpider)
process.start()
