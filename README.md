
# Django E-Commerce

[![](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## About
E-commerce website using Django framework

Based on the following:
* [GitHub Project](https://github.com/justdjango/django-ecommerce)
* [YouTube tutorial](https://www.youtube.com/watch?v=YZvRrldjf1Y)

### Installation

To install:
1. Clone repo
2. Run either of the two commands
   ```shell
   $ pip install -e .
   ```
   ```shell
   $ pip install -r requirements.txt
   ```
3. Create new superuser, and process migrations per Django documentation
   ```shell
   $ python manage.py createsuperuser
   ```
   ```shell
   $ python manage.py makemigrations
   ```
   ```shell
   $ python manage.py migrate
   ```
5. Start the development server
    ```shell
    $ python manage.py runserver
    ```
6. Create items in DB from the admin page.