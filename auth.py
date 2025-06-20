import mysql.connector
from db_config import DB_CONFIG

def verify_user(username, password):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT user_id, username, password, role
            FROM users 
            WHERE (username = %s OR user_id = %s) AND password = %s
        """, (username, username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            print(f"Debug: User found: {user}")
        else:
            print(f"Debug: No user found for username/user_id={username}, password={password}")
        return user
    except mysql.connector.Error as e:
        print(f"Error verifying user: {e}")
        return None