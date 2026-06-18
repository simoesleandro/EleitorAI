import bcrypt
import pytest
from app import create_app


@pytest.fixture
def client(monkeypatch, tmp_path):
    from core.config import get_settings
    get_settings.cache_clear()
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv("ADMIN_PASS", "test-pass")
    from core.db import init_db, get_db
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    hashed = bcrypt.hashpw(b"test-pass", bcrypt.gensalt()).decode()
    conn = get_db(db_path=db_path)
    conn.execute(
        "INSERT INTO usuarios (username, password_hash, nome) VALUES (?, ?, ?)",
        ("admin", hashed, "Admin Test"),
    )
    conn.commit()
    conn.close()
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_login_get_returns_form(client):
    resp = client.get("/login")
    assert resp.status_code == 200
    assert b"login" in resp.data.lower() or b"senha" in resp.data.lower()


def test_login_post_success_redirects(client):
    resp = client.post("/login", data={"username": "admin", "password": "test-pass"}, follow_redirects=False)
    assert resp.status_code in (302, 301)


def test_login_post_wrong_password(client):
    resp = client.post("/login", data={"username": "admin", "password": "wrong"}, follow_redirects=False)
    assert resp.status_code == 401


def test_login_post_user_not_found(client):
    resp = client.post("/login", data={"username": "nobody", "password": "whatever"}, follow_redirects=False)
    assert resp.status_code == 401


def test_logout_redirects(client):
    resp = client.post("/logout", follow_redirects=False)
    assert resp.status_code in (302, 301)
