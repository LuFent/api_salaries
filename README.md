# API salaries

Получает по API сайтов [Headhunter](https://hh.ru/) и [Superjob](https://www.superjob.ru/) информацию о зарплатах программистов на различных языках и выводит информацию в виде таблицы.


Список языков - JavaScript, Java, Python, Ruby, PHP, C++, CSS, C#, C, Go.

## Как установить
- Скачать Python 3.x.


- Склонировать репозиторий:

 ```
 git clone https://github.com/LuFent/api_salaries
 ```


- Перейти в папку с репозиторием.

- Скачать необходимые библиотеки:

 ```
  pip install -r requirements.txt
```


- [Получить API токен сервиса superjob](https://api.superjob.ru/), создать файл .env в который записать строку
```
SUPER_JOB_KEY=<Ваш токен>.
```


- Запустить скрипт - команда:

 ```
 python main.py
 ```


- Подождать несколько минут.


- Получить результат.


## Цель проекта

Проект создан в целях тренировки работы с API различных сервисов.
