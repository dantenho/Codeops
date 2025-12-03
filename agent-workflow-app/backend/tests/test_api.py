"""Basic API smoke tests."""

from app import create_app


def test_list_workflows():
    app = create_app()
    client = app.test_client()
    response = client.get("/api/workflows")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_skeleton_summary():
    app = create_app()
    client = app.test_client()
    response = client.get("/api/skeleton/summary")
    assert response.status_code == 200
    data = response.get_json()
    assert "total_workflows" in data

