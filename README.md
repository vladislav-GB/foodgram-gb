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

## 🚀 Запуск проекта через Docker Hub

Выполните:

```bash
docker pull avengusgb/foodgram-gb:latest
docker run -d -p 8000:8000 avengusgb/foodgram-gb
```
В файле infra/docker-compose.yml заменить
  
  backend:
    image: avengusgb/foodgram-gb:latest
    ...
    build:  # ❌ удалить

---

### 𐀪𐀪 Пользователи

| Имя пользователя | Email                                               | Пароль    |
| ---------------- | --------------------------------------------------- | --------- |
| ADMIN            | [avengus.gb@gmail.com](mailto:avengus.gb@gmail.com) | 1604admin |
| Heisenberg       | [vlad16918@gmail.com](mailto:vlad16918@gmail.com)   | 1604admin |
| Vasilok          | [avenvisual@gmail.com](mailto:avenvisual@gmail.com) | 1604admin |

---

```
🔗 Ссылка на DockerHub:[https://hub.docker.com/r/avengusgb/foodgram-gb](https://hub.docker.com/r/avengusgb/foodgram-gb)

---

## 🔗 Доступ

* Главная: [http://localhost/](http://localhost/)
* Админка: [http://localhost/admin/](http://localhost/admin/)

---

## 👤 Автор

**Владислав Лубягин**
📧 [avengus.gb@gmail.com](mailto:avengus.gb@gmail.com)
🔗 [GitHub: vladislav-GB](https://github.com/vladislav-GB)

Ссылка на GitHub: https://github.com/vladislav-GB/foodgram-gb






# Foodgram

Проект Foodgram — это онлайн-сервис для публикации рецептов, добавления их в избранное и формирования списка покупок. Пользователи могут подписываться друг на друга, искать рецепты по ингредиентам и сохранять понравившиеся блюда.

---

## 🚀 Запуск проекта через Docker Hub

Выполните команды:

```bash
docker pull avengusgb/foodgram-gb:latest
docker run -d -p 8000:8000 avengusgb/foodgram-gb
```

### 🔧 Для docker-compose

Если вы используете `infra/docker-compose.yml`, замените секцию `backend`:

```yaml
  backend:
    image: avengusgb/foodgram-gb:latest
    container_name: foodgram-backend
    env_file:
      - .env
    volumes:
      - ../backend/foodgram:/app  
      - ../data:/data
      - static:/app/static/
      - media:/app/media/
    depends_on:
      - db
    ports:
      - "8000:8000"
    restart: always
```

> ❗️ Не забудьте **удалить или закомментировать** строку `build:` в секции `backend`.

---

### 👤 Тестовые пользователи

| Имя пользователя | Email                                               | Пароль    |
| ---------------- | --------------------------------------------------- | --------- |
| ADMIN            | [avengus.gb@gmail.com](mailto:avengus.gb@gmail.com) | 1604admin |
| Heisenberg       | [vlad16918@gmail.com](mailto:vlad16918@gmail.com)   | 1604admin |
| Vasilok          | [avenvisual@gmail.com](mailto:avenvisual@gmail.com) | 1604admin |

---

### 📦 Docker Hub

🔗 [https://hub.docker.com/r/avengusgb/foodgram-gb](https://hub.docker.com/r/avengusgb/foodgram-gb)

---

### 📁 Содержимое проекта

* **backend/** — бэкенд Django-приложения
* **frontend/** — сборка React-интерфейса
* **infra/** — инфраструктура Docker, конфигурации и nginx
* **docs/** — документация к API и проекту

---

### 🚧 Основной стек

* Python 3.11
* Django / DRF
* PostgreSQL
* Nginx
* Docker / Docker Compose

---

### 🔹 Пример запроса API

```
GET /api/recipes/?is_favorited=1
```

Ответ:

```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "name": "Борщ",
      "is_favorited": true,
      ...
    }
  ]
}
```

---

### 🌐 Автор

**Vladislav Golub**
GitHub: [https://github.com/vladislav-GB](https://github.com/vladislav-GB)
