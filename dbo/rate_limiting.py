from fastapi import HTTPException
from datetime import datetime, timedelta
from app.dbo.get_db_connection import get_db_connection


async def request_ratelimit(request, user):
    if user:
        user_id = user[0]
        user_max_requests = user[4]

        conn = get_db_connection()
        cursor = conn.cursor()

        since = datetime.utcnow() - timedelta(days=1)

        cursor.execute(
            "SELECT COUNT(*) FROM api_requests WHERE user_id = %s AND timestamp > %s",
            (user_id, since),
        )
        request_count = cursor.fetchone()[0]

        # Extracting some information from the request object
        request_endpoint = str(request.url)

        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            # Take the first IP from X-Forwarded-For, which is the original client IP
            client_ip = x_forwarded_for.split(",")[0]
        else:
            client_ip = request.client.host

        cursor.execute(
            "INSERT INTO api_requests (user_id, endpoint, client_ip) VALUES (%s, %s, %s)",
            (user_id, request_endpoint, client_ip),
        )
        conn.commit()
        cursor.close()
        conn.close()

        try:
            user_max_requests_int = int(user_max_requests)
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid user_max_requests value"
            )

        remaining_requests = user_max_requests_int - request_count

        return remaining_requests
