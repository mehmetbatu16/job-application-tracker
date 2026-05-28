from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection

def register_user(username, password):
    hashed_password = generate_password_hash(password)
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password)
        )
        connection.commit()
        return True
    except Exception as e:
        print(f"Registration error: {e}")
        return False
    finally:
        connection.close()

def authenticate_user(username, password):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    connection.close()
    
    if user and check_password_hash(user['password'], password):
        return user
    return None