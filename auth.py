import mysql.connector
from db_config import DB_CONFIG

def verify_user(username, password):
    """Xác thực người dùng và lấy thông tin giáo viên nếu là Teacher."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user and user['password'] == password:
            if user['role'] == 'Teacher' and user['teacher_id']:
                cursor.execute("""
                    SELECT t.full_name, d.degree_name, dept.dept_name
                    FROM teachers t
                    LEFT JOIN degrees d ON t.degree_id = d.degree_id
                    LEFT JOIN departments dept ON t.dept_id = dept.dept_id
                    WHERE t.teacher_id = %s
                """, (user['teacher_id'],))
                teacher_info = cursor.fetchone()
                if teacher_info:
                    user.update(teacher_info)
            return user
        return None
    except mysql.connector.Error as e:
        print(f"Lỗi cơ sở dữ liệu: {e}")
        return None
    finally:
        cursor.close()
        conn.close()