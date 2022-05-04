"""
Домашнее задание к уроку 5:

Написать программу, которая собирает посты из группы https://vk.com/tokyofashion
Будьте внимательны к сайту! Делайте задержки, не делайте частых запросов!

1) В программе должен быть ввод, который передается в поисковую строку по постам группы
2) Соберите данные постов:
- Дата поста
- Текст поста
- Ссылка на пост(полная)
- Ссылки на изображения(если они есть; необязательно)
- Количество лайков, "поделиться" и просмотров поста
3) Сохраните собранные данные в MongoDB
4) Скролльте страницу, чтобы получить больше постов(хотя бы 2-3 раза)
5) (Необязательно) Придумайте как можно скроллить "до конца" до тех пор пока посты не перестанут добавляться

Чем пользоваться?
Selenium, можно пользоваться lxml, BeautifulSoup

Советы по дз:
1) Окно, которое мешает сбору данных появляется не сразу - напишите отдельную функцию для его поиска
Ну и подумайте как можно спровоцировать его появление и поймите что нужно нажать, чтобы продолжить работу с сайтом
2) Можете подумать как собрать все посты(скроллить "до упора"), но это необязательно, достаточно сделать 2-5 скроллов
3) Сделайте отдельную функцию, чтобы посылать запрос в поисковую строку по постам
"""

import time
from bs4 import BeautifulSoup
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


DRIVER_PATH = "../selenium_drivers/chromedriver.exe"
URL = "https://vk.com/tokyofashion"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    "Accept": "*/*",
}

MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "tokyofashion"
MONGO_COLLECTION = "posts"


class ScrapperVK:
    def __init__(self, string):
        self.posts = []
        self.str_input = string
        self.driver, self.actions = self.get_driver()

    @staticmethod
    def get_driver():
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(DRIVER_PATH, options=options)
        driver.get(URL)
        actions = ActionChains(driver)
        return driver, actions

    # Прокрутка вниз и закрытие окна авторизации:
    def close_window_auth(self):
        time.sleep(3)
        bottom_page = self.driver.find_element_by_id("page_search_posts")
        self.actions.move_to_element(bottom_page).perform()
        close = self.driver.find_element_by_class_name("UnauthActionBox__close")
        close.click()

    # Поиск постов по строке:
    def find_posts(self):
        # Перемещаемся по странице к строке поиска:
        cursor = self.driver.find_element_by_id("wall_tabs")
        self.actions.move_to_element(cursor).perform()
        time.sleep(3)
        # Нажимаем на лупу:
        button_search = self.driver.find_element_by_css_selector("a.ui_tab_search")
        button_search.click()
        time.sleep(3)
        # Ищем:
        search_wall = self.driver.find_element_by_class_name("ui_search_field")
        search_wall.clear()
        search_wall.send_keys(self.str_input)
        search_wall.send_keys(Keys.ENTER)

        # Скроллим страницы до 3х раз - добираемся до крайнего поста, чтобы открылись посты дальше:
        for i in range(3):
            time.sleep(3)
            last_post = self.driver.find_elements_by_class_name("post--withPostBottomAction")
            if not last_post:
                break
            self.actions.move_to_element(last_post[-1]).perform()

        html = self.driver.page_source
        self.driver.quit()
        return html

    # Извлечение данных и запись в БД:
    @staticmethod
    def extract_posts(html):
        soup = BeautifulSoup(html, "html.parser")
        posts = soup.find_all('div', class_='post--withPostBottomAction')
        for post in posts:
            date = post.find('span', class_='rel_date').text.replace('\xa0', ' ')
            content = post.find('div', class_='wall_post_text').text
            link = 'https://vk.com' + post.find('a', class_='post_link').get('href')
            likes = post.find('div', class_='PostButtonReactions__title').text
            shares = post.find('div', class_='_share').get('data-count')
            views = post.find('div', class_='like_views--inActionPanel')
            # Есть очень старые посты без просмотров, поэтому дополнительно проверяем:
            if views:
                views = views.find('span', class_='_views').text
            else:
                views = None
            # Запись в БД:
            with MongoClient(MONGO_HOST, MONGO_PORT) as client:
                db = client[MONGO_DB]
                collection = db[MONGO_COLLECTION]
                collection.update_one(
                    {
                        'link': link,
                    },
                    {
                        "$set": {
                            'date': date,
                            'content': content,
                            'likes': likes,
                            'shares': shares,
                            'views': views,
                        }
                    },
                    upsert=True,
                )

    def pipeline(self):
        self.close_window_auth()
        html = self.find_posts()
        self.extract_posts(html)


if __name__ == "__main__":
    try:
        str_input = input("Введите строку для поиска по постам группы: ")
        # str_input = 'Япония'
        scraper_vk = ScrapperVK(str_input)
        scraper_vk.pipeline()
    except Exception as e:
        print(e)
