from get_db_connection import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("DELETE FROM api_requests")
conn.commit()
cursor.close()
conn.close()

print("Rate limit reset")