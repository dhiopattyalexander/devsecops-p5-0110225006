"""
Unit tests for Flask HTTP REST API routes.
"""

import pytest
from src.app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "secure-task-api"


def test_task_api_workflow(client):
    # 1. Create a task
    create_resp = client.post("/api/v1/tasks", json={
        "title": "Config SAST Bandit",
        "description": "Add Bandit to GitHub Actions pipeline",
        "priority": "high"
    })
    assert create_resp.status_code == 201
    created_task = create_resp.get_json()["data"]
    task_id = created_task["task_id"]

    # 2. Get task detail
    get_resp = client.get(f"/api/v1/tasks/{task_id}")
    assert get_resp.status_code == 200
    assert get_resp.get_json()["data"]["title"] == "Config SAST Bandit"

    # 3. List tasks
    list_resp = client.get("/api/v1/tasks")
    assert list_resp.status_code == 200
    assert list_resp.get_json()["data"]["count"] >= 1

    # 4. Update status
    update_resp = client.put(f"/api/v1/tasks/{task_id}/status", json={"status": "completed"})
    assert update_resp.status_code == 200
    assert update_resp.get_json()["data"]["status"] == "completed"

    # 5. Delete task
    del_resp = client.delete(f"/api/v1/tasks/{task_id}")
    assert del_resp.status_code == 200


def test_validation_error_handling(client):
    # Missing required title
    resp = client.post("/api/v1/tasks", json={"description": "Missing title"})
    assert resp.status_code == 400
    assert resp.get_json()["success"] is False
