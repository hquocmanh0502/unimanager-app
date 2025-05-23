from customtkinter import *
from tkinter import ttk, messagebox, END
import mysql.connector
from db_config import DB_CONFIG
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import random



class DepartmentView:
    def __init__(self, window, user):
        self.window = window
        self.user = user
        self.window.title("Giao diện Khoa")
        self.window.geometry("1700x700")
        self.window.resizable(False, False)

        

        # Khởi tạo dept_id nếu là tài khoản khoa
        if self.user['role'] == 'Department':
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("SELECT dept_id FROM departments WHERE dept_id = %s", (self.user['user_id'],))
                result = cursor.fetchone()
                if result:
                    self.user['dept_id'] = result[0]
                else:
                    messagebox.showerror("Lỗi", "Không tìm thấy khoa tương ứng")
                    self.window.destroy()
                    return
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể tải thông tin khoa: {e}")
                self.window.destroy()
                return
            finally:
                cursor.close()
                conn.close()
        elif 'dept_id' not in self.user:
            messagebox.showerror("Lỗi", "Thiếu thông tin khoa cho tài khoản")
            self.window.destroy()
            return

        # Frame chính với gradient nền
        self.main_frame = CTkFrame(self.window, fg_color=("#E6F0FA", "#B0C4DE"))
        self.main_frame.pack(fill="both", expand=True)

        # Cấu hình style cho tiêu đề bảng (in đậm)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

        # Sidebar
        self.sidebar = CTkFrame(self.main_frame, width=250, fg_color="#1E3A8A")
        self.sidebar.pack(side="left", fill="y")

        # Tiêu đề sidebar
        CTkLabel(self.sidebar, text="Quản lý Khoa", font=("Helvetica", 20, "bold"), text_color="white").pack(pady=20)

        # Menu sidebar
        menu_items = ["Bằng cấp", "Khoa", "Giáo viên", "Thống kê", "Học phần", "Lớp học", "Lương"]
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

        # Tab Bằng cấp
        self.degree_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.setup_degree_tab()

        # Tab Khoa
        self.dept_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.setup_dept_tab()

        # Tab Quản lý Giáo viên
        self.teacher_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.setup_teacher_tab()

        # Tab Thống kê
        self.stats_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.setup_stats_tab()

        # Tab Quản lý Học phần
        self.module_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.setup_module_tab()

        # Tab Quản lý Lớp học
        self.class_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.setup_class_tab()

        # Tab Xem Lương
        self.salary_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.setup_salary_tab()

        # Hiển thị tab đầu tiên và gán current_tab
        self.current_tab = self.teacher_tab
        self.current_tab.pack(fill="both", expand=True)

        # Nút đăng xuất
        CTkButton(self.content_frame, text="Đăng xuất", font=("Helvetica", 14, "bold"), fg_color="#DC3545",
                  hover_color="#B02A37", command=self.logout).pack(pady=10, side="bottom", anchor="se")

    def setup_degree_tab(self):
        CTkLabel(self.degree_tab, text="Bằng cấp", font=("Helvetica", 18, "bold"), text_color="black").pack(pady=10)
        main_frame = CTkFrame(self.degree_tab, fg_color="transparent")
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Form chỉnh sửa bằng cấp
        form_frame = CTkFrame(main_frame, fg_color="#F0F0F0", corner_radius=10)
        form_frame.pack(side="left", padx=10, pady=10, fill="y")
        CTkLabel(form_frame, text="Quản lý Bằng cấp", font=("Helvetica", 16, "bold")).pack(pady=5)
        self.degree_name = CTkEntry(form_frame, placeholder_text="Tên bằng cấp", width=200)
        self.degree_name.pack(pady=5)
        self.degree_abbr = CTkEntry(form_frame, placeholder_text="Tên viết tắt", width=200)
        self.degree_abbr.pack(pady=5)
        self.degree_coeff = CTkEntry(form_frame, placeholder_text="Hệ số (ví dụ: 1.5)", width=200)
        self.degree_coeff.pack(pady=5)
        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        CTkButton(button_frame, text="Thêm", fg_color="#0085FF", command=self.add_degree).pack(side="left", padx=5)
        CTkButton(button_frame, text="Sửa", fg_color="#FFC107", command=self.edit_degree).pack(side="left", padx=5)
        CTkButton(button_frame, text="Xóa", fg_color="#F44336", command=self.delete_degree).pack(side="left", padx=5)
        CTkButton(button_frame, text="Reset", fg_color="#6C757D", command=self.reset_degree_fields).pack(side="left", padx=5)

        # Bảng bằng cấp
        table_frame = CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=10)
        table_frame.pack(side="right", padx=10, pady=10, fill="both", expand=True)
        self.degree_tree = ttk.Treeview(table_frame, columns=("ID", "Name", "Abbr", "Coefficient"), show="headings")
        self.degree_tree.heading("ID", text="Mã bằng cấp")
        self.degree_tree.heading("Name", text="Tên bằng cấp")
        self.degree_tree.heading("Abbr", text="Tên viết tắt")
        self.degree_tree.heading("Coefficient", text="Hệ số")
        self.degree_tree.column("ID", width=100, anchor="center")
        self.degree_tree.column("Name", width=200, anchor="center")
        self.degree_tree.column("Abbr", width=150, anchor="center")
        self.degree_tree.column("Coefficient", width=100, anchor="center")
        self.degree_tree.pack(padx=10, pady=10, fill="both", expand=True)
        self.degree_tree.bind("<<TreeviewSelect>>", self.on_degree_select)
        self.load_degrees()

    def setup_dept_tab(self):
        CTkLabel(self.dept_tab, text="Khoa", font=("Helvetica", 18, "bold"), text_color="black").pack(pady=10)
        main_frame = CTkFrame(self.dept_tab, fg_color="transparent")
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Form chỉnh sửa khoa
        form_frame = CTkFrame(main_frame, fg_color="#F0F0F0", corner_radius=10)
        form_frame.pack(side="left", padx=10, pady=10, fill="y")
        CTkLabel(form_frame, text="Quản lý Khoa", font=("Helvetica", 16, "bold")).pack(pady=5)
        self.dept_name = CTkEntry(form_frame, placeholder_text="Tên khoa", width=200)
        self.dept_name.pack(pady=5)
        self.dept_abbr = CTkEntry(form_frame, placeholder_text="Tên viết tắt", width=200)
        self.dept_abbr.pack(pady=5)
        self.dept_description = CTkEntry(form_frame, placeholder_text="Mô tả nhiệm vụ", width=200)
        self.dept_description.pack(pady=5)
        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        CTkButton(button_frame, text="Thêm", fg_color="#0085FF", command=self.add_dept).pack(side="left", padx=5)
        CTkButton(button_frame, text="Sửa", fg_color="#FFC107", command=self.edit_dept).pack(side="left", padx=5)
        CTkButton(button_frame, text="Xóa", fg_color="#F44336", command=self.delete_dept).pack(side="left", padx=5)
        CTkButton(button_frame, text="Reset", fg_color="#6C757D", command=self.reset_dept_fields).pack(side="left", padx=5)

        # Bảng khoa
        table_frame = CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=10)
        table_frame.pack(side="right", padx=10, pady=10, fill="both", expand=True)
        self.dept_tree = ttk.Treeview(table_frame, columns=("ID", "Name", "Abbr", "Description"), show="headings")
        self.dept_tree.heading("ID", text="Mã khoa")
        self.dept_tree.heading("Name", text="Tên khoa")
        self.dept_tree.heading("Abbr", text="Tên viết tắt")
        self.dept_tree.heading("Description", text="Mô tả nhiệm vụ")
        self.dept_tree.column("ID", width=60, anchor="center")
        self.dept_tree.column("Name", width=200, anchor="center")
        self.dept_tree.column("Abbr", width=60, anchor="center")
        self.dept_tree.column("Description", width=300, anchor="center")
        self.dept_tree.pack(padx=10, pady=10, fill="both", expand=True)
        self.dept_tree.bind("<<TreeviewSelect>>", self.on_dept_select)
        self.load_depts()

    def setup_teacher_tab(self):
        CTkLabel(self.teacher_tab, text="Giáo viên", font=("Helvetica", 18, "bold"), text_color="black").pack(pady=10)
        main_frame = CTkFrame(self.teacher_tab, fg_color="transparent")
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Form chỉnh sửa giáo viên
        form_frame = CTkFrame(main_frame, fg_color="#F0F0F0", corner_radius=10)
        form_frame.pack(side="left", padx=10, pady=10, fill="y")
        CTkLabel(form_frame, text="Quản lý Giáo viên", font=("Helvetica", 16, "bold")).pack(pady=5)
        self.teacher_name = CTkEntry(form_frame, placeholder_text="Họ tên", width=150)
        self.teacher_name.pack(pady=5)
        self.date_of_birth = CTkEntry(form_frame, placeholder_text="Ngày sinh (YYYY-MM-DD)", width=150)
        self.date_of_birth.pack(pady=5)
        self.phone = CTkEntry(form_frame, placeholder_text="Điện thoại", width=150)
        self.phone.pack(pady=5)
        self.email = CTkEntry(form_frame, placeholder_text="Email", width=150)
        self.email.pack(pady=5)
        self.dept_combobox = CTkComboBox(form_frame, width=150, values=self.get_departments())
        self.dept_combobox.pack(pady=5)
        self.degree_combobox = CTkComboBox(form_frame, width=150, values=self.get_degrees())
        self.degree_combobox.pack(pady=5)
        self.teacher_coeff = CTkEntry(form_frame, placeholder_text="Hệ số (ví dụ: 1.5)", width=150)
        self.teacher_coeff.pack(pady=5)
        self.degree_combobox.configure(command=self.update_teacher_coefficient)
        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=5)
        CTkButton(button_frame, text="Thêm", fg_color="#0085FF", command=self.add_teacher, width=70, font=("Helvetica", 12)).pack(side="left", padx=2)
        CTkButton(button_frame, text="Sửa", fg_color="#FFC107", command=self.edit_teacher, width=70, font=("Helvetica", 12)).pack(side="left", padx=2)
        CTkButton(button_frame, text="Xóa", fg_color="#F44336", command=self.delete_teacher, width=70, font=("Helvetica", 12)).pack(side="left", padx=2)
        CTkButton(button_frame, text="Reset", fg_color="#6C757D", command=self.reset_teacher_fields, width=70, font=("Helvetica", 12)).pack(side="left", padx=2)

        # Bảng giáo viên
        table_frame = CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=10)
        table_frame.pack(side="right", padx=10, pady=10, fill="both", expand=True)
        self.teacher_tree = ttk.Treeview(table_frame, columns=("ID", "Name", "DOB", "Phone", "Email", "Dept", "Degree", "Coefficient"), show="headings")
        self.teacher_tree.heading("ID", text="Mã số")
        self.teacher_tree.heading("Name", text="Họ tên")
        self.teacher_tree.heading("DOB", text="Ngày sinh")
        self.teacher_tree.heading("Phone", text="Điện thoại")
        self.teacher_tree.heading("Email", text="Email")
        self.teacher_tree.heading("Dept", text="Khoa")
        self.teacher_tree.heading("Degree", text="Bằng cấp")
        self.teacher_tree.heading("Coefficient", text="Hệ số")
        self.teacher_tree.column("ID", width=80, anchor="center")  # Tăng từ 80 lên 100
        self.teacher_tree.column("Name", width=150, anchor="center")  # Tăng từ 120 lên 150
        self.teacher_tree.column("DOB", width=100, anchor="center")  # Tăng từ 100 lên 120
        self.teacher_tree.column("Phone", width=100, anchor="center")  # Tăng từ 100 lên 120
        self.teacher_tree.column("Email", width=150, anchor="center")  # Tăng từ 120 lên 150
        self.teacher_tree.column("Dept", width=150, anchor="center")  # Tăng từ 120 lên 150
        self.teacher_tree.column("Degree", width=150, anchor="center")  # Tăng từ 120 lên 150
        self.teacher_tree.column("Coefficient", width=100, anchor="center")  # Tăng từ 80 lên 100
        self.teacher_tree.pack(padx=10, pady=10, fill="both", expand=True)
        self.teacher_tree.bind("<<TreeviewSelect>>", self.on_teacher_select)
        self.load_teachers()

    def setup_stats_tab(self):
        CTkLabel(self.stats_tab, text="Biểu đồ Thống kê", font=("Helvetica", 18, "bold"), text_color="black").pack(pady=10)

        # Frame chứa các nút điều hướng
        button_frame = CTkFrame(self.stats_tab, fg_color="#FFFFFF", corner_radius=10)
        button_frame.pack(padx=10, pady=10, fill="x")

        # Nút điều hướng đến các biểu đồ
        CTkButton(button_frame, text="Biểu đồ Độ tuổi", font=("Helvetica", 14, "bold"), fg_color="#36A2EB", hover_color="#2A82C5", height=40, command=self.show_age_chart).pack(side="left", padx=10, pady=10, fill="x", expand=True)
        CTkButton(button_frame, text="Biểu đồ Khoa", font=("Helvetica", 14, "bold"), fg_color="#FF6384", hover_color="#E55773", height=40, command=self.show_dept_chart).pack(side="left", padx=10, pady=10, fill="x", expand=True)
        CTkButton(button_frame, text="Biểu đồ Bằng cấp", font=("Helvetica", 14, "bold"), fg_color="#FFCE56", hover_color="#E5B74C", height=40, command=self.show_degree_chart).pack(side="left", padx=10, pady=10, fill="x", expand=True)

        # Frame chứa biểu đồ
        self.chart_frame = CTkFrame(self.stats_tab, fg_color="#FFFFFF", corner_radius=10)
        self.chart_frame.pack(padx=10, pady=10, fill="both", expand=True)

    def clear_chart_frame(self):
        """Xóa biểu đồ cũ trong chart_frame."""
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

    def show_age_chart(self):
        self.clear_chart_frame()

        age_labels, age_data = self.get_age_distribution()
        if not age_labels or not age_data:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu độ tuổi để hiển thị.")
            return

        # Tạo biểu đồ cột bằng Matplotlib
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(age_labels, age_data, color=["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"])
        ax.set_title("Phân bố Độ tuổi", fontsize=14, pad=15)
        ax.set_xlabel("Nhóm tuổi", fontsize=12)
        ax.set_ylabel("Số giáo viên", fontsize=12)
        ax.set_ylim(0, max(age_data) + 1 if age_data else 1)

        # Nhúng biểu đồ vào chart_frame
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def show_dept_chart(self):
        self.clear_chart_frame()

        dept_labels, dept_data = self.get_dept_distribution()
        if not dept_labels or not dept_data:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu khoa để hiển thị.")
            return

        # Tạo biểu đồ tròn bằng Matplotlib
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(dept_data, labels=dept_labels, colors=["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"], autopct='%1.1f%%', startangle=90)
        ax.set_title("Phân bố theo Khoa", fontsize=14, pad=15)
        ax.axis('equal')  # Đảm bảo biểu đồ tròn không bị méo

        # Nhúng biểu đồ vào chart_frame
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def show_degree_chart(self):
        self.clear_chart_frame()

        degree_labels, degree_data = self.get_degree_distribution()
        if not degree_labels or not degree_data:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu bằng cấp để hiển thị.")
            return

        # Tạo biểu đồ cột bằng Matplotlib
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(degree_labels, degree_data, color=["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"])
        ax.set_title("Phân bố theo Bằng cấp", fontsize=14, pad=15)
        ax.set_xlabel("Bằng cấp", fontsize=12)
        ax.set_ylabel("Số giáo viên", fontsize=12)
        ax.set_ylim(0, max(degree_data) + 1 if degree_data else 1)
        plt.xticks(rotation=0, ha="right")

        # Nhúng biểu đồ vào chart_frame
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    

    def setup_module_tab(self):
        CTkLabel(self.module_tab, text="Học phần", font=("Helvetica", 18, "bold"), text_color="black").pack(pady=10)
        main_frame = CTkFrame(self.module_tab, fg_color="transparent")
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Form chỉnh sửa học phần
        form_frame = CTkFrame(main_frame, fg_color="#F0F0F0", corner_radius=10)
        form_frame.pack(side="left", padx=10, pady=10, fill="y")
        CTkLabel(form_frame, text="Quản lý Học phần", font=("Helvetica", 16, "bold")).pack(pady=5)
        self.module_name = CTkEntry(form_frame, placeholder_text="Tên học phần", width=200)
        self.module_name.pack(pady=5)
        self.module_coeff = CTkEntry(form_frame, placeholder_text="Hệ số (ví dụ: 1.0)", width=200)
        self.module_coeff.pack(pady=5)
        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        CTkButton(button_frame, text="Thêm", fg_color="#0085FF", command=self.add_module).pack(side="left", padx=5)
        CTkButton(button_frame, text="Sửa", fg_color="#FFC107", command=self.edit_module).pack(side="left", padx=5)
        CTkButton(button_frame, text="Xóa", fg_color="#F44336", command=self.delete_module).pack(side="left", padx=5)
        CTkButton(button_frame, text="Reset", fg_color="#6C757D", command=self.reset_module_fields).pack(side="left", padx=5)

        # Bảng học phần
        table_frame = CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=10)
        table_frame.pack(side="right", padx=10, pady=10, fill="both", expand=True)
        self.module_tree = ttk.Treeview(table_frame, columns=("ID", "Name", "Coefficient", "Dept"), show="headings")
        self.module_tree.heading("ID", text="Mã học phần")
        self.module_tree.heading("Name", text="Tên học phần")
        self.module_tree.heading("Coefficient", text="Hệ số")
        self.module_tree.heading("Dept", text="Khoa")
        self.module_tree.column("ID", width=100, anchor="center")
        self.module_tree.column("Name", width=200, anchor="center")
        self.module_tree.column("Coefficient", width=100, anchor="center")
        self.module_tree.column("Dept", width=200, anchor="center")
        self.module_tree.pack(padx=10, pady=10, fill="both", expand=True)
        self.module_tree.bind("<<TreeviewSelect>>", self.on_module_select)
        self.load_modules()

    def setup_class_tab(self):
        CTkLabel(self.class_tab, text="Lớp học", font=("Helvetica", 18, "bold"), text_color="black").pack(pady=10)
        main_frame = CTkFrame(self.class_tab, fg_color="transparent")
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Form chỉnh sửa lớp học
        form_frame = CTkFrame(main_frame, fg_color="#F0F0F0", corner_radius=10)
        form_frame.pack(side="left", padx=10, pady=10, fill="y")
        CTkLabel(form_frame, text="Quản lý Lớp học", font=("Helvetica", 16, "bold")).pack(pady=5)
        self.module_combobox = CTkComboBox(form_frame, width=200, values=self.get_modules())
        self.module_combobox.pack(pady=5)
        self.teacher_combobox = CTkComboBox(form_frame, width=200, values=self.get_teachers())
        self.teacher_combobox.pack(pady=5)
        self.num_students = CTkEntry(form_frame, placeholder_text="Số sinh viên", width=200)
        self.num_students.pack(pady=5)
        self.actual_periods = CTkEntry(form_frame, placeholder_text="Số tiết", width=200)
        self.actual_periods.pack(pady=5)
        self.semester = CTkEntry(form_frame, placeholder_text="Học kỳ (ví dụ: 2025-1)", width=200)
        self.semester.pack(pady=5)
        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        CTkButton(button_frame, text="Thêm", fg_color="#0085FF", command=self.add_class).pack(side="left", padx=5)
        CTkButton(button_frame, text="Sửa", fg_color="#FFC107", command=self.edit_class).pack(side="left", padx=5)
        CTkButton(button_frame, text="Xóa", fg_color="#F44336", command=self.delete_class).pack(side="left", padx=5)
        CTkButton(button_frame, text="Reset", fg_color="#6C757D", command=self.reset_class_fields).pack(side="left", padx=5)

        # Bảng lớp học
        table_frame = CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=10)
        table_frame.pack(side="right", padx=10, pady=10, fill="both", expand=True)
        self.class_tree = ttk.Treeview(table_frame, columns=("ID", "Module", "Teacher", "Students", "Periods", "Semester"), show="headings")
        self.class_tree.heading("ID", text="Mã lớp")
        self.class_tree.heading("Module", text="Học phần")
        self.class_tree.heading("Teacher", text="Giáo viên")
        self.class_tree.heading("Students", text="Số sinh viên")
        self.class_tree.heading("Periods", text="Số tiết")
        self.class_tree.heading("Semester", text="Học kỳ")
        self.class_tree.column("ID", width=100, anchor="center")
        self.class_tree.column("Module", width=150, anchor="center")
        self.class_tree.column("Teacher", width=150, anchor="center")
        self.class_tree.column("Students", width=100, anchor="center")
        self.class_tree.column("Periods", width=100, anchor="center")
        self.class_tree.column("Semester", width=100, anchor="center")
        self.class_tree.pack(padx=10, pady=10, fill="both", expand=True)
        self.class_tree.bind("<<TreeviewSelect>>", self.on_class_select)
        self.load_classes()

    def setup_salary_tab(self):
        CTkLabel(self.salary_tab, text="Lương", font=("Helvetica", 18, "bold"), text_color="black").pack(pady=10)
        filter_frame = CTkFrame(self.salary_tab, fg_color="#F0F0F0", corner_radius=10)
        filter_frame.pack(padx=10, pady=10, fill="x")
        CTkLabel(filter_frame, text="Lọc Lương", font=("Helvetica", 16, "bold")).pack(pady=5, anchor="w", padx=10)
        CTkLabel(filter_frame, text="Lọc theo giáo viên:", font=("Helvetica", 14)).pack(side="left", padx=5)
        self.salary_teacher_combobox = CTkComboBox(filter_frame, width=200, values=self.get_teachers())
        self.salary_teacher_combobox.pack(side="left", padx=5)
        CTkLabel(filter_frame, text="Học kỳ:", font=("Helvetica", 14)).pack(side="left", padx=5)
        self.salary_semester = CTkEntry(filter_frame, placeholder_text="Học kỳ (ví dụ: 2025-1)", width=150)
        self.salary_semester.pack(side="left", padx=5)
        button_frame = CTkFrame(filter_frame, fg_color="transparent")
        button_frame.pack(side="left", padx=5)
        CTkButton(button_frame, text="Lọc", fg_color="#0085FF", command=self.load_salaries).pack(side="left", padx=5)
        CTkButton(button_frame, text="Reset", fg_color="#6C757D", command=self.reset_salary_fields).pack(side="left", padx=5)
        table_frame = CTkFrame(self.salary_tab, fg_color="#FFFFFF", corner_radius=10)
        table_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.salary_tree = ttk.Treeview(table_frame, columns=("Teacher", "Module", "Amount", "Semester", "Date"), show="headings")
        self.salary_tree.heading("Teacher", text="Giáo viên")
        self.salary_tree.heading("Module", text="Học phần")
        self.salary_tree.heading("Amount", text="Số tiền")
        self.salary_tree.heading("Semester", text="Học kỳ")
        self.salary_tree.heading("Date", text="Ngày tính")
        self.salary_tree.column("Teacher", width=150, anchor="center")
        self.salary_tree.column("Module", width=150, anchor="center")
        self.salary_tree.column("Amount", width=120, anchor="center")
        self.salary_tree.column("Semester", width=100, anchor="center")
        self.salary_tree.column("Date", width=150, anchor="center")
        self.salary_tree.pack(padx=10, pady=10, fill="both", expand=True)
        self.load_salaries()

    def switch_tab(self, tab_name):
        if hasattr(self, 'current_tab') and self.current_tab:
            self.current_tab.pack_forget()
        if tab_name == "Bằng cấp":
            self.current_tab = self.degree_tab
        elif tab_name == "Khoa":
            self.current_tab = self.dept_tab
        elif tab_name == "Giáo viên":
            self.current_tab = self.teacher_tab
        elif tab_name == "Thống kê":
            self.current_tab = self.stats_tab
        elif tab_name == "Học phần":
            self.current_tab = self.module_tab
        elif tab_name == "Lớp học":
            self.current_tab = self.class_tab
        elif tab_name == "Lương":
            self.current_tab = self.salary_tab
        else:
            return
        self.current_tab.pack(fill="both", expand=True)

    def get_departments(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT dept_id, dept_name FROM departments")
            depts = [f"{row[0]}: {row[1]}" for row in cursor.fetchall()]
            return depts if depts else ["Không có khoa"]
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách khoa: {e}")
            return ["Lỗi tải khoa"]
        finally:
            cursor.close()
            conn.close()

    def get_degrees(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT degree_id, degree_name FROM degrees")
            degrees = [f"{row[0]}: {row[1]}" for row in cursor.fetchall()]
            return degrees if degrees else ["Không có bằng cấp"]
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách bằng cấp: {e}")
            return ["Lỗi tải bằng cấp"]
        finally:
            cursor.close()
            conn.close()

    def get_teachers(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT teacher_id, full_name FROM teachers WHERE dept_id = %s", (self.user['dept_id'],))
            teachers = [f"{row[0]}: {row[1]}" for row in cursor.fetchall()]
            return teachers if teachers else ["Không có giáo viên"]
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách giáo viên: {e}")
            return ["Lỗi tải giáo viên"]
        finally:
            cursor.close()
            conn.close()

    def get_modules(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT module_id, module_name FROM course_modules WHERE dept_id = %s", (self.user['dept_id'],))
            modules = [f"{row[0]}: {row[1]}" for row in cursor.fetchall()]
            return modules if modules else ["Không có học phần"]
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách học phần: {e}")
            return ["Lỗi tải học phần"]
        finally:
            cursor.close()
            conn.close()

    import random

    def add_degree(self):
        selected = self.degree_tree.selection()
        if selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng reset form trước khi thêm mới!")
            return

        name = self.degree_name.get().strip()
        abbr = self.degree_abbr.get().strip()
        coeff = self.degree_coeff.get().strip()

        if not all([name, abbr, coeff]):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return

        try:
            coeff = float(coeff)
            if coeff <= 0:
                messagebox.showerror("Lỗi", "Hệ số phải lớn hơn 0")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Hệ số phải là số hợp lệ")
            return

        # Kiểm tra trùng tên bằng cấp và tên viết tắt
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT degree_name FROM degrees WHERE degree_name = %s", (name,))
            if cursor.fetchone():
                messagebox.showerror("Lỗi", "Tên bằng cấp đã tồn tại. Vui lòng chọn tên khác!")
                return
            cursor.fetchall()  # Đọc hết kết quả để tránh lỗi Unread result

            cursor.execute("SELECT degree_abbr FROM degrees WHERE degree_abbr = %s", (abbr,))
            if cursor.fetchone():
                messagebox.showerror("Lỗi", "Tên viết tắt đã tồn tại. Vui lòng chọn tên viết tắt khác!")
                return
            cursor.fetchall()  # Đọc hết kết quả để tránh lỗi Unread result
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể kiểm tra trùng lặp: {e}")
            return
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn thêm bằng cấp này?")
        if not confirm:
            return

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            # Tạo mã số ngẫu nhiên DEGxxxxx
            while True:
                random_num = random.randint(0, 99999)
                degree_id = f"DEG{str(random_num).zfill(5)}"
                cursor.execute("SELECT degree_id FROM degrees WHERE degree_id = %s", (degree_id,))
                if not cursor.fetchone():
                    cursor.fetchall()  # Đọc hết kết quả để tránh lỗi Unread result
                    break

            cursor.execute("INSERT INTO degrees (degree_id, degree_name, degree_abbr, coefficient) VALUES (%s, %s, %s, %s)",
                        (degree_id, name, abbr, coeff))
            conn.commit()
            messagebox.showinfo("Thành công", f"Thêm bằng cấp thành công với mã số {degree_id}")
            self.reset_degree_fields()
            self.load_degrees()
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể thêm bằng cấp: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def edit_degree(self):
        selected_item = self.degree_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn bằng cấp để sửa!")
            return

        item = self.degree_tree.item(selected_item)
        degree_id = item["values"][0]
        name = self.degree_name.get().strip()
        abbr = self.degree_abbr.get().strip()
        coeff = self.degree_coeff.get().strip()

        if not all([name, abbr, coeff]):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return

        try:
            coeff = float(coeff)
            if coeff <= 0:
                messagebox.showerror("Lỗi", "Hệ số phải lớn hơn 0")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Hệ số phải là số hợp lệ")
            return

        # Kiểm tra trùng tên bằng cấp và tên viết tắt (ngoại trừ chính bằng cấp đang sửa)
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT degree_name FROM degrees WHERE degree_name = %s AND degree_id != %s", (name, degree_id))
            if cursor.fetchone():
                messagebox.showerror("Lỗi", "Tên bằng cấp đã tồn tại. Vui lòng chọn tên khác!")
                return

            cursor.execute("SELECT degree_abbr FROM degrees WHERE degree_abbr = %s AND degree_id != %s", (abbr, degree_id))
            if cursor.fetchone():
                messagebox.showerror("Lỗi", "Tên viết tắt đã tồn tại. Vui lòng chọn tên viết tắt khác!")
                return
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể kiểm tra trùng lặp: {e}")
            return
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn cập nhật thông tin bằng cấp này?")
        if not confirm:
            return

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("UPDATE degrees SET degree_name = %s, degree_abbr = %s, coefficient = %s WHERE degree_id = %s",
                        (name, abbr, coeff, degree_id))
            conn.commit()
            messagebox.showinfo("Thành công", "Cập nhật bằng cấp thành công")
            self.reset_degree_fields()
            self.load_degrees()
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể sửa bằng cấp: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()


    def delete_degree(self):
        selected_item = self.degree_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn bằng cấp để xóa!")
            return
        item = self.degree_tree.item(selected_item)
        degree_id = item["values"][0]
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa bằng cấp này?"):
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM teachers WHERE degree_id = %s LIMIT 1", (degree_id,))
                if cursor.fetchone():
                    messagebox.showerror("Lỗi", "Không thể xóa bằng cấp vì có giáo viên liên quan")
                    return
                cursor.execute("DELETE FROM degrees WHERE degree_id = %s", (degree_id,))
                conn.commit()
                messagebox.showinfo("Thành công", "Xóa bằng cấp thành công")
                self.reset_degree_fields()
                self.load_degrees()
                self.degree_combobox.configure(values=self.get_degrees())
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể xóa bằng cấp: {e}")
            finally:
                cursor.close()
                conn.close()

    def load_degrees(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT degree_id, degree_name, degree_abbr, coefficient FROM degrees")
            for item in self.degree_tree.get_children():
                self.degree_tree.delete(item)
            rows = cursor.fetchall()
            if not rows:
                messagebox.showwarning("Cảnh báo", "Không có dữ liệu bằng cấp")
            for row in rows:
                self.degree_tree.insert("", "end", values=row)
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu bằng cấp: {e}")
        finally:
            cursor.close()
            conn.close()

    def on_degree_select(self, event):
        selected_item = self.degree_tree.selection()
        if not selected_item:
            return
        item = self.degree_tree.item(selected_item)
        self.degree_name.delete(0, END)
        self.degree_name.insert(0, item["values"][1])
        self.degree_name.configure(placeholder_text="")
        self.degree_abbr.delete(0, END)
        self.degree_abbr.insert(0, item["values"][2])
        self.degree_abbr.configure(placeholder_text="")
        self.degree_coeff.delete(0, END)
        self.degree_coeff.insert(0, item["values"][3])
        self.degree_coeff.configure(placeholder_text="")

    def reset_degree_fields(self):
        self.degree_name.delete(0, END)
        self.degree_name.configure(placeholder_text="Tên bằng cấp")
        self.degree_abbr.delete(0, END)
        self.degree_abbr.configure(placeholder_text="Tên viết tắt")
        self.degree_coeff.delete(0, END)
        self.degree_coeff.configure(placeholder_text="Hệ số (ví dụ: 1.5)")
        # Bỏ chọn dòng trong bảng degree_tree
        for item in self.degree_tree.selection():
            self.degree_tree.selection_remove(item)

    def add_dept(self):
        selected = self.dept_tree.selection()
        if selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng reset form trước khi thêm mới!")
            return

        name = self.dept_name.get().strip()
        abbr = self.dept_abbr.get().strip()
        description = self.dept_description.get().strip()

        if not all([name, abbr, description]):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return

        # Kiểm tra trùng tên khoa và tên viết tắt
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT dept_name FROM departments WHERE dept_name = %s", (name,))
            if cursor.fetchone():
                messagebox.showerror("Lỗi", "Tên khoa đã tồn tại. Vui lòng chọn tên khác!")
                return
            cursor.fetchall()  # Đọc hết kết quả để tránh lỗi Unread result

            cursor.execute("SELECT dept_abbr FROM departments WHERE dept_abbr = %s", (abbr,))
            if cursor.fetchone():
                messagebox.showerror("Lỗi", "Tên viết tắt đã tồn tại. Vui lòng chọn tên viết tắt khác!")
                return
            cursor.fetchall()  # Đọc hết kết quả để tránh lỗi Unread result
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể kiểm tra trùng lặp: {e}")
            return
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

        # Xác nhận thêm khoa
        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn thêm khoa này?")
        if not confirm:
            return

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            # Tạo mã khoa ngẫu nhiên DEPTxxxx
            while True:
                random_num = random.randint(0, 9999)
                dept_id = f"DEPT{str(random_num).zfill(4)}"
                cursor.execute("SELECT dept_id FROM departments WHERE dept_id = %s", (dept_id,))
                if not cursor.fetchone():
                    cursor.fetchall()  # Đọc hết kết quả để tránh lỗi Unread result
                    break

            cursor.execute("INSERT INTO departments (dept_id, dept_name, dept_abbr, dept_description) VALUES (%s, %s, %s, %s)",
                        (dept_id, name, abbr, description))
            conn.commit()
            messagebox.showinfo("Thành công", f"Thêm khoa thành công với mã số {dept_id}")
            self.reset_dept_fields()
            self.load_depts()
            self.dept_combobox.configure(values=self.get_departments())
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể thêm khoa: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def edit_dept(self):
        selected_item = self.dept_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khoa để sửa!")
            return

        item = self.dept_tree.item(selected_item)
        dept_id = item["values"][0]
        name = self.dept_name.get().strip()
        abbr = self.dept_abbr.get().strip()
        description = self.dept_description.get().strip()

        if not all([name, abbr, description]):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return

        # Kiểm tra trùng tên khoa và tên viết tắt (ngoại trừ chính khoa đang sửa)
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT dept_name FROM departments WHERE dept_name = %s AND dept_id != %s", (name, dept_id))
            if cursor.fetchone():
                messagebox.showerror("Lỗi", "Tên khoa đã tồn tại. Vui lòng chọn tên khác!")
                return

            cursor.execute("SELECT dept_abbr FROM departments WHERE dept_abbr = %s AND dept_id != %s", (abbr, dept_id))
            if cursor.fetchone():
                messagebox.showerror("Lỗi", "Tên viết tắt đã tồn tại. Vui lòng chọn tên viết tắt khác!")
                return
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể kiểm tra trùng lặp: {e}")
            return
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

        # Xác nhận cập nhật khoa
        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn cập nhật thông tin khoa?")
        if not confirm:
            return

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("UPDATE departments SET dept_name = %s, dept_abbr = %s, dept_description = %s WHERE dept_id = %s",
                        (name, abbr, description, dept_id))
            conn.commit()
            messagebox.showinfo("Thành công", "Cập nhật khoa thành công")
            self.reset_dept_fields()
            self.load_depts()
            self.dept_combobox.configure(values=self.get_departments())
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể sửa khoa: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()


    def delete_dept(self):
        selected_item = self.dept_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khoa để xóa!")
            return

        dept_id = self.dept_tree.item(selected_item)["values"][0]

        # Xác nhận xóa
        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa khoa này? Tất cả các khóa học liên quan sẽ bị xóa!")
        if not confirm:
            return

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Xóa các bản ghi liên quan trong course_modules trước
            cursor.execute("DELETE FROM course_modules WHERE dept_id = %s", (dept_id,))
            # Xóa khoa trong departments
            cursor.execute("DELETE FROM departments WHERE dept_id = %s", (dept_id,))
            conn.commit()
            messagebox.showinfo("Thành công", "Xóa khoa thành công")
            self.reset_dept_fields()
            self.load_depts()
            self.dept_combobox.configure(values=self.get_departments())
            # Xóa dòng này vì stats_dept_combobox không tồn tại
            # self.stats_dept_combobox.configure(values=self.get_departments())
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể xóa khoa: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def load_depts(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT dept_id, dept_name, dept_abbr, dept_description FROM departments")
            for item in self.dept_tree.get_children():
                self.dept_tree.delete(item)
            rows = cursor.fetchall()
            if not rows:
                messagebox.showwarning("Cảnh báo", "Không có dữ liệu khoa")
            for row in rows:
                self.dept_tree.insert("", "end", values=row)
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu khoa: {e}")
        finally:
            cursor.close()
            conn.close()

    def on_dept_select(self, event):
        selected_item = self.dept_tree.selection()
        if not selected_item:
            return
        item = self.dept_tree.item(selected_item)
        self.dept_name.delete(0, END)
        self.dept_name.insert(0, item["values"][1])
        self.dept_name.configure(placeholder_text="")
        self.dept_abbr.delete(0, END)
        self.dept_abbr.insert(0, item["values"][2])
        self.dept_abbr.configure(placeholder_text="")
        self.dept_description.delete(0, END)
        self.dept_description.insert(0, item["values"][3])
        self.dept_description.configure(placeholder_text="")

    def reset_dept_fields(self):
        self.dept_name.delete(0, END)
        self.dept_name.configure(placeholder_text="Tên khoa")
        self.dept_abbr.delete(0, END)
        self.dept_abbr.configure(placeholder_text="Tên viết tắt")
        self.dept_description.delete(0, END)
        self.dept_description.configure(placeholder_text="Mô tả nhiệm vụ")
        # Bỏ chọn dòng trong bảng dept_tree
        for item in self.dept_tree.selection():
            self.dept_tree.selection_remove(item)

    def update_teacher_coefficient(self, event=None):
        degree = self.degree_combobox.get()
        if not degree or degree in ["Không có bằng cấp", "Lỗi tải bằng cấp"]:
            self.teacher_coeff.delete(0, END)
            self.teacher_coeff.insert(0, "1.0")
            return
        try:
            degree_id = degree.split(":")[0]
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT coefficient FROM degrees WHERE degree_id = %s", (degree_id,))
            result = cursor.fetchone()
            if result:
                self.teacher_coeff.delete(0, END)
                self.teacher_coeff.insert(0, str(result[0]))
            else:
                self.teacher_coeff.delete(0, END)
                self.teacher_coeff.insert(0, "1.0")
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải hệ số bằng cấp: {e}")
            self.teacher_coeff.delete(0, END)
            self.teacher_coeff.insert(0, "1.0")
        finally:
            cursor.close()
            conn.close()

    def on_teacher_select(self, event):
        selected_item = self.teacher_tree.selection()
        if not selected_item:
            return
        item = self.teacher_tree.item(selected_item)
        values = item["values"]
        self.teacher_name.delete(0, END)
        self.teacher_name.insert(0, values[1])
        self.teacher_name.configure(placeholder_text="")
        self.date_of_birth.delete(0, END)
        self.date_of_birth.insert(0, values[2] if values[2] != 'N/A' else '')
        self.date_of_birth.configure(placeholder_text="")
        self.phone.delete(0, END)
        self.phone.insert(0, values[3] if values[3] != 'N/A' else '')
        self.phone.configure(placeholder_text="")
        self.email.delete(0, END)
        self.email.insert(0, values[4] if values[4] != 'N/A' else '')
        self.email.configure(placeholder_text="")
        self.dept_combobox.set(values[5])
        self.degree_combobox.set(values[6])
        self.teacher_coeff.delete(0, END)
        self.teacher_coeff.insert(0, values[7])
        self.teacher_coeff.configure(placeholder_text="")

    def add_teacher(self):
        # Lấy dữ liệu đầu vào
        name = self.teacher_name.get().strip()
        dob = self.date_of_birth.get().strip()
        phone = self.phone.get().strip()
        email = self.email.get().strip()
        dept = self.dept_combobox.get()
        degree = self.degree_combobox.get()
        coeff = self.teacher_coeff.get().strip()

        # Kiểm tra dữ liệu trống
        if not all([name, phone, email, dept, degree, coeff]):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return

        try:
            # Kiểm tra định dạng ngày sinh
            if not dob:
                dob = datetime.now().strftime('%Y-%m-%d')
            else:
                try:
                    dob = datetime.strptime(dob, '%Y-%m-%d').strftime('%Y-%m-%d')
                except ValueError:
                    raise ValueError("Định dạng ngày sinh phải là YYYY-MM-DD")

            # Kiểm tra định dạng email
            if '@' not in email or '.' not in email:
                raise ValueError("Email không hợp lệ (phải chứa '@' và '.')")

            # Kiểm tra số điện thoại
            if not phone.isdigit() or len(phone) < 10 or len(phone) > 11:
                raise ValueError("Số điện thoại phải chứa 10-11 chữ số")

            # Kiểm tra hệ số
            coeff = float(coeff)
            if coeff <= 0:
                raise ValueError("Hệ số phải là số thực dương")

            # Kiểm tra và trích xuất dept_id
            if ":" not in dept:
                raise ValueError("Định dạng khoa không hợp lệ (phải là 'deptX: Tên khoa')")
            dept_id = dept.split(":")[0].strip()
            if not dept_id:
                raise ValueError("Mã khoa không được để trống")
            if len(dept_id) > 10:
                raise ValueError("Mã khoa vượt quá độ dài tối đa (10 ký tự)")

            # Kiểm tra và trích xuất degree_id
            if ":" not in degree:
                raise ValueError("Định dạng bằng cấp không hợp lệ (phải là 'degX: Tên bằng cấp')")
            degree_id = degree.split(":")[0].strip()
            if not degree_id:
                raise ValueError("Mã bằng cấp không được để trống")
            if len(degree_id) > 10:
                raise ValueError("Mã bằng cấp vượt quá độ dài tối đa (10 ký tự)")

            # ✅ Xác nhận thêm giáo viên
            confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn thêm giáo viên này?")
            if not confirm:
                return

            # Thêm giáo viên vào cơ sở dữ liệu
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            # Tạo mã giáo viên ngẫu nhiên TCHxxxxx
            while True:
                random_num = random.randint(0, 99999)
                teacher_id = f"TCH{str(random_num).zfill(5)}"
                cursor.execute("SELECT teacher_id FROM teachers WHERE teacher_id = %s", (teacher_id,))
                if not cursor.fetchone():
                    cursor.fetchall()  # Đọc hết kết quả để tránh lỗi Unread result
                    break

            cursor.execute("INSERT INTO teachers (teacher_id, full_name, date_of_birth, phone, email, degree_id, dept_id, teacher_coefficient) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (teacher_id, name, dob, phone, email, degree_id, dept_id, coeff))
            cursor.execute("INSERT INTO users (user_id, username, password, role) VALUES (%s, %s, %s, %s)",
                        (teacher_id, name.lower().replace(" ", "_") + "_teacher", "default123", "Teacher"))
            conn.commit()
            messagebox.showinfo("Thành công", f"Thêm giáo viên thành công với mã số {teacher_id}")
            self.reset_teacher_fields()
            self.load_teachers()
            self.teacher_combobox.configure(values=self.get_teachers())
            self.salary_teacher_combobox.configure(values=self.get_teachers())
        except ValueError as ve:
            messagebox.showerror("Lỗi", f"Lỗi dữ liệu: {ve}")
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể thêm giáo viên: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()


    def edit_teacher(self):
        selected_item = self.teacher_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn giáo viên để sửa!")
            return

        item = self.teacher_tree.item(selected_item)
        teacher_id = item["values"][0]
        name = self.teacher_name.get().strip()
        dob = self.date_of_birth.get().strip()
        phone = self.phone.get().strip()
        email = self.email.get().strip()
        dept = self.dept_combobox.get()
        degree = self.degree_combobox.get()
        coeff = self.teacher_coeff.get().strip()

        # Kiểm tra dữ liệu trống
        if not all([name, phone, email, dept, degree, coeff]):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return

        conn = None
        cursor = None
        try:
            # Kiểm tra định dạng ngày sinh
            if not dob:
                dob = datetime.now().strftime('%Y-%m-%d')
            else:
                try:
                    dob = datetime.strptime(dob, '%Y-%m-%d').strftime('%Y-%m-%d')
                except ValueError:
                    raise ValueError("Định dạng ngày sinh phải là YYYY-MM-DD")

            # Kiểm tra định dạng email
            if '@' not in email or '.' not in email:
                raise ValueError("Email không hợp lệ (phải chứa '@' và '.')")

            # Kiểm tra số điện thoại
            if not phone.isdigit() or len(phone) < 10 or len(phone) > 11:
                raise ValueError("Số điện thoại phải chứa 10-11 chữ số")

            # Kiểm tra hệ số
            coeff = float(coeff)
            if coeff <= 0:
                raise ValueError("Hệ số phải là số thực dương")

            # Xử lý dept_id
            if ":" not in dept:
                conn_temp = mysql.connector.connect(**DB_CONFIG)
                cursor_temp = conn_temp.cursor()
                cursor_temp.execute("SELECT dept_id, dept_name FROM departments WHERE dept_name = %s", (dept,))
                result = cursor_temp.fetchone()
                cursor_temp.close()
                conn_temp.close()
                if result:
                    dept = f"{result[0]}: {result[1]}"
            dept_id = dept.split(":")[0].strip()
            if not dept_id:
                raise ValueError("Mã khoa không được để trống")
            if len(dept_id) > 10:
                raise ValueError("Mã khoa vượt quá độ dài tối đa (10 ký tự)")

            # Xử lý degree_id
            if ":" not in degree:
                conn_temp = mysql.connector.connect(**DB_CONFIG)
                cursor_temp = conn_temp.cursor()
                cursor_temp.execute("SELECT degree_id, degree_name FROM degrees WHERE degree_name = %s", (degree,))
                result = cursor_temp.fetchone()
                cursor_temp.close()
                conn_temp.close()
                if result:
                    degree = f"{result[0]}: {result[1]}"
            degree_id = degree.split(":")[0].strip()
            if not degree_id:
                raise ValueError("Mã bằng cấp không được để trống")
            if len(degree_id) > 10:
                raise ValueError("Mã bằng cấp vượt quá độ dài tối đa (10 ký tự)")

            # ✅ Xác nhận cập nhật
            confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn cập nhật thông tin giáo viên?")
            if not confirm:
                return

            # Kết nối và cập nhật
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("UPDATE teachers SET full_name = %s, date_of_birth = %s, phone = %s, email = %s, degree_id = %s, dept_id = %s, teacher_coefficient = %s WHERE teacher_id = %s",
                        (name, dob, phone, email, degree_id, dept_id, coeff, teacher_id))
            cursor.execute("UPDATE users SET username = %s WHERE user_id = %s",
                        (name.lower().replace(" ", "_") + "_teacher", teacher_id))
            conn.commit()
            messagebox.showinfo("Thành công", "Cập nhật giáo viên thành công")
            self.load_teachers()
            self.teacher_combobox.configure(values=self.get_departments())
            self.salary_teacher_combobox.configure(values=self.get_teachers())
            self.reset_teacher_fields()
        except ValueError as ve:
            messagebox.showerror("Lỗi", f"Lỗi dữ liệu: {ve}")
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể sửa giáo viên: {e}")
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()


    def delete_teacher(self):
        selected_item = self.teacher_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn giáo viên để xóa!")
            return
        item = self.teacher_tree.item(selected_item)
        teacher_id = item["values"][0]
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa giáo viên này?"):
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM classes WHERE teacher_id = %s LIMIT 1", (teacher_id,))
                if cursor.fetchone():
                    messagebox.showerror("Lỗi", "Không thể xóa giáo viên vì có lớp học liên quan")
                    return
                cursor.execute("DELETE FROM users WHERE user_id = %s", (teacher_id,))
                cursor.execute("DELETE FROM teachers WHERE teacher_id = %s", (teacher_id,))
                conn.commit()
                messagebox.showinfo("Thành công", "Xóa giáo viên thành công")
                self.reset_teacher_fields()
                self.load_teachers()
                self.teacher_combobox.configure(values=self.get_teachers())
                self.salary_teacher_combobox.configure(values=self.get_teachers())
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể xóa giáo viên: {e}")
            finally:
                cursor.close()
                conn.close()

    def load_teachers(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.teacher_id, t.full_name, t.date_of_birth, t.phone, t.email, 
                    d.dept_id, d.dept_name, deg.degree_id, deg.degree_name, t.teacher_coefficient
                FROM teachers t
                JOIN departments d ON t.dept_id = d.dept_id
                JOIN degrees deg ON t.degree_id = deg.degree_id
            """)
            for item in self.teacher_tree.get_children():
                self.teacher_tree.delete(item)
            rows = cursor.fetchall()
            if not rows:
                messagebox.showwarning("Cảnh báo", "Không có dữ liệu giáo viên")
            departments = self.get_departments()
            degrees = self.get_degrees()
            for row in rows:
                dept_value = next((d for d in departments if d.startswith(row[5])), row[6])
                degree_value = next((d for d in degrees if d.startswith(row[7])), row[8])
                self.teacher_tree.insert("", "end", values=(
                    row[0],
                    row[1],
                    row[2] if row[2] else 'N/A',
                    row[3] if row[3] else 'N/A',
                    row[4] if row[4] else 'N/A',
                    dept_value,
                    degree_value,
                    row[9]
                ))
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu giáo viên: {e}")
        finally:
            cursor.close()
            conn.close()

    def load_stats(self):
        dept_value = self.stats_dept_combobox.get()
        dept_id = None if dept_value in ["Không có khoa", "Lỗi tải khoa"] else dept_value.split(":")[0]

        # Xóa các biểu đồ cũ nếu có
        for frame in [self.stats_tab.winfo_children()[2].winfo_children()[0],
                      self.stats_tab.winfo_children()[2].winfo_children()[1],
                      self.stats_tab.winfo_children()[2].winfo_children()[2]]:
            for item in frame.find_all():
                frame.delete(item)

        # Lấy dữ liệu
        age_labels, age_data = self.get_age_distribution(dept_id)
        dept_labels, dept_data = self.get_dept_distribution(dept_id)
        degree_labels, degree_data = self.get_degree_distribution(dept_id)

        # Biểu đồ độ tuổi (cột)
        if age_labels and age_data:
            CTkLabel(self.stats_tab.winfo_children()[2].winfo_children()[0], text="Phân bố Độ tuổi", font=("Helvetica", 14, "bold")).pack(pady=5)
            chart = {
                "type": "bar",
                "data": {
                    "labels": age_labels,
                    "datasets": [{
                        "label": "Số giáo viên",
                        "data": age_data,
                        "backgroundColor": ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"],
                        "borderColor": ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"],
                        "borderWidth": 1
                    }]
                },
                "options": {
                    "scales": {
                        "y": {
                            "beginAtZero": True,
                            "title": {
                                "display": True,
                                "text": "Số giáo viên"
                            }
                        },
                        "x": {
                            "title": {
                                "display": True,
                                "text": "Nhóm tuổi"
                            }
                        }
                    }
                }
            }
            code_block = f"""
```chartjs
{chart}
```
"""
            self.stats_tab.winfo_children()[2].winfo_children()[0].create_text(10, 50, text=code_block, anchor="nw", font=("Helvetica", 10))

        # Biểu đồ khoa (tròn)
        if dept_labels and dept_data:
            CTkLabel(self.stats_tab.winfo_children()[2].winfo_children()[1], text="Phân bố theo Khoa", font=("Helvetica", 14, "bold")).pack(pady=5)
            chart = {
                "type": "pie",
                "data": {
                    "labels": dept_labels,
                    "datasets": [{
                        "label": "Số giáo viên",
                        "data": dept_data,
                        "backgroundColor": ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"],
                        "borderColor": ["#FFFFFF"] * len(dept_labels),
                        "borderWidth": 1
                    }]
                },
                "options": {
                    "plugins": {
                        "legend": {
                            "position": "top"
                        }
                    }
                }
            }
            code_block = f"""
```chartjs
{chart}
```
"""
            self.stats_tab.winfo_children()[2].winfo_children()[1].create_text(10, 50, text=code_block, anchor="nw", font=("Helvetica", 10))

        # Biểu đồ bằng cấp (cột)
        if degree_labels and degree_data:
            CTkLabel(self.stats_tab.winfo_children()[2].winfo_children()[2], text="Phân bố theo Bằng cấp", font=("Helvetica", 14, "bold")).pack(pady=5)
            chart = {
                "type": "bar",
                "data": {
                    "labels": degree_labels,
                    "datasets": [{
                        "label": "Số giáo viên",
                        "data": degree_data,
                        "backgroundColor": ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"],
                        "borderColor": ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"],
                        "borderWidth": 1
                    }]
                },
                "options": {
                    "scales": {
                        "y": {
                            "beginAtZero": True,
                            "title": {
                                "display": True,
                                "text": "Số giáo viên"
                            }
                        },
                        "x": {
                            "title": {
                                "display": True,
                                "text": "Bằng cấp"
                            }
                        }
                    }
                }
            }
            code_block = f"""
```chartjs
{chart}
```
"""
            self.stats_tab.winfo_children()[2].winfo_children()[2].create_text(10, 50, text=code_block, anchor="nw", font=("Helvetica", 10))

    def add_module(self):
        selected = self.module_tree.selection()
        if selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng reset form trước khi thêm mới!")
            return
        module_name = self.module_name.get().strip()
        coefficient = self.module_coeff.get().strip()
        if not all([module_name, coefficient]):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return
        try:
            coefficient = float(coefficient)
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO course_modules (module_name, coefficient, dept_id) VALUES (%s, %s, %s)",
                           (module_name, coefficient, self.user['dept_id']))
            new_id = cursor.lastrowid
            module_id = f"mod{new_id}"
            cursor.execute("UPDATE course_modules SET module_id = %s WHERE id = %s", (module_id, new_id))
            conn.commit()
            messagebox.showinfo("Thành công", "Thêm học phần thành công")
            self.reset_module_fields()
            self.load_modules()
            self.module_combobox.configure(values=self.get_modules())
        except ValueError:
            messagebox.showerror("Lỗi", "Hệ số phải là số thực")
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể thêm học phần: {e}")
        finally:
            cursor.close()
            conn.close()

    def edit_module(self):
        selected_item = self.module_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn học phần để sửa!")
            return
        item = self.module_tree.item(selected_item)
        module_id = item["values"][0]
        name = self.module_name.get().strip()
        coefficient = self.module_coeff.get().strip()
        if not all([name, coefficient]):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return
        try:
            coefficient = float(coefficient)
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("UPDATE course_modules SET module_name = %s, coefficient = %s WHERE module_id = %s",
                           (name, coefficient, module_id))
            conn.commit()
            messagebox.showinfo("Thành công", "Cập nhật học phần thành công")
            self.reset_module_fields()
            self.load_modules()
            self.module_combobox.configure(values=self.get_modules())
        except ValueError:
            messagebox.showerror("Lỗi", "Hệ số phải là số thực")
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể sửa học phần: {e}")
        finally:
            cursor.close()
            conn.close()

    def delete_module(self):
        selected_item = self.module_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn học phần để xóa!")
            return
        item = self.module_tree.item(selected_item)
        module_id = item["values"][0]
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa học phần này?"):
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM classes WHERE module_id = %s LIMIT 1", (module_id,))
                if cursor.fetchone():
                    messagebox.showerror("Lỗi", "Không thể xóa học phần vì có lớp học liên quan")
                    return
                cursor.execute("DELETE FROM course_modules WHERE module_id = %s", (module_id,))
                conn.commit()
                messagebox.showinfo("Thành công", "Xóa học phần thành công")
                self.reset_module_fields()
                self.load_modules()
                self.module_combobox.configure(values=self.get_modules())
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể xóa học phần: {e}")
            finally:
                cursor.close()
                conn.close()

    def load_modules(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cm.module_id, cm.module_name, cm.coefficient, d.dept_name
                FROM course_modules cm
                JOIN departments d ON cm.dept_id = d.dept_id
                WHERE cm.dept_id = %s
            """, (self.user['dept_id'],))
            for item in self.module_tree.get_children():
                self.module_tree.delete(item)
            rows = cursor.fetchall()
            if not rows:
                messagebox.showwarning("Cảnh báo", "Không có dữ liệu học phần")
            for row in rows:
                self.module_tree.insert("", "end", values=row)
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu học phần: {e}")
        finally:
            cursor.close()
            conn.close()

    def on_module_select(self, event):
        selected_item = self.module_tree.selection()
        if not selected_item:
            return
        item = self.module_tree.item(selected_item)
        self.module_name.delete(0, END)
        self.module_name.insert(0, item["values"][1])
        self.module_name.configure(placeholder_text="")
        self.module_coeff.delete(0, END)
        self.module_coeff.insert(0, item["values"][2])
        self.module_coeff.configure(placeholder_text="")

    def reset_module_fields(self):
        self.module_name.delete(0, END)
        self.module_name.configure(placeholder_text="Tên học phần")
        self.module_coeff.delete(0, END)
        self.module_coeff.configure(placeholder_text="Hệ số (ví dụ: 1.0)")

    def add_class(self):
        selected = self.class_tree.selection()
        if selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng reset form trước khi thêm mới!")
            return
        module = self.module_combobox.get()
        teacher = self.teacher_combobox.get()
        num_students = self.num_students.get().strip()
        actual_periods = self.actual_periods.get().strip()
        semester = self.semester.get().strip()
        if not all([module, teacher, num_students, actual_periods, semester]):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return
        try:
            module_id = module.split(":")[0]
            teacher_id = teacher.split(":")[0]
            num_students = int(num_students)
            actual_periods = int(actual_periods)
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM classes WHERE module_id = %s AND teacher_id = %s AND semester = %s",
                           (module_id, teacher_id, semester))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Lỗi", "Lớp học này đã tồn tại với tổ hợp module, giáo viên và học kỳ!")
                return
            cursor.execute("INSERT INTO classes (module_id, teacher_id, num_students, actual_periods, semester) VALUES (%s, %s, %s, %s, %s)",
                           (module_id, teacher_id, num_students, actual_periods, semester))
            new_id = cursor.lastrowid
            class_id = f"cls{new_id}"
            cursor.execute("UPDATE classes SET class_id = %s WHERE id = %s", (class_id, new_id))
            conn.commit()
            messagebox.showinfo("Thành công", "Thêm lớp học thành công")
            self.reset_class_fields()
            self.load_classes()
        except ValueError:
            messagebox.showerror("Lỗi", "Số sinh viên và số tiết phải là số nguyên")
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể thêm lớp học: {e}")
        finally:
            cursor.close()
            conn.close()

    def edit_class(self):
        selected_item = self.class_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn lớp học để sửa!")
            return
        item = self.class_tree.item(selected_item)
        class_id = item["values"][0]
        module = self.module_combobox.get()
        teacher = self.teacher_combobox.get()
        num_students = self.num_students.get().strip()
        periods = self.actual_periods.get().strip()
        semester = self.semester.get().strip()
        if not all([module, teacher, num_students, periods, semester]):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return
        try:
            module_id = module.split(":")[0]
            teacher_id = teacher.split(":")[0]
            num_students = int(num_students)
            periods = int(periods)
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("UPDATE classes SET module_id = %s, teacher_id = %s, num_students = %s, actual_periods = %s, semester = %s WHERE class_id = %s",
                           (module_id, teacher_id, num_students, periods, semester, class_id))
            conn.commit()
            messagebox.showinfo("Thành công", "Cập nhật lớp học thành công")
            self.reset_class_fields()
            self.load_classes()
        except ValueError:
            messagebox.showerror("Lỗi", "Số sinh viên và số tiết phải là số nguyên")
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể sửa lớp học: {e}")
        finally:
            cursor.close()
            conn.close()

    def delete_class(self):
        selected_item = self.class_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn lớp học để xóa!")
            return
        item = self.class_tree.item(selected_item)
        class_id = item["values"][0]
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa lớp học này?"):
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM salaries WHERE class_id = %s LIMIT 1", (class_id,))
                if cursor.fetchone():
                    messagebox.showerror("Lỗi", "Không thể xóa lớp học vì có lương liên quan")
                    return
                cursor.execute("DELETE FROM classes WHERE class_id = %s", (class_id,))
                conn.commit()
                messagebox.showinfo("Thành công", "Xóa lớp học thành công")
                self.reset_class_fields()
                self.load_classes()
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể xóa lớp học: {e}")
            finally:
                cursor.close()
                conn.close()

    def load_classes(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.class_id, cm.module_name, t.full_name, c.num_students, c.actual_periods, c.semester
                FROM classes c
                JOIN course_modules cm ON c.module_id = cm.module_id
                JOIN teachers t ON c.teacher_id = t.teacher_id
                WHERE cm.dept_id = %s
            """, (self.user['dept_id'],))
            for item in self.class_tree.get_children():
                self.class_tree.delete(item)
            rows = cursor.fetchall()
            if not rows:
                messagebox.showwarning("Cảnh báo", "Không có dữ liệu lớp học")
            for row in rows:
                self.class_tree.insert("", "end", values=row)
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu lớp học: {e}")
        finally:
            cursor.close()
            conn.close()

    def on_class_select(self, event):
        selected_item = self.class_tree.selection()
        if not selected_item:
            return
        item = self.class_tree.item(selected_item)
        self.module_combobox.set(item["values"][1])
        self.teacher_combobox.set(item["values"][2])
        self.num_students.delete(0, END)
        self.num_students.insert(0, item["values"][3])
        self.num_students.configure(placeholder_text="")
        self.actual_periods.delete(0, END)
        self.actual_periods.insert(0, item["values"][4])
        self.actual_periods.configure(placeholder_text="")
        self.semester.delete(0, END)
        self.semester.insert(0, item["values"][5])
        self.semester.configure(placeholder_text="")

    def reset_class_fields(self):
        self.module_combobox.set(self.get_modules()[0] if self.get_modules() else "")
        self.teacher_combobox.set(self.get_teachers()[0] if self.get_teachers() else "")
        self.num_students.delete(0, END)
        self.num_students.configure(placeholder_text="Số sinh viên")
        self.actual_periods.delete(0, END)
        self.actual_periods.configure(placeholder_text="Số tiết")
        self.semester.delete(0, END)
        self.semester.configure(placeholder_text="Học kỳ (ví dụ: 2025-1)")

    def load_salaries(self):
        try:
            teacher = self.salary_teacher_combobox.get()
            semester = self.salary_semester.get().strip()
            teacher_id = teacher.split(":")[0] if teacher and teacher != "Không có giáo viên" and teacher != "Lỗi tải giáo viên" else None
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            query = """
                SELECT t.full_name, cm.module_name, s.salary_amount, s.semester, s.calculated_at
                FROM salaries s
                JOIN teachers t ON s.teacher_id = t.teacher_id
                JOIN classes c ON s.class_id = c.class_id
                JOIN course_modules cm ON c.module_id = cm.module_id
                WHERE t.dept_id = %s
            """
            params = [self.user['dept_id']]
            if teacher_id:
                query += " AND s.teacher_id = %s"
                params.append(teacher_id)
            if semester:
                query += " AND s.semester = %s"
                params.append(semester)
            cursor.execute(query, params)
            for item in self.salary_tree.get_children():
                self.salary_tree.delete(item)
            rows = cursor.fetchall()
            if not rows:
                messagebox.showwarning("Cảnh báo", "Không có dữ liệu lương")
            for row in rows:
                self.salary_tree.insert("", "end", values=row)
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu lương: {e}")
        finally:
            cursor.close()
            conn.close()

    def reset_salary_fields(self):
        self.salary_teacher_combobox.set(self.get_teachers()[0] if self.get_teachers() else "")
        self.salary_semester.delete(0, END)
        self.salary_semester.configure(placeholder_text="Học kỳ (ví dụ: 2025-1)")

    def logout(self):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn đăng xuất?"):
            self.window.destroy()

            import os
            os.system("python login_view.py")



    def reset_teacher_fields(self):
        self.teacher_name.delete(0, END)
        self.teacher_name.configure(placeholder_text="Họ tên")
        self.date_of_birth.delete(0, END)
        self.date_of_birth.configure(placeholder_text="Ngày sinh (YYYY-MM-DD)")
        self.phone.delete(0, END)
        self.phone.configure(placeholder_text="Điện thoại")
        self.email.delete(0, END)
        self.email.configure(placeholder_text="Email")
    

    def get_age_distribution(self):
        """Lấy phân bố độ tuổi của giáo viên."""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            current_year = datetime.now().year
            query = """
                SELECT YEAR(date_of_birth) 
                FROM teachers 
                WHERE date_of_birth IS NOT NULL
            """
            cursor.execute(query)
            ages = []
            for row in cursor.fetchall():
                birth_year = row[0]
                if birth_year:
                    age = current_year - birth_year
                    ages.append(age)

            # Phân nhóm tuổi
            bins = [20, 30, 40, 50, 60, 100]  # Nhóm tuổi: 20-30, 30-40, 40-50, 50-60, 60+
            labels = ["20-30", "30-40", "40-50", "50-60", "60+"]
            distribution = [0] * (len(bins) - 1)
            for age in ages:
                for i in range(len(bins) - 1):
                    if bins[i] <= age < bins[i + 1]:
                        distribution[i] += 1
                        break

            return labels, distribution
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu độ tuổi: {e}")
            return [], []
        finally:
            cursor.close()
            conn.close()

    def get_dept_distribution(self):
        """Lấy phân bố giáo viên theo khoa."""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            query = """
                SELECT d.dept_name, COUNT(t.teacher_id) 
                FROM departments d 
                LEFT JOIN teachers t ON d.dept_id = t.dept_id
                GROUP BY d.dept_id, d.dept_name
            """
            cursor.execute(query)
            labels = []
            data = []
            for row in cursor.fetchall():
                dept_name, count = row
                labels.append(dept_name)
                data.append(count)

            return labels, data
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu khoa: {e}")
            return [], []
        finally:
            cursor.close()
            conn.close()

    def get_degree_distribution(self):
        """Lấy phân bố giáo viên theo bằng cấp."""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            query = """
                SELECT d.degree_name, COUNT(t.teacher_id) 
                FROM degrees d 
                LEFT JOIN teachers t ON d.degree_id = t.degree_id
                GROUP BY d.degree_id, d.degree_name
            """
            cursor.execute(query)
            labels = []
            data = []
            for row in cursor.fetchall():
                degree_name, count = row
                labels.append(degree_name)
                data.append(count)

            return labels, data
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu bằng cấp: {e}")
            return [], []
        finally:
            cursor.close()
            conn.close()