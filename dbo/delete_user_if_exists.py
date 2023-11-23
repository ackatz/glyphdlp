from fastapi import HTTPException
from app.dbo.get_db_connection import get_db_connection


async def delete_user(email: str):
    # Connect to DB
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user:
        # If user exists, delete user
        cursor.execute("DELETE FROM users WHERE email = %s", (email,))
        conn.commit()  # Commit the deletion
        response = {"detail": "User deleted successfully"}
    else:
        # If user doesn't exist, prepare the response accordingly
        response = {"detail": "User doesn't exist"}

    cursor.close()
    conn.close()

    return response
