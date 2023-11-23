from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.dbo.get_db_connection import get_db_connection

security = HTTPBearer()


async def request_authorization(
    authorization: HTTPAuthorizationCredentials = Depends(security),
):
    api_key = authorization.credentials

    if api_key is None:
        raise HTTPException(status_code=401, detail="Authorization header required")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE api_key = %s", (api_key,))
    user = cursor.fetchone()

    cursor.close()  # Close the cursor first
    conn.close()  # Close the connection afterwards

    if user is None:
        raise HTTPException(status_code=403, detail="Invalid API key")

    return user
