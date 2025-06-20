import customtkinter as ctk
from tkinter import messagebox, ttk
import mysql.connector
from db_config import DB_CONFIG
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import re
from a import ModernNavbar
import pyperclip

class ModernDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message, icon_type, buttons):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x300")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Center dialog
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 300) // 2
        self.geometry(f"+{x}+{y}")

        main_frame = ctk.CTkFrame(self, fg_color="#F3F4F6", corner_radius=12)
        main_frame.pack(padx=15, pady=15, fill="both", expand=True)

        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="#3B82F6", corner_radius=8)
        header_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(header_frame, text=title, font=("Helvetica", 18, "bold"), text_color="white").pack(pady=10)

        # Message
        message_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=8)
        message_frame.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(message_frame, text=message, font=("Helvetica", 12), text_color="#1F2937", wraplength=350, justify="left").pack(pady=10, padx=10)

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=10)

        for btn_text in buttons:
            if btn_text == "Sao chép Email":
                ctk.CTkButton(button_frame, text=btn_text, fg_color="#1E3A8A", hover_color="#60A5FA",
                              command=self.copy_email).pack(side="left", padx=5)
            else:
                ctk.CTkButton(button_frame, text=btn_text, fg_color="#1E3A8A", hover_color="#60A5FA",
                              command=self.destroy).pack(side="left", padx=5)

    def copy_email(self):
        pyperclip.copy("admin@phenikaa.edu.vn")
        messagebox.showinfo("Thành công", "Đã sao chép email: admin@phenikaa.edu.vn")
        self.destroy()

class TeacherView:
    def __init__(self, window, user):
        self.window = window
        self.user = user
        self.teacher_id = user['user_id']
        self.window.title("Giao diện Giảng viên")
        self.window.geometry("1700x700")

        # Kiểm tra mật khẩu mặc định
        if user.get('password') == 'default123':
            self.show_change_password_dialog()

        # Frame chính
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.pack(fill="both", expand=True)

        # Menu items cho navbar
        self.navbar_menu_items = [
            {
                "label": "Lớp học phần",
                "icon": "📚",
                "fg_color": "#3E54AC",
                "hover_color": "#4B67D6",
                "text_color": "white",
                "command": lambda: self.switch_tab("Lớp học phần")
            },
            {
                "label": "Tiền dạy theo kỳ",
                "icon": "💰",
                "fg_color": "#3E54AC",
                "hover_color": "#4B67D6",
                "text_color": "white",
                "command": lambda: self.switch_tab("Tiền dạy theo kỳ")
            },
            {
                "label": "Báo cáo tiền dạy",
                "icon": "📈",
                "fg_color": "#3E54AC",
                "hover_color": "#4B67D6",
                "text_color": "white",
                "command": lambda: self.switch_tab("Báo cáo tiền dạy")
            },
            {
                "label": "Đổi mật khẩu",
                "icon": "🔒",
                "fg_color": "#3E54AC",
                "hover_color": "#4B67D6",
                "text_color": "white",
                "command": lambda: self.switch_tab("Đổi mật khẩu")
            }
        ]

        # Tạo navbar, truyền user vào
        self.navbar = ModernNavbar(self.main_frame, fg_color="#2B3467", menu_items=self.navbar_menu_items, 
                                logout_callback=self.logout, user=self.user)
        self.navbar.pack(side="left", fill="y")

        # Frame nội dung bên phải
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color=("#E6F0FA", "#B0C4DE"))
        self.content_frame.pack(side="right", fill="both", expand=True)

        # Frame chứa các tab
        self.tab_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.tab_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Khởi tạo các tab
        self.class_tab = ctk.CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.salary_calc_tab = ctk.CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.salary_report_tab = ctk.CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.password_change_tab = ctk.CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)

        # Gọi các hàm setup
        self.setup_class_tab()
        self.setup_salary_calc_tab()
        self.setup_salary_report_tab()
        self.setup_password_change_tab()

        # Hiển thị tab mặc định
        self.current_tab = self.class_tab
        self.current_tab.pack(fill="both", expand=True)

        # Cấu hình style cho Treeview
        style = ttk.Style()
        style.configure("Treeview",
                        font=("Helvetica", 10),
                        rowheight=20,
                        background="#FFFFFF",
                        foreground="black",
                        fieldbackground="#F0F0F0")
        style.configure("Treeview.Heading",
                        font=("Helvetica", 10, "bold"),
                        background="#D3D3D3",
                        foreground="black")

    def show_change_password_dialog(self):
        # Tạo cửa sổ đổi mật khẩu
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Đổi mật khẩu")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()

        # Căn giữa cửa sổ
        self.window.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() - 400) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - 300) // 2
        dialog.geometry(f"+{x}+{y}")

        main_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(main_frame, text="Đổi mật khẩu", font=("Helvetica", 18, "bold")).pack(pady=(0, 15))

        # Mật khẩu mới
        new_password = ctk.CTkEntry(main_frame, placeholder_text="Mật khẩu mới", show="*")
        new_password.pack(fill="x", pady=5)
        
        # Xác nhận mật khẩu
        confirm_password = ctk.CTkEntry(main_frame, placeholder_text="Xác nhận mật khẩu", show="*")
        confirm_password.pack(fill="x", pady=5)

        def save_password():
            new_pass = new_password.get().strip()
            confirm_pass = confirm_password.get().strip()

            # Kiểm tra mật khẩu
            if not new_pass or not confirm_pass:
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ mật khẩu!", parent=dialog)
                return
            if new_pass != confirm_pass:
                messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp!", parent=dialog)
                return
            if len(new_pass) < 8:
                messagebox.showerror("Lỗi", "Mật khẩu phải có ít nhất 8 ký tự!", parent=dialog)
                return
            if not re.search(r"[A-Z]", new_pass) or not re.search(r"[a-z]", new_pass) or not re.search(r"[0-9]", new_pass):
                messagebox.showerror("Lỗi", "Mật khẩu phải chứa chữ hoa, chữ thường và số!", parent=dialog)
                return

            # Cập nhật mật khẩu
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET password = %s WHERE user_id = %s", (new_pass, self.teacher_id))
                conn.commit()
                messagebox.showinfo("Thành công", "Mật khẩu đã được đổi thành công!", parent=dialog)
                dialog.destroy()
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể đổi mật khẩu: {e}", parent=dialog)
            finally:
                cursor.close()
                conn.close()

        # Nút Lưu và Sau
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=20)
        ctk.CTkButton(button_frame, text="Lưu", fg_color="#0085FF", command=save_password).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Sau", fg_color="#6c757d", command=dialog.destroy).pack(side="left", padx=10)

    def switch_tab(self, tab_name):
        if self.current_tab:
            self.current_tab.pack_forget()
        if tab_name == "Lớp học phần":
            self.current_tab = self.class_tab
        elif tab_name == "Tiền dạy theo kỳ":
            self.current_tab = self.salary_calc_tab
        elif tab_name == "Báo cáo tiền dạy":
            self.current_tab = self.salary_report_tab
        elif tab_name == "Đổi mật khẩu":
            self.current_tab = self.password_change_tab
        self.current_tab.pack(fill="both", expand=True)

    def logout(self):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn đăng xuất?"):
            self.window.destroy()
            import os
            os.system("python login_view.py")

    def setup_class_tab(self):
        # Header
        header_frame = ctk.CTkFrame(self.class_tab, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(header_frame, text="Quản lý lớp học phần", font=("Helvetica", 18, "bold"), text_color="black").pack(side="left")

        # Filter frame
        filter_frame = ctk.CTkFrame(self.class_tab, fg_color="transparent")
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Year filter
        year_filter_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        year_filter_frame.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(year_filter_frame, text="Năm học:", font=("Helvetica", 12), text_color="black").pack(side="left", padx=(0, 5))
        self.year_filter = ctk.CTkComboBox(year_filter_frame, values=[f"{y}-{y+1}" for y in range(2020, 2030)], width=150, command=self.update_filters)
        self.year_filter.pack(side="left")
        self.year_filter.set("2024-2025")

        # Semester filter
        semester_filter_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        semester_filter_frame.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(semester_filter_frame, text="Kỳ học:", font=("Helvetica", 12), text_color="black").pack(side="left", padx=(0, 5))
        self.semester_filter = ctk.CTkComboBox(semester_filter_frame, values=["Tất cả"], width=150, command=self.filter_classes)
        self.semester_filter.pack(side="left")
        self.semester_filter.set("Tất cả")

        # Module filter
        module_filter_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        module_filter_frame.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(module_filter_frame, text="Học phần:", font=("Helvetica", 12), text_color="black").pack(side="left", padx=(0, 5))
        self.module_filter = ctk.CTkComboBox(module_filter_frame, values=["Tất cả"], width=200, command=self.filter_classes)
        self.module_filter.pack(side="left")
        self.module_filter.set("Tất cả")

        # Main container
        self.class_container = ctk.CTkFrame(self.class_tab, fg_color="#FFFFFF", corner_radius=10)
        self.class_container.pack(padx=10, pady=10, fill="both", expand=True)

        # Heading
        heading_frame = ctk.CTkFrame(self.class_container, fg_color="#D3D3D3", corner_radius=0)
        heading_frame.pack(fill="x", padx=5, pady=(5, 0))
        headers = ["STT", "Mã lớp", "Tên lớp", "Học phần", "Kỳ học", "Số SV", "Giảng viên"]
        widths = [50, 100, 250, 200, 100, 80, 250]
        for i, header in enumerate(headers):
            ctk.CTkLabel(heading_frame, text=header, font=("Helvetica", 14, "bold"), text_color="black", width=widths[i], anchor="center").pack(side="left", padx=5)

        # List frame
        self.class_list_frame = ctk.CTkScrollableFrame(self.class_container, fg_color="transparent")
        self.class_list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Cập nhật combobox và load dữ liệu
        self.update_filters()

    def get_semesters_by_year(self, year):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT semester_name FROM semesters WHERE year = %s ORDER BY semester_name", (year,))
            semesters = [row[0] for row in cursor.fetchall()]
            return semesters if semesters else ["Tất cả"]
        except mysql.connector.Error:
            return ["Tất cả"]
        finally:
            cursor.close()
            conn.close()

    def get_modules_by_dept(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT cm.module_name
                FROM course_modules cm
                JOIN teachers t ON cm.dept_id = t.dept_id
                WHERE t.teacher_id = %s
                ORDER BY cm.module_name
            """, (self.teacher_id,))
            modules = [row[0] for row in cursor.fetchall()]
            return modules if modules else ["Tất cả"]
        except mysql.connector.Error:
            return ["Tất cả"]
        finally:
            cursor.close()
            conn.close()

    def update_filters(self, event=None):
        year = self.year_filter.get()
        semesters = self.get_semesters_by_year(year)
        self.semester_filter.configure(values=["Tất cả"] + semesters)
        self.semester_filter.set("Tất cả")
        modules = self.get_modules_by_dept()
        self.module_filter.configure(values=["Tất cả"] + modules)
        self.module_filter.set("Tất cả")
        self.filter_classes()

    def filter_classes(self, event=None):
        year = self.year_filter.get()
        semester = self.semester_filter.get()
        module = self.module_filter.get()

        for widget in self.class_list_frame.winfo_children():
            widget.destroy()

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            query = """
                SELECT c.class_id, c.class_name, cm.module_name, s.semester_name, 
                    COALESCE(ce.enrolled_students, 0), t.full_name
                FROM classes c
                JOIN semesters s ON c.semester_id = s.semester_id
                JOIN course_modules cm ON c.module_id = cm.module_id
                JOIN assignments a ON c.class_id = a.class_id
                JOIN teachers t ON a.teacher_id = t.teacher_id
                LEFT JOIN class_enrollments ce ON c.class_id = ce.class_id
                WHERE t.teacher_id = %s AND s.year = %s
            """
            params = [self.teacher_id, year]

            if semester != "Tất cả":
                query += " AND s.semester_name = %s"
                params.append(semester)
            if module != "Tất cả":
                query += " AND cm.module_name = %s"
                params.append(module)

            cursor.execute(query, params)
            classes = cursor.fetchall()

            if not classes:
                ctk.CTkLabel(self.class_list_frame, text="Không có dữ liệu lớp học", font=("Helvetica", 12), text_color="red").pack(pady=10)
            else:
                for idx, (class_id, class_name, module_name, semester_name, enrolled_students, teacher_name) in enumerate(classes, 1):
                    class_row = ctk.CTkFrame(self.class_list_frame, fg_color="#F5F5F5" if idx % 2 else "#FFFFFF")
                    class_row.pack(fill="x", pady=2)
                    class_row.configure(height=35)
                    class_row.pack_propagate(False)

                    widths = [50, 100, 250, 200, 100, 80, 250]
                    values = [str(idx), class_id, class_name, module_name, semester_name, str(enrolled_students), teacher_name]
                    for i, value in enumerate(values):
                        ctk.CTkLabel(class_row, text=value, font=("Helvetica", 12), width=widths[i], anchor="center").pack(side="left", padx=5)

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu lớp: {e}")
        finally:
            cursor.close()
            conn.close()

    def setup_salary_calc_tab(self):
        # Header
        header_frame = ctk.CTkFrame(self.salary_calc_tab, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(
            header_frame, 
            text="Tiền dạy theo kỳ", 
            font=("Helvetica", 24, "bold"), 
            text_color="#2B3467"
        ).pack(side="left")
        
        # Filter frame với thiết kế hiện đại
        filter_frame = ctk.CTkFrame(
            self.salary_calc_tab, 
            fg_color="#F5F7FA", 
            corner_radius=12, 
            border_width=1, 
            border_color="#E0E0E0"
        )
        filter_frame.pack(padx=20, pady=10, fill="x")
        
        # Year filter
        ctk.CTkLabel(
            filter_frame, 
            text="📅 Năm học:", 
            font=("Helvetica", 14, "bold"), 
            text_color="#2B3467"
        ).pack(side="left", padx=(15, 5), pady=10)
        self.salary_year_combobox = ctk.CTkComboBox(
            filter_frame, 
            width=200, 
            values=[f"{y}-{y+1}" for y in range(2020, 2030)], 
            command=self.update_salary_semester_filter,
            font=("Helvetica", 14),
            fg_color="#FFFFFF",
            button_color="#4B89DC",
            border_color="#4B89DC",
            text_color="#2B3467"
        )
        self.salary_year_combobox.pack(side="left", padx=5, pady=10)
        self.salary_year_combobox.set("2024-2025")
        
        # Semester filter
        ctk.CTkLabel(
            filter_frame, 
            text="📅 Kỳ học:", 
            font=("Helvetica", 14, "bold"), 
            text_color="#2B3467"
        ).pack(side="left", padx=(15, 5), pady=10)
        self.salary_semester_combobox = ctk.CTkComboBox(
            filter_frame, 
            width=200, 
            values=["Chọn kỳ học"], 
            command=self.calculate_salary,
            font=("Helvetica", 14),
            fg_color="#FFFFFF",
            button_color="#4B89DC",
            border_color="#4B89DC",
            text_color="#2B3467"
        )
        self.salary_semester_combobox.pack(side="left", padx=5, pady=10)
        self.salary_semester_combobox.set("Chọn kỳ học")
        
        # View button với màu sắc nổi bật
        # ctk.CTkButton(
        #     filter_frame, 
        #     text="Xem tiền dạy", 
        #     fg_color="#4B89DC", 
        #     hover_color="#3A67B1", 
        #     font=("Helvetica", 14, "bold"), 
        #     command=self.calculate_salary
        # ).pack(side="right", padx=15, pady=10)
        
        # Teacher info frame với thiết kế card-like và trang trí
        self.teacher_info_frame = ctk.CTkFrame(
            self.salary_calc_tab, 
            fg_color=("#E6F0FA", "#B0C4DE"), 
            corner_radius=12, 
            border_width=2, 
            border_color="#4B89DC"
        )
        self.teacher_info_frame.pack(padx=20, pady=10, fill="x")
        
        # Thêm biểu tượng và tiêu đề cho frame
        title_frame = ctk.CTkFrame(self.teacher_info_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(10, 5))
        ctk.CTkLabel(
            title_frame, 
            text="👤 Thông tin giảng viên", 
            font=("Helvetica", 16, "bold"), 
            text_color="#2B3467"
        ).pack(side="left", padx=15)
        
        # Thêm đường viền nhỏ dưới tiêu đề
        separator = ctk.CTkFrame(title_frame, height=2, fg_color="#4B89DC")
        separator.pack(fill="x", padx=15, pady=(5, 0))
        
        # Main info container with two columns
        info_container = ctk.CTkFrame(self.teacher_info_frame, fg_color="transparent")
        info_container.pack(padx=15, pady=5, fill="both", expand=True)
        info_container.grid_columnconfigure((0, 1), weight=1)
        
        # Left column (Personal info)
        left_frame = ctk.CTkFrame(info_container, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        left_info = [
            ("👤 Họ tên:", "salary_calc_teacher_name_value"),
            ("🆔 Mã GV:", "salary_calc_teacher_id_value"),
            ("🎓 Học vị:", "salary_calc_degree_value"),
            ("🏫 Khoa:", "salary_calc_dept_value")
        ]
        
        for idx, (label_text, attr_name) in enumerate(left_info):
            row_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            ctk.CTkLabel(
                row_frame, 
                text=label_text, 
                font=("Helvetica", 14, "bold"), 
                text_color="#2B3467",
                width=120,  # Đặt độ rộng cố định cho nhãn
                anchor="w"
            ).pack(side="left", padx=(0, 10))
            value_label = ctk.CTkLabel(
                row_frame, 
                text="", 
                font=("Helvetica", 14), 
                text_color="#333333",
                anchor="w"  # Căn lề trái cho giá trị
            )
            value_label.pack(side="left", fill="x", expand=True)
            setattr(self, attr_name, value_label)
        
        # Right column (Financial info)
        right_frame = ctk.CTkFrame(info_container, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        right_info = [
            ("⚖️ Hệ số:", "salary_calc_teacher_coeff_value"),
            ("💰 Định mức:", "salary_calc_rate_value"),
            ("⏳ Số tiết:", "salary_calc_period_value")
        ]
        
        for idx, (label_text, attr_name) in enumerate(right_info):
            row_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            ctk.CTkLabel(
                row_frame, 
                text=label_text, 
                font=("Helvetica", 14, "bold"), 
                text_color="#2B3467",
                width=120,  # Đặt độ rộng cố định cho nhãn
                anchor="w"
            ).pack(side="left", padx=(0, 10))
            value_label = ctk.CTkLabel(
                row_frame, 
                text="", 
                font=("Helvetica", 14), 
                text_color="#333333",
                anchor="w"  # Căn lề trái cho giá trị
            )
            value_label.pack(side="left", fill="x", expand=True)
            setattr(self, attr_name, value_label)
        
        # Table frame với thiết kế hiện đại
        self.salary_table_frame = ctk.CTkScrollableFrame(
            self.salary_calc_tab, 
            fg_color="#FFFFFF", 
            corner_radius=12, 
            border_width=1, 
            border_color="#E0E0E0"
        )
        self.salary_table_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Load initial data
        self.update_salary_semester_filter()

    def update_salary_semester_filter(self, event=None):
        year = self.salary_year_combobox.get()
        if year == "Chọn năm học":
            self.salary_semester_combobox.configure(values=["Chọn kỳ học"])
            self.salary_semester_combobox.set("Chọn kỳ học")
            return

        semesters = self.get_semesters_by_year(year)
        self.salary_semester_combobox.configure(values=["Chọn kỳ học"] + semesters)
        self.salary_semester_combobox.set("Chọn kỳ học")

    def calculate_salary(self, event=None):
        year = self.salary_year_combobox.get().strip()
        semester = self.salary_semester_combobox.get().strip()
        
        if year == "Chọn năm học" or semester == "Chọn kỳ học":
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn năm học và kỳ học!")
            return
        
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            # Lấy thông tin giáo viên
            cursor.execute("""
                SELECT t.full_name, t.teacher_id, d.degree_name, dept.dept_name
                FROM teachers t 
                JOIN degrees d ON t.degree_id = d.degree_id 
                JOIN departments dept ON t.dept_id = dept.dept_id 
                WHERE t.teacher_id = %s
            """, (self.teacher_id,))
            teacher = cursor.fetchone()
            if not teacher:
                messagebox.showerror("Lỗi", f"Không tìm thấy giáo viên với mã {self.teacher_id}")
                return
            full_name, teacher_id, degree_name, dept_name = teacher
            
            # Cập nhật thông tin giáo viên
            self.salary_calc_teacher_name_value.configure(text=full_name or '-')
            self.salary_calc_teacher_id_value.configure(text=teacher_id or '-')
            self.salary_calc_degree_value.configure(text=degree_name or '-')
            self.salary_calc_dept_value.configure(text=dept_name or '-')
            
            # Lấy teacher_coefficient
            cursor.execute("""
                SELECT tc.coefficient 
                FROM teacher_coefficients tc 
                JOIN teachers t ON tc.degree_id = t.degree_id 
                WHERE t.teacher_id = %s AND tc.year = %s
            """, (self.teacher_id, year))
            teacher_coeff = cursor.fetchone()
            teacher_coefficient = float(teacher_coeff[0]) if teacher_coeff else 1.0
            self.salary_calc_teacher_coeff_value.configure(text=f"{teacher_coefficient:.2f}")
            
            # Lấy teaching rate
            cursor.execute("SELECT amount_per_period FROM teaching_rate WHERE year = %s", (year,))
            rate = cursor.fetchone()
            amount_per_period = float(rate[0]) if rate else 0.0
            self.salary_calc_rate_value.configure(text=f"{amount_per_period:,.0f} ₫")
            
            # Xóa bảng cũ
            for widget in self.salary_table_frame.winfo_children():
                widget.destroy()
            
            # Lấy dữ liệu lớp học
            cursor.execute("""
                SELECT c.class_id, cm.periods, ce.enrolled_students, cm.coefficient AS hp_coeff
                FROM assignments a
                JOIN classes c ON a.class_id = c.class_id
                JOIN course_modules cm ON c.module_id = cm.module_id
                JOIN semesters s ON c.semester_id = s.semester_id
                LEFT JOIN class_enrollments ce ON c.class_id = ce.class_id
                WHERE a.teacher_id = %s AND s.semester_name = %s AND s.year = %s
            """, (self.teacher_id, semester, year))
            classes = cursor.fetchall()
            
            if not classes:
                ctk.CTkLabel(
                    self.salary_table_frame,
                    text="Không có dữ liệu lớp học trong kỳ này",
                    font=("Helvetica", 16),
                    text_color="#FF5555"
                ).pack(pady=20)
                self.salary_calc_period_value.configure(text="0")
                return
            
            # Heading
            heading_frame = ctk.CTkFrame(self.salary_table_frame, fg_color="#2B3467")
            heading_frame.pack(fill="x", pady=(0, 5))
            headers = ["STT", "Mã lớp", "Số tiết", "Số SV", "Hệ số HP", "Hệ số lớp", "Số tiết QĐ", "Thành tiền"]
            widths = [75, 200, 80, 80, 130, 130, 150, 240]
            for col, (header, width) in enumerate(zip(headers, widths)):
                ctk.CTkLabel(
                    heading_frame, 
                    text=header, 
                    width=width, 
                    anchor="center",
                    font=("Helvetica", 12, "bold"), 
                    text_color="white"
                ).grid(row=0, column=col, padx=5, pady=5)
            
            total_periods = 0
            total_salary = 0.0
            
            for idx, (class_id, periods, enrolled_students, hp_coeff) in enumerate(classes, 1):
                # Lấy hệ số lớp
                student_range = self.get_student_range(enrolled_students or 0)
                cursor.execute("SELECT coefficient FROM class_coefficients WHERE year = %s AND student_range = %s", (year, student_range))
                class_coeff = cursor.fetchone()
                class_coefficient = float(class_coeff[0]) if class_coeff else 0.0
                
                # Tính toán
                converted_periods = periods * (hp_coeff + class_coefficient)
                salary = converted_periods * teacher_coefficient * amount_per_period
                total_periods += converted_periods
                total_salary += salary
                
                # Hiển thị hàng
                row_frame = ctk.CTkFrame(
                    self.salary_table_frame, 
                    fg_color="#F5F5F5" if idx % 2 else "#FFFFFF"
                )
                row_frame.pack(fill="x", pady=2)
                values = [
                    str(idx), 
                    class_id, 
                    str(periods), 
                    str(enrolled_students or 0),
                    f"{hp_coeff:.2f}", 
                    f"{class_coefficient:.2f}", 
                    f"{converted_periods:.1f}", 
                    f"{salary:,.0f} ₫"
                ]
                for col, (value, width) in enumerate(zip(values, widths)):
                    ctk.CTkLabel(
                        row_frame, 
                        text=value, 
                        font=("Helvetica", 12), 
                        text_color="#333333", 
                        width=width, 
                        anchor="center"
                    ).grid(row=0, column=col, padx=5, pady=5)
            
            # Hàng tổng
            total_frame = ctk.CTkFrame(self.salary_table_frame, fg_color="#E3F2FD")
            total_frame.pack(fill="x", pady=(0, 0))
            total_values = [
                "TỔNG CỘNG:", "", "", "", "", "", 
                f"{total_periods:.1f}", 
                f"{total_salary:,.0f} ₫"
            ]
            for col, (value, width) in enumerate(zip(total_values, widths)):
                ctk.CTkLabel(
                    total_frame, 
                    text=value, 
                    font=("Helvetica", 12, "bold"), 
                    text_color="#2B3467", 
                    width=width, 
                    anchor="center"
                ).grid(row=0, column=col, padx=5, pady=5)
            
            self.salary_calc_period_value.configure(text=f"{total_periods:.1f}")
            
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_student_range(self, num_students):
        ranges = ['<20 sinh viên', '20-29 sinh viên', '30-39 sinh viên', '40-49 sinh viên', '50-59 sinh viên',
                  '60-69 sinh viên', '70-79 sinh viên', '80-89 sinh viên', '90-99 sinh viên', '>=100 sinh viên']
        if num_students < 20:
            return ranges[0]
        elif num_students < 30:
            return ranges[1]
        elif num_students < 40:
            return ranges[2]
        elif num_students < 50:
            return ranges[3]
        elif num_students < 60:
            return ranges[4]
        elif num_students < 70:
            return ranges[5]
        elif num_students < 80:
            return ranges[6]
        elif num_students < 90:
            return ranges[7]
        elif num_students < 100:
            return ranges[8]
        else:
            return ranges[9]

    def setup_salary_report_tab(self):
        # Header
        header_frame = ctk.CTkFrame(self.salary_report_tab, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(header_frame, text="Báo cáo tiền dạy", font=("Helvetica", 18, "bold"), text_color="black").pack(side="left")

        # Year filter
        filter_frame = ctk.CTkFrame(self.salary_report_tab, fg_color="#F0F0F0", corner_radius=10)
        filter_frame.pack(padx=10, pady=10, fill="x")
        ctk.CTkLabel(filter_frame, text="Năm học:", font=("Helvetica", 14), text_color="black").pack(side="left", padx=5)
        self.report_year_combobox = ctk.CTkComboBox(filter_frame, width=200, values=[f"{y}-{y+1}" for y in range(2020, 2030)], command=self.show_semester_report)
        self.report_year_combobox.pack(side="left", padx=5)
        self.report_year_combobox.set("2024-2025")

        # Content frame
        self.report_content_frame = ctk.CTkFrame(self.salary_report_tab, fg_color="#FFFFFF", corner_radius=10)
        self.report_content_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Load initial report
        self.show_semester_report()

    def show_semester_report(self, event=None):
        year = self.report_year_combobox.get()
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.semester_name, COUNT(c.class_id) as class_count,
                    COALESCE(SUM(cm.periods * (cm.coefficient + COALESCE(cc.coefficient, 0))), 0) as total_converted_periods,
                    COALESCE(SUM(cm.periods * (cm.coefficient + COALESCE(cc.coefficient, 0)) * COALESCE(tc.coefficient, 1) * COALESCE(tr.amount_per_period, 0)), 0) as total_salary
                FROM teachers t
                JOIN assignments a ON t.teacher_id = a.teacher_id
                JOIN classes c ON a.class_id = c.class_id
                JOIN semesters s ON c.semester_id = s.semester_id
                JOIN course_modules cm ON c.module_id = cm.module_id
                LEFT JOIN class_enrollments ce ON c.class_id = ce.class_id
                LEFT JOIN class_coefficients cc ON ce.enrolled_students BETWEEN 
                    CASE cc.student_range 
                        WHEN '<20 sinh viên' THEN 0 
                        WHEN '20-29 sinh viên' THEN 20 
                        WHEN '30-39 sinh viên' THEN 30 
                        WHEN '40-49 sinh viên' THEN 40 
                        WHEN '50-59 sinh viên' THEN 50 
                        WHEN '60-69 sinh viên' THEN 60 
                        WHEN '70-79 sinh viên' THEN 70 
                        WHEN '80-89 sinh viên' THEN 80 
                        WHEN '90-99 sinh viên' THEN 90 
                        WHEN '>=100 sinh viên' THEN 100 
                    END 
                    AND CASE cc.student_range 
                        WHEN '<20 sinh viên' THEN 19 
                        WHEN '20-29 sinh viên' THEN 29 
                        WHEN '30-39 sinh viên' THEN 39 
                        WHEN '40-49 sinh viên' THEN 49 
                        WHEN '50-59 sinh viên' THEN 59 
                        WHEN '60-69 sinh viên' THEN 69 
                        WHEN '70-79 sinh viên' THEN 79 
                        WHEN '80-89 sinh viên' THEN 89 
                        WHEN '90-99 sinh viên' THEN 99 
                        WHEN '>=100 sinh viên' THEN 9999 
                    END AND cc.year = %s
                LEFT JOIN teacher_coefficients tc ON t.degree_id = tc.degree_id AND tc.year = %s
                LEFT JOIN teaching_rate tr ON tr.year = %s
                WHERE t.teacher_id = %s AND s.year = %s
                GROUP BY s.semester_id, s.semester_name
                ORDER BY s.semester_name
            """, (year, year, year, self.teacher_id, year))
            semesters = cursor.fetchall()

            for widget in self.report_content_frame.winfo_children():
                widget.destroy()

            title_frame = ctk.CTkFrame(self.report_content_frame, fg_color="transparent")
            title_frame.pack(fill="x", pady=(0, 20))
            ctk.CTkLabel(title_frame, text=f"BÁO CÁO TIỀN DẠY", font=("Helvetica", 20, "bold"), text_color="#2B3467").pack(side="left")
            ctk.CTkLabel(title_frame, text=f"Năm học: {year}", font=("Helvetica", 14), text_color="#666666").pack(side="right")

            if not semesters:
                ctk.CTkLabel(self.report_content_frame, text=f"Không có dữ liệu trong năm {year}", font=("Helvetica", 14), text_color="red").pack(expand=True)
                return

            total_salary = sum(float(s[3] or 0) for s in semesters)
            if total_salary == 0:
                ctk.CTkLabel(self.report_content_frame, text=f"Cảnh báo: Tổng tiền = 0 trong năm {year}", font=("Helvetica", 14), text_color="orange").pack(expand=True)

            # Summary cards
            summary_frame = ctk.CTkFrame(self.report_content_frame, fg_color="transparent")
            summary_frame.pack(fill="x", pady=(0, 20))
            stats = {
                "Học kỳ": len(semesters),
                "Lớp học phần": sum(s[1] or 0 for s in semesters),
                "Tổng tiền": f"{int(total_salary):,} đ"
            }
            for i, (label, value) in enumerate(stats.items()):
                card = ctk.CTkFrame(summary_frame, fg_color="#4B89DC", corner_radius=10)
                card.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
                ctk.CTkLabel(card, text=value, font=("Helvetica", 16, "bold"), text_color="white").pack(pady=(5,0))
                ctk.CTkLabel(card, text=label, font=("Helvetica", 12), text_color="white").pack(pady=(0,5))
            summary_frame.grid_columnconfigure((0,1,2), weight=1)

            # Table and chart container
            content_frame = ctk.CTkFrame(self.report_content_frame, fg_color="transparent")
            content_frame.pack(fill="both", expand=True)
            content_frame.grid_columnconfigure(0, weight=7)
            content_frame.grid_columnconfigure(1, weight=3)

            # Table frame
            table_frame = ctk.CTkScrollableFrame(content_frame, fg_color="transparent")
            table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

            # Table header
            header_frame = ctk.CTkFrame(table_frame, fg_color="#2B3467")
            header_frame.pack(fill="x", pady=(0, 5))
            headers = ["STT", "HỌC KỲ", "SỐ LỚP", "TIẾT QĐ", "TỔNG TIỀN"]
            col_widths = [50, 150, 100, 100, 150]
            for col, (header, width) in enumerate(zip(headers, col_widths)):
                ctk.CTkLabel(header_frame, text=header, width=width, anchor="center", font=("Helvetica", 11, "bold"), text_color="white").grid(row=0, column=col, padx=5, pady=5)

            # Table rows
            for idx, (semester_name, class_count, converted_periods, salary) in enumerate(semesters, 1):
                row = ctk.CTkFrame(table_frame, fg_color="#FFFFFF" if idx % 2 == 0 else "#F0F0F0")
                row.pack(fill="x", pady=1)
                ctk.CTkLabel(row, text=str(idx), width=50, anchor="center").grid(row=0, column=0, padx=5, pady=2)
                ctk.CTkLabel(row, text=semester_name, width=150, anchor="w").grid(row=0, column=1, padx=5, pady=2)
                ctk.CTkLabel(row, text=str(class_count), width=100, anchor="center").grid(row=0, column=2, padx=5, pady=2)
                ctk.CTkLabel(row, text=str(int(float(converted_periods)) if converted_periods is not None else 0), width=100, anchor="center").grid(row=0, column=3, padx=5, pady=2)
                ctk.CTkLabel(row, text=f"{int(float(salary)) if salary is not None else 0:,} đ", width=150, anchor="center").grid(row=0, column=4, padx=5, pady=2)

            # Total row
            total_frame = ctk.CTkFrame(table_frame, fg_color="#E3F2FD")
            total_frame.pack(fill="x", pady=(5, 0))
            ctk.CTkLabel(total_frame, text="TỔNG CỘNG:", width=50, anchor="center", font=("Helvetica", 11, "bold"), text_color="#2B3467").grid(row=0, column=0, padx=5, pady=2)
            ctk.CTkLabel(total_frame, text="", width=130).grid(row=0, column=1, padx=5, pady=2)
            ctk.CTkLabel(total_frame, text=str(sum(s[1] or 0 for s in semesters)), width=100, anchor="center", font=("Helvetica", 11, "bold"), text_color="#2B3467").grid(row=0, column=2, padx=5, pady=2)
            ctk.CTkLabel(total_frame, text=str(int(sum(float(s[2] or 0) for s in semesters))), width=100, anchor="center", font=("Helvetica", 11, "bold"), text_color="#2B3467").grid(row=0, column=3, padx=5, pady=2)
            ctk.CTkLabel(total_frame, text=f"{int(sum(float(s[3] or 0) for s in semesters)):,} đ", width=150, anchor="center", font=("Helvetica", 11, "bold"), text_color="#2B3467").grid(row=0, column=4, padx=5, pady=2)

            # Chart frame
            chart_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            chart_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

            semester_names = [s[0] for s in semesters]
            salaries = [float(s[3] or 0) for s in semesters]

            if sum(salaries) > 0:
                fig, ax = plt.subplots(figsize=(4, 3))
                ax.bar(semester_names, salaries, color="#4B89DC")
                ax.set_title("Tiền dạy theo học kỳ")
                ax.set_ylabel("Số tiền (đ)")
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                canvas = FigureCanvasTkAgg(fig, master=chart_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)
            else:
                ctk.CTkLabel(chart_frame, text="Không có dữ liệu để vẽ biểu đồ", font=("Helvetica", 14)).pack(expand=True, fill="both")

            # Export button
            export_btn = ctk.CTkButton(self.report_content_frame, text="Xuất Excel", command=lambda: self.export_semester_report(year), fg_color="#28A745", hover_color="#218838")
            export_btn.pack(side="bottom", pady=10)

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {e}")
        finally:
            cursor.close()
            conn.close()

    def export_semester_report(self, year):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.semester_name, COUNT(c.class_id) as class_count,
                    COALESCE(SUM(cm.periods * (cm.coefficient + COALESCE(cc.coefficient, 0))), 0) as total_converted_periods,
                    COALESCE(SUM(cm.periods * (cm.coefficient + COALESCE(cc.coefficient, 0)) * COALESCE(tc.coefficient, 1) * COALESCE(tr.amount_per_period, 0)), 0) as total_salary
                FROM teachers t
                JOIN assignments a ON t.teacher_id = a.teacher_id
                JOIN classes c ON a.class_id = c.class_id
                JOIN semesters s ON c.semester_id = s.semester_id
                JOIN course_modules cm ON c.module_id = cm.module_id
                LEFT JOIN class_enrollments ce ON c.class_id = ce.class_id
                LEFT JOIN class_coefficients cc ON ce.enrolled_students BETWEEN 
                    CASE cc.student_range 
                        WHEN '<20 sinh viên' THEN 0 
                        WHEN '20-29 sinh viên' THEN 20 
                        WHEN '30-39 sinh viên' THEN 30 
                        WHEN '40-49 sinh viên' THEN 40 
                        WHEN '50-59 sinh viên' THEN 50 
                        WHEN '60-69 sinh viên' THEN 60 
                        WHEN '70-79 sinh viên' THEN 70 
                        WHEN '80-89 sinh viên' THEN 80 
                        WHEN '90-99 sinh viên' THEN 90 
                        WHEN '>=100 sinh viên' THEN 100 
                    END 
                    AND CASE cc.student_range 
                        WHEN '<20 sinh viên' THEN 19 
                        WHEN '20-29 sinh viên' THEN 29 
                        WHEN '30-39 sinh viên' THEN 39 
                        WHEN '40-49 sinh viên' THEN 49 
                        WHEN '50-59 sinh viên' THEN 59 
                        WHEN '60-69 sinh viên' THEN 69 
                        WHEN '70-79 sinh viên' THEN 79 
                        WHEN '80-89 sinh viên' THEN 89 
                        WHEN '90-99 sinh viên' THEN 99 
                        WHEN '>=100 sinh viên' THEN 9999 
                    END AND cc.year = %s
                LEFT JOIN teacher_coefficients tc ON t.degree_id = tc.degree_id AND tc.year = %s
                LEFT JOIN teaching_rate tr ON tr.year = %s
                WHERE t.teacher_id = %s AND s.year = %s
                GROUP BY s.semester_id, s.semester_name
            """, (year, year, year, self.teacher_id, year))
            semesters = cursor.fetchall()

            data = []
            for idx, (semester_name, class_count, converted_periods, salary) in enumerate(semesters, 1):
                data.append({
                    "STT": idx,
                    "HỌC KỲ": semester_name,
                    "SỐ LỚP": class_count,
                    "TỔNG SỐ TIẾT QUY ĐỔI": int(float(converted_periods)) if converted_periods is not None else 0,
                    "TỔNG TIỀN": int(float(salary)) if salary is not None else 0
                })

            df = pd.DataFrame(data)
            df.to_excel(f"semester_report_{self.teacher_id}_{year}.xlsx", index=False)
            messagebox.showinfo("Thành công", f"Báo cáo đã được xuất ra file: semester_report_{self.teacher_id}_{year}.xlsx")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất báo cáo: {e}")
        finally:
            cursor.close()
            conn.close()

    def setup_password_change_tab(self):
        # Header
        header_frame = ctk.CTkFrame(self.password_change_tab, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(header_frame, text="Đổi mật khẩu", font=("Helvetica", 24, "bold"), 
                    text_color="#2B3467").pack(side="left")

        # Main content
        content_frame = ctk.CTkFrame(self.password_change_tab, fg_color="white", corner_radius=12, 
                                   border_width=1, border_color="#E0E0E0")
        content_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Form container
        form_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        form_frame.pack(pady=20, padx=20, fill="x")

        # Current password
        ctk.CTkLabel(form_frame, text="Mật khẩu hiện tại:", font=("Helvetica", 14, "bold"), 
                    text_color="#2B3467").pack(anchor="w", pady=(0, 5))
        current_password = ctk.CTkEntry(form_frame, placeholder_text="Nhập mật khẩu hiện tại", show="*", width=300)
        current_password.pack(fill="x", pady=(0, 10))

        # New password
        ctk.CTkLabel(form_frame, text="Mật khẩu mới:", font=("Helvetica", 14, "bold"), 
                    text_color="#2B3467").pack(anchor="w", pady=(0, 5))
        new_password = ctk.CTkEntry(form_frame, placeholder_text="Nhập mật khẩu mới", show="*", width=300)
        new_password.pack(fill="x", pady=(0, 10))

        # Confirm password
        ctk.CTkLabel(form_frame, text="Xác nhận mật khẩu:", font=("Helvetica", 14, "bold"), 
                    text_color="#2B3467").pack(anchor="w", pady=(0, 5))
        confirm_password = ctk.CTkEntry(form_frame, placeholder_text="Xác nhận mật khẩu mới", show="*", width=300)
        confirm_password.pack(fill="x", pady=(0, 10))

        def save_password():
            current_pass = current_password.get().strip()
            new_pass = new_password.get().strip()
            confirm_pass = confirm_password.get().strip()

            # Kiểm tra mật khẩu
            if not current_pass or not new_pass or not confirm_pass:
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ các trường!", parent=self.password_change_tab)
                return
            if new_pass != confirm_pass:
                messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp!", parent=self.password_change_tab)
                return
            if len(new_pass) < 8:
                messagebox.showerror("Lỗi", "Mật khẩu mới phải có ít nhất 8 ký tự!", parent=self.password_change_tab)
                return
            if not re.search(r"[A-Z]", new_pass) or not re.search(r"[a-z]", new_pass) or not re.search(r"[0-9]", new_pass):
                messagebox.showerror("Lỗi", "Mật khẩu phải chứa chữ hoa, chữ thường và số!", parent=self.password_change_tab)
                return

            # Kiểm tra mật khẩu hiện tại
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("SELECT password FROM users WHERE user_id = %s", (self.teacher_id,))
                stored_password = cursor.fetchone()
                if not stored_password or stored_password[0] != current_pass:
                    messagebox.showerror("Lỗi", "Mật khẩu hiện tại không đúng!", parent=self.password_change_tab)
                    return

                # Cập nhật mật khẩu
                cursor.execute("UPDATE users SET password = %s WHERE user_id = %s", (new_pass, self.teacher_id))
                conn.commit()
                messagebox.showinfo("Thành công", "Mật khẩu đã được đổi thành công!", parent=self.password_change_tab)
                current_password.delete(0, "end")
                new_password.delete(0, "end")
                confirm_password.delete(0, "end")
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể đổi mật khẩu: {e}", parent=self.password_change_tab)
            finally:
                cursor.close()
                conn.close()

        # Buttons
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(pady=20)
        ctk.CTkButton(button_frame, text="Lưu mật khẩu", fg_color="#1E3A8A", hover_color="#60A5FA", 
                     command=save_password).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Khôi phục mật khẩu", fg_color="#3B82F6", hover_color="#60A5FA",
                     command=self.show_restore_password_dialog).pack(side="left", padx=10)

    def show_restore_password_dialog(self):
        ModernDialog(
            self.window,
            "Khôi phục mật khẩu",
            "Để khôi phục mật khẩu, vui lòng liên hệ với quản trị viên hệ thống:\n\n"
            "📧 Email: admin@phenikaa.edu.vn\n"
            "📞 Điện thoại: 024-6291-8088\n"
            "🕒 Thời gian: 8:00 - 17:00 (Thứ 2 - Thứ 6)\n\n"
            "Quản trị viên sẽ hỗ trợ bạn reset mật khẩu trong vòng 24h.",
            "info",
            ["Đã hiểu", "Sao chép Email"]
        )

if __name__ == "__main__":
    window = ctk.CTk()
    user = {"user_id": "TCH62958", "username": "hoang_quoc_manh_teacher", "role": "Teacher", "password": "default123"}
    app = TeacherView(window, user)
    window.mainloop()