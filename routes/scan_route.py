from fastapi import Request
from fastapi.responses import JSONResponse
import json
import base64
import magic
from app.dbo.auth import request_authorization
from app.dbo.rate_limiting import request_ratelimit
from app.operations import (
    text_type,
    xlsx_type,
    csv_type,
    json_type,
    word_type,
    pdf_type,
)
import binascii
from fastapi import APIRouter, HTTPException, Depends
from app.detections import accepted_mime_types
from pydantic import BaseModel, Field


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


class ScanRequestBody(BaseModel):
    content: str = Field(..., description="The Base64-encoded content to be scanned")


scan_route = APIRouter()


@scan_route.post(
    "/scan",
    summary="Scan a Base64-encoded file",
    description="Scan a Base64-encoded file",
    response_description="Scan a Base64-encoded a file",
    response_class=PrettyJSONResponse,
    tags=["File Operations"],
    responses={
        200: {
            "description": "Success",
            "content": {
                "application/json": {
                    "example": {
                        "status": 200,
                        "message": "Success",
                        "content_type": "text/plain",
                        "findings": [{"email_address": "example@example.org"}],
                    }
                }
            },
        },
        400: {
            "description": "Invalid parameters",
            "content": {
                "application/json": {
                    "example": {
                        "status": 400,
                        "message": "Invalid parameters: only 'content' parameter is allowed",
                    }
                }
            },
        },
        403: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {
                        "status": 403,
                        "message": "Invalid API key",
                    }
                }
            },
        },
        429: {
            "description": "Rate limit exceeded",
            "content": {
                "application/json": {
                    "example": {
                        "status": 429,
                        "message": "Rate limit exceeded",
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {
                        "status": 500,
                        "message": "Error returning scan: <Exception>",
                    }
                }
            },
        },
    },
)
async def scan(
    scan_request: ScanRequestBody,
    request: Request,
    user: dict = Depends(request_authorization),
):
    rate_limit_remaining = await request_ratelimit(request, user)

    if rate_limit_remaining < 1:
        return JSONResponse(
            content={
                "status": 429,
                "message": "Rate limit exceeded",
            },
            headers={"X-RateLimit-Remaining": str(rate_limit_remaining)},
            status_code=429,
        )

    message_body = await request.body()

    max_size = 10 * 1024 * 1024  # 10MB

    if len(message_body) > max_size:
        return JSONResponse(
            content={"status": 400, "message": "Request payload too large"},
            status_code=400,
        )

    body_json = json.loads(message_body)

    # Check if only the 'content' key is present in body_json
    if set(body_json.keys()) != {"content"}:
        return JSONResponse(
            content={
                "status": 400,
                "message": "Invalid parameters: only 'content' parameter is allowed",
            },
            status_code=400,
        )

    try:
        encoded_content = scan_request.content

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

        return JSONResponse(
            content={
                "status": 200,
                "message": "Success",
                "content_type": content_type,
                "findings": findings,
            },
            headers={"X-RateLimit-Remaining": str(rate_limit_remaining)},
            status_code=200,
        )

    # This will catch the HTTPException first before the generic Exception
    except HTTPException as he:
        return JSONResponse(
            content={"status": he.status_code, "message": he.detail},
            status_code=he.status_code,
        )

    except Exception as e:
        return JSONResponse(
            content={"status": 500, "message": "Error returning scan: " + str(e)},
            status_code=500,
        )