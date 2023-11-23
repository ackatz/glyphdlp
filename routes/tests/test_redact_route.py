import base64
import json
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routes import redact_route  # adjust import to your file structure
import os

app = FastAPI()
app.include_router(redact_route.redact_route, prefix="/api/v1")

client = TestClient(app)

glyphdlp_api_key = os.environ.get("glyphdlp_api_key")


def test_successful_redact_text():
    content = "example@example.com"
    encoded_content = base64.b64encode(content.encode()).decode()
    headers = {"Authorization": "Bearer " + glyphdlp_api_key}
    payload = {"content": encoded_content}
    response = client.post("/api/v1/redact", data=json.dumps(payload), headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert response.json()["message"] == "Success"
    assert response.json()["content_type"] == "text/plain"
    assert response.json()["redacted"] == "[REDACTED]"


def test_successful_redact_csv():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(current_dir, "test_files", "test_csv.csv")

    with open(test_file_path, "rb") as file:
        content = file.read()
        encoded_content = base64.b64encode(content).decode()

    headers = {"Authorization": "Bearer " + glyphdlp_api_key}
    payload = {"content": encoded_content}
    response = client.post("/api/v1/redact", data=json.dumps(payload), headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert response.json()["message"] == "Success"
    assert response.json()["content_type"] == "text/csv"
    # Check that 'redacted' contains valid Base64 encoded data
    try:
        base64.b64decode(response.json()["redacted"])
        is_valid_base64 = True
    except base64.binascii.Error:
        is_valid_base64 = False
    assert (
        is_valid_base64
    ), "Returned redacted content is not valid Base64 encoded data."


def test_successful_redact_docx():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(current_dir, "test_files", "test_docx.docx")

    with open(test_file_path, "rb") as file:
        content = file.read()
        encoded_content = base64.b64encode(content).decode()

    headers = {"Authorization": "Bearer " + glyphdlp_api_key}
    payload = {"content": encoded_content}
    response = client.post("/api/v1/redact", data=json.dumps(payload), headers=headers)

    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert response.json()["message"] == "Success"
    assert (
        response.json()["content_type"]
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    # Check that 'redacted' contains valid Base64 encoded data
    try:
        base64.b64decode(response.json()["redacted"])
        is_valid_base64 = True
    except base64.binascii.Error:
        is_valid_base64 = False
    assert (
        is_valid_base64
    ), "Returned redacted content is not valid Base64 encoded data."


def test_successful_redact_json():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(current_dir, "test_files", "test_json.json")

    with open(test_file_path, "rb") as file:
        content = file.read()
        encoded_content = base64.b64encode(content).decode()

    headers = {"Authorization": "Bearer " + glyphdlp_api_key}
    payload = {"content": encoded_content}
    response = client.post("/api/v1/redact", data=json.dumps(payload), headers=headers)

    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert response.json()["message"] == "Success"
    assert response.json()["content_type"] == "application/json"
    assert response.text.count("[REDACTED]") == 1


def test_successful_redact_pdf():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(current_dir, "test_files", "test_pdf.pdf")

    with open(test_file_path, "rb") as file:
        content = file.read()
        encoded_content = base64.b64encode(content).decode()

    headers = {"Authorization": "Bearer " + glyphdlp_api_key}
    payload = {"content": encoded_content}
    response = client.post("/api/v1/redact", data=json.dumps(payload), headers=headers)

    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert response.json()["message"] == "Success"
    assert response.json()["content_type"] == "application/pdf"
    # Check that 'redacted' contains valid Base64 encoded data
    try:
        base64.b64decode(response.json()["redacted"])
        is_valid_base64 = True
    except base64.binascii.Error:
        is_valid_base64 = False
    assert (
        is_valid_base64
    ), "Returned redacted content is not valid Base64 encoded data."


def test_successful_redact_xlsx():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(current_dir, "test_files", "test_xlsx.xlsx")

    with open(test_file_path, "rb") as file:
        content = file.read()
        encoded_content = base64.b64encode(content).decode()

    headers = {"Authorization": "Bearer " + glyphdlp_api_key}
    payload = {"content": encoded_content}
    response = client.post("/api/v1/redact", data=json.dumps(payload), headers=headers)

    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert response.json()["message"] == "Success"
    assert (
        response.json()["content_type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    # Check that 'redacted' contains valid Base64 encoded data
    try:
        base64.b64decode(response.json()["redacted"])
        is_valid_base64 = True
    except base64.binascii.Error:
        is_valid_base64 = False
    assert (
        is_valid_base64
    ), "Returned redacted content is not valid Base64 encoded data."


def test_payload_too_large():
    content = "A" * (10 * 1024 * 1024 + 1)  # Just over 10MB
    encoded_content = base64.b64encode(content.encode()).decode()
    headers = {"Authorization": "Bearer " + glyphdlp_api_key}
    payload = {"content": encoded_content}
    response = client.post("/api/v1/redact", data=json.dumps(payload), headers=headers)
    assert response.status_code == 400
    assert response.json()["message"] == "Request payload too large"


def test_invalid_parameters():
    headers = {"Authorization": "Bearer " + glyphdlp_api_key}
    payload = {"content": "SGVsbG8sIFdvcmxkIQ==", "extra": "invalid_param"}
    response = client.post("/api/v1/redact", data=json.dumps(payload), headers=headers)
    assert response.status_code == 400
    assert (
        response.json()["message"]
        == "Invalid parameters: only 'content' parameter is allowed"
    )


def test_invalid_base64_content():
    headers = {"Authorization": "Bearer " + glyphdlp_api_key}
    payload = {"content": "invalid_base64!!"}
    response = client.post("/api/v1/redact", data=json.dumps(payload), headers=headers)
    assert response.status_code == 400
    assert response.json()["message"] == "Invalid base64 content"
