# Предварительное описание. Проект дорабатывается, во время второго этапа проверки примет финальный вид. Команды могут измениться.
# "Продуктовый помощник" (Foodgram)
![foodgram_workflow](https://github.com/LunarBirdMYT/foodgram-project-react/workflows/foodgram_workflow/badge.svg)
### Описание:
На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд. В мою задачу входила разработка backend-части проекта(написание API).

### Технологии:
![Python](https://img.shields.io/badge/Python-3.7-green)
![Django](https://img.shields.io/badge/Django-2.2.16-green)

### Для запуска на собственном сервере
1. Скопируйте из репозитория файлы, расположенные в директории infra:
    - docker-compose.yml
    - nginx.conf
2. На сервере создайте директорию foodgram;
3. В директории foodgram создайте директорию infra и поместите в неё файлы:
    - docker-compose.yml
    - nginx.conf
    - .env (пустой)
4. Файл .env должен быть заполнен следующими данными(исходя из того, что используется PostegreSQL):
```
SECRET_KEY=<КЛЮЧ>
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<ИМЯ БАЗЫ ДАННЫХ>
POSTGRES_USER=<ИМЯ ПОЛЬЗВОАТЕЛЯ БД>
POSTGRES_PASSWORD=<ПАРОЛЬ БД>
DB_HOST=db
DB_PORT=5432
```

5. В директории infra следует выполнить команды:
```
docker-compose up -d
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --no-input
```

6. Для создания суперпользователя, выполните команду:
```
docker-compose exec backend python manage.py createsuperuser
```

7. Для добавления ингредиентов в базу данных, выполните команду:
С проектом поставляются данные об ингредиентах.  
Заполнить базу данных ингредиентами можно выполнив следующую команду из папки "./infra/":
```bash
docker-compose exec backend python manage.py fill_ingredients_from_csv --path data/
```

8. Теги вручную добавляются в админ-зоне в модель Tags;
