import logging
import sys
import traceback

import requests
from bs4 import BeautifulSoup as bs

from settings import DB_NAME
from db import VacanciesShelve


class Parser:
    headers = {
        'authority': 'samara.hh.ru',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        # 'cookie': '__ddg1_=ci8hFZE0xigrEgzJjcRD; region_clarified=NOT_SET; hhtoken=UEEAtoHzyQ0ik2AOJPZ5zyUbnyQM; hhuid=p3bv_s3g69y49mUQSUZHNQ--; _ga=GA1.2.1469326932.1695566152; _ym_uid=1695566153202474942; _ym_d=1695566153; tmr_lvid=177a717c2be25dfd5ebb958ba0ecec5a; tmr_lvidTS=1695566152831; iap.uid=4aefe01705e3495385b98618acf1ba59; hhul=4bb52e8125fc4952a6cb0ff418089129502e272ff449179d5f43e33e10424cd7; _xsrf=0c898c473ecde0de2024d98fe444d50e; redirect_host=samara.hh.ru; hhrole=applicant; display=desktop; crypted_hhuid=1241CE5D8D8577B0138036553D53A0422B99D2927E8542CB1010C59C1C3EBE6A; crypted_id=8FFEAF68B9D1A130888399D7FCF9D558A5471C6F722104504734B32F0D03E9F8; GMT=4; _gid=GA1.2.1154119689.1695922054; _ym_isad=1; _ym_visorc=w; regions=113; total_searches=10; _hi=52000178; tmr_detect=1%7C1695924120467; cfidsgib-w-hh=ueMcferUmlkxEE4NCIxzpQTM9sL+eQk3+JtI6YEJR4LFibY0x0YFj/MpN4P5hJLj779oa9uy4Qrmfv++BKXowrtA3XAA4tIXGtWBWUm+ygOD5cZcdBtKOBGP0RxGQMdasgEqOVwj1AJoeSTc4nVaEjHWFeS7v0loNQ2jAb0=; gsscgib-w-hh=4axLsaFq1Hf/PHIzXG26vZxkrF/n4vyaVCfr8vpxoBRSkjfpw3yy8Pb4nLrsNsiG24V2m15wJnyGoFceAzrfdA/xCCfF/qyJztIDE7BuaWuQUFgC7HQ2aYNGmdGX/BHpSkAtP4MYcRkOTQ4rZGiSxrpMiSorivib4SN8/kC1bX3wuT7tDQ2MiV2+uLBPO85lIcQvbvd1PtrtsYDuBSP+4jmouEmqSufnTEBSXVDrS9TMBhBqgPZMPzf+FQYmZSbdZENI0aSCJ9NDZPtt0EEL; gsscgib-w-hh=4axLsaFq1Hf/PHIzXG26vZxkrF/n4vyaVCfr8vpxoBRSkjfpw3yy8Pb4nLrsNsiG24V2m15wJnyGoFceAzrfdA/xCCfF/qyJztIDE7BuaWuQUFgC7HQ2aYNGmdGX/BHpSkAtP4MYcRkOTQ4rZGiSxrpMiSorivib4SN8/kC1bX3wuT7tDQ2MiV2+uLBPO85lIcQvbvd1PtrtsYDuBSP+4jmouEmqSufnTEBSXVDrS9TMBhBqgPZMPzf+FQYmZSbdZENI0aSCJ9NDZPtt0EEL; _gali=HH-React-Root; device_magritte_breakpoint=m; device_breakpoint=m; __zzatgib-w-hh=MDA0dC0jViV+FmELHw4/aQsbSl1pCENQGC9LXy0vQWgmG0pcIEhafn1ZHEV3cydXOj9jPXZzLyluHyYZOVURCxIXRF5cVWl1FRpLSiVueCplJS0xViR8SylEW1Z+LhsUfW8nVw4MVy8NPjteLW8PKhMjZHYhP04hC00+KlwVNk0mbjN3RhsJHlksfEspNVcLMyYcEX9xVQwPQBQ/cissMUNoIWNKYCFDVlIKWR4RfmwqUAkNYUMzaWVpcC9gIBIlEU1HGEVkW0I2KBVLcU8cenZffSpBbiJoSVwlR1lVfy4Ve0M8YwxxFU11cjgzGxBhDyMOGFgJDA0yaFF7CT4VHThHKHIzd2UuPWUdX0hgJzVRP0FaW1Q4NmdBEXUmCQg3LGBwVxlRExpceEdXeisiFghtJlULD2NEQmllbQwtUlFRS2IPHxo0aQteTA==9MyVfA==; __zzatgib-w-hh=MDA0dC0jViV+FmELHw4/aQsbSl1pCENQGC9LXy0vQWgmG0pcIEhafn1ZHEV3cydXOj9jPXZzLyluHyYZOVURCxIXRF5cVWl1FRpLSiVueCplJS0xViR8SylEW1Z+LhsUfW8nVw4MVy8NPjteLW8PKhMjZHYhP04hC00+KlwVNk0mbjN3RhsJHlksfEspNVcLMyYcEX9xVQwPQBQ/cissMUNoIWNKYCFDVlIKWR4RfmwqUAkNYUMzaWVpcC9gIBIlEU1HGEVkW0I2KBVLcU8cenZffSpBbiJoSVwlR1lVfy4Ve0M8YwxxFU11cjgzGxBhDyMOGFgJDA0yaFF7CT4VHThHKHIzd2UuPWUdX0hgJzVRP0FaW1Q4NmdBEXUmCQg3LGBwVxlRExpceEdXeisiFghtJlULD2NEQmllbQwtUlFRS2IPHxo0aQteTA==9MyVfA==; fgsscgib-w-hh=rQpo749e684036e5ecbd768cb0dbfcd8c8e8b668; fgsscgib-w-hh=rQpo749e684036e5ecbd768cb0dbfcd8c8e8b668; cfidsgib-w-hh=KSs66UbNMJpahF829sG7eGyJpYxPaQOdA9x61dffi7FYQ4Ouu786OuLO5TvECIKlxcsl1oZNyu5HqqR4Kp1XtnT8FMjsW5Tuv5dbwbYUS7d+PpwKm+HhbQuo5Sjxes191DMitA+8ypbwgyXA7y1csihQHLbixO9WclilMAQ=; cfidsgib-w-hh=KSs66UbNMJpahF829sG7eGyJpYxPaQOdA9x61dffi7FYQ4Ouu786OuLO5TvECIKlxcsl1oZNyu5HqqR4Kp1XtnT8FMjsW5Tuv5dbwbYUS7d+PpwKm+HhbQuo5Sjxes191DMitA+8ypbwgyXA7y1csihQHLbixO9WclilMAQ=',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
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
        try:
            self.__found_new_vacancies()
        except BaseException as err:
            self.api['errors'] = self.__error_formatter(err)

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

        # Отлов ошибки временное
        if not soup:
            logging.info(f'Пустой soup. response: {response}')

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

                vacancys_soup = soup.find(id='a11y-main-content').find_all(class_='serp-item__title')

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

        db_connect = VacanciesShelve(DB_NAME)
        last_vacancies = db_connect.read_data('hh')
        new_vacancies = {}

        current_vacancies = self.__parse_vacancies()

        for vacancy_url, vacancy_name in current_vacancies.items():
            if vacancy_url not in last_vacancies:
                new_vacancies[vacancy_url] = vacancy_name

        logging.info(f'Выбрали новые вакансии. Количество новых: {len(new_vacancies)}')

        db_connect.write_data('hh', current_vacancies)

        logging.info(f'Записали текущие вакансии в db. Теперь в db вакансий: {len(db_connect.read_data("hh"))}')

        self.api['data'] = new_vacancies


if __name__ == '__main__':
    hh_parser = Parser()
    hh_parser.generate()
    print(hh_parser.api['data'])
