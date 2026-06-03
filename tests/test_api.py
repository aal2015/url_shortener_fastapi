import string
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from main import app, generate_short_code
from database import Base, engine, get_db
from unittest.mock import patch
import pytest

DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

client = TestClient(app)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_database():

    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)

######### Base root test

def test_read_root():
    response = client.get("")
    assert response.status_code == 200
    assert response.json() == "Server is running"

######### generate_short_code function test

def test_generate_short_code_default_length(length=6):
    code = generate_short_code()

    assert len(code) == 6

def test_generate_short_code_custom_length():
    code = generate_short_code(10)

    assert len(code) == 10

def test_generate_short_code_valid_characters():

    code = generate_short_code()

    valid_characters = set(
        string.ascii_letters + string.digits
    )

    assert all(
        character in valid_characters
        for character in code
    )

def test_generate_short_code_returns_string():

    code = generate_short_code()

    assert isinstance(code, str)

def test_generate_short_code_mocked():

    with patch(
        "main.random.choice",
        return_value="A"
    ):
        code = generate_short_code(4)

    assert code == "AAAA"

######### short code creation test

def test_create_short_url():

    response = client.post(
        "/generateShortURL",
        json={
            "long_url": "https://google.com"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Short URL created"
    assert len(data["short_code"]) == 6

def test_custom_alias():

    response = client.post(
        "/generateShortURL",
        json={
            "long_url": "https://openai.com",
            "custom_alias": "openai"
        }
    )

    assert response.status_code == 200

    assert response.json()["short_code"] == "openai"

def test_duplicate_alias():

    client.post(
        "/generateShortURL",
        json={
            "long_url": "https://site1.com",
            "custom_alias": "alias123"
        }
    )

    response = client.post(
        "/generateShortURL",
        json={
            "long_url": "https://site2.com",
            "custom_alias": "alias123"
        }
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": "Custom alias already exists"
    }

def test_get_original_url():

    client.post(
        "/generateShortURL",
        json={
            "long_url": "https://stackoverflow.com",
            "custom_alias": "stack"
        }
    )

    response = client.get(
        "/getOriginalURL/stack"
    )

    assert response.status_code == 200

    assert response.json() == {
        "long_url": "https://stackoverflow.com"
    }

def test_url_not_found():

    response = client.get(
        "/getOriginalURL/notfound"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Short URL not found"
    }