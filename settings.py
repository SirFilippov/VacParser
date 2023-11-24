import logging
import os
from os import getenv
from dotenv import load_dotenv

env_file = os.path.abspath('.env')
load_dotenv(env_file)

TOKEN = getenv('TOKEN')
ADMIN_ID = getenv('ADMIN_ID')

VAC_BOARDS = (
    'hh',
)

MONGO_COLLECTIONS = (
    'all',
    'last_request',
)
MONGO_PORT = 27017
MONGO_HOST = 'localhost'

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s]: %(message)s",
    encoding='utf-8',
)


"""
https://hh.ru/search/vacancy?text=Python+junior&items_on_page=20&employment=probation&employment=part&employment=full&employment=project&employment=volunteer&schedule=remote&area=113&professional_role=96&search_field=name&search_field=description&saved_search_id=69129685&no_magic=true&L_is_autosearch=true
"""