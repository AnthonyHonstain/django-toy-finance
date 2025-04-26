

## Setup of Environment

* Initialize mamba environment `mamba create -n django-finance -c conda-forge  python=3.13`
* `mamba activate django-finance`
* `pip install poetry`
* `poetry install --no-root`
* `python manage.py migrate`
* `python manage.py createsuperuser`
* `python manage.py runserver 8002`
    *  Alternatively can run with gunicorn `gunicorn --bind 0.0.0.0:8002 finance_service.wsgi -w 1`
* `python manage.py test`
* `mypy .`
* `black .`

### How I created the service

Get poetry bootstrapped

```shell
pip install poetry

poetry init 
poetry add django
poetry add psycopg2-binary

poetry add --group dev pytest
poetry add --group dev black
poetry add --group dev mypy
```

Get the Django app going

```shell
django-admin startproject finance_service .

python manage.py startapp finance

❯ tree
.
├── finance
│ ├── admin.py
│ ├── apps.py
│ ├── __init__.py
│ ├── migrations
│ │ └── __init__.py
│ ├── models.py
│ ├── tests.py
│ └── views.py
├── finance_service
│ ├── asgi.py
│ ├── __init__.py
│ ├── __pycache__
│ │ ├── __init__.cpython-313.pyc
│ │ └── settings.cpython-313.pyc
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
├── manage.py
├── poetry.lock
└── pyproject.toml



```