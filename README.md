# Парсер сайтов с вакансиями для личного пользования

Этот проект предназначен для мониторинга сайтов с вакансиями. Парсер работает по заданному фильтру и с определенным интервалом проверяет сайт на наличие новых вакансий. В случае появления новых вакансий, он присылает их сообщением в Телеграм.

## Настройка

Для переменных окружения используется файл `.env` с переменными `TOKEN`, `ADMIN_ID`.

## Зависимости

Все зависимости указаны в файле `req.txt`.

## Стек технологий

- aiogram
- bs4
- requests
- mongodb

## Поддерживаемые сайты

На текущий момент парсер поддерживает следующие сайты:

- hh.ru
