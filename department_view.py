from customtkinter import *
from tkinter import ttk, messagebox, END
import mysql.connector
from db_config import DB_CONFIG
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import random
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkComboBox
import re
from tkcalendar import DateEntry
from tkcalendar import Calendar
from customtkinter import CTk, CTkFrame, CTkLabel, CTkButton, CTkComboBox, CTkEntry, CTkToplevel
from PIL import Image, ImageTk


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

        style = ttk.Style()
        style.configure("Treeview", 
                        font=("Helvetica", 10),  # Font đồng bộ cho nội dung
                        rowheight=20,           # Chiều cao hàng phù hợp
                        background="#FFFFFF", 
                        foreground="black", 
                        fieldbackground="#F0F0F0")
        style.configure("Treeview.Heading", 
                        font=("Helvetica", 10, "bold"),  # Font đồng bộ cho tiêu đề
                        background="#D3D3D3", 
                        foreground="black")

        # Frame chính với gradient nền
        self.main_frame = CTkFrame(self.window, fg_color=("#E6F0FA", "#B0C4DE"))
        self.main_frame.pack(fill="both", expand=True)

        # Cấu hình style cho tiêu đề bảng (in đậm)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

        # Sidebar
        self.sidebar = CTkFrame(self.main_frame, width=250, fg_color="#1E3A8A")
        self.sidebar.pack(side="left", fill="y")

        # Thêm logo ở vị trí cao nhất
        try:
            logo_image = Image.open("logo.png")  # Giả định logo.png nằm trong thư mục dự án
            logo_image = logo_image.resize((150, 50), Image.Resampling.LANCZOS)  # Điều chỉnh kích thước logo
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            self.logo = CTkLabel(self.sidebar, image=CTkImage(light_image=logo_image, dark_image=logo_image, size=(115,75)), text="")
            self.logo.pack(pady=(10, 15))  # Tăng pady để tạo khoảng cách với mép trên và mục chính bên dưới
        except Exception as e:
            # Nếu không tìm thấy logo, hiển thị placeholder
            CTkLabel(self.sidebar, text="[Logo Placeholder]", font=("Helvetica", 14, "italic"), text_color="white").pack(pady=(10, 15))

        # Dictionary để theo dõi trạng thái hiển thị của các tab con
        self.submenu_visible = {
            "Quản lý thông tin giáo viên": False,
            "Quản lý lớp học phần": False,
            "Thống kê": False
        }

        # Dictionary để lưu các button của tab con
        self.submenu_buttons = {
            "Quản lý thông tin giáo viên": [],
            "Quản lý lớp học phần": [],
            "Thống kê": []
        }

        # Dictionary để lưu các frame chứa tab con
        self.submenu_frames = {
            "Quản lý thông tin giáo viên": None,
            "Quản lý lớp học phần": None,
            "Thống kê": None
        }

        # Dictionary để ánh xạ mục chính với các tab con
        self.submenu_items = {
            "Quản lý thông tin giáo viên": ["Bằng cấp", "Khoa", "Giáo viên"],
            "Quản lý lớp học phần": ["Học phần", "Kỳ học", "Lớp học", "Phân công"],
            "Thống kê": ["Thống kê giáo viên", "Thống kê lớp"]
        }

        # Menu sidebar với cơ chế drop down
        # Mục chính: Quản lý thông tin giáo viên
        self.teacher_info_button = CTkButton(self.sidebar, text="▶ Quản lý thông tin giáo viên", font=("Helvetica", 18, "bold"), fg_color="#2A4B8D",
                                        text_color="white", hover_color="#4A78E0",
                                        command=lambda: self.toggle_submenu("Quản lý thông tin giáo viên"))
        self.teacher_info_button.pack(pady=(15, 0), padx=10, fill="x")
        self.submenu_frames["Quản lý thông tin giáo viên"] = CTkFrame(self.sidebar, fg_color="transparent", height=0)
        self.submenu_frames["Quản lý thông tin giáo viên"].pack(pady=0, padx=10, fill="x")

        # Mục chính: Quản lý lớp học phần
        self.class_management_button = CTkButton(self.sidebar, text="▶ Quản lý lớp học phần", font=("Helvetica", 18, "bold"), fg_color="#2A4B8D",
                                                text_color="white", hover_color="#4A78E0",
                                                command=lambda: self.toggle_submenu("Quản lý lớp học phần"))
        self.class_management_button.pack(pady=(15, 0), padx=10, fill="x")
        self.submenu_frames["Quản lý lớp học phần"] = CTkFrame(self.sidebar, fg_color="transparent", height=0)
        self.submenu_frames["Quản lý lớp học phần"].pack(pady=0, padx=10, fill="x")

        # Mục chính: Thống kê
        self.stats_button = CTkButton(self.sidebar, text="▶ Thống kê", font=("Helvetica", 18, "bold"), fg_color="#2A4B8D",
                                    text_color="white", hover_color="#4A78E0",
                                    command=lambda: self.toggle_submenu("Thống kê"))
        self.stats_button.pack(pady=(15, 0), padx=10, fill="x")
        self.submenu_frames["Thống kê"] = CTkFrame(self.sidebar, fg_color="transparent", height=0)
        self.submenu_frames["Thống kê"].pack(pady=0, padx=10, fill="x")

        # Mục chính: Lương (không có tab con)
        CTkButton(self.sidebar, text="Lương", font=("Helvetica", 18, "bold"), fg_color="#2A4B8D",
                text_color="white", hover_color="#4A78E0",
                command=lambda: self.switch_tab("Lương")).pack(pady=(15, 0), padx=10, fill="x")

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

        # Tab Kỳ học
        self.semester_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.setup_semester_tab()

        # Tab Phân công giảng viên
        self.assignment_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.setup_assignment_tab()

        # Tab Thống kê số lớp
        self.class_stats_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.setup_class_stats_tab()

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

    from tkcalendar import DateEntry

    def setup_semester_tab(self):
        # Tiêu đề tab
        CTkLabel(self.semester_tab, text="Kỳ học", font=("Helvetica", 18, "bold"), text_color="black").pack(pady=10)
        main_frame = CTkFrame(self.semester_tab, fg_color="transparent")
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Form chỉnh sửa kỳ học (bên trái) - thu hẹp chiều ngang
        form_frame = CTkFrame(main_frame, fg_color="#F0F0F0", corner_radius=10, width=250)
        form_frame.pack(side="left", padx=5, pady=10, fill="y")
        form_frame.pack_propagate(False)
        CTkLabel(form_frame, text="Quản lý Kỳ học", font=("Helvetica", 16, "bold")).pack(pady=5)

        # Combobox cho tên kỳ học
        CTkLabel(form_frame, text="Tên kỳ học:", font=("Helvetica", 11)).pack(pady=(5, 0), padx=10)
        self.semester_name = CTkComboBox(
            form_frame,
            values=["Học kỳ 1", "Học kỳ 2", "Học kỳ 3"],
            width=200,
            height=32,
            font=("Helvetica", 11),
            fg_color="#E0E0E0",
            text_color="black",
            border_color="#4A4A4A",
            border_width=2,
            button_color="#4A4A4A",
            button_hover_color="#666666",
            dropdown_fg_color="#E0E0E0",
            dropdown_text_color="black",
            dropdown_hover_color="#A0A0A0"
        )
        self.semester_name.pack(pady=5, padx=(10, 10), fill="x")
        self.semester_name.set("Học kỳ 1")

        # Combobox cho năm học
        CTkLabel(form_frame, text="Năm học:", font=("Helvetica", 11)).pack(pady=(5, 0), padx=10)
        self.semester_year = CTkComboBox(
            form_frame,
            values=self.get_academic_years(),
            width=200,
            height=32,
            font=("Helvetica", 11),
            fg_color="#E0E0E0",
            text_color="black",
            border_color="#4A4A4A",
            border_width=2,
            button_color="#4A4A4A",
            button_hover_color="#666666",
            dropdown_fg_color="#E0E0E0",
            dropdown_text_color="black",
            dropdown_hover_color="#A0A0A0"
        )
        self.semester_year.pack(pady=5, padx=(10, 10), fill="x")
        self.semester_year.set("2025-2026")

        # Ngày bắt đầu: Sử dụng CTkEntry với nút lịch
        CTkLabel(form_frame, text="Ngày bắt đầu:", font=("Helvetica", 11)).pack(pady=(5, 0), padx=10)
        date_frame_start = CTkFrame(form_frame, fg_color="transparent")
        date_frame_start.pack(pady=5, padx=(10, 10), fill="x")  # Đồng bộ padx với các ô phía trên

        # Tạo frame con để chứa ô nhập liệu và nút lịch
        inner_frame_start = CTkFrame(date_frame_start, fg_color="transparent")
        inner_frame_start.pack(side="right")  # Dịch sang phải

        # Nút lịch cho Ngày bắt đầu
        calendar_button_start = CTkButton(
            inner_frame_start,
            text="📅",
            width=30,
            height=32,
            fg_color="#4A4A4A",
            hover_color="#666666",
            command=lambda: self.open_calendar(self.start_date)
        )
        calendar_button_start.pack(side="right")

        # Ô nhập liệu Ngày bắt đầu
        self.start_date = CTkEntry(
            inner_frame_start,
            placeholder_text="YYYY-MM-DD",
            placeholder_text_color="#666666",
            width=200,
            height=32,
            font=("Helvetica", 11),
            fg_color="#E0E0E0",
            text_color="black",
            border_color="#4A4A4A",
            border_width=2,
            corner_radius=5
        )
        self.start_date.pack(side="right", padx=(0, 5))
        self.start_date.insert(0, "2025-01-01")

        # Ngày kết thúc: Sử dụng CTkEntry với nút lịch
        CTkLabel(form_frame, text="Ngày kết thúc:", font=("Helvetica", 11)).pack(pady=(5, 0), padx=10)
        date_frame_end = CTkFrame(form_frame, fg_color="transparent")
        date_frame_end.pack(pady=5, padx=(10, 10), fill="x")

        # Tạo frame con để chứa ô nhập liệu và nút lịch
        inner_frame_end = CTkFrame(date_frame_end, fg_color="transparent")
        inner_frame_end.pack(side="right")

        # Nút lịch cho Ngày kết thúc
        calendar_button_end = CTkButton(
            inner_frame_end,
            text="📅",
            width=30,
            height=32,
            fg_color="#4A4A4A",
            hover_color="#666666",
            command=lambda: self.open_calendar(self.end_date)
        )
        calendar_button_end.pack(side="right")

        # Ô nhập liệu Ngày kết thúc
        self.end_date = CTkEntry(
            inner_frame_end,
            placeholder_text="YYYY-MM-DD",
            placeholder_text_color="#666666",
            width=200,
            height=32,
            font=("Helvetica", 11),
            fg_color="#E0E0E0",
            text_color="black",
            border_color="#4A4A4A",
            border_width=2,
            corner_radius=5
        )
        self.end_date.pack(side="right", padx=(0, 5))
        self.end_date.insert(0, "2025-12-31")

        # Gán sự kiện cho combobox Năm học
        self.semester_year.bind("<<ComboboxSelected>>", self.update_date_years)

        # Cập nhật giá trị ban đầu
        self.update_date_years()

        # Các nút chức năng
        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        CTkButton(button_frame, text="Thêm", fg_color="#0085FF", command=self.add_semester, width=50).pack(side="left", padx=3)
        CTkButton(button_frame, text="Sửa", fg_color="#FFC107", command=self.edit_semester, width=50).pack(side="left", padx=3)
        CTkButton(button_frame, text="Xóa", fg_color="#F44336", command=self.delete_semester, width=50).pack(side="left", padx=3)
        CTkButton(button_frame, text="Reset", fg_color="#6C757D", command=self.reset_semester_fields, width=50).pack(side="left", padx=3)

        # Bảng kỳ học (bên phải)
        table_frame = CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=10)
        table_frame.pack(side="right", padx=10, pady=10, fill="both", expand=True)
        self.semester_tree = ttk.Treeview(table_frame, columns=("ID", "Name", "Year", "Start Date", "End Date"), show="headings")

        self.semester_tree.heading("ID", text="Mã kỳ")
        self.semester_tree.heading("Name", text="Tên kỳ")
        self.semester_tree.heading("Year", text="Năm học")
        self.semester_tree.heading("Start Date", text="Ngày bắt đầu")
        self.semester_tree.heading("End Date", text="Ngày kết thúc")
        self.semester_tree.column("ID", width=80, anchor="center")
        self.semester_tree.column("Name", width=120, anchor="center")
        self.semester_tree.column("Year", width=80, anchor="center")
        self.semester_tree.column("Start Date", width=100, anchor="center")
        self.semester_tree.column("End Date", width=100, anchor="center")
        self.semester_tree.pack(padx=10, pady=10, fill="both", expand=True)
        self.semester_tree.bind("<<TreeviewSelect>>", self.on_semester_select)
        self.load_semesters()


    
    def setup_assignment_tab(self):
        CTkLabel(self.assignment_tab, text="Phân công giảng viên", font=("Helvetica", 18, "bold"), text_color="black").pack(pady=10)
        main_frame = CTkFrame(self.assignment_tab, fg_color="transparent")
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Form nhập liệu (bên trái)
        form_frame = CTkFrame(main_frame, fg_color="#F0F0F0", corner_radius=10)
        form_frame.pack(side="left", padx=5, pady=10, fill="y")
        CTkLabel(form_frame, text="Quản lý Phân công", font=("Helvetica", 16, "bold")).pack(pady=5)

        # Kỳ học
        CTkLabel(form_frame, text="Chọn kỳ học:", font=("Helvetica", 12)).pack(pady=(5, 0))
        self.assignment_semester_combobox = CTkComboBox(form_frame, width=150, values=self.get_semesters(), command=self.load_classes_by_semester)
        self.assignment_semester_combobox.pack(pady=5)
        self.assignment_semester_combobox.set(self.get_semesters()[0] if self.get_semesters() else "")

        # Bộ lọc học phần
        CTkLabel(form_frame, text="Lọc học phần:", font=("Helvetica", 12)).pack(pady=(5, 0))
        self.assignment_module_combobox = CTkComboBox(form_frame, width=150, values=["Tất cả"] + [module.split(":")[1].strip() for module in self.get_modules()], command=self.load_classes_by_semester)
        self.assignment_module_combobox.pack(pady=5)
        self.assignment_module_combobox.set("Tất cả")

        # Các nút thao tác
        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=5)
        self.assign_button = CTkButton(button_frame, text="Phân công", fg_color="#0085FF", command=self.assign_teacher, width=70, font=("Helvetica", 12), state="disabled")
        self.assign_button.pack(side="left", padx=5)
        self.edit_button = CTkButton(button_frame, text="Sửa", fg_color="#FFC107", command=self.edit_assignment, width=70, font=("Helvetica", 12), state="disabled")
        self.edit_button.pack(side="left", padx=5)
        self.delete_button = CTkButton(button_frame, text="Xóa", fg_color="#F44336", command=self.delete_assignment, width=70, font=("Helvetica", 12), state="disabled")
        self.delete_button.pack(side="left", padx=5)
        self.reset_button = CTkButton(button_frame, text="Reset", fg_color="#6C757D", command=self.reset_assignment_fields, width=70, font=("Helvetica", 12), state="disabled")
        self.reset_button.pack(side="left", padx=5)

        # Bảng lớp học phần (bên phải)
        table_frame = CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=10)
        table_frame.pack(side="right", padx=10, pady=10, fill="both", expand=True)
        self.assignment_tree = ttk.Treeview(table_frame, columns=("Semester", "Module", "ID", "Name", "Students", "Teacher"), show="headings")
        self.assignment_tree.heading("Semester", text="Kỳ học")
        self.assignment_tree.heading("Module", text="Học phần")
        self.assignment_tree.heading("ID", text="Mã lớp")
        self.assignment_tree.heading("Name", text="Tên lớp")
        self.assignment_tree.heading("Students", text="Số sinh viên")
        self.assignment_tree.heading("Teacher", text="Giáo viên")
        self.assignment_tree.column("Semester", width=150, anchor="center")
        self.assignment_tree.column("Module", width=200, anchor="center")
        self.assignment_tree.column("ID", width=150, anchor="center")
        self.assignment_tree.column("Name", width=200, anchor="center")
        self.assignment_tree.column("Students", width=150, anchor="center")
        self.assignment_tree.column("Teacher", width=200, anchor="center")
        self.assignment_tree.pack(padx=10, pady=10, fill="both", expand=True)
        self.assignment_tree.bind("<<TreeviewSelect>>", self.on_assignment_select)
        self.load_classes_by_semester(None)  # Tải danh sách lớp học phần khi khởi tạo

    def setup_class_stats_tab(self):
        CTkLabel(self.class_stats_tab, text="Thống kê lớp học phần", font=("Helvetica", 18, "bold"), text_color="black").pack(pady=10)

        # Frame chứa bộ lọc
        filter_frame = CTkFrame(self.class_stats_tab, fg_color="#F0F0F0", corner_radius=10)
        filter_frame.pack(padx=10, pady=10, fill="x")
        CTkLabel(filter_frame, text="Chọn năm học:", font=("Helvetica", 14)).pack(side="left", padx=5)
        self.stats_year_combobox = CTkComboBox(filter_frame, width=200, values=self.get_academic_years())
        self.stats_year_combobox.pack(side="left", padx=5)
        self.stats_year_combobox.set("2025-2026")

        # Frame chứa các nút (gộp tất cả nút vào một hàng)
        stats_button_frame = CTkFrame(self.class_stats_tab, fg_color="transparent")
        stats_button_frame.pack(pady=5)
        CTkButton(stats_button_frame, text="Thống kê theo bảng", fg_color="#0085FF", command=self.show_class_stats_table).pack(side="left", padx=5)
        CTkButton(stats_button_frame, text="Thống kê theo biểu đồ", fg_color="#FF6384", command=self.show_class_stats_chart).pack(side="left", padx=5)
        CTkButton(stats_button_frame, text="Xuất Excel", fg_color="#36A2EB", command=self.export_excel).pack(side="left", padx=5)

        # Frame chứa nội dung (biểu đồ hoặc bảng)
        self.class_stats_frame = CTkFrame(self.class_stats_tab, fg_color="#FFFFFF", corner_radius=10)
        self.class_stats_frame.pack(padx=10, pady=10, fill="both", expand=True)

    def setup_module_tab(self):
        CTkLabel(self.module_tab, text="Học phần", font=("Helvetica", 18, "bold"), text_color="black").pack(pady=10)
        main_frame = CTkFrame(self.module_tab, fg_color="transparent")
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Form chỉnh sửa học phần
        form_frame = CTkFrame(main_frame, fg_color="#F0F0F0", corner_radius=10)
        form_frame.pack(side="left", padx=10, pady=10, fill="y")
        CTkLabel(form_frame, text="Quản lý Học phần", font=("Helvetica", 16, "bold")).pack(pady=5)

        # Tên học phần
        self.module_name = CTkEntry(form_frame, placeholder_text="Tên học phần", width=200)
        self.module_name.pack(pady=5)

        # Số tín chỉ
        self.module_credits = CTkEntry(form_frame, placeholder_text="Số tín chỉ", width=200)
        self.module_credits.pack(pady=5)

        # Hệ số học phần
        self.module_coefficient = CTkEntry(form_frame, placeholder_text="Hệ số (ví dụ: 1.5)", width=200)
        self.module_coefficient.pack(pady=5)

        # Số tiết
        self.module_periods = CTkEntry(form_frame, placeholder_text="Số tiết", width=200)
        self.module_periods.pack(pady=5)

        # Các nút chức năng
        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        CTkButton(button_frame, text="Thêm", fg_color="#0085FF", command=self.add_module).pack(side="left", padx=5)
        CTkButton(button_frame, text="Sửa", fg_color="#FFC107", command=self.edit_module).pack(side="left", padx=5)
        CTkButton(button_frame, text="Xóa", fg_color="#F44336", command=self.delete_module).pack(side="left", padx=5)
        CTkButton(button_frame, text="Reset", fg_color="#6C757D", command=self.reset_module_fields).pack(side="left", padx=5)

        # Bảng học phần
        table_frame = CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=10)
        table_frame.pack(side="right", padx=10, pady=10, fill="both", expand=True)
        self.module_tree = ttk.Treeview(table_frame, columns=("ID", "Name", "Credits", "Coefficient", "Periods"), show="headings")
        self.module_tree.heading("ID", text="Mã số")
        self.module_tree.heading("Name", text="Tên học phần")
        self.module_tree.heading("Credits", text="Số tín chỉ")
        self.module_tree.heading("Coefficient", text="Hệ số học phần")
        self.module_tree.heading("Periods", text="Số tiết")
        self.module_tree.column("ID", width=100, anchor="center")
        self.module_tree.column("Name", width=200, anchor="center")
        self.module_tree.column("Credits", width=100, anchor="center")
        self.module_tree.column("Coefficient", width=100, anchor="center")
        self.module_tree.column("Periods", width=100, anchor="center")
        self.module_tree.pack(padx=10, pady=10, fill="both", expand=True)
        self.module_tree.bind("<<TreeviewSelect>>", self.on_module_select)
        self.load_modules()

    def setup_class_tab(self):
        CTkLabel(self.class_tab, text="Lớp học", font=("Helvetica", 18, "bold"), text_color="black").pack(pady=10)
        main_frame = CTkFrame(self.class_tab, fg_color="transparent")
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Form chỉnh sửa lớp học (bên trái) - điều chỉnh giống tab Giáo viên
        form_frame = CTkFrame(main_frame, fg_color="#F0F0F0", corner_radius=10)
        form_frame.pack(side="left", padx=5, pady=10, fill="y")
        CTkLabel(form_frame, text="Quản lý Lớp học", font=("Helvetica", 16, "bold")).pack(pady=5)

        # Kỳ học
        self.class_semester = CTkComboBox(form_frame, width=150, values=self.get_semesters())  # Đặt width=150 giống tab Giáo viên
        self.class_semester.pack(pady=5)
        self.class_semester.set(self.get_semesters()[0] if self.get_semesters() else "")

        # Học phần
        self.class_module = CTkComboBox(form_frame, width=150, values=self.get_modules())
        self.class_module.pack(pady=5)
        self.class_module.set(self.get_modules()[0] if self.get_modules() else "")

        # Số lượng lớp tạo
        self.class_count = CTkComboBox(form_frame, width=150, values=[str(i) for i in range(1, 9)])
        self.class_count.pack(pady=5)
        self.class_count.set("1")

        # Số sinh viên
        self.class_size = CTkEntry(form_frame, placeholder_text="Số sinh viên", width=150)
        self.class_size.pack(pady=5)

        # Các nút chức năng
        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=5)  # Giảm padding để giống tab Giáo viên
        CTkButton(button_frame, text="Thêm", fg_color="#0085FF", command=self.add_class, width=70, font=("Helvetica", 12)).pack(side="left", padx=2)
        CTkButton(button_frame, text=" Sửa", fg_color="#FFC107", command=self.edit_class, width=70, font=("Helvetica", 12)).pack(side="left", padx=2)
        CTkButton(button_frame, text="Xóa", fg_color="#F44336", command=self.delete_class, width=70, font=("Helvetica", 12)).pack(side="left", padx=2)
        CTkButton(button_frame, text="Reset", fg_color="#6C757D", command=self.reset_class_fields, width=70, font=("Helvetica", 12)).pack(side="left", padx=2)

        # Bảng lớp học (bên phải) - mở rộng và điều chỉnh cột
        table_frame = CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=10)
        table_frame.pack(side="right", padx=10, pady=10, fill="both", expand=True)
        self.class_tree = ttk.Treeview(table_frame, columns=("Semester", "Module", "ID", "Name", "Students"), show="headings")
        self.class_tree.heading("Semester", text="Thuộc kỳ")
        self.class_tree.heading("Module", text="Thuộc học phần")
        self.class_tree.heading("ID", text="Mã lớp")
        self.class_tree.heading("Name", text="Tên lớp")
        self.class_tree.heading("Students", text="Số sinh viên")
        self.class_tree.column("Semester", width=200, anchor="center")  # Tăng chiều rộng để tận dụng không gian
        self.class_tree.column("Module", width=250, anchor="center")
        self.class_tree.column("ID", width=150, anchor="center")
        self.class_tree.column("Name", width=300, anchor="center")
        self.class_tree.column("Students", width=150, anchor="center")
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
        elif tab_name == "Học phần":
            self.current_tab = self.module_tab
        elif tab_name == "Kỳ học":
            self.current_tab = self.semester_tab
        elif tab_name == "Lớp học":
            self.current_tab = self.class_tab
        elif tab_name == "Phân công":
            self.current_tab = self.assignment_tab
        elif tab_name == "Thống kê giáo viên":
            self.current_tab = self.stats_tab
        elif tab_name == "Thống kê lớp":
            self.current_tab = self.class_stats_tab
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
            cursor.execute("SELECT teacher_id, full_name FROM teachers")
            teachers = [f"{row[0]}: {row[1]}" for row in cursor.fetchall()]
            if not teachers:
                messagebox.showwarning("Cảnh báo", "Không có giáo viên nào trong hệ thống!")
                return ["Không có giáo viên"]
            return teachers
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
            cursor.execute("SELECT module_id, module_name FROM course_modules")
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
        teacher_name = item["values"][1]

        # Kiểm tra xem giáo viên có liên quan đến phân công không
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT assignment_id, class_id FROM assignments WHERE teacher_id = %s", (teacher_id,))
            assignments = cursor.fetchall()
            
            # Nếu có phân công, kiểm tra xem có lương liên quan không
            if assignments:
                class_ids = [assignment[1] for assignment in assignments]  # Lấy danh sách class_id
                cursor.execute("SELECT class_id FROM salaries WHERE class_id IN (%s)" % ','.join(['%s'] * len(class_ids)), class_ids)
                salary_classes = cursor.fetchall()
                
                if salary_classes:
                    # Có lương liên quan, hỏi người dùng có muốn xóa tất cả không
                    if messagebox.askyesno("Xác nhận", f"Giáo viên '{teacher_name}' có phân công và lương liên quan. Xóa giáo viên sẽ xóa cả phân công và lương. Bạn có chắc muốn tiếp tục?"):
                        # Xóa lương
                        cursor.execute("DELETE FROM salaries WHERE class_id IN (%s)" % ','.join(['%s'] * len(class_ids)), class_ids)
                        # Xóa phân công
                        cursor.execute("DELETE FROM assignments WHERE teacher_id = %s", (teacher_id,))
                        conn.commit()
                    else:
                        return
                else:
                    # Có phân công nhưng không có lương, chỉ cần xóa phân công
                    if messagebox.askyesno("Xác nhận", f"Giáo viên '{teacher_name}' có phân công liên quan. Xóa giáo viên sẽ xóa cả phân công. Bạn có chắc muốn tiếp tục?"):
                        cursor.execute("DELETE FROM assignments WHERE teacher_id = %s", (teacher_id,))
                        conn.commit()
                    else:
                        return
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể kiểm tra ràng buộc: {e}")
            return
        finally:
            cursor.close()
            conn.close()

        # Xóa giáo viên
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa giáo viên '{teacher_name}'?"):
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE user_id = %s", (teacher_id,))
                cursor.execute("DELETE FROM teachers WHERE teacher_id = %s", (teacher_id,))
                conn.commit()
                messagebox.showinfo("Thành công", f"Xóa giáo viên '{teacher_name}' thành công")
                self.reset_teacher_fields()
                self.load_teachers()
                # Chỉ cập nhật salary_teacher_combobox (trong tab Lương)
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

        name = self.module_name.get().strip()
        credits = self.module_credits.get().strip()
        coefficient = self.module_coefficient.get().strip()
        periods = self.module_periods.get().strip()

        if not all([name, credits, coefficient, periods]):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return

        try:
            credits = int(credits)
            if credits <= 0:
                messagebox.showerror("Lỗi", "Số tín chỉ phải là số nguyên dương!")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Số tín chỉ phải là số nguyên!")
            return

        try:
            coefficient = float(coefficient)
            if coefficient <= 0:
                messagebox.showerror("Lỗi", "Hệ số học phần phải lớn hơn 0!")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Hệ số học phần phải là số thực!")
            return

        try:
            periods = int(periods)
            if periods <= 0:
                messagebox.showerror("Lỗi", "Số tiết phải là số nguyên dương!")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Số tiết phải là số nguyên!")
            return

        # Kiểm tra trùng tên học phần
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT module_id FROM course_modules WHERE module_name = %s", (name,))
            if cursor.fetchone():
                messagebox.showerror("Lỗi", "Tên học phần đã tồn tại. Vui lòng chọn tên khác!")
                return
            cursor.fetchall()  # Đọc hết kết quả để tránh lỗi Unread result
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể kiểm tra trùng lặp: {e}")
            return
        finally:
            cursor.close()
            conn.close()

        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn thêm học phần này?")
        if not confirm:
            return

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            # Tạo mã số ngẫu nhiên MODxxxxx
            while True:
                random_num = random.randint(0, 99999)
                module_id = f"MOD{str(random_num).zfill(5)}"
                cursor.execute("SELECT module_id FROM course_modules WHERE module_id = %s", (module_id,))
                if not cursor.fetchone():
                    cursor.fetchall()  # Đọc hết kết quả để tránh lỗi Unread result
                    break

            cursor.execute("INSERT INTO course_modules (module_id, module_name, credits, coefficient, periods) VALUES (%s, %s, %s, %s, %s)",
                        (module_id, name, credits, coefficient, periods))
            conn.commit()
            messagebox.showinfo("Thành công", f"Thêm học phần thành công với mã số {module_id}")
            self.reset_module_fields()
            self.load_modules()
            # Cập nhật combobox ở các tab khác nếu cần
            if hasattr(self, 'module_combobox'):
                self.module_combobox.configure(values=self.get_modules())
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
        credits = self.module_credits.get().strip()
        coefficient = self.module_coefficient.get().strip()
        periods = self.module_periods.get().strip()

        if not all([name, credits, coefficient, periods]):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return

        try:
            credits = int(credits)
            if credits <= 0:
                messagebox.showerror("Lỗi", "Số tín chỉ phải là số nguyên dương!")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Số tín chỉ phải là số nguyên!")
            return

        try:
            coefficient = float(coefficient)
            if coefficient <= 0:
                messagebox.showerror("Lỗi", "Hệ số học phần phải lớn hơn 0!")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Hệ số học phần phải là số thực!")
            return

        try:
            periods = int(periods)
            if periods <= 0:
                messagebox.showerror("Lỗi", "Số tiết phải là số nguyên dương!")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Số tiết phải là số nguyên!")
            return

        # Kiểm tra trùng tên học phần (ngoại trừ chính học phần đang sửa)
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT module_id FROM course_modules WHERE module_name = %s AND module_id != %s", (name, module_id))
            if cursor.fetchone():
                messagebox.showerror("Lỗi", "Tên học phần đã tồn tại. Vui lòng chọn tên khác!")
                return
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể kiểm tra trùng lặp: {e}")
            return
        finally:
            cursor.close()
            conn.close()

        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn cập nhật thông tin học phần này?")
        if not confirm:
            return

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("UPDATE course_modules SET module_name = %s, credits = %s, coefficient = %s, periods = %s WHERE module_id = %s",
                        (name, credits, coefficient, periods, module_id))
            conn.commit()
            messagebox.showinfo("Thành công", "Cập nhật học phần thành công")
            self.reset_module_fields()
            self.load_modules()
            if hasattr(self, 'module_combobox'):
                self.module_combobox.configure(values=self.get_modules())
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

        # Kiểm tra xem học phần có liên quan đến lớp học không
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM classes WHERE module_id = %s LIMIT 1", (module_id,))
            if cursor.fetchone():
                messagebox.showerror("Lỗi", "Không thể xóa học phần vì có lớp học liên quan")
                return
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể kiểm tra lớp học liên quan: {e}")
            return
        finally:
            cursor.close()
            conn.close()

        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa học phần này?"):
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM course_modules WHERE module_id = %s", (module_id,))
                conn.commit()
                messagebox.showinfo("Thành công", "Xóa học phần thành công")
                self.reset_module_fields()
                self.load_modules()
                if hasattr(self, 'module_combobox'):
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
            cursor.execute("SELECT module_id, module_name, credits, coefficient, periods FROM course_modules")
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
        values = item['values']
        self.module_name.delete(0, END)
        self.module_name.insert(0, values[1])
        self.module_name.configure(placeholder_text="")
        self.module_credits.delete(0, END)
        self.module_credits.insert(0, values[2])
        self.module_credits.configure(placeholder_text="")
        self.module_coefficient.delete(0, END)
        self.module_coefficient.insert(0, values[3])
        self.module_coefficient.configure(placeholder_text="")
        self.module_periods.delete(0, END)
        self.module_periods.insert(0, values[4])
        self.module_periods.configure(placeholder_text="")

    def reset_module_fields(self):
        self.module_name.delete(0, END)
        self.module_name.configure(placeholder_text="Tên học phần")
        self.module_credits.delete(0, END)
        self.module_credits.configure(placeholder_text="Số tín chỉ")
        self.module_coefficient.delete(0, END)
        self.module_coefficient.configure(placeholder_text="Hệ số (ví dụ: 1.5)")
        self.module_periods.delete(0, END)
        self.module_periods.configure(placeholder_text="Số tiết")
        # Bỏ chọn dòng trong bảng module_tree
        for item in self.module_tree.selection():
            self.module_tree.selection_remove(item)

    def add_class(self):
        selected = self.class_tree.selection()
        if selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng reset form trước khi thêm mới!")
            return

        semester = self.class_semester.get().strip()
        module = self.class_module.get().strip()
        class_count = self.class_count.get().strip()
        num_students = self.class_size.get().strip()

        # Kiểm tra đầu vào
        if not all([semester, module, class_count, num_students]):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return

        semester_id = semester.split(":")[0].strip()
        module_id = module.split(":")[0].strip()
        module_name = module.split(":")[1].strip()

        try:
            class_count = int(class_count)
            if class_count < 1 or class_count > 8:
                messagebox.showerror("Lỗi", "Số lượng lớp phải từ 1 đến 8!")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Số lượng lớp phải là số nguyên!")
            return

        try:
            num_students = int(num_students)
            if num_students <= 0:
                messagebox.showerror("Lỗi", "Số sinh viên phải lớn hơn 0!")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Số sinh viên phải là số nguyên!")
            return

        # Kiểm tra số lớp hiện có của học phần trong kỳ học
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT class_name FROM classes WHERE semester_id = %s AND module_id = %s",
                        (semester_id, module_id))
            existing_classes = cursor.fetchall()
            current_count = len(existing_classes)

            # Kiểm tra giới hạn 8 lớp cho học phần trong kỳ học
            if current_count + class_count > 8:
                messagebox.showerror("Lỗi", f"Học phần này đã có {current_count} lớp trong kỳ học. Không thể tạo thêm {class_count} lớp vì vượt quá giới hạn 8 lớp!")
                return

            # Tìm các số thứ tự hiện có và xác định khoảng trống
            existing_numbers = []
            for class_tuple in existing_classes:
                class_name = class_tuple[0]
                if class_name.startswith(module_name) and "N" in class_name:
                    number = int(class_name.split("N")[-1])
                    existing_numbers.append(number)
            existing_numbers.sort()

            # Tìm các khoảng trống (NXX bị thiếu) và số lớn nhất
            if existing_numbers:
                max_number = max(existing_numbers)
                # Tạo danh sách các số từ 1 đến max_number
                all_numbers = set(range(1, max_number + 1))
                existing_numbers_set = set(existing_numbers)
                # Tìm các số bị thiếu (khoảng trống)
                missing_numbers = sorted(list(all_numbers - existing_numbers_set))
                next_number = max_number + 1
            else:
                missing_numbers = []
                next_number = 1

            # Tạo danh sách các số thứ tự sẽ sử dụng để đặt tên lớp
            numbers_to_use = []
            for i in range(class_count):
                if missing_numbers:
                    # Lấy số nhỏ nhất từ các khoảng trống
                    numbers_to_use.append(missing_numbers.pop(0))
                else:
                    # Nếu không còn khoảng trống, dùng số tiếp theo
                    numbers_to_use.append(next_number)
                    next_number += 1

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể kiểm tra số lớp: {e}")
            return
        finally:
            cursor.close()
            conn.close()

        # Hỏi xác nhận
        confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn tạo {class_count} lớp học cho {module_name} trong kỳ {semester.split(':')[1].strip()}?")
        if not confirm:
            return

        # Tạo các lớp
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            for number in numbers_to_use:
                # Tạo tên lớp
                class_name = f"{module_name} N{str(number).zfill(2)}"
                # Tạo mã lớp
                while True:
                    random_num = random.randint(0, 99999)
                    class_id = f"CLS{str(random_num).zfill(5)}"
                    cursor.execute("SELECT class_id FROM classes WHERE class_id = %s", (class_id,))
                    if not cursor.fetchone():
                        break
                # Thêm lớp vào CSDL
                cursor.execute("INSERT INTO classes (class_id, semester_id, module_id, class_name, num_students) VALUES (%s, %s, %s, %s, %s)",
                            (class_id, semester_id, module_id, class_name, num_students))
            conn.commit()
            messagebox.showinfo("Thành công", f"Tạo {class_count} lớp học thành công!")
            self.reset_class_fields()
            self.load_classes()
            if hasattr(self, 'assignment_class_combobox'):
                self.assignment_class_combobox.configure(values=self.get_classes())
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tạo lớp học: {e}")
        finally:
            cursor.close()
            conn.close()

    def edit_class(self):
        selected_item = self.class_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn lớp học để sửa!")
            return

        item = self.class_tree.item(selected_item)
        values = item['values']
        class_id = self.selected_class_id  # Lấy class_id từ on_class_select

        # Lấy thông tin hiện tại của lớp
        current_semester_display = values[0]
        current_module_display = values[1]
        current_class_name = values[3]
        current_num_students = values[4]

        # Tìm semester_id và module_id hiện tại
        current_semester_id = None
        current_module_id = None
        for sem in self.get_semesters():
            if sem.endswith(current_semester_display):
                current_semester_id = sem.split(":")[0]
                break
        for mod in self.get_modules():
            if mod.endswith(current_module_display):
                current_module_id = mod.split(":")[0]
                break

        # Tạo cửa sổ pop-up
        edit_window = CTkToplevel(self.window)
        edit_window.title("Sửa lớp học")
        edit_window.geometry("400x450")
        edit_window.resizable(False, False)

        # Frame chứa các trường nhập liệu
        form_frame = CTkFrame(edit_window, fg_color="transparent")
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Kỳ học
        CTkLabel(form_frame, text="Học kỳ:", font=("Helvetica", 12)).pack(pady=(5, 0))
        semester_var = CTkComboBox(form_frame, width=350, values=self.get_semesters())
        semester_var.pack(pady=5)
        semester_var.set(current_semester_id + ": " + current_semester_display if current_semester_id else "")

        # Học phần
        CTkLabel(form_frame, text="Học phần:", font=("Helvetica", 12)).pack(pady=(5, 0))
        module_var = CTkComboBox(form_frame, width=350, values=self.get_modules())
        module_var.pack(pady=5)
        module_var.set(current_module_id + ": " + current_module_display if current_module_id else "")

        # Tên lớp
        CTkLabel(form_frame, text="Tên lớp:", font=("Helvetica", 12)).pack(pady=(5, 0))
        class_name_var = CTkEntry(form_frame, width=350)
        class_name_var.pack(pady=5)
        class_name_var.insert(0, current_class_name)

        # Số sinh viên
        CTkLabel(form_frame, text="Số sinh viên:", font=("Helvetica", 12)).pack(pady=(5, 0))
        num_students_var = CTkEntry(form_frame, width=350)
        num_students_var.pack(pady=5)
        num_students_var.insert(0, str(current_num_students))

        # Hàm xử lý khi nhấn nút "Lưu"
        def save_changes():
            semester = semester_var.get().strip()
            module = module_var.get().strip()
            class_name = class_name_var.get().strip()
            num_students = num_students_var.get().strip()

            # Kiểm tra đầu vào
            if not all([semester, module, class_name, num_students]):
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin", parent=edit_window)
                return

            semester_id = semester.split(":")[0].strip()
            module_id = module.split(":")[0].strip()

            try:
                num_students = int(num_students)
                if num_students <= 0:
                    messagebox.showerror("Lỗi", "Số sinh viên phải lớn hơn 0!", parent=edit_window)
                    return
            except ValueError:
                messagebox.showerror("Lỗi", "Số sinh viên phải là số nguyên!", parent=edit_window)
                return

            # Nếu kỳ học hoặc học phần thay đổi, kiểm tra giới hạn 8 lớp
            if semester_id != current_semester_id or module_id != current_module_id:
                try:
                    conn = mysql.connector.connect(**DB_CONFIG)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM classes WHERE semester_id = %s AND module_id = %s AND class_id != %s",
                                (semester_id, module_id, class_id))
                    current_count = cursor.fetchone()[0]
                    if current_count >= 8:
                        messagebox.showerror("Lỗi", f"Học phần này đã có {current_count} lớp trong kỳ học mới. Không thể chuyển vì vượt quá giới hạn 8 lớp!", parent=edit_window)
                        return
                except mysql.connector.Error as e:
                    messagebox.showerror("Lỗi", f"Không thể kiểm tra số lớp: {e}", parent=edit_window)
                    return
                finally:
                    cursor.close()
                    conn.close()

            # Kiểm tra trùng lặp tên lớp trong cùng kỳ học và học phần (ngoại trừ lớp đang sửa)
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("SELECT class_id FROM classes WHERE semester_id = %s AND module_id = %s AND class_name = %s AND class_id != %s",
                            (semester_id, module_id, class_name, class_id))
                if cursor.fetchone():
                    messagebox.showerror("Lỗi", f"Tên lớp '{class_name}' đã tồn tại trong kỳ học và học phần này!", parent=edit_window)
                    return
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể kiểm tra trùng lặp tên lớp: {e}", parent=edit_window)
                return
            finally:
                cursor.close()
                conn.close()

            # Xác nhận trước khi lưu
            confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn cập nhật thông tin lớp học này?", parent=edit_window)
            if not confirm:
                return

            # Lưu thay đổi vào CSDL
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("UPDATE classes SET semester_id = %s, module_id = %s, class_name = %s, num_students = %s WHERE class_id = %s",
                            (semester_id, module_id, class_name, num_students, class_id))
                conn.commit()
                messagebox.showinfo("Thành công", "Cập nhật lớp học thành công", parent=edit_window)
                self.reset_class_fields()
                self.load_classes()
                edit_window.destroy()  # Đóng cửa sổ sau khi lưu thành công
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể sửa lớp học: {e}", parent=edit_window)
            finally:
                cursor.close()
                conn.close()

        # Hàm đóng cửa sổ
        def cancel():
            edit_window.destroy()

        # Nút Lưu và Hủy
        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        CTkButton(button_frame, text="Lưu", fg_color="#0085FF", command=save_changes, width=100).pack(side="left", padx=5)
        CTkButton(button_frame, text="Hủy", fg_color="#6C757D", command=cancel, width=100).pack(side="left", padx=5)

    def delete_class(self):
        selected_item = self.class_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn lớp học để xóa!")
            return

        item = self.class_tree.item(selected_item)
        class_id = item["values"][2]

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM assignments WHERE class_id = %s LIMIT 1", (class_id,))
            if cursor.fetchone():
                messagebox.showerror("Lỗi", "Không thể xóa lớp học vì có phân công liên quan")
                return
            cursor.execute("SELECT 1 FROM salaries WHERE class_id = %s LIMIT 1", (class_id,))
            if cursor.fetchone():
                messagebox.showerror("Lỗi", "Không thể xóa lớp học vì có lương liên quan")
                return
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể kiểm tra liên quan: {e}")
            return
        finally:
            cursor.close()
            conn.close()

        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa lớp học này?"):
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM classes WHERE class_id = %s", (class_id,))
                conn.commit()
                messagebox.showinfo("Thành công", "Xóa lớp học thành công")
                self.reset_class_fields()
                self.load_classes()
                if hasattr(self, 'assignment_class_combobox'):
                    self.assignment_class_combobox.configure(values=self.get_classes())
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
                SELECT c.semester_id, s.semester_name, s.year, c.module_id, m.module_name, c.class_id, c.class_name, c.num_students
                FROM classes c
                JOIN semesters s ON c.semester_id = s.semester_id
                JOIN course_modules m ON c.module_id = m.module_id
            """)
            for item in self.class_tree.get_children():
                self.class_tree.delete(item)
            rows = cursor.fetchall()
            if not rows:
                messagebox.showwarning("Cảnh báo", "Không có dữ liệu lớp học")
            for row in rows:
                semester_display = f"{row[1]} {row[2]}"  # Hiển thị tên kỳ và năm
                module_display = row[4]  # Hiển thị tên học phần
                self.class_tree.insert("", "end", values=(semester_display, module_display, row[5], row[6], row[7]))
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
        values = item['values']
        # Tìm semester_id từ semester_display
        semester_display = values[0]
        semester_id = None
        for semester in self.get_semesters():
            if semester.endswith(semester_display):
                semester_id = semester.split(":")[0]
                break
        # Tìm module_id từ module_display
        module_display = values[1]
        module_id = None
        for module in self.get_modules():
            if module.endswith(module_display):
                module_id = module.split(":")[0]
                break
        self.class_semester.set(semester_id + ": " + semester_display if semester_id else "")
        self.class_module.set(module_id + ": " + module_display if module_id else "")
        self.class_count.set("1")  # Không hiển thị số lượng lớp đã tạo
        self.class_size.delete(0, END)
        self.class_size.insert(0, values[4])
        self.class_size.configure(placeholder_text="")
        self.selected_class_id = values[2]  # Lưu class_id để sử dụng khi sửa

    def reset_class_fields(self):
        self.class_semester.set(self.get_semesters()[0] if self.get_semesters() else "")
        self.class_module.set(self.get_modules()[0] if self.get_modules() else "")
        self.class_count.set("1")
        self.class_size.delete(0, END)
        self.class_size.configure(placeholder_text="Số sinh viên")
        # Bỏ chọn dòng trong bảng class_tree
        for item in self.class_tree.selection():
            self.class_tree.selection_remove(item)

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


    def get_years(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT year FROM semesters")
            years = [row[0] for row in cursor.fetchall()]
            return years if years else ["Không có năm học"]
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách năm học: {e}")
            return ["Lỗi tải năm học"]
        finally:
            cursor.close()
            conn.close()

    def add_semester(self):
        selected = self.semester_tree.selection()
        if selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng reset form trước khi thêm mới!")
            return

        name = self.semester_name.get().strip()
        year_range = self.semester_year.get().strip()
        start_date_str = self.start_date.get().strip()
        end_date_str = self.end_date.get().strip()

        if not all([name, year_range, start_date_str, end_date_str]):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return

        try:
            start_year, end_year = map(int, year_range.split('-'))
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            messagebox.showerror("Lỗi", "Ngày tháng không hợp lệ. Vui lòng nhập theo định dạng YYYY-MM-DD!")
            return

        if start_date.year != start_year:
            messagebox.showerror("Lỗi", f"Ngày bắt đầu phải thuộc năm {start_year}")
            return
        if end_date.year not in [start_year, end_year]:
            messagebox.showerror("Lỗi", f"Ngày kết thúc phải thuộc năm {start_year} hoặc {end_year}")
            return

        if start_date >= end_date:
            messagebox.showerror("Lỗi", "Ngày bắt đầu phải nhỏ hơn ngày kết thúc")
            return

        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT semester_id FROM semesters WHERE semester_name = %s AND year = %s", (name, year_range))
            if cursor.fetchone():
                messagebox.showerror("Lỗi", "Kỳ học đã tồn tại trong năm học này!")
                return

            cursor.execute("SELECT semester_id FROM semesters ORDER BY CAST(SUBSTRING(semester_id, 4) AS UNSIGNED) DESC LIMIT 1")
            result = cursor.fetchone()
            if result:
                last_id = result[0]
                last_num = int(last_id[3:])
                new_num = last_num + 1
            else:
                new_num = 1
            semester_id = f"SEM{str(new_num).zfill(5)}"

            # Hỏi xác nhận trước khi thêm
            confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn thêm kỳ học '{name} {year_range}' với mã {semester_id}?")
            if not confirm:
                return

            cursor.execute("INSERT INTO semesters (semester_id, semester_name, year, start_date, end_date) VALUES (%s, %s, %s, %s, %s)",
                        (semester_id, name, year_range, start_date, end_date))
            conn.commit()
            messagebox.showinfo("Thành công", f"Thêm kỳ học thành công với mã {semester_id}")
            self.reset_semester_fields()
            self.load_semesters()
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể thêm kỳ học: {e}")
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    def edit_semester(self):
        selected = self.semester_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn kỳ học để sửa!")
            return

        name = self.semester_name.get().strip()
        year_range = self.semester_year.get().strip()
        start_date_str = self.start_date.get().strip()
        end_date_str = self.end_date.get().strip()

        if not all([name, year_range, start_date_str, end_date_str]):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return

        try:
            start_year, end_year = map(int, year_range.split('-'))
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            messagebox.showerror("Lỗi", "Ngày tháng không hợp lệ. Vui lòng nhập theo định dạng YYYY-MM-DD!")
            return

        if start_date.year != start_year:
            messagebox.showerror("Lỗi", f"Ngày bắt đầu phải thuộc năm {start_year}")
            return
        if end_date.year not in [start_year, end_year]:
            messagebox.showerror("Lỗi", f"Ngày kết thúc phải thuộc năm {start_year} hoặc {end_year}")
            return

        if start_date >= end_date:
            messagebox.showerror("Lỗi", "Ngày bắt đầu phải nhỏ hơn ngày kết thúc")
            return

        semester_id = self.semester_tree.item(selected)['values'][0]

        # Sử dụng messagebox.askyesno để xác nhận
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn sửa kỳ học này?"):
            conn = None
            cursor = None
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("SELECT semester_id FROM semesters WHERE semester_name = %s AND year = %s AND semester_id != %s",
                            (name, year_range, semester_id))
                if cursor.fetchone():
                    messagebox.showerror("Lỗi", "Kỳ học đã tồn tại trong năm học này!")
                    return

                cursor.execute("UPDATE semesters SET semester_name = %s, year = %s, start_date = %s, end_date = %s WHERE semester_id = %s",
                            (name, year_range, start_date, end_date, semester_id))
                conn.commit()
                messagebox.showinfo("Thành công", "Cập nhật kỳ học thành công!")
                self.reset_semester_fields()
                self.load_semesters()
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể cập nhật kỳ học: {e}")
            finally:
                if cursor is not None:
                    cursor.close()
                if conn is not None:
                    conn.close()

    def delete_semester(self):
        selected_item = self.semester_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn kỳ học để xóa!")
            return

        item = self.semester_tree.item(selected_item)
        semester_id = item["values"][0]

        # Kiểm tra xác nhận bằng messagebox
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa kỳ học này?"):
            conn = None
            cursor = None
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                # Kiểm tra xem kỳ học có lớp học liên quan không
                cursor.execute("SELECT 1 FROM classes WHERE semester_id = %s LIMIT 1", (semester_id,))
                if cursor.fetchone():
                    messagebox.showerror("Lỗi", "Không thể xóa kỳ học vì có lớp học liên quan")
                    return
                # Thực hiện xóa
                cursor.execute("DELETE FROM semesters WHERE semester_id = %s", (semester_id,))
                conn.commit()
                messagebox.showinfo("Thành công", "Xóa kỳ học thành công")
                self.reset_semester_fields()
                self.load_semesters()
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể xóa kỳ học: {str(e)}")
            finally:
                if cursor is not None:
                    cursor.close()
                if conn is not None:
                    conn.close()

    def load_semesters(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT semester_id, semester_name, year, start_date, end_date FROM semesters")
            for item in self.semester_tree.get_children():
                self.semester_tree.delete(item)
            rows = cursor.fetchall()
            if not rows:
                messagebox.showwarning("Cảnh báo", "Không có dữ liệu kỳ học")
            for row in rows:
                semester_id, semester_name, year, start_date, end_date = row
                # Đảm bảo định dạng ngày đầy đủ
                start_date = start_date.strftime('%Y-%m-%d') if start_date else "N/A"
                end_date = end_date.strftime('%Y-%m-%d') if end_date else "N/A"
                print(f"semester_id={semester_id}, start_date={start_date}, end_date={end_date}")
                self.semester_tree.insert("", "end", values=(semester_id, semester_name, year, start_date, end_date))
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu kỳ học: {e}")
        finally:
            cursor.close()
            conn.close()

    def on_semester_select(self, event):
        selected = self.semester_tree.selection()
        if not selected:
            return
        item = self.semester_tree.item(selected)
        values = item['values']
        # print(f"values={values}")  # Debug giá trị từ Treeview
        semester_id, name, year, start_date, end_date = values
        
        self.semester_name.set(name)
        self.semester_year.set(year)
        
        # Hiển thị ngày bắt đầu
        # print(f"Trước khi chèn start_date: {self.start_date.get()}")  # Debug giá trị trước khi chèn
        self.start_date.delete(0, "end")
        if start_date != "N/A" and start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
                self.start_date.insert(0, start_date)
            except ValueError:
                messagebox.showwarning("Cảnh báo", f"Ngày bắt đầu không hợp lệ: {start_date}. Đặt về mặc định.")
                self.start_date.insert(0, "2025-01-01")
        else:
            self.start_date.insert(0, "2025-01-01")
        # print(f"Sau khi chèn start_date: {self.start_date.get()}")  # Debug giá trị sau khi chèn
        
        # Hiển thị ngày kết thúc
        print(f"Trước khi chèn end_date: {self.end_date.get()}")  # Debug giá trị trước khi chèn
        self.end_date.delete(0, "end")
        if end_date != "N/A" and end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
                self.end_date.insert(0, end_date)
            except ValueError:
                messagebox.showwarning("Cảnh báo", f"Ngày kết thúc không hợp lệ: {end_date}. Đặt về mặc định.")
                self.end_date.insert(0, "2025-12-31")
        else:
            self.end_date.insert(0, "2025-12-31")
        print(f"Sau khi chèn end_date: {self.end_date.get()}")  # Debug giá trị sau khi chèn
        
        # Tạm thời bỏ gọi update_date_years để kiểm tra
        # self.update_date_years()
        
    def reset_semester_fields(self):
        self.semester_name.set("Học kỳ 1")
        self.semester_year.set("2025-2026")
        self.start_date.delete(0, "end")
        self.start_date.insert(0, "2025-01-01")
        self.end_date.delete(0, "end")
        self.end_date.insert(0, "2025-12-31")
        # Bỏ chọn dòng trong bảng semester_tree
        for item in self.semester_tree.selection():
            self.semester_tree.selection_remove(item)

    
    def get_classes(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.class_id, m.module_name 
                FROM classes c 
                JOIN course_modules m ON c.module_id = m.module_id
            """)
            classes = [f"{row[0]}: {row[1]}" for row in cursor.fetchall()]
            return classes if classes else ["Không có lớp học"]
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách lớp học: {e}")
            return ["Lỗi tải lớp học"]
        finally:
            cursor.close()
            conn.close()

    # def add_assignment(self):
    #     selected = self.assignment_tree.selection()
    #     if selected:
    #         messagebox.showwarning("Cảnh báo", "Vui lòng reset form trước khi thêm mới!")
    #         return

    #     class_info = self.assignment_class_combobox.get()
    #     teacher = self.assignment_teacher_combobox.get()

    #     if not all([class_info, teacher]):
    #         messagebox.showerror("Lỗi", "Vui lòng chọn đầy đủ thông tin")
    #         return

    #     class_id = class_info.split(":")[0]
    #     teacher_id = teacher.split(":")[0]

    #     try:
    #         conn = mysql.connector.connect(**DB_CONFIG)
    #         cursor = conn.cursor()
    #         cursor.execute("SELECT assignment_id FROM assignments WHERE class_id = %s", (class_id,))
    #         if cursor.fetchone():
    #             messagebox.showerror("Lỗi", "Lớp học này đã được phân công!")
    #             return

    #         while True:
    #             random_num = random.randint(0, 99999)
    #             assignment_id = f"ASN{str(random_num).zfill(5)}"
    #             cursor.execute("SELECT assignment_id FROM assignments WHERE assignment_id = %s", (assignment_id,))
    #             if not cursor.fetchone():
    #                 break

    #         cursor.execute("INSERT INTO assignments (assignment_id, class_id, teacher_id) VALUES (%s, %s, %s)",
    #                     (assignment_id, class_id, teacher_id))
    #         conn.commit()
    #         messagebox.showinfo("Thành công", f"Phân công thành công với mã {assignment_id}")
    #         self.reset_assignment_fields()
    #         self.load_assignments()
    #     except mysql.connector.Error as e:
    #         messagebox.showerror("Lỗi", f"Không thể thêm phân công: {e}")
    #     finally:
    #         cursor.close()
    #         conn.close()

    # def edit_assignment(self):
    #     selected_item = self.assignment_tree.selection()
    #     if not selected_item:
    #         messagebox.showwarning("Cảnh báo", "Vui lòng chọn phân công để sửa!")
    #         return

    #     item = self.assignment_tree.item(selected_item)
    #     assignment_id = item["values"][0]
    #     class_info = self.assignment_class_combobox.get()
    #     teacher = self.assignment_teacher_combobox.get()

    #     if not all([class_info, teacher]):
    #         messagebox.showerror("Lỗi", "Vui lòng chọn đầy đủ thông tin")
    #         return

    #     class_id = class_info.split(":")[0]
    #     teacher_id = teacher.split(":")[0]

    #     try:
    #         conn = mysql.connector.connect(**DB_CONFIG)
    #         cursor = conn.cursor()
    #         cursor.execute("UPDATE assignments SET class_id = %s, teacher_id = %s WHERE assignment_id = %s",
    #                     (class_id, teacher_id, assignment_id))
    #         conn.commit()
    #         messagebox.showinfo("Thành công", "Cập nhật phân công thành công")
    #         self.reset_assignment_fields()
    #         self.load_assignments()
    #     except mysql.connector.Error as e:
    #         messagebox.showerror("Lỗi", f"Không thể sửa phân công: {e}")
    #     finally:
    #         cursor.close()
    #         conn.close()

    def delete_assignment(self):
        if not hasattr(self, 'selected_class_id'):
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn lớp học phần!")
            return

        class_id = self.selected_class_id

        # Kiểm tra lớp học có phân công không
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT assignment_id FROM assignments WHERE class_id = %s", (class_id,))
            assignment = cursor.fetchone()
            if not assignment:
                messagebox.showwarning("Cảnh báo", "Lớp học này chưa được phân công!")
                return
            assignment_id = assignment[0]

            # Kiểm tra xem phân công có liên quan đến lương không (dùng class_id thay vì assignment_id)
            cursor.execute("SELECT 1 FROM salaries WHERE class_id = %s LIMIT 1", (class_id,))
            if cursor.fetchone():
                if messagebox.askyesno("Xác nhận", "Phân công này có liên quan đến lương. Xóa phân công sẽ xóa cả dữ liệu lương. Bạn có chắc muốn tiếp tục?"):
                    # Xóa dữ liệu lương liên quan
                    cursor.execute("DELETE FROM salaries WHERE class_id = %s", (class_id,))
                    conn.commit()
                else:
                    return
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể kiểm tra phân công: {e}")
            return
        finally:
            cursor.close()
            conn.close()

        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa phân công của lớp học này?"):
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM assignments WHERE assignment_id = %s", (assignment_id,))
                conn.commit()
                messagebox.showinfo("Thành công", "Xóa phân công thành công")
                self.load_classes_by_semester(None)
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể xóa phân công: {e}")
            finally:
                cursor.close()
                conn.close()

    def load_assignments(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.assignment_id, c.class_id, cm.module_name, t.full_name, a.assigned_at
                FROM assignments a
                JOIN classes c ON a.class_id = c.class_id
                JOIN course_modules cm ON c.module_id = cm.module_id
                JOIN teachers t ON a.teacher_id = t.teacher_id
                WHERE cm.dept_id = %s
            """, (self.user['dept_id'],))
            for item in self.assignment_tree.get_children():
                self.assignment_tree.delete(item)
            rows = cursor.fetchall()
            if not rows:
                messagebox.showwarning("Cảnh báo", "Không có dữ liệu phân công")
            for row in rows:
                self.assignment_tree.insert("", "end", values=(row[0], f"{row[1]}: {row[2]}", row[3], row[4]))
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu phân công: {e}")
        finally:
            cursor.close()
            conn.close()

    def on_assignment_select(self, event):
        selected_item = self.assignment_tree.selection()
        if selected_item:
            self.assign_button.configure(state="normal")
            self.edit_button.configure(state="normal")
            self.delete_button.configure(state="normal")
            self.reset_button.configure(state="normal")
            item = self.assignment_tree.item(selected_item)
            self.selected_class_id = item['values'][2]  # Lưu class_id để sử dụng khi phân công/xóa
        else:
            self.assign_button.configure(state="disabled")
            self.edit_button.configure(state="disabled")
            self.delete_button.configure(state="disabled")
            self.reset_button.configure(state="disabled")

    def reset_assignment_fields(self):
        self.assignment_semester_combobox.set(self.get_semesters()[0] if self.get_semesters() else "")
        self.assignment_module_combobox.set("Tất cả")
        # Làm mới bảng dữ liệu với tất cả dữ liệu (không áp dụng bộ lọc)
        self.load_classes_by_semester(None)
        for item in self.assignment_tree.selection():
            self.assignment_tree.selection_remove(item)
        self.assign_button.configure(state="disabled")
        self.edit_button.configure(state="disabled")
        self.delete_button.configure(state="disabled")
        self.reset_button.configure(state="disabled")

    def get_academic_years(self):
        current_year = datetime.now().year
        years = [f"{y}-{y+1}" for y in range(current_year - 5, current_year + 5)]
        return years if years else ["2025-2026"]
    
    def get_date_options(self):
        dates = []
        for year in range(2025, 2027):  # Từ 2025 đến 2026
            for month in range(1, 13):  # Từ tháng 1 đến tháng 12
                try:
                    date = datetime(year, month, 1).strftime('%Y-%m-%d')
                    dates.append(date)
                except ValueError:
                    continue  # Bỏ qua các tháng không hợp lệ (nếu có)
        return dates
    

    def update_date_years(self, event=None):
        year_range = self.semester_year.get().strip()
        print(f"update_date_years: year_range={year_range}")  # Debug giá trị năm học
        if not year_range:
            self.start_date.delete(0, "end")
            self.start_date.insert(0, "2025-01-01")
            self.end_date.delete(0, "end")
            self.end_date.insert(0, "2025-12-31")
            return
        try:
            start_year, end_year = map(int, year_range.split('-'))
            # Cập nhật ngày bắt đầu và kết thúc
            start_date = f"{start_year}-01-01"
            end_date = f"{end_year}-12-31"
            # Chỉ cập nhật nếu ô nhập liệu đang trống
            if not self.start_date.get():
                self.start_date.delete(0, "end")
                self.start_date.insert(0, start_date)
            if not self.end_date.get():
                self.end_date.delete(0, "end")
                self.end_date.insert(0, end_date)
        except ValueError:
            messagebox.showerror("Lỗi", "Năm học không hợp lệ. Vui lòng chọn lại!")
            self.start_date.delete(0, "end")
            self.start_date.insert(0, "2025-01-01")
            self.end_date.delete(0, "end")
            self.end_date.insert(0, "2025-12-31")

    def open_calendar(self, entry_widget):
        # Tạo cửa sổ pop-up
        top = CTkToplevel(self.window)
        top.title("Chọn ngày")
        top.geometry("300x300")

        # Lấy ngày hiện tại từ ô nhập liệu (nếu có)
        try:
            current_date = datetime.strptime(entry_widget.get(), '%Y-%m-%d')
        except ValueError:
            current_date = datetime.now()

        # Tạo lịch
        cal = Calendar(
            top,
            selectmode="day",
            year=current_date.year,
            month=current_date.month,
            day=current_date.day,
            date_pattern="yyyy-mm-dd"
        )
        cal.pack(pady=10, fill="both", expand=True)

        # Nút xác nhận
        def set_date():
            selected_date = cal.get_date()
            entry_widget.delete(0, "end")
            entry_widget.insert(0, selected_date)
            top.destroy()

        CTkButton(top, text="Xác nhận", command=set_date, fg_color="#0085FF").pack(pady=5)

    def get_semesters(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT semester_id, semester_name, year FROM semesters")
            semesters = [f"{row[0]}: {row[1]} {row[2]}" for row in cursor.fetchall()]
            return semesters if semesters else ["Không có kỳ học"]
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách kỳ học: {e}")
            return ["Lỗi tải kỳ học"]
        finally:
            cursor.close()
            conn.close()

    def load_classes_by_semester(self, event=None):
        semester = self.assignment_semester_combobox.get().strip()
        module_filter = self.assignment_module_combobox.get().strip()

        if not semester:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn kỳ học")
            return

        semester_id = semester.split(":")[0].strip()

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            query = """
                SELECT s.semester_name, s.year, m.module_name, c.class_id, c.class_name, c.num_students, t.full_name
                FROM classes c
                JOIN semesters s ON c.semester_id = s.semester_id
                JOIN course_modules m ON c.module_id = m.module_id
                LEFT JOIN assignments a ON c.class_id = a.class_id
                LEFT JOIN teachers t ON a.teacher_id = t.teacher_id
                WHERE c.semester_id = %s
            """
            params = [semester_id]
            if module_filter != "Tất cả":
                query += " AND m.module_name = %s"
                params.append(module_filter)

            cursor.execute(query, params)
            for item in self.assignment_tree.get_children():
                self.assignment_tree.delete(item)
            rows = cursor.fetchall()
            if not rows:
                messagebox.showwarning("Cảnh báo", "Không có dữ liệu lớp học phần")
            for row in rows:
                semester_display = f"{row[0]} {row[1]}"
                teacher_display = row[6] if row[6] else "Chưa phân công"
                self.assignment_tree.insert("", "end", values=(semester_display, row[2], row[3], row[4], row[5], teacher_display))
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu lớp học phần: {e}")
        finally:
            cursor.close()
            conn.close()


    def assign_teacher(self):
        if not hasattr(self, 'selected_class_id'):
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn lớp học phần!")
            return

        class_id = self.selected_class_id

        # Kiểm tra lớp học đã được phân công chưa
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT assignment_id, teacher_id FROM assignments WHERE class_id = %s", (class_id,))
            existing_assignment = cursor.fetchone()
            if existing_assignment:
                messagebox.showwarning("Cảnh báo", "Lớp học này đã được phân công! Vui lòng xóa phân công cũ trước.")
                return
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể kiểm tra phân công: {e}")
            return
        finally:
            cursor.close()
            conn.close()

        # Tạo cửa sổ pop-up
        assign_window = CTkToplevel(self.window)
        assign_window.title("Phân công giảng viên")
        assign_window.geometry("400x200")
        assign_window.resizable(False, False)

        # Frame chứa các trường nhập liệu
        form_frame = CTkFrame(assign_window, fg_color="transparent")
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Giáo viên
        CTkLabel(form_frame, text="Chọn giảng viên:", font=("Helvetica", 12)).pack(pady=(5, 0))
        teachers = self.get_teachers()
        teacher_var = CTkComboBox(form_frame, width=350, values=teachers)
        teacher_var.pack(pady=5)
        if teachers and teachers[0] not in ["Không có giáo viên", "Lỗi tải giáo viên"]:
            teacher_var.set(teachers[0])
        else:
            teacher_var.set(teachers[0])

        # Hàm xử lý khi nhấn nút "Phân công"
        def save_assignment():
            teacher = teacher_var.get().strip()

            if not teacher or teacher in ["Không có giáo viên", "Lỗi tải giáo viên"]:
                messagebox.showerror("Lỗi", "Không có giáo viên để phân công!", parent=assign_window)
                return

            teacher_id = teacher.split(":")[0].strip()

            # Hỏi xác nhận
            confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn phân công giảng viên này?", parent=assign_window)
            if not confirm:
                return

            # Tạo phân công mới
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                while True:
                    random_num = random.randint(0, 99999)
                    assignment_id = f"ASN{str(random_num).zfill(5)}"
                    cursor.execute("SELECT assignment_id FROM assignments WHERE assignment_id = %s", (assignment_id,))
                    if not cursor.fetchone():
                        break
                assigned_at = datetime.now().strftime('%Y-%m-%d')
                cursor.execute("INSERT INTO assignments (assignment_id, class_id, teacher_id, assigned_at) VALUES (%s, %s, %s, %s)",
                            (assignment_id, class_id, teacher_id, assigned_at))
                conn.commit()
                messagebox.showinfo("Thành công", f"Phân công thành công với mã {assignment_id}", parent=assign_window)
                self.load_classes_by_semester(None)
                assign_window.destroy()
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể phân công: {e}", parent=assign_window)
            finally:
                cursor.close()
                conn.close()

        # Hàm đóng cửa sổ
        def cancel():
            assign_window.destroy()

        # Nút Phân công và Hủy
        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        CTkButton(button_frame, text="Phân công", fg_color="#0085FF", command=save_assignment, width=100).pack(side="left", padx=5)
        CTkButton(button_frame, text="Hủy", fg_color="#6C757D", command=cancel, width=100).pack(side="left", padx=5)

    def show_class_stats(self):
        year = self.stats_year_combobox.get().strip()
        if not year:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn năm học!")
            return

        # Lấy dữ liệu thống kê
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            query = """
                SELECT cm.module_name, COUNT(c.class_id) as num_classes, SUM(c.num_students) as total_students
                FROM classes c
                JOIN semesters s ON c.semester_id = s.semester_id
                JOIN course_modules cm ON c.module_id = cm.module_id
                WHERE s.year = %s
                GROUP BY cm.module_id, cm.module_name
            """
            cursor.execute(query, (year,))
            rows = cursor.fetchall()
            if not rows:
                messagebox.showwarning("Cảnh báo", "Không có dữ liệu để thống kê.")
                return

            # Lưu dữ liệu để dùng cho xuất báo cáo
            self.stats_data = [{"Module": row[0], "Num Classes": row[1], "Total Students": row[2]} for row in rows]

            # Xóa biểu đồ cũ, giữ lại stats_table_frame nếu nó tồn tại
            for widget in self.class_stats_frame.winfo_children():
                if widget != getattr(self, 'stats_table_frame', None):  # Giữ lại stats_table_frame nếu tồn tại
                    widget.destroy()

            # Kiểm tra và tái tạo stats_table_frame nếu cần
            if not hasattr(self, 'stats_table_frame') or not self.stats_table_frame.winfo_exists():
                self.stats_table_frame = CTkFrame(self.class_stats_frame, fg_color="#FFFFFF", corner_radius=10)
                self.stats_table_frame.pack(side="bottom", padx=10, pady=10, fill="both", expand=True)

            # Kiểm tra và tái tạo class_stats_tree nếu cần
            if not hasattr(self, 'class_stats_tree') or not self.class_stats_tree.winfo_exists():
                self.class_stats_tree = ttk.Treeview(self.stats_table_frame, columns=("Module", "Num Classes", "Total Students"), show="headings")
                self.class_stats_tree.heading("Module", text="Học phần")
                self.class_stats_tree.heading("Num Classes", text="Số lớp mở")
                self.class_stats_tree.heading("Total Students", text="Tổng số sinh viên")
                self.class_stats_tree.column("Module", width=200, anchor="center")
                self.class_stats_tree.column("Num Classes", width=100, anchor="center")
                self.class_stats_tree.column("Total Students", width=100, anchor="center")
                self.class_stats_tree.pack(padx=10, pady=10, fill="both", expand=True)

            # Vẽ biểu đồ
            labels = [row[0] for row in rows]
            num_classes = [row[1] for row in rows]
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(labels, num_classes, color="#36A2EB")
            ax.set_title(f"Số lớp mở theo học phần ({year})", fontsize=14, pad=15)
            ax.set_xlabel("Học phần", fontsize=12)
            ax.set_ylabel("Số lớp mở", fontsize=12)
            ax.set_ylim(0, max(num_classes) + 1 if num_classes else 1)
            plt.xticks(rotation=45, ha="right")

            # Nhúng biểu đồ vào giao diện
            canvas = FigureCanvasTkAgg(fig, master=self.class_stats_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            # Hiển thị bảng
            for item in self.class_stats_tree.get_children():
                self.class_stats_tree.delete(item)
            for row in rows:
                self.class_stats_tree.insert("", "end", values=row)
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu thống kê: {e}")
        finally:
            cursor.close()
            conn.close()

    
    def export_excel(self):
        import pandas as pd

        year = self.stats_year_combobox.get().strip()
        if not year or not hasattr(self, 'stats_data') or not self.stats_data:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu để xuất báo cáo!")
            return

        try:
            # Tạo DataFrame từ dữ liệu thống kê
            df = pd.DataFrame(self.stats_data)
            output_file = f"Class_Stats_Report_{year}.xlsx"
            df.to_excel(output_file, index=False)
            messagebox.showinfo("Thành công", f"Báo cáo đã được xuất dưới dạng Excel: {output_file}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu file Excel. Vui lòng kiểm tra thư mục: {e}")


    def show_class_stats_table(self):
        year = self.stats_year_combobox.get().strip()
        if not year:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn năm học!")
            return

        # Lấy dữ liệu thống kê
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            query = """
                SELECT cm.module_name, COUNT(c.class_id) as num_classes, SUM(c.num_students) as total_students
                FROM classes c
                JOIN semesters s ON c.semester_id = s.semester_id
                JOIN course_modules cm ON c.module_id = cm.module_id
                WHERE s.year = %s
                GROUP BY cm.module_id, cm.module_name
            """
            cursor.execute(query, (year,))
            rows = cursor.fetchall()
            if not rows:
                messagebox.showwarning("Cảnh báo", "Không có dữ liệu để thống kê.")
                return

            # Lưu dữ liệu để dùng cho xuất báo cáo
            self.stats_data = [{"Module": row[0], "Num Classes": row[1], "Total Students": row[2]} for row in rows]

            # Xóa nội dung cũ trong class_stats_frame
            for widget in self.class_stats_frame.winfo_children():
                widget.destroy()

            # Tạo stats_table_frame để hiển thị bảng
            self.stats_table_frame = CTkFrame(self.class_stats_frame, fg_color="#FFFFFF", corner_radius=10)
            self.stats_table_frame.pack(padx=10, pady=10, fill="both", expand=True)
            self.class_stats_tree = ttk.Treeview(self.stats_table_frame, columns=("Module", "Num Classes", "Total Students"), show="headings")
            self.class_stats_tree.heading("Module", text="Học phần")
            self.class_stats_tree.heading("Num Classes", text="Số lớp mở")
            self.class_stats_tree.heading("Total Students", text="Tổng số sinh viên")
            self.class_stats_tree.column("Module", width=200, anchor="center")
            self.class_stats_tree.column("Num Classes", width=100, anchor="center")
            self.class_stats_tree.column("Total Students", width=100, anchor="center")
            self.class_stats_tree.pack(padx=10, pady=10, fill="both", expand=True)

            # Hiển thị bảng
            for item in self.class_stats_tree.get_children():
                self.class_stats_tree.delete(item)
            for row in rows:
                self.class_stats_tree.insert("", "end", values=row)
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu thống kê: {e}")
        finally:
            cursor.close()
            conn.close()

    def show_class_stats_chart(self):
        year = self.stats_year_combobox.get().strip()
        if not year:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn năm học!")
            return

        # Lấy dữ liệu thống kê
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            query = """
                SELECT cm.module_name, COUNT(c.class_id) as num_classes, SUM(c.num_students) as total_students
                FROM classes c
                JOIN semesters s ON c.semester_id = s.semester_id
                JOIN course_modules cm ON c.module_id = cm.module_id
                WHERE s.year = %s
                GROUP BY cm.module_id, cm.module_name
            """
            cursor.execute(query, (year,))
            rows = cursor.fetchall()
            if not rows:
                messagebox.showwarning("Cảnh báo", "Không có dữ liệu để thống kê.")
                return

            # Lưu dữ liệu để dùng cho xuất báo cáo
            self.stats_data = [{"Module": row[0], "Num Classes": row[1], "Total Students": row[2]} for row in rows]

            # Xóa nội dung cũ trong class_stats_frame
            for widget in self.class_stats_frame.winfo_children():
                widget.destroy()

            # Vẽ biểu đồ
            labels = [row[0] for row in rows]
            num_classes = [row[1] for row in rows]
            fig, ax = plt.subplots(figsize=(5, 2))
            ax.bar(labels, num_classes, color="#36A2EB")
            ax.set_title(f"Số lớp mở theo học phần ({year})", fontsize=14, pad=15)
            ax.set_xlabel("Học phần", fontsize=12)
            ax.set_ylabel("Số lớp mở", fontsize=12)
            ax.set_ylim(0, max(num_classes) + 1 if num_classes else 1)
            plt.xticks(rotation=0, ha="right")

            # Nhúng biểu đồ vào giao diện
            canvas = FigureCanvasTkAgg(fig, master=self.class_stats_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu thống kê: {e}")
        finally:
            cursor.close()
            conn.close()


    def toggle_submenu(self, main_item):
        # Ẩn tất cả các drop down khác trước
        for other_main_item in self.submenu_visible:
            if other_main_item != main_item and self.submenu_visible[other_main_item]:
                self.submenu_visible[other_main_item] = False
                self.hide_submenu_buttons(other_main_item)
                # Cập nhật biểu tượng mũi tên cho mục chính khác
                button = getattr(self, f"{other_main_item.lower().replace(' ', '_')}_button", None)
                if button:
                    button.configure(text=f"▶ {other_main_item}")

        # Toggle trạng thái hiển thị của mục chính hiện tại
        self.submenu_visible[main_item] = not self.submenu_visible[main_item]

        # Cập nhật biểu tượng mũi tên cho mục chính hiện tại
        button = getattr(self, f"{main_item.lower().replace(' ', '_')}_button", None)
        if button:
            button.configure(text=f"▼ {main_item}" if self.submenu_visible[main_item] else f"▶ {main_item}")

        if self.submenu_visible[main_item]:
            # Hiển thị các tab con
            button_height = 40  # Chiều cao của mỗi button
            for idx, item in enumerate(self.submenu_items[main_item]):
                btn = CTkButton(self.submenu_frames[main_item], text=f"  {item}", font=("Helvetica", 14), fg_color="transparent",
                                text_color="#DDEEFF", hover_color="#5A9BFF",
                                command=lambda x=item: self.switch_tab(x))
                btn.place(relx=0, rely=0, y=-button_height, relwidth=1.0)
                self.submenu_buttons[main_item].append(btn)
                # Hiệu ứng slide down
                self.slide_down(btn, idx * button_height, -button_height)
            # Đặt chiều cao của frame để chứa tất cả các button
            self.submenu_frames[main_item].configure(height=len(self.submenu_items[main_item]) * button_height)
        else:
            # Ẩn các tab con
            self.hide_submenu_buttons(main_item)

    def hide_submenu_buttons(self, main_item):
        buttons = self.submenu_buttons[main_item]
        if not buttons:
            return

        def destroy_buttons():
            for btn in buttons:
                btn.destroy()
            self.submenu_buttons[main_item] = []
            # Đặt lại chiều cao frame về 0 sau khi ẩn
            self.submenu_frames[main_item].configure(height=0)

        # Hiệu ứng slide up cho tất cả các button
        button_height = 40
        for idx, btn in enumerate(buttons):
            target_y = -button_height
            current_y = idx * button_height
            self.slide_up(btn, target_y, current_y, callback=lambda: destroy_buttons() if btn == buttons[-1] else None)

    def slide_down(self, button, target_y, current_y):
        if current_y < target_y:
            button.place(relx=0, rely=0, y=current_y, relwidth=1.0)
            button.after(10, lambda: self.slide_down(button, target_y, current_y + 5))
        else:
            button.place(relx=0, rely=0, y=target_y, relwidth=1.0)

    def slide_up(self, button, target_y, current_y, callback=None):
        if current_y > target_y:
            button.place(relx=0, rely=0, y=current_y, relwidth=1.0)
            button.after(10, lambda: self.slide_up(button, target_y, current_y - 5, callback))
        else:
            button.place(relx=0, rely=0, y=target_y, relwidth=1.0)
            if callback:
                callback()

    def edit_assignment(self):
        if not hasattr(self, 'selected_class_id'):
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn lớp học phần để sửa!")
            return

        class_id = self.selected_class_id

        # Kiểm tra xem lớp học đã được phân công chưa
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT assignment_id, teacher_id FROM assignments WHERE class_id = %s", (class_id,))
            existing_assignment = cursor.fetchone()
            if not existing_assignment:
                messagebox.showwarning("Cảnh báo", "Lớp học này chưa được phân công! Vui lòng phân công trước khi sửa.")
                return
            assignment_id, current_teacher_id = existing_assignment
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể kiểm tra phân công: {e}")
            return
        finally:
            cursor.close()
            conn.close()

        # Tạo cửa sổ pop-up
        edit_window = CTkToplevel(self.window)
        edit_window.title("Sửa phân công giảng viên")
        edit_window.geometry("400x200")
        edit_window.resizable(False, False)

        # Frame chứa các trường nhập liệu
        form_frame = CTkFrame(edit_window, fg_color="transparent")
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Giáo viên
        CTkLabel(form_frame, text="Chọn giảng viên:", font=("Helvetica", 12)).pack(pady=(5, 0))
        teachers = self.get_teachers()
        teacher_var = CTkComboBox(form_frame, width=350, values=teachers)
        teacher_var.pack(pady=5)
        if teachers and teachers[0] not in ["Không có giáo viên", "Lỗi tải giáo viên"]:
            # Tìm và đặt giảng viên hiện tại
            for teacher in teachers:
                if teacher.startswith(current_teacher_id):
                    teacher_var.set(teacher)
                    break
            else:
                teacher_var.set(teachers[0])
        else:
            teacher_var.set(teachers[0])

        # Hàm xử lý khi nhấn nút "Lưu"
        def save_assignment():
            teacher = teacher_var.get().strip()

            if not teacher or teacher in ["Không có giáo viên", "Lỗi tải giáo viên"]:
                messagebox.showerror("Lỗi", "Không có giáo viên để sửa phân công!", parent=edit_window)
                return

            teacher_id = teacher.split(":")[0].strip()

            # Hỏi xác nhận
            confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn sửa phân công này?", parent=edit_window)
            if not confirm:
                return

            # Cập nhật phân công
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("UPDATE assignments SET teacher_id = %s WHERE assignment_id = %s", (teacher_id, assignment_id))
                conn.commit()
                messagebox.showinfo("Thành công", "Sửa phân công thành công", parent=edit_window)
                self.load_classes_by_semester(None)
                edit_window.destroy()
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể sửa phân công: {e}", parent=edit_window)
            finally:
                cursor.close()
                conn.close()

        # Hàm đóng cửa sổ
        def cancel():
            edit_window.destroy()

        # Nút Lưu và Hủy
        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        CTkButton(button_frame, text="Lưu", fg_color="#0085FF", command=save_assignment, width=100).pack(side="left", padx=5)
        CTkButton(button_frame, text="Hủy", fg_color="#6C757D", command=cancel, width=100).pack(side="left", padx=5)