![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)

# Проект Foodgram
### Описание проекта:

Foodgram - это веб-приложение для любителей кулинарии, позволяющее пользователям создавать и публиковать свои рецепты блюд, а также подписываться на других авторов и искать интересные рецепты для приготовления.

### Основные функции:

### Рецепты блюд:

Пользователи могут создавать рецепты блюд, включая название, ингредиенты, шаги приготовления и изображения.
Рецепты можно редактировать и удалять.

### Подписка на авторов:

Пользователи могут подписываться на других авторов и следить за их новыми рецептами.
Поиск и фильтрация:

### API проекта:

Приложение предоставляет API для взаимодействия с данными, позволяя разработчикам получать информацию о рецептах, пользователях и других объектах проекта.
Использованные технологии:
- Python,
- Django,
- Node.js,
- JavaScript,
- DRF,
- Djoser

### Как запустить проект на сервере?
Для запуска на собственном сервере:
Скопируйте из репозитория файлы из папки 'infra', на сервер:
### docker-compose-production.yml и nginx.conf
Клонируем репозиторий:
```python
git@github.com:Amir800S/foodgram-project-react.git
```
В папке с этими файлами создайте файл .env он должен быть заполнен данными:
```python
SECRET_KEY=<КЛЮЧ ПРОЕКТА>
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<ИМЯ БАЗЫ ДАННЫХ>
POSTGRES_USER=<ИМЯ ПОЛЬЗОВАТЕЛЯ БД>
POSTGRES_PASSWORD=<ПАРОЛЬ>
DB_HOST=db
DB_PORT=5432
```
Далее поднимаем проект в докере, делаем миграции и собираем статику:
```python
docker-compose up -d
docker-compose exec <имя_контейнера_бэкэнда> python3 manage.py makemigrations
docker-compose exec <имя_контейнера_бэкэнда> python3 manage.py migrate
docker-compose exec <имя_контейнера_бэкэнда> python3 manage.py collectstatic
```

Создаем администратора командой:
```python
docker-compose exec <имя_контейнера_бэкэнда> python manage.py createsuperuser
```
Добавить ингредиенты из csv:
```python
docker-compose exec <имя_контейнера_бэкэнда> python3 manage.py import_csv ingredients.csv
```
Теги добавляем вручную в админ-зоне, не надо лениться!
### Проект готов к работе!

### *Автор: Сосламбеков Амир* 