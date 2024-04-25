import json
import os
import time
import traceback
from datetime import datetime, date

import httplib2
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

project_name = 'input_urls'

SCOPES = ["https://www.googleapis.com/auth/indexing"]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

request_counters = {}


def send_pages_to_index(data, key, log_file):
    json_key_file = f"./{key}.json"
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_key_file, scopes=SCOPES)
    http = credentials.authorize(httplib2.Http())

    request_counter = request_counters.get(key, 0)

    sent_urls_for_recrawl_set = set()
    for url in data:
        urls = {
            'url': '{}'.format(url),
            'type': 'URL_UPDATED'
        }

        response, content = http.request(ENDPOINT, method="POST", body=json.dumps(urls))
        now = datetime.now().strftime("%H:%M:%S")

        time.sleep(1)

        if response['status'] != '200':
            print(f"{date.today()} - {now},  ошибка, {now}, ключ {key} - код ответа {response['status']}")
            log_file.write(f"{date.today()} - {now},  ошибка, ключ {key} - код ответа {response['status']}")
            break

        else:
            log_line = f"{date.today()} - {now}, страница {url} - успешно, код {response['status']}"
            print(log_line)
            log_file.write(log_line + '\n')

            sent_urls_for_recrawl_set.add(url)

            request_counter += 1

    request_counters[key] = request_counter

    return sent_urls_for_recrawl_set


def delete_sent_urls_and_export_new_table(main_urls_set, sent_urls_for_index_set):
    main_urls_set_without_sent_urls = main_urls_set - sent_urls_for_index_set
    rest_urls_list = list(main_urls_set_without_sent_urls)
    data = pd.DataFrame({'urls': rest_urls_list})
    export_data_to_excel(data)


def send_pages_to_google(data, key_column_index, key, log_file):
    now = datetime.now().strftime("%H:%M:%S")

    main_urls_set = set(data.iloc[:, key_column_index].to_list())
    sent_urls_for_recrawl_set = send_pages_to_index(main_urls_set, key, log_file)
    delete_sent_urls_and_export_new_table(main_urls_set, sent_urls_for_recrawl_set)
    log_file.write(f"{date.today()} - {now}, адрес отправлен на переобход и удален из таблицы исходной\n")


def error_report(log_file):
    now = datetime.now().strftime("%H:%M:%S")
    error_msg = f"{date.today()} - {now}, ошибка - {traceback.format_exc()}"
    print(error_msg)
    log_file.write(error_msg + '\n')


current_directory = os.path.dirname(__file__)
current_path = open("current_path.txt").read()
project_file_path = os.path.join(current_path, f'{project_name}.xlsx')


def export_data_to_excel(data):
    export_file_path = os.path.join(current_path, f'{project_name}.xlsx')
    data.to_excel(export_file_path, index=False)


def main():
    log_filename = f"{date.today()}_logs.txt"
    with open(log_filename, 'a') as log_file:
        input_keys = pd.read_excel(os.path.join(current_path, 'input_keys.xlsx'), engine='openpyxl', header=None)
        input_keys_list = input_keys.iloc[:, 0].tolist()
        table_with_urls_for_recrawl = pd.read_excel(project_file_path, engine='openpyxl')

        now = datetime.now().strftime("%H:%M:%S")

        if table_with_urls_for_recrawl.empty:
            log_file.write(f"{date.today()} - {now}, cтраницы в таблице input_urls.xlsx закончились\n")
            print(f"{date.today()} - {now}, cтраницы в таблице input_urls.xlsx закончились")
            return

        key_column_index = 0
        log_file.write("Все ключи:\n" + str(input_keys) + '\n')
        print("Все ключи:\n" + str(input_keys) + '\n')

        for key in input_keys_list:
            log_file.write(f'{date.today()} - {now}, используется ключ: {key}\n')
            print(f'{date.today()} - {now}, используется ключ: {key}')
            try:
                send_pages_to_google(table_with_urls_for_recrawl, key_column_index, key, log_file)
            except Exception:
                error_report(log_file)
                print(f"Exception в функиции отправки запроса ~109 строка: {error_report(log_file)}")

        total_requests_count = sum(request_counters.values())
        log_file.write(
            f"{date.today()} - {now}, работа завершена, отправлено на переобход {total_requests_count} страниц\n")
        print(
            f"{date.today()} - {now}, работа завершена, отправлено на переобход {total_requests_count} страниц")


if __name__ == "__main__":
    main()
