
Задание:
=============
Реализовать декларативный язык описания и систему валидации запросов к HTTP API сервиса скоринга. 
Сервис скоринга предоставляет единственный метод /method, который принимает на вход JSON с данными пользователя и возвращает
результат в виде JSON.


Описание методов:
=============
Метод online_score:
-------------------
Метод принимает на вход данные пользователя и возвращает значение его скорингового балла.

Параметры:
* phone - телефон пользователя (строка или число)
* email - электронная почта пользователя
* first_name - имя пользователя
* last_name - фамилия пользователя
* birtday - день рождения пользователя
* gender - пол пользователя (число 0, 1 или 2)
* client_id - идентификатор пользователя (число от 0 до 4294967295)

Все параметры являются необязательными, однако хотя бы одна пара параметров phone-email, first name-last name или client_id должна быть передана.


Метод clients_interests:
------------------------
Метод принимает на вход идентификаторы пользователей и возвращает их заинтересованные категории.

Параметры:
* client_ids - массив идентификаторов пользователей (массив чисел)
* date - дата, на которую нужно получить информацию (строка в формате dd.mm.YYYY)

Параметр client_ids является обязательным.


Примеры запросов:
=============
Метод online_score:
```
curl -X POST  -H "Content-Type: application/json" -d '{"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95", "arguments": {"phone": "79175002040", "first_name": "Стансилав", "last_name": "Ступников", "birthday": "01.01.1990", "email": "test@mail.ru", "gender": 1}}' http://127.0.0.1:8080/method/
```

Тело ответа:
```
{"code": 200, "response": {"score": 5.0}}
```

Метод clients_interests:
```
curl -X POST  -H "Content-Type: application/json" -d '{"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95", "arguments": {"client_ids": [1,2,3], "date":"20.07.2017"}}' http://127.0.0.1:8080/method/
```

Тело ответа:
```
{"code": 200, "response": {"1": ["books", "hi-tech"], "2": ["pets", "tv"], "3": ["travel", "music"]}}
```
