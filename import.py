import pandas as pd
import mysql.connector
from db_config import DB_CONFIG  # Giả sử bạn đã có DB_CONFIG trong admin_view.py

# Đọc file CSV
df = pd.read_csv('svthucte_random.csv')

# Kết nối cơ sở dữ liệu
try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Xóa dữ liệu cũ trong bảng class_enrollments (tùy chọn)
    cursor.execute("DELETE FROM class_enrollments")

    # Chèn dữ liệu từ CSV vào bảng class_enrollments
    for _, row in df.iterrows():
        query = """
            INSERT INTO class_enrollments (class_id, enrolled_students, last_updated)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE enrolled_students = %s, last_updated = %s
        """
        values = (
            row['class_id'], row['enrolled_students'], row['last_updated'],
            row['enrolled_students'], row['last_updated']
        )
        cursor.execute(query, values)

    conn.commit()
    print("Đã nhập dữ liệu từ svthucte.csv vào bảng class_enrollments thành công!")

except mysql.connector.Error as e:
    print(f"Lỗi khi nhập dữ liệu: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()