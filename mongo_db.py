from datetime import datetime
from pymongo import MongoClient
from settings import MONGO_HOST, MONGO_PORT, VAC_BOARDS, MONGO_COLLECTIONS

mongo_client = MongoClient(MONGO_HOST, MONGO_PORT)

# Создание бд и коллекций
for vac_board in VAC_BOARDS:
    if vac_board not in mongo_client.list_database_names():
        parser_db = mongo_client[vac_board]
        parser_db.create_collection('all')
        parser_db.create_collection('last_request')


class DBManager:
    def __init__(self):
        self.client = mongo_client

    def write_data(self, db: str, vacancies: dict) -> None:
        """Записывает данные в базу данных"""

        if db not in VAC_BOARDS or not isinstance(vacancies, dict):
            raise ValueError('Нет такого парсера или неподдерживаемый формат данных')
        else:
            self.__add_vacancies(db, vacancies)

    def read_data(self, db: str, request_type: str) -> dict:
        """ Читает данные из базы данных"""

        if db not in VAC_BOARDS or request_type not in MONGO_COLLECTIONS:
            raise ValueError('Нет такой площадки или Неподдерживаемый запрос')
        else:
            vacancies = self.__read_vacancies(db, request_type)
            return vacancies

    def __read_vacancies(self, db: str, request_type: str) -> dict:
        """Читает вакансии из базы данных

        :parameter db: str, наименование площадки сбора ваканский
        :parameter request_type: str, с какой коллекции берём данные
        :return: last_request_vacancies: dict, последние добавленные вакансии в формате {url: наимменование, ...}
        """

        collection = self.client[db][request_type]
        vacancies = collection.find()
        vacancies = sorted(vacancies, key=lambda x: x['add_datetime'], reverse=True)
        vacancies = {vac['url']: vac['name'] for vac in vacancies}
        return vacancies

    def __add_vacancies(self, db: str, data_to_add: dict) -> None:
        """Распределяет словарь последних взятых вакансий на две таблицы:
        - вакансии с последнего запроса
        - все вакансии

        При этом если во "всех" вакансиях есть вакансии "с последнего запроса", дата появления берется именно с
        даты во "всех" вакансиях для последующей сортировки по дате появления в бд

        :parameter db: str, наименование площадки сбора ваканский
        :parameter data_to_add: dict, вакансии в формате {url: наимменование, ...}
        :return: None
        """

        all_collection = self.client[db]['all']
        last_request_collection = self.client[db]['last_request']

        last_request_collection.delete_many({})

        for key, value in data_to_add.items():
            querry = {
                'url': key,
                'name': value,
            }

            new_vac = {
                'url': key,
                'name': value,
                'add_datetime': datetime.now(),
            }

            vac_is_exist = all_collection.find_one(querry)

            if vac_is_exist:
                new_vac['add_datetime'] = vac_is_exist['add_datetime']
                last_request_collection.insert_one(new_vac)
            else:
                last_request_collection.insert_one(new_vac)
                all_collection.insert_one(new_vac)


if __name__ == '__main__':
    a = DBManager()

    # data = {1: 'afsdf',}

    # a.write_data('hh', data)

    print(a.read_data('hh', 'last_request'))
