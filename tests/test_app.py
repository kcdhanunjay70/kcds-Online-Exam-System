from app import create_app


def client():
    app = create_app({"TESTING": True, "SECRET_KEY": "test", "MONGO_URI": ""})
    return app.test_client()


def test_home_and_health():
    test_client = client()
    assert test_client.get("/").status_code == 200
    response = test_client.get("/api/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_complete_exam_flow():
    test_client = client()
    response = test_client.post(
        "/start",
        data={"name": "Test Student", "email": "student@example.com"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Question 1 of 10" in response.data

    response = test_client.post(
        "/submit",
        data={f"question_{i}": "0" for i in range(1, 11)},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Assessment complete" in response.data


def test_exam_requires_candidate():
    response = client().get("/exam")
    assert response.status_code == 302
