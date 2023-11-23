from fastapi.responses import JSONResponse
import base64
import magic
from app.operations import (
    text_type,
    xlsx_type,
    csv_type,
    json_type,
    word_type,
    pdf_type,
)
import binascii
from app.detections import accepted_mime_types
import json, typing
from starlette.responses import Response


class PrettyJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=4,
            separators=(", ", ": "),
        ).encode("utf-8")


async def scan(encoded_content):

    max_size = 10 * 1024 * 1024  # 10MB

    if len(encoded_content) > max_size:
        return JSONResponse(
            content={"status": 400, "message": "Request payload too large"},
            status_code=400,
        )

    try:
        decoded_content = base64.b64decode(encoded_content)

    except binascii.Error:  # this will catch invalid base64 errors
        return JSONResponse(
            content={"status": 400, "message": "Invalid base64 content"},
            status_code=400,
        )

    content_type = magic.from_buffer(decoded_content, mime=True)

    # Check if the MIME type is in ACCEPTED_MIME_TYPES
    if content_type not in accepted_mime_types.type_list:
        return JSONResponse(
            content={"status": 400, "message": "Unsupported file type"},
            status_code=400,
        )

    # Plain Text Scan

    if content_type == "text/plain":
        findings = text_type.scan(decoded_content.decode("utf-8"))

    # XLSX Scan

    if (
        content_type
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ):
        findings = xlsx_type.scan(decoded_content)

    # CSV Scan

    if content_type == "text/csv":
        findings = csv_type.scan(decoded_content)

    # JSON Scan

    if content_type == "application/json":
        findings = json_type.scan(decoded_content)

    # Word Scan

    if (
        content_type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        findings = word_type.scan(decoded_content)

    # PDF Scan

    if content_type == "application/pdf":
        findings = pdf_type.scan(decoded_content)

    # Main returned JSON response

    return PrettyJSONResponse(
        content={
            "status": 200,
            "message": "Success",
            "content_type": content_type,
            "findings": findings,
        },
        status_code=200,
    )
