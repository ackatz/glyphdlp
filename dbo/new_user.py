from fastapi import HTTPException
from app.dbo.get_db_connection import get_db_connection
import uuid


async def new_user(request, username, email, max_requests):
    # Connect to DB
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user:
        cursor.close()
        conn.close()  # Close the DB connection before raising the exception
        raise HTTPException(status_code=400, detail="Email already registered")
    else:
        # If user doesn't exist, generate and store new API key
        api_key = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO users (name, email, api_key, max_requests) VALUES (%s, %s, %s, %s)",
            (username, email, api_key, max_requests),
        )
        conn.commit()
        cursor.close()
        conn.close()

    return api_key
