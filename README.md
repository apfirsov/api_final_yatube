## Добро пожаловать в проект YATUBE
Это Full Rest API приложение для ведения блогов на фреймоворке DRF.
Проект решает задачу создания блогерской вебплатформы, с возможностью подключения:
- web-клиентов
- мобильных приложений
- любых других видов клиентов, подерживающих работу с RestAPI 

### Технологии
- [Django 2.2.16]("https://docs.djangoproject.com/en/4.0/releases/2.2.16/")
- [DRF 3.12.4]("https://www.django-rest-framework.org/community/release-notes/")

Подробнее в [requirements.txt]("https://github.com/apfirsov/api_final_yatube/blob/master/requirements.txt")

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

Документация к API с примерами запросов/ответов:

```
http://<your_host>/redoc/
```
### Enjoy!

****
##  Об авторе
**Автор:** [Артем Фирсов]("https://github.com/apfirsov")

**Другие проекты:** [Доступны на GitHub]("https://github.com/apfirsov")