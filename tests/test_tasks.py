# Tests for tasks
import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    # create temp sqlite db for tests
    fd, path = tempfile.mkstemp(suffix=".sqlite3")
    os.close(fd)

    engine = create_engine(
        f"sqlite:///{path}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()

    engine.dispose()   # <-- THIS LINE FIXES WINDOWS SQLITE LOCKING

    os.remove(path)


def test_create_and_get_task(client):
    res = client.post(
        "/tasks",
        json={"title": "Buy milk", "description": "2 liters"},
    )
    assert res.status_code == 201

    task = res.json()
    assert task["title"] == "Buy milk"
    assert task["status"] == "todo"

    task_id = task["id"]

    res = client.get(f"/tasks/{task_id}")
    assert res.status_code == 200
    assert res.json()["id"] == task_id


def test_list_and_search_tasks(client):
    client.post("/tasks", json={"title": "Alpha"})
    client.post("/tasks", json={"title": "Beta"})
    client.post("/tasks", json={"title": "Gamma"})

    res = client.get("/tasks", params={"query": "bet"})
    assert res.status_code == 200

    tasks = res.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Beta"


def test_update_status(client):
    res = client.post("/tasks", json={"title": "Test task"})
    task_id = res.json()["id"]

    res = client.patch(
        f"/tasks/{task_id}",
        json={"status": "in_progress"},
    )
    assert res.status_code == 200
    assert res.json()["status"] == "in_progress"


def test_delete_task(client):
    res = client.post("/tasks", json={"title": "Delete me"})
    task_id = res.json()["id"]

    res = client.delete(f"/tasks/{task_id}")
    assert res.status_code == 204

    res = client.get(f"/tasks/{task_id}")
    assert res.status_code == 404


def test_404_cases(client):
    assert client.get("/tasks/999").status_code == 404
    assert client.patch(
        "/tasks/999",
        json={"status": "done"},
    ).status_code == 404
    assert client.delete("/tasks/999").status_code == 404
