import string
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from main import app, generate_short_code
from database import Base, engine, get_db
from unittest.mock import patch

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

def test_read_root():
    response = client.get("")
    assert response.status_code == 200
    assert response.json() == "Server is running"

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

def setup():
    Base.metadata.create_all(bind=engine)

def teardown():
    Base.metadata.drop_all(bind=engine)