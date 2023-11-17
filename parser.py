import copy
import logging
import time
import traceback
from datetime import datetime
import os

import bs4
import requests
from bs4 import BeautifulSoup as bs

from mongo_db import DBManager


class Parser:
    headers = {
        'authority': 'samara.hh.ru',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/117.0.0.0 Safari/537.36',
    }

    params = {
        'text': 'Python junior',
        'salary': '',
        'employment': [
            'probation',
            'part',
            'full',
            'project',
            'volunteer',
        ],
        'schedule': 'remote',
        'professional_role': '96',
        # 'saved_search_id': '69129685',
        'no_magic': 'true',
        'ored_clusters': 'true',
        'items_on_page': '20',
        'search_field': [
            'name',
            'description'
        ],
        'area': '113',
        'page': '0'
    }

    def __init__(self):
        self.sess = requests.Session()
        self.sess.headers.update(self.headers)
        self.api = {
            'data': {},
            'errors': '',
                    }

    def generate(self):
        self.__found_new_vacancies()
        return self.api

    @staticmethod
    def error_formatter(err_obj: BaseException):
        traceback_str = traceback.format_exc()
        traceback_str = traceback_str.split("\n")[1].strip()
        error_formatted = f'{traceback_str}: {err_obj.__str__()}'
        return error_formatted

    def __vacansys_founder(self, soup: bs4.BeautifulSoup, response: requests.Response) -> list:
        try:
            vacancys_soups = soup.find(id='a11y-main-content').find_all(class_='serp-item__title')
            return vacancys_soups
        except AttributeError as err:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if not os.path.exists('errors'):
                os.makedirs('errors')

            with open(f'./errors/response_{now}.html', mode='w', encoding='utf-8') as file:
                file.write(response.text)
                print('\nHeaders:')
                for header, value in response.headers.items():
                    file.write(f"{header}: {value}\n")

            logging.info(f'Нет элементов в soup. Текст супа сохранён. Повторная попытка.')
            self.api['errors'] = self.error_formatter(err)

            time.sleep(5)
            self.__vacansys_founder(soup, response)

    def __parse_vacancies(self) -> dict:
        """
        Парсит текущие вакансии по заданному фильтру
        :return: Возвращает словарь в виде: {url: *vacancy_name*, url: *vacancy_name*, ...}
        """

        vacancys_data = {}
        response = self.sess.get('https://hh.ru/search/vacancy', params=self.params)
        soup = bs(response.text, 'lxml')

        # Ищем количество страниц с вакансиями
        page_value = soup.find(class_='pager')
        if page_value:
            page_value = len(page_value.find_all('span', recursive=False))
        else:
            page_value = 1

        # page_value = 1

        # Парсим названия и линки на вакансии
        for page in range(page_value):
            if page == 0:
                vacancys_soup = self.__vacansys_founder(soup, response)
            else:
                params = copy.copy(self.params)
                params['page'] = page
                page_response = self.sess.get('https://hh.ru/search/vacancy', params=params)
                page_soup = bs(page_response.text, 'lxml')
                vacancys_soup = self.__vacansys_founder(page_soup, page_response)

            for vacancy in vacancys_soup:
                link = vacancy['href']
                vacancys_data[link] = vacancy.text

        logging.info(f'Собрали вакансии. Количество страниц: {page_value} Количество вакансий: {len(vacancys_data)}')

        return vacancys_data

    def __found_new_vacancies(self) -> None:
        """
        Сравнивает только что полученные вакансии с последними в бд
        Если есть новые вакансии форматирует, вставляя url в имя вакансии
        :return: Новые вакансии в виде: {url: *vacancy_name*, url: *vacancy_name*, ...}
        """

        db_connect = DBManager()
        all_vacancies = db_connect.read_data('hh', 'all')
        new_vacancies = {}

        current_vacancies = self.__parse_vacancies()

        for vacancy_url, vacancy_name in current_vacancies.items():
            if vacancy_url not in all_vacancies:
                new_vacancies[vacancy_url] = vacancy_name

        logging.info(f'Выбрали новые вакансии. Количество новых: {len(new_vacancies)}')

        db_connect.write_data('hh', current_vacancies)

        logging.info(f'Записали текущие вакансии в db. Теперь в db вакансий: {len(db_connect.read_data("hh", "all"))}')

        self.api['data'] = new_vacancies


if __name__ == '__main__':
    while True:
        hh_parser = Parser()
        hh_parser.generate()
        # print(hh_parser.api['data'])
        time.sleep(5)
