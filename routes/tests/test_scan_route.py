import base64
import json
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routes import scan_route  # adjust import to your file structure
import os

app = FastAPI()
app.include_router(scan_route.scan_route, prefix="/api/v1")

client = TestClient(app)

glyphdlp_api_key = os.environ.get("glyphdlp_api_key")


def test_successful_scan_text():
    content = "example@example.com"
    encoded_content = base64.b64encode(content.encode()).decode()
    headers = {"Authorization": "Bearer " + glyphdlp_api_key}
    payload = {"content": encoded_content}
    response = client.post("/api/v1/scan", data=json.dumps(payload), headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert response.json()["message"] == "Success"
    assert response.json()["content_type"] == "text/plain"
    assert response.json()["findings"] == {"email_address": ["example@example.com"]}


def test_successful_scan_csv():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(current_dir, "test_files", "test_csv.csv")

    with open(test_file_path, "rb") as file:
        content = file.read()
        encoded_content = base64.b64encode(content).decode()

    headers = {"Authorization": "Bearer " + glyphdlp_api_key}
    payload = {"content": encoded_content}
    response = client.post("/api/v1/scan", data=json.dumps(payload), headers=headers)

    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert response.json()["message"] == "Success"
    assert response.json()["content_type"] == "text/csv"
    assert response.json()["findings"] == {"email_address": ["example@example.com"]}


def test_successful_scan_docx():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(current_dir, "test_files", "test_docx.docx")

    with open(test_file_path, "rb") as file:
        content = file.read()
        encoded_content = base64.b64encode(content).decode()

    headers = {"Authorization": "Bearer " + glyphdlp_api_key}
    payload = {"content": encoded_content}
    response = client.post("/api/v1/scan", data=json.dumps(payload), headers=headers)

    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert response.json()["message"] == "Success"
    assert (
        response.json()["content_type"]
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert response.json()["findings"] == {"email_address": ["example@example.com"]}


def test_successful_scan_json():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(current_dir, "test_files", "test_json.json")

    with open(test_file_path, "rb") as file:
        content = file.read()
        encoded_content = base64.b64encode(content).decode()

    headers = {"Authorization": "Bearer " + glyphdlp_api_key}
    payload = {"content": encoded_content}
    response = client.post("/api/v1/scan", data=json.dumps(payload), headers=headers)

    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert response.json()["message"] == "Success"
    assert response.json()["content_type"] == "application/json"
    assert response.json()["findings"] == {"email_address": ["example@example.com"]}


def test_successful_scan_pdf():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(current_dir, "test_files", "test_pdf.pdf")

    with open(test_file_path, "rb") as file:
        content = file.read()
        encoded_content = base64.b64encode(content).decode()

    headers = {"Authorization": "Bearer " + glyphdlp_api_key}
    payload = {"content": encoded_content}
    response = client.post("/api/v1/scan", data=json.dumps(payload), headers=headers)

    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert response.json()["message"] == "Success"
    assert response.json()["content_type"] == "application/pdf"
    assert response.json()["findings"] == {"email_address": ["example@example.com"]}


def test_successful_scan_xlsx():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(current_dir, "test_files", "test_xlsx.xlsx")

    with open(test_file_path, "rb") as file:
        content = file.read()
        encoded_content = base64.b64encode(content).decode()

    headers = {"Authorization": "Bearer " + glyphdlp_api_key}
    payload = {"content": encoded_content}
    response = client.post("/api/v1/scan", data=json.dumps(payload), headers=headers)

    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert response.json()["message"] == "Success"
    assert (
        response.json()["content_type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert response.json()["findings"] == {"email_address": ["example@example.com"]}


def test_payload_too_large():
    content = "A" * (10 * 1024 * 1024 + 1)  # Just over 10MB
    encoded_content = base64.b64encode(content.encode()).decode()
    headers = {"Authorization": "Bearer " + glyphdlp_api_key}
    payload = {"content": encoded_content}
    response = client.post("/api/v1/scan", data=json.dumps(payload), headers=headers)
    assert response.status_code == 400
    assert response.json()["message"] == "Request payload too large"


def test_invalid_parameters():
    headers = {"Authorization": "Bearer " + glyphdlp_api_key}
    payload = {"content": "SGVsbG8sIFdvcmxkIQ==", "extra": "invalid_param"}
    response = client.post("/api/v1/scan", data=json.dumps(payload), headers=headers)
    assert response.status_code == 400
    assert (
        response.json()["message"]
        == "Invalid parameters: only 'content' parameter is allowed"
    )


def test_invalid_base64_content():
    headers = {"Authorization": "Bearer " + glyphdlp_api_key}
    payload = {"content": "invalid_base64!!"}
    response = client.post("/api/v1/scan", data=json.dumps(payload), headers=headers)
    assert response.status_code == 400
    assert response.json()["message"] == "Invalid base64 content"
