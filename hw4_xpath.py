# Домашнее задание к уроку 4:
# 1. Написать приложение (используя XPath, нельзя использовать BeautifulSoup),
# которое собирает основные (главные) новости с сайтов news.mail.ru, lenta.ru, yandex.news.
# Структура данных должна содержать:
# - название источника (mail и яндекс не источники, а аггрегаторы, см. страницу новости);
# - наименование новости;
# - ссылку на новость;
# - дата публикации.
# 2. Сложить все новости в БД, новости должны обновляться, т.е. используйте update или upsert.
# Минимум один сайт, максимум - все три.


import requests
from pprint import pprint
from lxml.html import fromstring
from datetime import datetime
from pymongo import MongoClient

URL = "https://yandex.ru/news/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    "Accept": "*/*",
}
ITEMS_XPATH = '//section[1]//div[contains(@class, "mg-grid__col")]'
HREF_XPATH = './/h2[contains(@class, "mg-card__title")]/a/@href'
TITLE_XPATH = './/h2[contains(@class, "mg-card__title")]/a/text()'
SOURCE_XPATH = './/span[contains(@class, "mg-card-source__source")]//a/text()'
TIME_XPATH = './/span[contains(@class, "mg-card-source__time")]/text()'

MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "news"
MONGO_COLLECTION = "main_news_today"


class MainNews:
    def __init__(self):
        self.news_list = []

    @staticmethod
    def get_dom():
        r = requests.get(URL, headers=HEADERS)
        dom = fromstring(r.text)
        return dom

    # Получение новостей и запись в БД (если запись уже есть -> обновить):
    def get_info_news(self, items):
        for item in items:
            info = {}
            info["href"] = item.xpath(HREF_XPATH)[0]
            info["title"] = item.xpath(TITLE_XPATH)[0].replace('\xa0', ' ')
            info["source"] = item.xpath(SOURCE_XPATH)[0]
            info["time"] = self.get_datetime(item.xpath(TIME_XPATH)[0])
            # print(info)
            self.news_list.append(info)

            with MongoClient(MONGO_HOST, MONGO_PORT) as client:
                db = client[MONGO_DB]
                collection = db[MONGO_COLLECTION]
                collection.update_one(
                    {
                        'title': info['title'],
                    },
                    {
                        "$set": {
                            'href': info['href'],
                            'source': info["source"],
                            'time': info["time"]
                        }
                    },
                    upsert=True,
                )

    # Обработка времени в формат даты:
    @staticmethod
    def get_datetime(time):
        date_time = f'{str(datetime.now().date())} {time}'
        return datetime.strptime(date_time, '%Y-%m-%d %H:%M')

    @staticmethod
    def read_db():
        with MongoClient(MONGO_HOST, MONGO_PORT) as client:
            db = client[MONGO_DB]
            collection = db[MONGO_COLLECTION]
            return list(collection.find())

    def pipeline(self):
        dom = self.get_dom()
        items = dom.xpath(ITEMS_XPATH)
        self.get_info_news(items)
        # pprint(self.read_db())


if __name__ == "__main__":
    try:
        news_today = MainNews()
        news_today.pipeline()
    except Exception as e:
        print(e)
