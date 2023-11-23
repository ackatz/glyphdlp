from fastapi import HTTPException
from app.dbo.get_db_connection import get_db_connection


async def login(request, api_key, email_login):
    # Connect to DB
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user already exists
    cursor.execute(
        "SELECT * FROM users WHERE api_key = %s AND email = %s",
        (
            api_key,
            email_login,
        ),
    )
    user = cursor.fetchone()

    if not user:
        cursor.close()
        conn.close()  # Close the DB connection before raising the exception
        raise HTTPException(status_code=400, detail="API key or e-mail not found")
    else:
        # Extracting some information from the user object
        user_name = user[1]
        user_email = user[2]
        user_max_requests = user[4]

        cursor.close()
        conn.close()

        return api_key, user_name, user_email, user_max_requests
