# Auth RBAC Test Task

> Русская версия документации ниже.  
> English summary can be provided on request.

Сервис на FastAPI, демонстрирующий аутентификацию, ролевую модель доступа и управление разрешениями через административный API.

Проект реализует небольшой backend-сервис с поддержкой:

- регистрации и логина пользователей
- JWT access token аутентификации
- self-service эндпоинтов для профиля пользователя
- авторизации на основе ролей, ресурсов и permissions
- уровней доступа `own` / `all`
- административных эндпоинтов для просмотра и изменения permissions
- mock-ресурсов для демонстрации правил доступа
- logout с отзывом токена через базу данных

---

## Цель проекта

Цель этого проекта — показать полный и воспроизводимый сценарий разграничения доступа:

- аутентификация пользователя
- определение текущего пользователя по bearer token
- авторизация по ролям и permissions
- изменение правил доступа администратором
- немедленное влияние изменения permissions на защищённые эндпоинты
- отзыв access token при logout

---

## Стек

- Python 3.11
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- Alembic
- Docker Compose
- JWT (`python-jose`)
- pytest
- Ruff
- GitHub Actions

---

## Реализованная функциональность

### Аутентификация
- регистрация пользователя
- логин пользователя
- выдача JWT access token
- получение текущего пользователя из bearer token
- logout с отзывом токена через `revoked_tokens`

### Self-service для пользователя
- получение своего профиля
- обновление своего профиля
- soft delete своего профиля

### Авторизация
- RBAC-подобная модель доступа
- роли
- ресурсы
- permissions
- action-based проверки:
  - `read`
  - `create`
  - `update`
  - `delete`
- scope-based уровни доступа:
  - `all`
  - `own`

### Административные возможности
- просмотр ролей
- просмотр permissions
- изменение permissions для role/resource пары

### Mock-ресурсы
Авторизация демонстрируется на mock-ресурсах:

- projects
- tasks
- reports

---

## Модель данных

Основная модель доступа построена вокруг следующих таблиц:

- `users`
- `roles`
- `user_roles`
- `resources`
- `role_permissions`
- `revoked_tokens`

### Как устроена модель доступа

Каждая запись в `role_permissions` принадлежит роли и ресурсу и содержит:

- `can_read`
- `can_create`
- `can_update`
- `can_delete`
- `scope`

Таблица `revoked_tokens` используется для хранения отозванных access token по `jti`.

Примеры:

- обычный пользователь может читать все projects
- обычный пользователь может читать и обновлять только свои tasks
- обычный пользователь не может читать reports по умолчанию
- admin имеет полный доступ ко всем ресурсам
- после logout access token попадает в список отозванных и больше не принимается сервером

---

## Структура проекта

```text
app/
  api/
    admin.py
    auth.py
    mock_resources.py
    users.py
  core/
    config.py
    dependencies.py
    security.py
  db/
    base.py
    session.py
  models/
    resource.py
    revoked_token.py
    role.py
    role_permission.py
    user.py
  schemas/
    auth.py
    mock_resources.py
    permission.py
    user.py
  scripts/
    demo.sh
    seed.py
  services/
    permission_service.py
  main.py

alembic/
tests/
Dockerfile
docker-compose.yml
Makefile
requirements.txt
pyproject.toml
````

---

## Быстрый запуск

### 1. Создать `.env`

Скопируйте `.env.example` в `.env`.

### 2. Подготовить demo-окружение

```bash
make demo-prepare
```

Команда:

* полностью сбрасывает состояние базы данных
* поднимает контейнеры
* применяет миграции
* заполняет базу demo-данными

### 3. Выполнить демонстрационный сценарий

```bash
make demo-run
```

### 4. Или выполнить всё одной командой

```bash
make demo
```

После подготовки Swagger UI будет доступен по адресу:

```text
http://localhost:8000/docs
```

---

## Ручной запуск по шагам

Если нужен запуск без demo-таргетов:

```bash
make rebuild
make migrate
make seed
```

Полезные команды:

```bash
make up
make down
make logs
make shell
make lint
make fix
make test
```

---

## Demo-данные для входа

### Администратор

* email: `admin@example.com`
* password: `admin123`

### Обычный пользователь

* email: `user@example.com`
* password: `user123`

---

## Демонстрационный сценарий

Сценарий `make demo-run` показывает следующий поток:

1. логин под обычным пользователем
2. доступ к `GET /mock/projects` → разрешён
3. доступ к `GET /mock/reports` → запрещён
4. логин под администратором
5. изменение permission через `PATCH /admin/permissions/6`
6. повторный логин под обычным пользователем
7. доступ к `GET /mock/reports` → разрешён
8. logout пользователя
9. повторное использование того же токена → `401 Token has been revoked`

Этот сценарий показывает, что:

* permissions хранятся в базе данных
* администратор может изменять правила доступа
* изменение permissions немедленно влияет на защищённые эндпоинты
* logout действительно отзывает access token

---

## Обзор API

### Auth

* `POST /auth/register`
* `POST /auth/login`
* `POST /auth/logout`

### User

* `GET /users/me`
* `PATCH /users/me`
* `DELETE /users/me`

### Admin

* `GET /admin/roles`
* `GET /admin/permissions`
* `PATCH /admin/permissions/{permission_id}`

### Mock Resources

* `GET /mock/projects`
* `GET /mock/projects/{project_id}`
* `GET /mock/tasks`
* `GET /mock/tasks/{task_id}`
* `POST /mock/tasks`
* `PATCH /mock/tasks/{task_id}`
* `GET /mock/reports`

---

## Тесты

Запуск тестов:

```bash
make test
```

Покрыты следующие сценарии:

* успешный логин
* logout отзывает access token
* обычный пользователь не имеет доступа к reports по умолчанию
* администратор может выдать доступ к reports обычному пользователю
* обычный пользователь не может обновить чужую задачу
* администратор может обновить любую задачу

---

## Линтинг

Проверка кода:

```bash
make lint
```

Автоисправление части замечаний:

```bash
make fix
```

Проект использует Ruff для статических проверок и базового контроля качества кода.

---

## CI

GitHub Actions workflow запускается на `push` и `pull_request` и выполняет:

* Ruff lint checks
* pytest test suite

---

## Ограничения решения

Проект намеренно реализован как компактный demo-сервис.

Текущие ограничения:

* mock-ресурсы хранятся в памяти, а не в отдельных таблицах базы данных
* реализован только access-token flow без refresh token механизма
* модель авторизации специально оставлена простой и наглядной
* управление ролями пользователей через отдельный административный API не реализовано

Эти ограничения приняты осознанно, чтобы сфокусировать решение на ключевой части задания:

* аутентификация
* авторизация
* управление permissions
* демонстрируемое изменение доступа к защищённым ресурсам
* отзыв токена при logout

---

## Примечание

Проект упакован как воспроизводимый backend demo, а не как production-ready identity platform.

Основная цель — показать:

* понятную структуру API
* рабочий auth flow
* модель permissions, привязанную к базе данных
* воспроизводимый локальный запуск
* автоматическую проверку через тесты и CI
* демонстрационный сценарий, который можно прогнать одной командой
