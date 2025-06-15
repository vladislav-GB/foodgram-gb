# 🧑‍🍳 Продуктовый помощник Foodgram

## 📌 Описание проекта

Foodgram — сервис публикации рецептов. Пользователи могут:

- создавать рецепты,
- добавлять чужие рецепты в избранное,
- формировать список покупок,
- подписываться на других авторов.

---

## 🚀 Технологии

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)

---

## ⚙️ Как запустить проект

### 🔧 Dev-режим (проверка API в Postman, без Docker)

> 💡 Рекомендуемая конфигурация: `DEBUG=True`, `DB=sqlite3`

1. Клонируйте репозиторий:

```bash
git clone https://github.com/vladislav-GB/foodgram-gb.git
cd foodgram/backend
```

2. Установите виртуальное окружение (для Windows):

```bash
python -m venv venv
source venv/Scripts/activate
```

3. Установите зависимости:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Запустите проект:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

### 🐳 Полный запуск через Docker

1. В папке `infra` создайте `.env` файл:

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY=supersecretkey
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=foodgram.settings
```

2. Соберите и запустите контейнеры:

```bash
docker compose build
docker compose up -d
```

3. Создайте суперпользователя:

```bash
docker compose exec backend python manage.py createsuperuser
```

---

### 🐋 Запуск с Docker Hub

Если не хотите собирать образ:

1. В `docker-compose.yml` укажите:

```yaml
  backend:
    image: avengusgb/foodgram:latest
```
    Ссылка на DockerHub:https://hub.docker.com/repository/docker/avengusgb/foodgram/general
---

## 🔗 Доступ

* Главная: [http://localhost/](http://localhost/)
* Админка: [http://localhost/admin/](http://localhost/admin/)

---

## 👤 Автор

**Владислав Лубягин**
📧 [avengus.gb@gmail.com](mailto:avengus.gb@gmail.com)
🔗 [GitHub: vladislav-GB](https://github.com/vladislav-GB)

Ссылка на GitHub: https://github.com/vladislav-GB/foodgram-gb/blob/main/README.md

