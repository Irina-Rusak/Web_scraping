# Необходимо собрать информацию о вакансиях на вводимую должность (используем input)
# с сайтов Superjob(необязательно) и HH(обязательно).
# Приложение должно анализировать несколько страниц сайта (также вводим через input).
# Получившийся список должен содержать в себе минимум:
# 1) Наименование вакансии.
# 2) Предлагаемую зарплату (отдельно минимальную и максимальную;
# дополнительно - собрать валюту; можно использовать regexp или if'ы).
# 3) Ссылку на саму вакансию.
# 4) Сайт, откуда собрана вакансия.
# По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
# Структура должна быть одинаковая для вакансий с обоих сайтов. Сохраните результат в json-файл.

import time
import json
import requests
from bs4 import BeautifulSoup

# https://hh.ru/search/vacancy?text=python&page=0
url_hh = 'https://hh.ru/search/vacancy'
params_hh = {
    'text': 'python',
    'page': 0,
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    "Accept": "*/*",
}
save_file = 'vacancy_hh.json'


class VacancyScrapperHH:
    def __init__(self, url, vacancy, page):
        self.url = url
        self.vacancy = vacancy
        self.page_number = page
        self.headers = headers
        self.params = self.create_params()
        self.bank_vacancy = []

    def create_params(self):
        params_hh['text'] = self.vacancy
        return params_hh

    def get_html_string(self):
        try:
            response = requests.get(self.url, params=self.params, headers=self.headers)
            response.raise_for_status()
            time.sleep(1)
        except Exception as error:
            print(error)
            time.sleep(1)
            return None
        return response.text

    @staticmethod
    def get_dom(html_string):
        return BeautifulSoup(html_string, "html.parser")

    @staticmethod
    def get_salary(salary):
        if salary:
            salary = salary.text.replace('\u202f', '')
            salary = salary.split(' ')
            if salary[0] == 'от':
                min_salary = salary[1]
                max_salary = None
                currency = salary[2]
            else:
                if salary[0] == 'до':
                    min_salary = None
                    max_salary = salary[1]
                    currency = salary[2]
                else:
                    min_salary = salary[0]
                    max_salary = salary[2]
                    currency = salary[3]
        else:
            min_salary = None
            max_salary = None
            currency = None
        return min_salary, max_salary, currency

    def get_info_vacancy_hh(self, soup):
        vacancy_elements = soup.find_all('div', class_='vacancy-serp-item__layout')
        for element in vacancy_elements:
            title = element.find('a', class_='bloko-link').text.strip()
            salary = element.find('span', class_='bloko-header-section-3')
            min_salary, max_salary, currency = self.get_salary(salary)
            link = element.find('a', class_='bloko-link').get('href')
            vacancy = dict(title=title, min_salary=min_salary, max_salary=max_salary,
                           currency=currency, link=link, source='https://hh.ru/')
            self.bank_vacancy.append(vacancy)

    def pipeline(self):
        for page in range(0, self.page_number):
            print(f'Getting data from page {page+1}')
            self.params['page'] = page
            response = self.get_html_string()
            soup = self.get_dom(response)
            self.get_info_vacancy_hh(soup)
        return self.bank_vacancy

    @staticmethod
    def save_json(data, path):
        with open(path, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f'Data written to file {path}.')


if __name__ == "__main__":
    try:
        vacancy_input = input("Please enter vacancy: ")
        page_number = int(input("Please enter number of pages: "))
        scraper_hh = VacancyScrapperHH(url_hh, vacancy_input, page_number)
        data_vacancy = scraper_hh.pipeline()
        scraper_hh.save_json(data_vacancy, save_file)
    except Exception as e:
        print(e)
