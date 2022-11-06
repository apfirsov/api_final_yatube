## Добро пожаловать в проект YATUBE
Это блог, реализованный на Django + templates, функционал:
- Ведение текстовых блогов в разрезе групп, с поддержкой изображений и комментариев к постам
- Пользователи/Регистрация
- Подписчиски/Отслеживание подписок

Дополнительно реализован Rest API на фреймоворке DRF.
API реализует возможность подключения к платформе:
- web-клиентов
- мобильных приложений
- любых других видов клиентов, подерживающих работу с RestAPI 

### Технологии
- [Django 2.2.16](https://docs.djangoproject.com/en/4.0/releases/2.2.16/)
- [DRF 3.12.4](https://www.django-rest-framework.org/community/release-notes/)

Подробнее в [requirements.txt](https://github.com/apfirsov/api_final_yatube/blob/master/requirements.txt)

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:apfirsov/api_final_yatube.git
```

```
cd api_final_yatube
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

#### Документация к API с примерами запросов/ответов:

Подробная докeментация доступна по url:
```
http://<your_host>/redoc/
```

Пример получения постов:
```
GET /api/v1/posts/
```
```
{
  "count": 123,
  "next": "http://api.example.org/accounts/?offset=400&limit=100",
  "previous": "http://api.example.org/accounts/?offset=200&limit=100",
  "results": [
    {
      "id": 0,
      "author": "string",
      "text": "string",
      "pub_date": "2021-10-14T20:41:29.648Z",
      "image": "string",
      "group": 0
    }
  ]
}
```
Пример публикации постов:
```
POST /api/v1/posts/
```

content type application/json:
```
{
  "text": "string",
  "image": "string",
  "group": 0
}
```
Response:
```
{
  "id": 0,
  "author": "string",
  "text": "string",
  "pub_date": "2019-08-24T14:15:22Z",
  "image": "string",
  "group": 0
}
```
### Enjoy!

****
##  Об авторе
**Автор:** [Артем Фирсов](https://github.com/apfirsov)

**Другие проекты:** [Доступны на GitHub](https://github.com/apfirsov)