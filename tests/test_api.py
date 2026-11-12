
from uuid import uuid4

from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


def test_root():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200


def test_echo():
    with TestClient(app) as client:
        response = client.post(
            "/echo",
            headers={"X-API-Key": settings.api_key},
            json={
                "message": "Pytest başarılı!",
                "sender": "test",
            },
        )

        assert response.status_code == 200
        assert response.json()["success"] is True


def test_api_key_protection():
    with TestClient(app) as client:
        response = client.get("/todos")
        assert response.status_code == 422

        response = client.get(
            "/todos",
            headers={"X-API-Key": "wrong-key"},
        )
        assert response.status_code == 401


def test_todo_crud_and_audit_logs():
    with TestClient(app) as client:
        headers = {"X-API-Key": settings.api_key}
        marker = f"pytest-{uuid4().hex}"

        # CREATE
        response = client.post(
            "/todos",
            headers=headers,
            json={
                "title": marker,
                "description": "Otomatik test görevi",
            },
        )

        assert response.status_code == 201

        todo = response.json()
        todo_id = todo["id"]

        assert todo["title"] == marker

        # READ
        response = client.get(
            f"/todos/{todo_id}",
            headers=headers,
        )

        assert response.status_code == 200

        # UPDATE
        response = client.put(
            f"/todos/{todo_id}",
            headers=headers,
            json={
                "title": f"{marker}-updated",
                "completed": True,
            },
        )

        assert response.status_code == 200
        assert response.json()["completed"] is True

        # DELETE
        response = client.delete(
            f"/todos/{todo_id}",
            headers=headers,
        )

        assert response.status_code == 200

        # Silinen görev bulunmamalı.
        response = client.get(
            f"/todos/{todo_id}",
            headers=headers,
        )

        assert response.status_code == 404

        # İşlem geçmişi korunmalı.
        response = client.get("/logs", headers=headers)

        assert response.status_code == 200

        logs = response.json()
        actions = [log["action"] for log in logs]

        assert "created" in actions
        assert "updated" in actions
        assert "deleted" in actions
