
Реализовано:
================
HTTP сервер, который умеет:
* принимать GET и head запросы 
* выдавать статические файлы
* обрабатывать исключения


Запуск:
================
* Запуск сервера: 
```
python3 httpd.py
```
* Принимамые параметры:
    * -p --port - порт, на котором будет запущен сервер
    * -a --address - адрес, на котором будет запущен сервер
    * -r --document_root - директория, в которой будут искаться файлы для отдачи
    * -w --workers - количество воркеров


Тестирование:
================
* Запуск тестов:
```
python3 httptest.py
  ``` 
  или 
```
docker-compose up --abort-on-container-exit --exit-code-from tests
```

Архитектура:
================
Реализовано с использованием multiprocessing и multithreading.
* Мастер-процесс запускает воркеры и слушает сокет. 
При получении запроса мастер-процесс передает его воркеру, который в свою очередь запускает обработчик запроса, 
используя механизмы многопоточности.
* Воркеры запускаются в отдельных процессах, а обработчики запросов в отдельных потоках.
* Результаты тестирования ab:
```
ab -n 50000 -c 100 -r -s 60 http://127.0.0.1:80/
```
```
Document Length:        11 bytes

Concurrency Level:      100
Time taken for tests:   2.173 seconds
Complete requests:      50000
Failed requests:        0
Total transferred:      1500000 bytes
HTML transferred:       550000 bytes
Requests per second:    23012.29 [#/sec] (mean)
Time per request:       4.346 [ms] (mean)
Time per request:       0.043 [ms] (mean, across all concurrent requests)
Transfer rate:          674.19 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.1      0       4
Processing:     0    4   0.8      4      18
Waiting:        0    4   0.8      4      18
Total:          2    4   0.8      4      19
```
Конфигурация виртуальной машины, на которой проводилось тестирование:
```
    *-firmware
          description: BIOS
          vendor: Parallels International GmbH.
          physical id: 0
          version: 18.0.1 (53056)
          date: Thu, 25 Aug 2022 17:04:57
          size: 128KiB
          capacity: 2MiB
          capabilities: pci bootselect acpi smartbattery uefi
     *-cpu:0
          description: CPU
          product: ARMv8 (None)
          vendor: Apple
          physical id: 4
          bus info: cpu@0
          version: Apple Silicon
          serial: None
          slot: CPU
          size: 2GHz
          capacity: 2GHz
          configuration: cores=2 enabledcores=2 threads=1
     *-memory
          description: System Memory
          physical id: 5
          slot: System board or motherboard
          size: 4GiB
        *-bank
             description: DIMM DRAM EDO
             physical id: 0
             size: 4GiB
             width: 32 bits
