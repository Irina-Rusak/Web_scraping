# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import re

MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "jobs"


# вариант получше здесь -
# https://docs.scrapy.org/en/latest/topics/item-pipeline.html#write-items-to-mongodb
class JobparserPipeline:

    def __init__(self):
        self.client = MongoClient(MONGO_HOST, MONGO_PORT) # доработать
        self.db = self.client[MONGO_DB]

    def process_salary_hh(self, salary_list: list):
        if salary_list[0] != 'з/п не указана' and salary_list:
            salary = "".join(salary_list)
            salary = salary.replace('\xa0', '')
            salary = salary.split(' ')
            if salary[0] == 'от':
                min_salary = int(salary[1])
                if salary[2] == 'до':
                    max_salary = int(salary[3])
                    currency = salary[4]
                else:
                    max_salary = None
                    currency = salary[2]
            else:
                if salary[0] == 'до':
                    min_salary = None
                    max_salary = int(salary[1])
                    currency = salary[2]
                else:
                    min_salary = int(salary[0])
                    max_salary = int(salary[2])
                    currency = salary[3]
        else:
            min_salary = None
            max_salary = None
            currency = None
        return min_salary, max_salary, currency

    def process_salary_sj(self, salary_list: list):
        if salary_list[0] != 'По договорённости' and salary_list:
            salary_list = [element.replace('\xa0', '') for element in salary_list]
            salary = [element for element in salary_list if element]
            if salary[0] == 'от':
                min_salary = int(re.findall(r'\d+', salary[1])[0])
                max_salary = None
                currency = re.findall(r'\D+', salary[1])[0]
            else:
                if salary[0] == 'до':
                    min_salary = None
                    max_salary = int(re.findall(r'\d+', salary[1])[0])
                    currency = re.findall(r'\D+', salary[1])[0]
                else:
                    if len(salary) == 2:
                        min_salary = int(salary[0])
                        max_salary = int(salary[0])
                        currency = salary[1]
                    else:
                        min_salary = int(salary[0])
                        max_salary = int(salary[2])
                        currency = salary[3]
        else:
            min_salary = None
            max_salary = None
            currency = None
        return min_salary, max_salary, currency

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            item["salary_min"], item["salary_max"], item["salary_currency"] = self.process_salary_hh(item["salary"])
        if spider.name == 'sjru':
            item["salary_min"], item["salary_max"], item["salary_currency"] = self.process_salary_sj(item["salary"])
        item["title"] = " ".join(item["title"])
        item.pop("salary")
        collection = self.db[spider.name]
        collection.update_one(
            {
                'url': item['url'],
            },
            {
                "$set": {
                    'title': item['title'],
                    'salary_min': item["salary_min"],
                    'salary_max': item["salary_max"],
                    'salary_currency': item["salary_currency"]
                }
            },
            upsert=True,
        )
        return item