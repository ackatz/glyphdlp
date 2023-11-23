from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routes import types_route  # Adjust import based on your file structure
import os

app = FastAPI()
app.include_router(types_route.types_route, prefix="/api/v1")

client = TestClient(app)

glyphdlp_api_key = os.environ.get("glyphdlp_api_key")


def test_file_types():
    headers = {"Authorization": "Bearer " + glyphdlp_api_key}
    response = client.get("/api/v1/files", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert response.json()["message"] == "Success"
    # Checking that the response contains the 'accepted_mime_types' key and its value is a list
    assert isinstance(response.json().get("accepted_mime_types"), list)


def test_detection_types():
    headers = {"Authorization": "Bearer " + glyphdlp_api_key}
    response = client.get("/api/v1/detections", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert response.json()["message"] == "Success"
    # Checking that the response contains the 'supported_detections' key and its value is a list
    assert isinstance(response.json().get("supported_detections"), list)
