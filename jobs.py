from database import get_db_connection

def add_job_application(user_id, company_name, position, status, application_date, notes):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO applications (user_id, company_name, position, status, application_date, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, company_name, position, status, application_date, notes)
        )
        connection.commit()
        return True
    except Exception as e:
        print(f"Error adding application: {e}")
        return False
    finally:
        connection.close()

def get_user_applications(user_id, status_filter=None):
    connection = get_db_connection()
    cursor = connection.cursor()
    if status_filter:
        cursor.execute(
            "SELECT * FROM applications WHERE user_id = ? AND status = ? ORDER BY application_date DESC",
            (user_id, status_filter)
        )
    else:
        cursor.execute(
            "SELECT * FROM applications WHERE user_id = ? ORDER BY application_date DESC",
            (user_id,)
        )
    applications = cursor.fetchall()
    connection.close()
    return applications