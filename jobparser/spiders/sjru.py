import scrapy
from scrapy.http import TextResponse

from ..items import JobparserItem

TEMPLATE_URL = "https://russia.superjob.ru/vacancy/search/?keywords="

class SJruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    max_page_number = 2

    def __init__(self, query, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [TEMPLATE_URL + query]


    def parse_item(self, response: TextResponse):
        title_xpath = '//h1[contains(@class, "KySx7 Oert7 _2APER Q0JS1 _2L5ou _1TcZY Bbtm8")]//text()'
        salary_xpath = '//span[contains(@class, "_2eYAG -gENC _1TcZY dAWx1")]//text()'
        title = response.xpath(title_xpath).getall()
        salary = response.xpath(salary_xpath).getall()
        item = JobparserItem()
        item["title"] = title
        item["salary"] = salary
        item["url"] = response.url
        yield item

    def parse(self, response: TextResponse, page_number: int = 1, **kwargs):
        items = response.xpath('//a[contains(@class, "YrERR")]')
        for item in items:
            url = 'https://russia.superjob.ru' + item.xpath("./@href").get()
            yield response.follow(url, callback=self.parse_item)

        next_url = 'https://russia.superjob.ru' + \
                         response.xpath('//a[contains(@class, "f-test-link-Dalshe")]/@href').get()
        if next_url and page_number < self.max_page_number:
            new_kwargs = {
                "page_number": page_number + 1,
            }
            yield response.follow(
                next_url,
                callback=self.parse,
                cb_kwargs=new_kwargs
            )