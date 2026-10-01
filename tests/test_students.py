from fastapi.testclient import TestClient

URL = "/api/v1/students"


def payload(n: int = 1, **over: object) -> dict[str, object]:
    base = {
        "admission_number": f"ADM-{n:05d}",
        "first_name": "Asha",
        "last_name": "Verma",
        "date_of_birth": "2012-05-01",
        "gender": "female",
        "guardian_name": "R Verma",
        "guardian_phone": "9876543210",
    }
    return {**base, **over}


def test_requires_auth(client: TestClient) -> None:
    assert client.get(URL).status_code == 401


def test_bad_login(client: TestClient) -> None:
    r = client.post("/api/v1/auth/login", json={"username": "admin", "password": "nope"})
    assert r.status_code == 401


def test_create_get_update_delete(client: TestClient, admin: dict[str, str]) -> None:
    r = client.post(URL, json=payload(), headers=admin)
    assert r.status_code == 201
    sid = r.json()["id"]

    assert client.get(f"{URL}/{sid}", headers=admin).json()["first_name"] == "Asha"

    r = client.patch(f"{URL}/{sid}", json={"first_name": "Isha", "status": "graduated"}, headers=admin)
    assert r.json()["first_name"] == "Isha" and r.json()["status"] == "graduated"

    assert client.delete(f"{URL}/{sid}", headers=admin).status_code == 204
    assert client.get(f"{URL}/{sid}", headers=admin).status_code == 404  # soft-deleted


def test_duplicate_admission_number(client: TestClient, admin: dict[str, str]) -> None:
    assert client.post(URL, json=payload(), headers=admin).status_code == 201
    r = client.post(URL, json=payload(), headers=admin)
    assert r.status_code == 409 and r.json()["error"]["code"] == "conflict"


def test_validation(client: TestClient, admin: dict[str, str]) -> None:
    assert client.post(URL, json=payload(date_of_birth="2999-01-01"), headers=admin).status_code == 422
    assert client.post(URL, json=payload(guardian_phone="abc"), headers=admin).status_code == 422


def test_unknown_classroom(client: TestClient, admin: dict[str, str]) -> None:
    assert client.post(URL, json=payload(classroom_id=999), headers=admin).status_code == 404


def test_rbac_teacher_is_read_only(client: TestClient, teacher: dict[str, str]) -> None:
    assert client.post(URL, json=payload(), headers=teacher).status_code == 403
    assert client.get(URL, headers=teacher).status_code == 200


def test_pagination_search_filter(client: TestClient, admin: dict[str, str]) -> None:
    cls = client.post(
        "/api/v1/classrooms", json={"grade": 5, "section": "A", "academic_year": "2025-2026"}, headers=admin
    ).json()
    for n in range(1, 26):
        client.post(
            URL,
            json=payload(n, first_name="Zoya" if n % 5 == 0 else "Asha", classroom_id=cls["id"] if n <= 10 else None),
            headers=admin,
        )

    page = client.get(URL, params={"size": 10, "page": 3}, headers=admin).json()
    assert page["total"] == 25 and len(page["items"]) == 5 and page["pages"] == 3

    assert client.get(URL, params={"q": "zoy"}, headers=admin).json()["total"] == 5
    assert client.get(URL, params={"classroom_id": cls["id"]}, headers=admin).json()["total"] == 10
    assert client.get(URL, params={"size": 1000}, headers=admin).status_code == 422  # capped


def test_health(client: TestClient) -> None:
    assert client.get("/health/ready").json() == {"status": "ok"}
