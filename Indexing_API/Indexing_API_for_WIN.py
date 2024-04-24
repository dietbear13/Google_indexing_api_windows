import json
import time
import traceback
from datetime import datetime
import os
import httplib2
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

project_name = 'input_urls'

SCOPES = ["https://www.googleapis.com/auth/indexing"]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"


def send_pages_to_index(data, key):
    json_key_file = f"./{key}.json"
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_key_file, scopes=SCOPES)
    http = credentials.authorize(httplib2.Http())

    sent_urls_for_recrawl_set = set()
    for url in data:
        urls = {
            'url': '{}'.format(url),
            'type': 'URL_UPDATED'
        }

        response, content = http.request(ENDPOINT, method="POST", body=json.dumps(urls))
        now = datetime.now().strftime("%H:%M:%S")
        print(f"{now}, страница {url} - успешно, код {response['status']}")

        time.sleep(1)

        if response['status'] != '200':
            raise Exception(f"{now}, ошибка {content['type']} → код ответа {response['status']}")

        sent_urls_for_recrawl_set.add(url)

    return sent_urls_for_recrawl_set


def delete_sent_urls_and_export_new_table(main_urls_set, sent_urls_for_index_set):
    main_urls_set_without_sent_urls = main_urls_set - sent_urls_for_index_set
    rest_urls_list = list(main_urls_set_without_sent_urls)
    data = pd.DataFrame({'urls': rest_urls_list})
    export_data_to_excel(data)


def send_pages_to_google(data, key_column_index, key):
    main_urls_set = set(data.iloc[:, key_column_index].to_list())
    sent_urls_for_recrawl_set = send_pages_to_index(main_urls_set, key)
    delete_sent_urls_and_export_new_table(main_urls_set, sent_urls_for_recrawl_set)
    print("Адрес отправлен на переобход и удален из таблицы исходной")


def error_report():
    print(f'Ошибка → {traceback.print_exc()}')
    # traceback.print_exc()


current_directory = os.path.dirname(__file__)

current_path = open("path.txt").read()

project_file_path = os.path.join(current_path, f'{project_name}.xlsx')


def export_data_to_excel(data):
    export_file_path = os.path.join(current_path, f'{project_name}.xlsx')
    data.to_excel(export_file_path, index=False)


def main():
    input_keys = pd.read_excel(os.path.join(current_path, 'input_keys.xlsx'), engine='openpyxl', header=None)
    input_keys_list = input_keys.iloc[:, 0].tolist()
    table_with_urls_for_recrawl = pd.read_excel(project_file_path, engine='openpyxl')

    if table_with_urls_for_recrawl.empty:
        print("Страницы в таблице input_urls.xlsx закончились")
        return

    key_column_index = 0
    print("Все ключи:\n", input_keys)

    for key in input_keys_list:
        print(f'Используется ключ: {key}')
        send_pages_to_google(table_with_urls_for_recrawl, key_column_index, key)


if __name__ == "__main__":
    main()
