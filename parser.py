import logging
import traceback

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
        'saved_search_id': '69129685',
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
        # try:
        #     self.__found_new_vacancies()
        # except BaseException as err:
        #     self.api['errors'] = self.__error_formatter(err)

        return self.api

    def clear_cache(self):
        self.api = {
            'data': {},
            'errors': '',
        }

    @staticmethod
    def __error_formatter(err_obj: BaseException):
        traceback_str = traceback.format_exc()
        traceback_str = traceback_str.split("\n")[1].strip()
        error_formatted = f'{traceback_str}: {err_obj.__str__()}'
        return error_formatted

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
                vacancys_soup = soup.find(id='a11y-main-content')

                # Отлов ошибки временное
                try:
                    vacancys_soup = vacancys_soup.find_all(class_='serp-item__title')
                except AttributeError as err:
                    with open('error_response.html', mode='w', encoding='utf-8') as res_file:
                        res_file.write(vacancys_soup.text)
                    logging.info(f'Пустой vacancys_soup. текст супа сохранён')
                    self.api['errors'] = self.__error_formatter(err)
                    break

            else:
                self.params['page'] = str(page)
                page_soup = self.sess.get('https://hh.ru/search/vacancy', params=self.params)
                page_soup = bs(page_soup.text, 'lxml')
                vacancys_soup = page_soup.find(id='a11y-main-content').find_all(class_='serp-item__title')

            for vacancy in vacancys_soup:
                link = vacancy['href']
                name = vacancy.text
                vacancys_data[link] = name

        self.params['page'] = '0'

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
    hh_parser = Parser()
    hh_parser.generate()
    print(hh_parser.api['data'])
