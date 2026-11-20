import pytest
from fastapi.testclient import TestClient
from alembic import command
from alembic.config import Config
from pathlib import Path
from main import create_app

@pytest.fixture
def migration_config(tmp_path):
    project_dir = Path(__file__).resolve().parents[1]
    config = Config(str(project_dir / "alembic.ini"))
    config.attributes["database_path"] = tmp_path / "test.sqlite3"
    return config

@pytest.fixture
def database_path(migration_config):
    # Тестовая БД создаётся теми же миграциями, что и рабочая.
    command.upgrade(migration_config, "head")
    return migration_config.attributes["database_path"]


@pytest.fixture
def client(database_path):
    # Таблица уже создана Alembic в изолированной тестовой базе.
    with TestClient(create_app(database_path)) as test_client:
        yield test_client



def create_review(client, author="", text="какой-то текст"):
    response = client.post(
        "/reviews",
        json={"author": author, "text": text},
    )
    assert response.status_code == 201
    return response.json()


def test_create_review(client):
    response = client.post(
        "/reviews",
        json={"author": "ААААА", "text": "какой-то текст"},
    )

    assert response.status_code == 201
    review = response.json()

    assert isinstance(review["id"], int)
    assert review["author"] == "ААААА"
    assert review["text"] == "какой-то текст"


@pytest.mark.parametrize(
    "body",
    [
        {}, 
        {"author": "ААААА"}, 
        {"text": "какой-то текст"}, 
        {"author": "", "text": "какой-то текст"},
        {"author": "ААААА", "text": ""},
        {"author": "А" * 121, "text": "какой-то текст"},
        {"author": "ААААА", "text": "А" * 10001},
        {"author": "   ", "text": "А"},
        {"author": "ААААА", "text": "     "},
    ],
)
def test_create_review_invalid_input(client, body):
    response = client.post("/reviews", json=body)
    assert response.status_code == 422 or response.status_code == 400

