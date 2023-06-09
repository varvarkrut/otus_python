Анализатор логов.
================

Анализирует лог файл и выводит статистику по самым часто встречающимся запросам и временным характеристикам запросов.


Установка зависимостей
------------------
Для установки зависимостей необходимо выполнить команду:
```
pip3 install -r requirements.txt
```


Конфигурация
-------------
В конфигурационном файле можно задать следующие параметры:
* LOG_DIR - путь к директории с логами
* REPORT_DIR - путь к директории, в которую складывать отчеты
* REPORT_SIZE - максимальный размер отчета в байтах

Запуск
------
Для запуска скрипта необходимо выполнить команду:
```
python3 log_analyzer.py --config <путь к конфигурационному файлу>
```
В случае отсутствия параметра --config скрипт загрузит конфигурационный файл по умолчанию.

Тестирование
------------
Для запуска тестов необходимо выполнить команду:
```
pytest -v test_log_analyzer.py
```

[//]: # ( vim: set tw=79 sw=4 sts=4 et : )

