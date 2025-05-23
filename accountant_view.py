from customtkinter import *
from tkinter import ttk, messagebox
import mysql.connector
from db_config import DB_CONFIG
import uuid
from datetime import datetime

class AccountantView:
    def __init__(self, window, user):
        self.window = window
        self.user = user
        self.window.title("Giao diện Kế toán")
        self.window.geometry("1000x600")
        self.window.resizable(False, False)

        # Frame chính với gradient nền
        self.main_frame = CTkFrame(self.window, fg_color=("#E6F0FA", "#B0C4DE"))
        self.main_frame.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = CTkFrame(self.main_frame, width=250, fg_color="#1E3A8A")
        self.sidebar.pack(side="left", fill="y")

        # Tiêu đề sidebar
        CTkLabel(self.sidebar, text="Quản lý Kế toán", font=("Helvetica", 20, "bold"), text_color="white").pack(pady=20)

        # Menu sidebar
        menu_items = ["Quản lý Lương", "Tính Lương", "Thống kê"]
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

        # Tab Quản lý Lương
        self.salary_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.setup_salary_tab()

        # Tab Tính Lương
        self.calculate_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.setup_calculate_tab()

        # Hiển thị tab đầu tiên
        self.current_tab = self.salary_tab
        self.salary_tab.pack(fill="both", expand=True)

        # Nút đăng xuất
        CTkButton(self.content_frame, text="Đăng xuất", font=("Helvetica", 14, "bold"), fg_color="#DC3545",
                  hover_color="#B02A37", command=self.logout).pack(pady=10, side="bottom", anchor="se")

    def setup_salary_tab(self):
        # Tiêu đề
        CTkLabel(self.salary_tab, text="Danh sách Lương", font=("Helvetica", 18, "bold"), text_color="black").pack(pady=10)

        # Bảng lương
        table_frame = CTkFrame(self.salary_tab, fg_color="#FFFFFF", corner_radius=10)
        table_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.salary_tree = ttk.Treeview(table_frame, columns=("Teacher", "Module", "Amount", "Semester", "Date"), show="headings")
        self.salary_tree.heading("Teacher", text="Giáo viên")
        self.salary_tree.heading("Module", text="Học phần")
        self.salary_tree.heading("Amount", text="Số tiền")
        self.salary_tree.heading("Semester", text="Học kỳ")
        self.salary_tree.heading("Date", text="Ngày tính")
        self.salary_tree.column("Teacher", width=150)
        self.salary_tree.column("Module", width=150)
        self.salary_tree.column("Amount", width=120)
        self.salary_tree.column("Semester", width=100)
        self.salary_tree.column("Date", width=150)
        self.salary_tree.pack(padx=10, pady=10, fill="both", expand=True)

        self.load_salaries()

    def setup_calculate_tab(self):
        # Tiêu đề
        CTkLabel(self.calculate_tab, text="Tính Lương", font=("Helvetica", 18, "bold"), text_color="black").pack(pady=10)

        # Form tính lương
        form_frame = CTkFrame(self.calculate_tab, fg_color="#F0F0F0", corner_radius=10)
        form_frame.pack(padx=10, pady=10, fill="x")

        CTkLabel(form_frame, text="Tính Lương Giáo viên", font=("Helvetica", 16, "bold")).pack(pady=5)
        self.teacher_combobox = CTkComboBox(form_frame, width=200, values=self.get_teachers())
        self.teacher_combobox.pack(pady=5)
        self.class_combobox = CTkComboBox(form_frame, width=200, values=[])
        self.class_combobox.pack(pady=5)
        self.semester = CTkEntry(form_frame, placeholder_text="Học kỳ (ví dụ: 2025-1)", width=200)
        self.semester.pack(pady=5)
        CTkButton(form_frame, text="Tính lương", fg_color="#0085FF", command=self.calculate_salary).pack(pady=10)

        # Cập nhật danh sách lớp học khi chọn giáo viên
        self.teacher_combobox.bind("<<ComboboxSelected>>", self.update_classes)

    def switch_tab(self, tab_name):
        self.current_tab.pack_forget()
        if tab_name == "Quản lý Lương":
            self.current_tab = self.salary_tab
        elif tab_name == "Tính Lương":
            self.current_tab = self.calculate_tab
        else:
            return
        self.current_tab.pack(fill="both", expand=True)

    def get_teachers(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT teacher_id, full_name FROM teachers")
            teachers = [f"{row[0]}: {row[1]}" for row in cursor.fetchall()]
            return teachers if teachers else ["Không có giáo viên"]
        except mysql.connector.Error as e:
            print(f"Lỗi: {e}")
            return ["Lỗi tải giáo viên"]
        finally:
            cursor.close()
            conn.close()

    def update_classes(self, event=None):
        teacher = self.teacher_combobox.get()
        if not teacher:
            return
        teacher_id = teacher.split(":")[0]
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.class_id, cm.module_name
                FROM classes c
                JOIN course_modules cm ON c.module_id = cm.module_id
                WHERE c.teacher_id = %s
            """, (teacher_id,))
            classes = [f"{row[0]}: {row[1]}" for row in cursor.fetchall()]
            self.class_combobox.configure(values=classes if classes else ["Không có lớp học"])
            self.class_combobox.set(classes[0] if classes else "Không có lớp học")
        except mysql.connector.Error as e:
            print(f"Lỗi: {e}")
        finally:
            cursor.close()
            conn.close()

    def calculate_salary(self):
        teacher = self.teacher_combobox.get()
        class_info = self.class_combobox.get()
        semester = self.semester.get()
        if not all([teacher, class_info, semester]):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return

        teacher_id = teacher.split(":")[0]
        class_id = class_info.split(":")[0]
        base_rate = 1000  # Giả sử giá cơ bản mỗi tiết

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)

            # Lấy thông tin lớp học, hệ số học phần, hệ số bằng cấp
            cursor.execute("""
                SELECT c.num_students, c.actual_periods, cm.coefficient AS module_coeff, d.coefficient AS degree_coeff
                FROM classes c
                JOIN course_modules cm ON c.module_id = cm.module_id
                JOIN teachers t ON c.teacher_id = t.teacher_id
                JOIN degrees d ON t.degree_id = d.degree_id
                WHERE c.class_id = %s AND c.teacher_id = %s
            """, (class_id, teacher_id))
            data = cursor.fetchone()

            if not data:
                messagebox.showerror("Lỗi", "Không tìm thấy thông tin lớp học")
                return

            # Tính lương
            salary_amount = (data['actual_periods'] * data['module_coeff'] * data['degree_coeff'] *
                           data['num_students'] * base_rate)

            # Lưu vào bảng salaries
            salary_id = str(uuid.uuid4())
            calculated_at = datetime.now()
            cursor.execute("""
                INSERT INTO salaries (salary_id, teacher_id, class_id, salary_amount, semester, calculated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (salary_id, teacher_id, class_id, salary_amount, semester, calculated_at))
            conn.commit()

            messagebox.showinfo("Thành công", f"Tính lương thành công: {salary_amount}")
            self.semester.delete(0, END)
            self.load_salaries()

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tính lương: {e}")
        finally:
            cursor.close()
            conn.close()

    def load_salaries(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT t.full_name, cm.module_name, s.salary_amount, s.semester, s.calculated_at
                FROM salaries s
                JOIN teachers t ON s.teacher_id = t.teacher_id
                JOIN classes c ON s.class_id = c.class_id
                JOIN course_modules cm ON c.module_id = cm.module_id
            """)
            salaries = cursor.fetchall()
            
            for item in self.salary_tree.get_children():
                self.salary_tree.delete(item)
            
            for salary in salaries:
                self.salary_tree.insert("", "end", values=(
                    salary['full_name'],
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