from customtkinter import *
from tkinter import ttk, messagebox
import mysql.connector
from db_config import DB_CONFIG

class TeacherView:
    def __init__(self, window, user):
        self.window = window
        self.user = user
        self.window.title("Giao diện Giáo viên")
        self.window.geometry("1200x700")
        self.window.resizable(False, False)

        # Frame chính với gradient nền
        self.main_frame = CTkFrame(self.window, fg_color=("#E6F0FA", "#B0C4DE"))
        self.main_frame.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = CTkFrame(self.main_frame, width=250, fg_color="#1E3A8A")
        self.sidebar.pack(side="left", fill="y")

        # Tiêu đề sidebar
        CTkLabel(self.sidebar, text="Giáo viên", font=("Helvetica", 20, "bold"), text_color="white").pack(pady=20)

        # Menu sidebar
        menu_items = ["Thông tin cá nhân", "Lịch giảng dạy", "Xem lương"]
        for item in menu_items:
            btn = CTkButton(self.sidebar, text=item, font=("Helvetica", 14), fg_color="transparent",
                            text_color="white", hover_color="#3B82F6", command=lambda x=item: self.switch_tab(x))
            btn.pack(pady=10, padx=20, fill="x")

        # Frame chính (bên phải)
        self.content_frame = CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(side="right", padx=10, pady=10, fill="both", expand=True)

        # Frame chứa các tab
        self.tab_frame = CTkFrame(self.content_frame, fg_color="transparent")
        self.tab_frame.pack(fill="both", expand=True)

        # Tab Thông tin cá nhân
        self.personal_info_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.setup_personal_info_tab()

        # Tab Lịch giảng dạy
        self.schedule_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.setup_schedule_tab()

        # Tab Xem lương
        self.salary_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.setup_salary_tab()

        # Hiển thị tab đầu tiên
        self.current_tab = self.personal_info_tab
        self.personal_info_tab.pack(fill="both", expand=True)

        # Nút đăng xuất
        CTkButton(self.content_frame, text="Đăng xuất", font=("Helvetica", 14, "bold"), fg_color="#DC3545",
                  hover_color="#B02A37", command=self.logout).pack(pady=10, side="bottom", anchor="se")

    def setup_personal_info_tab(self):
        # Tiêu đề
        CTkLabel(self.personal_info_tab, text="Thông tin cá nhân", font=("Helvetica", 18, "bold"), text_color="black").pack(pady=10)

        # Frame hiển thị thông tin
        info_frame = CTkFrame(self.personal_info_tab, fg_color="#F0F0F0", corner_radius=10)
        info_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Lấy thông tin giáo viên từ cơ sở dữ liệu
        teacher_info = self.load_teacher_info()

        # Hiển thị thông tin
        CTkLabel(info_frame, text=f"Mã số: {teacher_info['teacher_id']}", font=("Helvetica", 14)).pack(pady=5, anchor="w", padx=20)
        CTkLabel(info_frame, text=f"Họ tên: {teacher_info['full_name']}", font=("Helvetica", 14)).pack(pady=5, anchor="w", padx=20)
        CTkLabel(info_frame, text=f"Ngày sinh: {teacher_info['date_of_birth']}", font=("Helvetica", 14)).pack(pady=5, anchor="w", padx=20)
        CTkLabel(info_frame, text=f"Điện thoại: {teacher_info['phone']}", font=("Helvetica", 14)).pack(pady=5, anchor="w", padx=20)
        CTkLabel(info_frame, text=f"Email: {teacher_info['email']}", font=("Helvetica", 14)).pack(pady=5, anchor="w", padx=20)
        CTkLabel(info_frame, text=f"Thuộc khoa: {teacher_info['dept_name']}", font=("Helvetica", 14)).pack(pady=5, anchor="w", padx=20)
        CTkLabel(info_frame, text=f"Bằng cấp: {teacher_info['degree_name']}", font=("Helvetica", 14)).pack(pady=5, anchor="w", padx=20)

    def setup_schedule_tab(self):
        # Tiêu đề
        CTkLabel(self.schedule_tab, text="Lịch giảng dạy", font=("Helvetica", 18, "bold"), text_color="black").pack(pady=10)

        # Bảng lịch giảng dạy
        table_frame = CTkFrame(self.schedule_tab, fg_color="#FFFFFF", corner_radius=10)
        table_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.schedule_tree = ttk.Treeview(table_frame, columns=("Module", "Students", "Periods", "Semester"), show="headings")
        self.schedule_tree.heading("Module", text="Học phần")
        self.schedule_tree.heading("Students", text="Số sinh viên")
        self.schedule_tree.heading("Periods", text="Số tiết")
        self.schedule_tree.heading("Semester", text="Học kỳ")
        self.schedule_tree.column("Module", width=150)
        self.schedule_tree.column("Students", width=100)
        self.schedule_tree.column("Periods", width=100)
        self.schedule_tree.column("Semester", width=100)
        self.schedule_tree.pack(padx=10, pady=10, fill="both", expand=True)

        self.load_schedule()

    def setup_salary_tab(self):
        # Tiêu đề
        CTkLabel(self.salary_tab, text="Xem Lương", font=("Helvetica", 18, "bold"), text_color="black").pack(pady=10)

        # Bảng lương
        table_frame = CTkFrame(self.salary_tab, fg_color="#FFFFFF", corner_radius=10)
        table_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.salary_tree = ttk.Treeview(table_frame, columns=("Module", "Amount", "Semester", "Date"), show="headings")
        self.salary_tree.heading("Module", text="Học phần")
        self.salary_tree.heading("Amount", text="Số tiền")
        self.salary_tree.heading("Semester", text="Học kỳ")
        self.salary_tree.heading("Date", text="Ngày tính")
        self.salary_tree.column("Module", width=150)
        self.salary_tree.column("Amount", width=120)
        self.salary_tree.column("Semester", width=100)
        self.salary_tree.column("Date", width=150)
        self.salary_tree.pack(padx=10, pady=10, fill="both", expand=True)

        self.load_salaries()

    def switch_tab(self, tab_name):
        self.current_tab.pack_forget()
        if tab_name == "Thông tin cá nhân":
            self.current_tab = self.personal_info_tab
        elif tab_name == "Lịch giảng dạy":
            self.current_tab = self.schedule_tab
        elif tab_name == "Xem lương":
            self.current_tab = self.salary_tab
        else:
            return
        self.current_tab.pack(fill="both", expand=True)

    def load_teacher_info(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT t.teacher_id, t.full_name, t.date_of_birth, t.phone, t.email, 
                       d.dept_name, deg.degree_name
                FROM teachers t
                JOIN departments d ON t.dept_id = d.dept_id
                JOIN degrees deg ON t.degree_id = deg.degree_id
                WHERE t.teacher_id = %s
            """, (self.user['teacher_id'],))
            teacher = cursor.fetchone()
            if not teacher:
                teacher = {
                    'teacher_id': 'N/A', 'full_name': 'N/A', 'date_of_birth': 'N/A',
                    'phone': 'N/A', 'email': 'N/A', 'dept_name': 'N/A', 'degree_name': 'N/A'
                }
            return teacher
        except mysql.connector.Error as e:
            print(f"Lỗi: {e}")
            return {
                'teacher_id': 'N/A', 'full_name': 'N/A', 'date_of_birth': 'N/A',
                'phone': 'N/A', 'email': 'N/A', 'dept_name': 'N/A', 'degree_name': 'N/A'
            }
        finally:
            cursor.close()
            conn.close()

    def load_schedule(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT cm.module_name, c.num_students, c.actual_periods, c.semester
                FROM classes c
                JOIN course_modules cm ON c.module_id = cm.module_id
                WHERE c.teacher_id = %s
            """, (self.user['teacher_id'],))
            classes = cursor.fetchall()
            
            for item in self.schedule_tree.get_children():
                self.schedule_tree.delete(item)
            
            for cls in classes:
                self.schedule_tree.insert("", "end", values=(
                    cls['module_name'],
                    cls['num_students'],
                    cls['actual_periods'],
                    cls['semester']
                ))
        except mysql.connector.Error as e:
            print(f"Lỗi: {e}")
        finally:
            cursor.close()
            conn.close()

    def load_salaries(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT cm.module_name, s.salary_amount, s.semester, s.calculated_at
                FROM salaries s
                JOIN classes c ON s.class_id = c.class_id
                JOIN course_modules cm ON c.module_id = cm.module_id
                WHERE s.teacher_id = %s
            """, (self.user['teacher_id'],))
            salaries = cursor.fetchall()
            
            for item in self.salary_tree.get_children():
                self.salary_tree.delete(item)
            
            for salary in salaries:
                self.salary_tree.insert("", "end", values=(
                    salary['module_name'],
                    salary['salary_amount'],
                    salary['semester'],
                    salary['calculated_at'].strftime("%Y-%m-%d %H:%M:%S")
                ))
        except mysql.connector.Error as e:
            print(f"Lỗi: {e}")
        finally:
            cursor.close()
            conn.close()

    def logout(self):
        self.window.destroy()
        from login_view import LoginPage
        new_window = CTk()
        app = LoginPage(new_window)
        new_window.mainloop()