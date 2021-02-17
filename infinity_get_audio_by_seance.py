import os

import requests
from dotenv import load_dotenv

load_dotenv()
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
API_URL = 'http://{host}:{port}/stat/{method}/'
FILE = 'seances.txt'
FOLDER = 'audio'


def welcome():
    print('\nСкрипт скачивания аудио по IVR-кампании.\n'
          '----------------------------------------\n\n'
          'Исходные данные — файл seances.txt, ожидаемый формат строки:\n'
          'seance_id, phone_number\n'
          '(без заголовков, одним столбцом, данные через ", ")\n\n'
          'Перед запуском убедитесь, '
          'что настройки в файле .env заполненны корректно.\n\n'
          'Всё готово? Начинаем? [y/n]')
    start = input()
    if start == 'y':
        processing_lines_of_the_file()


def processing_lines_of_the_file():
    with open(FILE) as register:
        for line in register:
            seance, phone = line.replace('\n', '').split(', ')
            connection = get_connection_by_seance(seance)
            title = f'{FOLDER}/{phone}.wav'
            get_recorded_file_by_connection(connection, title)


def get_connection_by_seance(seance):
    params = {
        'IDSeance': seance,
        'Recorded': 1
    }
    connection = requests.get(
        API_URL.format(host=HOST, port=PORT, method='connectionsbyseance'),
        params=params
    )
    return connection.json()['result']['Connections'][0]


def get_recorded_file_by_connection(connection, title):
    params = {
        'IDConnection': connection
    }
    sound = requests.post(
        API_URL.format(host=HOST, port=PORT, method='getrecordedfile'),
        params=params,
        stream=True
    )
    with open(title, 'wb') as audio_file:
        for chunk in sound.iter_content(chunk_size=128):
            audio_file.write(chunk)


welcome()
