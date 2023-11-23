# Glyph DLP

## Introduction

Glyph DLP is an API-based data loss prevention solution.

## Testing

Decrypt the .env file

```commandline
age -d -i ~/.age/ak.age -o .env .env.age
```

Log in to Stripe

```commandline
stripe login
```

Forward events to the Glyph DLP /stripe_submit endpoint

```commandline
stripe listen --forward-to localhost:8000/stripe_submit
```

Add the Stripe webhook signing secret to the .env file

```commandline
STRIPE_WEBHOOK_SECRET=whsec_...
```

Build the container

```commandline
docker build -f Dockerfile-tests -t glyphdlp-tests .
```

Run the container

```commandline
docker run -p 8000:8000 --env-file .env glyphdlp-tests
```

Run the tests inside the container

```commandline
pytest -vs /app
```

## Features

### Scan for sensitive information

Glyph can automatically recognize and scan for sensitive data from the following file types:

- Text
- Word (.DOCX)
- Excel (.XLSX/.XLS)
- CSV
- JSON

The API returns a JSON object that shows which sensitive data types were found in the file.

##### Example request

```json
{
  "scan": "ewogICAgImdsb3NzYXJ5IjogewogICAgICAgICJ0aXRsZSI6ICJleGFtcGxlIGdsb3NzYXJ5IiwKCQkiR2xvc3NEaXYiOiB7CiAgICAgICAgICAgICJ0aXRsZSI6ICJTIiwKCQkJIkdsb3NzTGlzdCI6IHsKICAgICAgICAgICAgICAgICJHbG9zc0VudHJ5IjogewogICAgICAgICAgICAgICAgICAgICJJRCI6ICJTR01MIiwKCQkJCQkiU29ydEFzIjogIlNHTUwiLAoJCQkJCSJHbG9zc1Rlcm0iOiAiMDkwLTI0LTIxNDMiLAoJCQkJCSJBY3JvbnltIjogIkRMMTIzNDU2NyIsCgkJCQkJIkFiYnJldiI6ICJJU08gODg3OToxOTg2IiwKCQkJCQkiR2xvc3NEZWYiOiB7CiAgICAgICAgICAgICAgICAgICAgICAgICJwYXJhIjogIkEgbWV0YS1tYXJrdXAgbGFuZ3VhZ2UsIHVzZWQgdG8gY3JlYXRlIG1hcmt1cCBsYW5ndWFnZXMgc3VjaCBhcyBEb2NCb29rLiIsCgkJCQkJCSJHbG9zc1NlZUFsc28iOiBbIkdNTCIsICJYTUwiXQogICAgICAgICAgICAgICAgICAgIH0sCgkJCQkJIkdsb3NzU2VlIjogImFuZHJld0Bha2F0ei5vcmciCiAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgIH0KICAgICAgICB9CiAgICB9Cn0="
}
```

##### Example response

```json
{
  "status": 200,
  "message": "Success",
  "content_type": "application/json",
  "findings": {
    "email_address": ["andrew@akatz.org"]
  }
}
```

### Redact sensitive information

Glyph can automatically recognize and redact sensitive data from the following file types:

- Text -> Returns text
- Excel (.XLSX) -> Returns Base64-encoded .XLSX file
- CSV -> Returns CSV --> Returns Base64-encoded .CSV file
- JSON -> Returns JSON
- Word (.DOCX) -> Returns Base64-encoded .DOCX file

## Todo

### File Type Additions

- Scan and redact sensitive information from the following file types

  - [x] Word (.DOCX)
  - [x] PDF
  - [x] JSON
  - [x] CSV

- Detections

  - [ ] API keys
  - [ ] Private keys
  - [ ] Anything else?

- Tests

  - [x] Detections
  - [ ] All routes
  - [ ] Operations

- Misc
  - [x] Get Domains (.com, .app, .net)
  - [x] Set up domains
  - [x] Front end of website
  - [x] How to deploy?
  - [x] Figure out how to architect this thing. Use AWS?
  - [x] How to allow people to generate their API keys?
