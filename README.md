# Анализатор страниц

Веб-приложение для анализа веб-страниц. Позволяет добавлять URL-адреса и проверять их, извлекая метаинформацию (заголовки, статус-коды и прочее).

**Демо:** [https://python-project-83-mkox.onrender.com/](https://python-project-83-mkox.onrender.com/)

## Статус проекта

[![Actions Status](https://github.com/GrScode404/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/GrScode404/python-project-83/actions)

## Описание

Page Analyzer — это веб-приложение, которое помогает анализировать веб-страницы. С его помощью вы можете:

- **Добавлять URL-адреса** в базу данных
- **Проверять страницы** и извлекать ключевую информацию:
  - Статус код HTTP
  - Заголовки страницы (title)
  - Основные заголовки (h1)
  - Описание страницы (meta description)
- **Отслеживать историю проверок** для каждой страницы
- **Просматривать список всех добавленных URL-адресов**

## Технологический стек

- **Backend:** Python 3.12+, Flask
- **Сервер:** Gunicorn
- **База данных:** PostgreSQL
- **Парсинг HTML:** BeautifulSoup4
- **Валидация:** Validators
- **HTTP запросы:** Requests
- **Тестирование:** pytest, pytest-cov
- **Линтер:** Ruff

## Установка

### Требования

- Python 3.12+
- PostgreSQL
- pip или uv

### Шаги установки

1. Склонируйте репозиторий:

```bash
git clone https://github.com/GrScode404/python-project-83.git
cd python-project-83
```
2. Установите зависимости:
```bash
make install
```

3. Создайте файл `.env` с необходимыми переменными окружения:
```
DATABASE_URL=postgresql://user:password@localhost:5432/page_analyzer
SECRET_KEY=your-secret-key-here
```

4. Инициализируйте базу данных:
```bash
psql -U user -d page_analyzer -f database.sql
```

## Использование

### Запуск в режиме разработки

```bash
make dev
```

Приложение будет запущено на `http://localhost:8000`

### Запуск в production

```bash
make start
```

### Выполнение тестов

```bash
make test
```

### Проверка кода линтером

```bash
make lint
```

### Автоисправление ошибок линтера

```bash
make fixlint
```

## Структура проекта

```
page_analyzer/
├── app.py                 # Основное приложение Flask и маршруты
├── db.py                  # Функции для работы с БД
├── templates/             # HTML шаблоны
│   ├── index.html        # Главная страница
│   ├── url.html          # Страница отдельного URL-адреса
│   └── urls.html         # Список всех URL-адресов
└── __init__.py

tests/                      # Тесты
├── test_app.py
└── test_dummy.py

database.sql              # SQL миграции
Makefile                  # Команды для разработки
pyproject.toml            # Конфигурация проекта
```

## API маршруты

| Метод | Маршрут | Описание |
|-------|---------|---------|
| GET | `/` | Главная страница |
| POST | `/urls` | Добавить новый URL |
| GET | `/urls` | Список всех URL-адресов |
| GET | `/urls/<id>` | Информация о конкретном URL |
| POST | `/urls/<id>/checks` | Проверить URL |

## Примеры использования

### Добавление URL

Отправьте POST запрос с URL-адресом:
```
POST /urls
Content-Type: application/x-www-form-urlencoded

url=https://example.com
```

### Проверка страницы

```
POST /urls/1/checks
```

Приложение загрузит страницу и сохранит информацию в БД.

## Переменные окружения

- `DATABASE_URL` — строка подключения к PostgreSQL
- `SECRET_KEY` — секретный ключ для Flask сессий
- `PORT` — порт для запуска (по умолчанию 8000)
