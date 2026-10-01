import os

os.environ["SMS_ENVIRONMENT"] = "test"
os.environ["SMS_SECRET_KEY"] = "test-secret-key-test-secret-key-0123456789"
os.environ["SMS_DATABASE_URL"] = "sqlite:///./data/test.db"

from collections.abc import Iterator  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.core.security import hash_password  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import User  # noqa: E402
from app.models.enums import Role  # noqa: E402


@pytest.fixture(autouse=True)
def _fresh_db() -> Iterator[None]:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as s:
        s.add_all(
            [
                User(username="admin", full_name="Admin", password_hash=hash_password("pw"), role=Role.ADMIN),
                User(username="teacher", full_name="T", password_hash=hash_password("pw"), role=Role.TEACHER),
            ]
        )
        s.commit()
    yield


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _login(client: TestClient, username: str) -> dict[str, str]:
    r = client.post("/api/v1/auth/login", json={"username": username, "password": "pw"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def admin(client: TestClient) -> dict[str, str]:
    return _login(client, "admin")


@pytest.fixture
def teacher(client: TestClient) -> dict[str, str]:
    return _login(client, "teacher")
