from urllib.parse import quote

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from bookparser import settings
from bookparser.spiders.chitai_gorod import ChitaiGorodSpider

if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(ChitaiGorodSpider)

    process.start()