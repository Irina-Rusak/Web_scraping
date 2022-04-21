# 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев
# для конкретного пользователя, сохранить JSON-вывод в файле *.json; написать функцию,
# возвращающую(return) список репозиториев.

import json
import requests


SAVE_REPOSITORIES_PATH = "github_repositories.json"


class GitHub:
    def __init__(self, user_name):
        self.url = 'https://api.github.com/users/%s/repos'
        self.user_name = user_name

    def get_url_github(self):
        return self.url % self.user_name

    @staticmethod
    def get_info_user_repositories(url_user):
        try:
            rep_info = requests.get(url_user)
            rep_info.raise_for_status()
            rep_info_json = rep_info.json()
            return rep_info_json
        except Exception as e:
            print(e)
        return None

    @staticmethod
    def return_list_repositories(data):
        list_repositories = []
        for element in data:
            list_repositories.append(element["name"])
        return list_repositories

    @staticmethod
    def save_repositories_info(repos_info, path):
        with open(path, "w") as f:
            json.dump(repos_info, f, indent=2)
        print(f'Data written to file {path}.')

    def pipeline(self, path):
        try:
            url = self.get_url_github()
            data = self.get_info_user_repositories(url)
            print(f'Repositories of user {self.user_name}: {self.return_list_repositories(data)}')
            self.save_repositories_info(data, path)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    user_input = input("Please enter user name: ")
    # user_input = "Irina-Rusak"
    github = GitHub(user_input)
    github.pipeline(SAVE_REPOSITORIES_PATH)
