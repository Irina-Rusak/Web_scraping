# 2. Зарегистрироваться на https://openweathermap.org/api и написать
# функцию, которая получает погоду в данный момент для города,
# название которого получается через input. https://openweathermap.org/current

import json
import requests
import os
from dotenv import load_dotenv

SAVE_WEATHER_PATH = "weather.json"
load_dotenv('./.env')


class WeatherCity:
    def __init__(self, city):
        self.url = 'https://api.openweathermap.org/data/2.5/weather?q=%s&appid=%s'
        self.city = city

    @staticmethod
    def get_api_key():
        return os.getenv('API_KEY_OPEN_WEATHER_MAP')

    def get_url(self, api_key):
        return self.url % (self.city, api_key)

    @staticmethod
    def get_info_weather(url):
        try:
            weather_info = requests.get(url)
            weather_info.raise_for_status()
            weather_info_json = weather_info.json()
            return weather_info_json
        except Exception as e:
            print(e)
        return None

    @staticmethod
    def save_weather_info(weather_info, path):
        with open(path, "w") as f:
            json.dump(weather_info, f, indent=2)
        print(f'Data written to file {path}.')

    def pipeline(self, path):
        try:
            api_key = self.get_api_key()
            url = self.get_url(api_key)
            data = self.get_info_weather(url)
            print(f'The weather in {self.city} is {data["main"]["temp"]} Kelvin.')
            self.save_weather_info(data, path)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    city_input = input("Please enter city: ")
    # city_input = "Minsk"
    weather = WeatherCity(city_input)
    weather.pipeline(SAVE_WEATHER_PATH)
