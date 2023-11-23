from fastapi import FastAPI, Request, Form, File, UploadFile
from starlette.responses import JSONResponse, PlainTextResponse
from app.routes.scan_route import scan_route
from app.routes.redact_route import redact_route
from app.routes.types_route import types_route
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from app.dbo.new_user import new_user
from app.dbo.login import login
from app.dbo.delete_user_if_exists import delete_user
from fastapi import HTTPException
from fastapi.openapi.utils import get_openapi
from app.upload_operations import upload_scan, upload_redact
import requests
import os
import stripe
import sendgrid
import base64
from slowapi import Limiter
from typing import Union


def get_real_address(request: Request) -> Union[str, None]:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        real_ip = forwarded_for.split(",")[0]
    else:
        real_ip = request.client.host
    return real_ip



recaptcha_site_key = os.environ.get("recaptcha_site_key")
recaptcha_secret_key = os.environ.get("recaptcha_secret_key")
limiter = Limiter(key_func=get_real_address)


class FormData(BaseModel):
    username: str
    email: str


app = FastAPI(
    redoc_url=None,
    docs_url="/api/v1/docs",
    description="""Glyph DLP is a data loss prevention API that can be used to scan or redact sensitive data from documents.
              Send Glyph a Base64-encoded document via our secure REST API and we will scan or redact any sensitive information.
              
              Community ("free") accounts are limited to 20 requests per day. If you exceed this limit, you will receive a 429 error.

              If you require more than 20 requests per day, please view our pricing page and consider upgrading to a Premium or Pro account.
              
              """,
    title="Glyph DLP",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    servers=[{"url": "https://glyphdlp.com"}],
    contact={
        "name": "Glyph DLP",
        "url": "https://glyphdlp.com",
        "email": "info@glyphdlp.com",
    },
)

# Custom OpenAPI to remove 422


def custom_openapi():
    if not app.openapi_schema:
        app.openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            terms_of_service=app.terms_of_service,
            contact=app.contact,
            license_info=app.license_info,
            routes=app.routes,
            tags=app.openapi_tags,
            servers=app.servers,
        )
        for _, method_item in app.openapi_schema.get("paths").items():
            for _, param in method_item.items():
                responses = param.get("responses")
                # remove 422 response, also can remove other status code
                if "422" in responses:
                    del responses["422"]
        # Delete schemas
        for schema in list(app.openapi_schema["components"]["schemas"]):
            if schema == "HTTPValidationError" or schema == "ValidationError":
                del app.openapi_schema["components"]["schemas"][schema]

    return app.openapi_schema


app.openapi = custom_openapi

app.include_router(scan_route, prefix="/api/v1")
app.include_router(redact_route, prefix="/api/v1")
app.include_router(types_route, prefix="/api/v1")
app.mount("/app/static", StaticFiles(directory="/app/static"), name="static")
templates = Jinja2Templates(directory="/app/templates")


@app.middleware("http")
async def custom_http_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers[
        "Strict-Transport-Security"
    ] = "max-age=31536000; includeSubDomains"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "no-referrer"
    csp_header = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com/ https://cdn.tailwindcss.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://cdn.counter.dev https://www.google.com/recaptcha/ https://www.gstatic.com/recaptcha/; "
        "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; "
        "img-src 'self' https://glyphdlp.com data:; "
        "connect-src 'self' https://cdn.counter.dev https://t.counter.dev/; "
        "font-src 'self' https://cdnjs.cloudflare.com; "
        "frame-src 'self' https://www.google.com/recaptcha/; "
        "base-uri 'none'; "
        "form-action 'self'; "
        "block-all-mixed-content; "
        "upgrade-insecure-requests;"
    )
    response.headers["Content-Security-Policy"] = csp_header
    response.headers["X-Content-Type-Options"] = "nosniff"

    if response.status_code in (404, 405) and not request.url.path.startswith(
        "/api/v1"
    ):
        return templates.TemplateResponse(
            "404.html", {"request": request}, status_code=404
        )
    elif response.status_code == 500 and not request.url.path.startswith("/api/v1"):
        return templates.TemplateResponse(
            "ouch.html", {"request": request}, status_code=500
        )
    return response


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def page_index(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("index.html", context)


@app.get("/demo", response_class=HTMLResponse, include_in_schema=False)
async def upload_page(request: Request):
    return templates.TemplateResponse("demo.html", {"request": request})


@app.post("/process_file", include_in_schema=False)
@limiter.limit("2/minute")
async def process_file(request: Request, file: UploadFile = File(...), action: str = Form(...)):

    content = await file.read()

    encoded_content = base64.b64encode(content)

    if action == "scan":

        response = await upload_scan.scan(encoded_content)

        return response

    if action == "redact":

        response = await upload_redact.redact(encoded_content)

        return response

@app.get("/contact", response_class=HTMLResponse, include_in_schema=False)
async def page_contact(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("contact.html", context)


@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
async def page_docs(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("docs.html", context)


@app.get("/register", response_class=HTMLResponse, include_in_schema=False)
async def page_register(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("register.html", context)


@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def page_login(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("register.html", context)


@app.get("/privacy", response_class=HTMLResponse, include_in_schema=False)
async def page_privacy(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("privacy.html", context)


@app.get("/pricing", response_class=HTMLResponse, include_in_schema=False)
async def page_pricing(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("pricing.html", context)


@app.post("/submit", response_class=HTMLResponse, include_in_schema=False)
async def function_register_free_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    g_recaptcha_response: str = Form(
        "", alias="g-recaptcha-response"
    ),  # Capture the reCAPTCHA response
):
    # Check for the presence of the g-recaptcha-response field
    if not g_recaptcha_response:
        context = {"request": request, "message": "reCAPTCHA verification failed"}
        return templates.TemplateResponse("register.html", context)

    # Verify the reCAPTCHA response
    response = requests.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={
            "secret": recaptcha_secret_key,  # Replace with your reCAPTCHA secret key
            "response": g_recaptcha_response,
        },
    )
    result = response.json()
    if not result["success"]:
        context = {"request": request, "message": "reCAPTCHA verification failed"}
        return templates.TemplateResponse("register.html", context)

    try:
        api_key = await new_user(request, username, email, 20)

        context = {"request": request, "api_key": api_key}

        return templates.TemplateResponse("submit.html", context)

    except HTTPException as e:
        context = {"request": request, "message": "User already exists"}
        return templates.TemplateResponse("register.html", context)


@app.post("/login", response_class=HTMLResponse, include_in_schema=False)
async def function_user_login(
    request: Request,
    api_key: str = Form(...),
    email_login: str = Form(...),
    g_recaptcha_response: str = Form(
        "", alias="g-recaptcha-response"
    ),  # Capture the reCAPTCHA response
):
    # Check for the presence of the g-recaptcha-response field
    if not g_recaptcha_response:
        context = {"request": request, "message": "reCAPTCHA verification failed"}
        return templates.TemplateResponse("register.html", context)

    # Verify the reCAPTCHA response
    response = requests.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={
            "secret": recaptcha_secret_key,  # Replace with your reCAPTCHA secret key
            "response": g_recaptcha_response,
        },
    )
    result = response.json()
    if not result["success"]:
        context = {"request": Request, "message": "reCAPTCHA verification failed"}
        return templates.TemplateResponse("register.html", context)

    try:
        account_info = await login(request, api_key, email_login)

        user_name = account_info[1]
        user_email = account_info[2]
        user_max_requests = account_info[3]

        context = {
            "request": request,
            "api_key": api_key,
            "user_name": user_name,
            "user_email": user_email,
            "user_max_requests": user_max_requests,
        }
        return templates.TemplateResponse("account.html", context)

    except HTTPException as e:
        context = {"request": request, "message": "API key not found"}
        return templates.TemplateResponse("register.html", context)


@app.post("/stripe_submit", response_class=HTMLResponse, include_in_schema=False)
async def function_register_paid_user(request: Request):
    sig_header = request.headers.get("Stripe-Signature")
    if not sig_header:
        context = {"request": request, "message": "Stripe verification failed"}
        return templates.TemplateResponse("register.html", context)

    payload = await request.body()

    stripe_signing_secret = os.environ.get("stripe_signing_secret")
    stripe.api_key = os.environ.get("stripe_secret_key")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_signing_secret
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")

    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    if event.type == "payment_intent.succeeded":
        session = event.data.object

        customer_id = session.customer

        customer = stripe.Customer.retrieve(customer_id)

        email = customer.email
        username = customer.name

        if session["amount"] == 300:
            await delete_user(email)

            max_requests = 250
            api_key = await new_user(request, username, email, max_requests)

            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail

            dynamic_data = {"api_key": api_key}

            message = Mail(
                from_email="info@glyphdlp.com",
                to_emails=email,
                subject="Glyph DLP - Your API Key",
            )

            message.dynamic_template_data = dynamic_data
            message.template_id = "d-79d8029d6c864bc2b2797f0946670029"
            sg = SendGridAPIClient(os.environ.get("sendgrid_api_key"))
            sg.send(message)

        if session["amount"] == 2000:
            await delete_user(email)

            max_requests = 2000
            api_key = await new_user(request, username, email, max_requests)

            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail

            dynamic_data = {"api_key": api_key}

            message = Mail(
                from_email="info@glyphdlp.com",
                to_emails=email,
                subject="Glyph DLP - Your API Key",
            )

            message.dynamic_template_data = dynamic_data
            message.template_id = "d-79d8029d6c864bc2b2797f0946670029"
            sg = SendGridAPIClient(os.environ.get("sendgrid_api_key"))
            sg.send(message)

    return JSONResponse(status_code=200, content={"message": "Success"})


@app.get("/robots.txt", response_class=PlainTextResponse, include_in_schema=False)
async def read_robots(request: Request):
    content = """
    User-agent: *
    Disallow:
    """
    return PlainTextResponse(content)
