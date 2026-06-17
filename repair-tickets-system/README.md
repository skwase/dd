# Система учёта ремонтных заявок

Full-stack веб-приложение для управления заявками на ремонт и обслуживание в организации.

## 📋 Функциональность

- ✅ Регистрация и авторизация пользователей
- ✅ Разграничение ролей (пользователь, ответственный, администратор)
- ✅ Создание, просмотр и редактирование заявок
- ✅ Назначение исполнителей
- ✅ Изменение статусов (Новая → В работе → Выполнена)
- ✅ Категории и приоритеты заявок
- ✅ Комментарии к заявкам
- ✅ История изменений
- ✅ Поиск и фильтрация
- ✅ REST API
- ✅ Адаптивный дизайн

## 🛠 Технологии

- **Backend**: Python 3.11, Flask
- **Database**: SQLite (SQLAlchemy ORM)
- **Frontend**: Bootstrap 5, Jinja2 templates
- **Testing**: pytest, pytest-cov
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Deployment**: Render.com

## 🚀 Быстрый старт

### Локальный запуск

```bash
# Клонирование репозитория
git clone https://github.com/your-username/repair-tickets-system.git
cd repair-tickets-system

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt

# Инициализация базы данных
python
>>> from app import create_app, db
>>> from app.models import User, Category
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
>>> exit()

# Запуск приложения
python run.py