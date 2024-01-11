# Описание
Приложение позволяет оставлять отзывы о произведениях в различных категориях и жанрах,
а также оставлять оценки произведениям и комментировать существующие отзывы.

## Запуск проекта:
Скопируйте проект из репозитория:
```bash 
git clone https://github.com/Ogyrecheg/yamdb_final.git
```
Перейти в дерикторию скачанного проекта.
Создать и активировать virtual enviroment:
```bash
py -3.7 -m venv -venv
source venv/scripts/activate
```
При активированном virtual env скачать необходимые зависимости проекта:
```bash
(venv) pip install -r api_yamdb/requirements.txt
```
##### Установить докер на вашу машину ([туториал](https://docs.docker.com/engine/install/))
### Настройка переменных окружения:

 В корневой папке проекта необходимо создать файл .env и указать в нем переменные окружения.

#### Пример:
```SECRET_KEY='p&l%385148kslhtyn^##a1)ilz@4zqj=rq&agdol^##zgl9(vs'``` - ключ от джанго проекта
 
```DB_ENGINE=django.db.backends.postgresql``` - указываем, что работаем с postgresql

```DB_NAME=postgres``` - имя базы данных

```POSTGRES_USER=postgres``` - логин для подключения к базе данных

```POSTGRES_PASSWORD=postgres``` - пароль для подключения к БД (установите свой)

```DB_HOST=db``` - название сервиса (контейнера)

```DB_PORT=5432``` - порт для подключения к БД


Запуск приложения из докер контейнера:
```bash
cd infra
docker-compose up -d --build
```

После сборки образов и создания - запуска контейнеров приложения необходимо произвести миграции в БД, создание суперюзера и сбор статики:
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
```
Если все прошло успешно, попробуйте залогиниться в админ-панель django проекта по адресу:
http://localhost/admin/
Для того, чтобы наполнить БД записями выполните команды:
```bash
cd api_yamdb
python manage.py loaddata ../infra/fixtures.json
```

### Основные запросы API

Регистрация нового пользователя POST```/api/v1/auth/signup/```

Получение токена POST ```/api/v1/auth/token/```

Получение списка произведений GET ```/api/v1/titles/```

Получение конкретного произведения GET ```/api/v1/titles/{titles_id}/```

Получение списка всех отзывов GET ```/api/v1/titles/{title_id}/reviews/```

Получение списка всех комментариев GET ```/api/v1/titles/{title_id}/reviews/{review_id}/comments/```


**Технологии:**
- Python
- Django
- PostgreSQl
- DRF
- GitHub, GitActions
- Nginx
- Gunicorn
- Docker

### Автор проекта:
студент когорты №17 [Шевченко Александр](https://github.com/Ogyrecheg)

![work_flow](https://github.com/Ogyrecheg/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)


