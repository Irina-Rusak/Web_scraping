import scrapy
from scrapy.http import TextResponse
from scrapy.loader import ItemLoader
from bookparser.items import BookparserItem


class ChitaiGorodSpider(scrapy.Spider):
    name = 'chitai_gorod'
    allowed_domains = ['chitai-gorod.ru']
    start_urls = ['https://www.chitai-gorod.ru/catalog/books/nauka_i_tekhnika-9170/']

    def parse(self, response: TextResponse, **kwargs):
        item_urls = response.xpath('//a[contains(@class, "product-card__link")]/@href').getall()
        for item_url in item_urls:
            print(f'https://www.chitai-gorod.ru/{item_url}')
            yield response.follow(f'https://www.chitai-gorod.ru/{item_url}', callback=self.parse_item)

    def parse_item(self, response: TextResponse):
        print()
        title_xpath = '//h1[contains(@class, "product__title")]/text()'
        img_url_list_xpath = '//div[@id="popup-gallery"]//li/@data-slide-original'
        price_xpath = '//div[@class="price"]/text()'
        item_info_xpath = '//div[@class="product__props"]'

        loader = ItemLoader(item=BookparserItem(), response=response)
        loader.add_value("url", response.url)
        loader.add_xpath("title", title_xpath)
        loader.add_xpath("prices", price_xpath)
        loader.add_xpath("item_info", item_info_xpath)
        loader.add_xpath("img_urls", img_url_list_xpath)

        yield loader.load_item()