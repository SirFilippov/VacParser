import shelve
from typing import Any


class VacanciesShelve:
    def __init__(self, db_name: str):
        self.db_name = f'{db_name}.txt'

    def write_data(self, key_to_save: str, data: Any):
        """ Записывает данные в базу данных"""

        with shelve.open(self.db_name, writeback=True) as db:
            db[key_to_save] = data

    def read_data(self, key_to_read: str):
        """ Читает данные из базы данных"""

        with shelve.open(self.db_name) as db:
            if key_to_read in db:
                return db[key_to_read]
            else:
                return {}


if __name__ == "__main__":
    last_vacancies = VacanciesShelve('vacancies').read_data('hh')
    print(last_vacancies)