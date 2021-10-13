import logging
import os

import requests
from dotenv import load_dotenv

load_dotenv()
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
API_URL = 'http://{host}:{port}/stat/{method}/'
FILE = 'seances.txt'
FOLDER = 'audio'

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)


def main():
    logging.debug('Приложение запущенно')
    print('\nСкрипт скачивания аудио телефонных разговоров, АТС Infinity.\n'
          '------------------------------------------------------------\n\n'
          'Исходные данные — файл seances.txt, ожидаемый формат строки:\n'
          'seance_id, phone_number\n'
          '(без заголовков, одним столбцом, данные через ", ").\n'
          'На выходе — все аудио в папке audio, '
          'переименованные по номеру телефона абонента.\n\n'
          'Перед запуском убедитесь, '
          'что настройки в файле .env заполненны корректно.\n\n'
          'Всё готово? Начинаем? [y/n]')
    start = input()
    if start == 'y':
        processing_lines_of_the_file()
        logging.debug('Запуск скриптовой части подтверждён')
    else:
        logging.debug('Выполнение скриптовой части отклоненно пользователем')


def processing_lines_of_the_file():
    logging.debug('Попытка открыть файл со списком сеансов')
    try:
        with open(FILE) as register:
            for line in register:
                seance, phone = line.replace('\n', '').split(', ')
                logging_and_print_debug_message(
                    f'{seance} -> {phone} получен в обработку'
                )
                connection = get_connection_by_seance(seance)
                title = f'{FOLDER}/{phone}.wav'
                if len(connection) == 2:
                    get_recorded_file_by_connection(connection[1], title)
                else:
                    get_recorded_file_by_connection(connection[0], title)
                logging_and_print_debug_message(
                    f'{seance} -> {phone} полностью обработан'
                )
    except Exception as e:
        message = f'Неразрешимая ошибка: {e}'
        logging_and_print_error_message(message)


def get_connection_by_seance(seance):
    logging.debug(f'Попытка получить connection для {seance}')
    try:
        params = {
            'IDSeance': seance,
            'Recorded': 1
        }
        connection = requests.get(
            API_URL.format(host=HOST, port=PORT, method='connectionsbyseance'),
            params=params
        )
        logging.debug(f'Connection для {seance} получен')
        return connection.json()['result']['Connections']
    except ConnectionError as e:
        message = f'Не удалось получить connection для seance={seance}. {e}'
        logging_and_print_error_message(message)


def get_recorded_file_by_connection(connection, title):
    logging.debug(f'Попытка скачать файл {connection}')
    try:
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
        logging.debug(f'{title} успешно сохранён')
    except ConnectionError as e:
        message = f'Не удалось скачать {connection}. {e}'
        logging_and_print_error_message(message)


def logging_and_print_debug_message(message):
    logging.debug(message)
    print(message)


def logging_and_print_error_message(message):
    logging.error(message)
    print(message)


if __name__ == '__main__':
    main()
