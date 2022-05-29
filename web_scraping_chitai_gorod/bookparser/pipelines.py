# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from scrapy.http import Request
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
import os

MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "books"

class BookparserPipeline:
    def process_item(self, item, spider):
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB]
        collection = db[spider.name]
        collection.update_one(
            {
                'url': item['url'],
            },
            {
                "$set": {
                    'title': item["title"],
                    'item_info': item["item_info"],
                    'prices': item["prices"],
                    'img_urls': item['img_urls']
                }
            },
            upsert=True,
        )
        return item


class BookparserImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item["img_urls"]:
            for img_url in item["img_urls"]:
                try:
                    path_image = f'image/{img_url.split("/")[-1].split("_")[0]}'
                    if not os.path.exists(path_image):
                        os.mkdir(path_image)
                    response = Request(img_url)
                    with open(f"{path_image}/{img_url.split('/')[-1]}", "wb") as f:
                        f.write(response.content)

                    yield Request(img_url)
                except Exception as e:
                    print(e)


    def item_completed(self, results, item, info):
        print("ITEM_COMPLETED")
        print()
        if results:
            item["img_info"] = [r[1] for r in results if r[0]]
            del item["img_urls"]
        print()
        return item