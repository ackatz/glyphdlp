import http
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, Depends
from app.dbo.auth import request_authorization
from app.detections import accepted_mime_types, regex

types_route = APIRouter()


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

@types_route.get(
    "/files",
    summary="Get accepted file types",
    description="Get accepted file types",
    response_description="Get accepted file types",
    response_class=PrettyJSONResponse,
    tags=["Types"],
    responses={
        200: {
            "description": "Success",
            "content": {
                "application/json": {
                    "example": {
                        "status": 200,
                        "message": "Success",
                        "accepted_mime_types": [
                            "text/csv",
                            "application/pdf",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            "text/plain",
                            "application/json",
                        ],
                    }
                }
            },
        },
        403: {
            "description": "Invalid API key",
            "content": {
                "application/json": {
                    "example": {
                        "status": 403,
                        "message": "Invalid API key",
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
                        "message": "Error returning accepted file types: <Exception>",
                    }
                }
            },
        },
    },
)
async def file_types(request: Request, user: dict = Depends(request_authorization)):
    try:
        # Main returned JSON response

        return JSONResponse(
            content={
                "status": 200,
                "message": "Success",
                "accepted_mime_types": list(accepted_mime_types.type_list),
            },
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
            content={
                "status": 500,
                "message": "Error returning accepted mime types: " + str(e),
            },
            status_code=500,
        )


@types_route.get(
    "/detections",
    summary="List supported detections",
    description="List supported detections",
    response_description="List supported detections",
    response_class=PrettyJSONResponse,
    tags=["Types"],
    responses={
        200: {
            "description": "Success",
            "content": {
                "application/json": {
                    "example": {
                        "status": 200,
                        "message": "Success",
                        "supported_detections": [
                            "ssn",
                            "credit_card",
                            "account_number",
                            "routing_number",
                            "tax_id",
                            "email_address",
                            "date_of_birth",
                            "medical_record_number",
                            "id_or_passport",
                            "health_insurance",
                            "medicare_number",
                        ],
                    }
                }
            },
        },
        403: {
            "description": "Invalid API key",
            "content": {
                "application/json": {
                    "example": {
                        "status": 403,
                        "message": "Invalid API key",
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
                        "message": "Error returning supported detections: <Exception>",
                    }
                }
            },
        },
    },
)
async def detection_types(
    request: Request, user: dict = Depends(request_authorization)
):
    try:
        # Main returned JSON response

        return JSONResponse(
            content={
                "status": 200,
                "message": "Success",
                "supported_detections": list(regex.patterns.keys()),
            },
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
            content={
                "status": 500,
                "message": "Error returning supported detections: " + str(e),
            },
            status_code=500,
        )
