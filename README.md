Скрипт отправляет на переобход сколько угодно URL-адресов, используя несколько ключей Google Indexing API. После отправки отправленные адреса удалятся из исходной таблицы. Читай инструкцию Read me!.docx

 
1.	Что делать сначала?
  - Создаём проект в Google cloud (https://console.cloud.google.com/welcome) → инструкция со скринами https://pixelplus.ru/samostoyatelno/stati/indeksatsiya/indexing-api-v-google.html#anchor-2-4
  -	Создаём в нём сервисный аккаунт, внутри которого создаём новый ключ в формате JSON и скачиваем его.
  -	Хотим много страниц и ключей – создаём новый сервисный аккаунт, под ним новый ключ и так далее.
  -	В Google Cloud в каждом сервисном аккаунте в поиске вводим «Indexing api» и нам откроются настройки Indexing API проекта, где нажимаем «Enable».
  -	Дальше нужно выдать доступ нашим аккаунт на действия в Search Console. При создании сервисного аккаунта создаётся сервисная почта, которая показана на скрине ниже. Дальше идём в Google Search Console в проекты, для которых он будет использоваться: Настройки → Пользователи и разрешения и добавляем эти сервисные почты с правом «Владелец».

Настройка доступов завершена, теперь готовим всё для работы скрипта.
 
2.	В файле current_path.txt указываем ссылку на текущую папку, где лежит файл запуска.
 
3.	Кладем в папку с файлом скаченные ключи из Google, а в файле input_keys.url в 1 столбце без всяких заголовков перечисляем названия файлов без расширения.
 
4.	В файле input_urls.xlsx в 1 столбце создаём заголовок «Urls» и ниже вставляем сколько угодно ссылок на переиндексацию.
 
5.	Запускаем файл Index_NOW и если программа работает правильно, вы увидите список своих ключей и логи отправки страниц.
   -	Если программа почти моментально завершилась, то произошла ошибка – попробуйте не использовать пробелы и заглавные буквы кириллицы в пути, по которому лежит скрипт. Короче, в папке C:/indexing_api точно будет работать.

6.	После работы будет создан файл логами вида 2024-04-25_logs.txt, который создаётся при запуске ежедневно и в котором видна работа ключей и отправляемые адреса.
