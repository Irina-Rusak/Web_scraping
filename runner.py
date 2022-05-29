from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from jobparser.spiders.hhru import HHruSpider
from jobparser.spiders.sjru import SJruSpider
from jobparser import settings

if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)

    job_kwargs = {"query": "data"}
    process.crawl(HHruSpider, **job_kwargs)
    process.crawl(SJruSpider, **job_kwargs)

    process.start()
