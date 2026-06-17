import pytest


def _login(client, username: str, password: str):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )


def test_smoke_login_and_protected_endpoints():
    import sys
    from pathlib import Path

    # Добавляем директорию проекта в sys.path, чтобы импорт app работал и локально, и в CI
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(PROJECT_ROOT))

    from app.api_fixed import create_app


    # Пытаемся импортировать пакет корректно для разных путей/CI
    # (при запуске pytest root может быть выше директории проекта)
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})

    app.config.update({"WTF_CSRF_ENABLED": False})

    with app.test_client() as client:
        # После входа пользователь должен попасть на / (который редиректит на /tickets)
        resp = _login(client, "admin", "admin123")
        assert resp.status_code in (302, 303)

        # Доступ к protected страницам.
        # В приложении список тикетов отдается по маршруту '/' (редиректит на tickets.list_tickets).
        resp2 = client.get("/", follow_redirects=False)
        # / может вернуть либо редирект, либо сразу HTML (в зависимости от того, где тестовый клиент оказался)
        assert resp2.status_code in (200, 302, 303)

        resp3 = client.get("/", follow_redirects=True)
        assert resp3.status_code == 200






def test_create_ticket_requires_auth_and_visible_for_author():
    from app.api_fixed import create_app

    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})

    with app.test_client() as client:
        # 1) Без авторизации создание должно редиректить на /login
        resp = client.post("/create", data={"title": "t1"})
        assert resp.status_code in (302, 401, 403)

        # 2) Авторизуемся как admin (role=admin -> ответственный)
        _login(client, "admin", "admin123")

        # 3) Создаем тикет
        resp2 = client.post(
            "/create",
            data={
                "title": "Заявка CI",
                "description": "Описание",
                "category_id": "1",
                "priority": "high",
            },
            follow_redirects=False,
        )
        assert resp2.status_code in (302, 303)

        # 4) Страница со списком тикетов должна быть доступна.
        # В приложении список отдается по '/' (редиректит на tickets.list_tickets)
        resp3 = client.get("/", follow_redirects=True)
        assert resp3.status_code == 200
        assert "Заявка CI".encode("utf-8") in resp3.data


