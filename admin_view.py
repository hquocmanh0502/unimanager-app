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
import customtkinter as ctk
import pandas as pd
import tkinter as tk
from a import ModernNavbar

class AdminView:
    def __init__(self, window, user):
        self.window = window
        self.user = user
        self.window.title("Giao diện Khoa")
        self.window.geometry("1700x700")

        # Khởi tạo admin_id nếu là tài khoản admin
        if self.user['role'] == 'Admin':
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (self.user['user_id'],))
                result = cursor.fetchone()
                if result:
                    self.user['admin_id'] = result[0]
                    cursor.execute("SELECT dept_id FROM departments LIMIT 1")
                    dept_result = cursor.fetchone()
                    if dept_result:
                        self.user['dept_id'] = dept_result[0]
                    print(f"Debug: User admin_id: {self.user['admin_id']}, dept_id: {self.user['dept_id']}")
                else:
                    messagebox.showerror("Lỗi", "Không tìm thấy admin tương ứng")
                    self.window.destroy()
                    return
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể tải thông tin admin: {e}")
                self.window.destroy()
                return
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
        
        # Frame chính chứa toàn bộ giao diện 
        self.main_frame = CTkFrame(self.window)
        self.main_frame.pack(fill="both", expand=True)

        # Định nghĩa menu_items cho navbar
        self.navbar_menu_items = [
            {
                "label": "Quản lý giáo viên",
                "icon": "👨",
                "fg_color": "#3E54AC",
                "hover_color": "#4B67D6",
                "text_color": "white",
                "command": None,
                "submenu": [
                    {"label": "Bằng cấp", "command": lambda: self.switch_tab("Bằng cấp")},
                    {"label": "Khoa", "command": lambda: self.switch_tab("Khoa")},
                    {"label": "Giáo viên", "command": lambda: self.switch_tab("Giáo viên")}
                ]
            },
            {
                "label": "Quản lý lớp học phần",
                "icon": "📚",
                "fg_color": "#3E54AC",
                "hover_color": "#4B67D6",
                "text_color": "white",
                "command": None,
                "submenu": [
                    {"label": "Học phần", "command": lambda: self.switch_tab("Học phần")},
                    {"label": "Kỳ học", "command": lambda: self.switch_tab("Kỳ học")},
                    {"label": "Lớp học", "command": lambda: self.switch_tab("Lớp học")},
                    {"label": "Phân công", "command": lambda: self.switch_tab("Phân công")}
                ]
            },
            {
                "label": "Thống kê",
                "icon": "📊",
                "fg_color": "#3E54AC",
                "hover_color": "#4B67D6",
                "text_color": "white",
                "command": None,
                "submenu": [
                    {"label": "Thống kê giáo viên", "command": lambda: self.switch_tab("Thống kê giáo viên")},
                    {"label": "Thống kê lớp", "command": lambda: self.switch_tab("Thống kê lớp")}
                ]
            },
            {
                "label": "Tiền dạy",
                "icon": "💰",
                "fg_color": "#3E54AC",
                "hover_color": "#4B67D6",
                "text_color": "white",
                "command": None,
                "submenu": [
                    {"label": "Định mức tiền theo tiết", "command": lambda: self.switch_tab("Định mức tiền theo tiết")},
                    {"label": "Hệ số giáo viên", "command": lambda: self.switch_tab("Hệ số giáo viên")},
                    {"label": "Hệ số lớp", "command": lambda: self.switch_tab("Hệ số lớp")},
                    {"label": "Tính tiền dạy", "command": lambda: self.switch_tab("Tính tiền dạy")}
                ]
            },
            {
                "label": "Báo cáo",
                "icon": "📈",
                "fg_color": "#3E54AC",
                "hover_color": "#4B67D6",
                "text_color": "white",
                "command": lambda: self.switch_tab("Báo cáo")  # Chỉ giữ command mà không có submenu
            }
        ]

        # Tạo navbar với menu_items và logout_callback
        self.navbar = ModernNavbar(self.main_frame, fg_color="#2B3467", menu_items=self.navbar_menu_items, logout_callback=self.logout)
        self.navbar.pack(side="left", fill="y")

        # Cập nhật thông tin người dùng trong footer của navbar
        self.navbar.footer.winfo_children()[1].winfo_children()[0].configure(text=self.user['username'])
        self.navbar.footer.winfo_children()[1].winfo_children()[1].configure(text=self.user['role'])

        # Frame chính bên phải chứa nội dung
        self.content_frame = CTkFrame(self.main_frame, fg_color=("#E6F0FA", "#B0C4DE"))
        self.content_frame.pack(side="right", fill="both", expand=True)

        # Frame chứa các tab
        self.tab_frame = CTkFrame(self.content_frame, fg_color="transparent")
        self.tab_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Khởi tạo các tab
        self.degree_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.dept_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.teacher_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.stats_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.module_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.class_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.semester_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.class_stats_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.teacher_coefficient_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.teaching_rate_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.class_coefficient_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.salary_calc_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.report_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.assignment_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)  # Thêm tab Phân công

        # Gọi các hàm setup cho các tab
        self.setup_degree_tab()
        self.setup_dept_tab()
        self.setup_teacher_tab()
        self.setup_stats_tab()
        self.setup_module_tab()
        self.setup_class_tab()
        self.setup_semester_tab()
        self.setup_class_stats_tab()
        self.setup_teacher_coefficient_tab()
        self.setup_teaching_rate_tab()
        self.setup_class_coefficient_tab()
        self.setup_salary_calc_tab()
        self.setup_report_tab()
        self.setup_assignment_tab()

        # Hiển thị tab mặc định
        self.current_tab = self.teacher_tab
        self.current_tab.pack(fill="both", expand=True)

        # Khởi tạo các biến cho tính lương
        self.salary_calc_teacher_name_value = None
        self.salary_calc_teacher_id_value = None
        self.salary_calc_degree_value = None
        self.salary_calc_dept_value = None
        self.salary_calc_teacher_coeff_value = None
        self.salary_calc_rate_value = None
        self.salary_calc_period_value = None

        # Khởi tạo các biến cho báo cáo lương
        self.salary_report_teacher_name_value = None
        self.salary_report_teacher_id_value = None
        self.salary_report_teacher_degree_value = None
        self.salary_report_teacher_dept_value = None
        self.salary_report_total_salary_label = None
        self.salary_report_total_classes_label = None
        self.salary_report_total_periods_label = None
        self.salary_report_total_salary_temp_label = None

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

    def setup_degree_tab(self):
        # Tiêu đề tab
        header_frame = CTkFrame(self.degree_tab, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)
        CTkLabel(header_frame, text="Quản lý bằng cấp", font=("Helvetica", 18, "bold"), text_color="black").pack(side="left")
        CTkButton(header_frame, text="Thêm bằng cấp mới", fg_color="#0085FF", command=self.add_degree).pack(side="right")

        # Frame chứa heading và danh sách
        self.degree_container = CTkFrame(self.degree_tab, fg_color="#FFFFFF", corner_radius=10)
        self.degree_container.pack(padx=10, pady=10, fill="both", expand=True)

        # Heading
        heading_frame = CTkFrame(self.degree_container, fg_color="#D3D3D3", corner_radius=0)
        heading_frame.pack(fill="x", padx=5, pady=(5, 0))
        
        # Tạo các cột heading với chiều rộng lớn hơn để lấp đầy không gian
        # Tạo các cột heading với chiều rộng lớn hơn để lấp đầy không gian
        CTkLabel(heading_frame, text="Mã bằng cấp", font=("Helvetica", 12, "bold"), text_color="black", width=160, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Tên bằng cấp", font=("Helvetica", 12, "bold"), text_color="black", width=400, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Tên viết tắt", font=("Helvetica", 12, "bold"), text_color="black", width=250, anchor="center").pack(side="left", padx=5)
        # CTkLabel(heading_frame, text="Hệ số", font=("Helvetica", 12, "bold"), text_color="black", width=150, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Thao tác", font=("Helvetica", 12, "bold"), text_color="black", width=200, anchor="center").pack(side="left", padx=5)

        # Frame chứa danh sách bằng cấp
        self.degree_list_frame = CTkFrame(self.degree_container, fg_color="transparent")
        self.degree_list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Tải dữ liệu bằng cấp
        self.load_degrees()

    def setup_dept_tab(self):
        # Tiêu đề tab
        header_frame = CTkFrame(self.dept_tab, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)
        CTkLabel(header_frame, text="Quản lý khoa", font=("Helvetica", 18, "bold"), text_color="black").pack(side="left")
        CTkButton(header_frame, text="Thêm khoa mới", fg_color="#0085FF", command=self.add_dept).pack(side="right")

        # Frame chứa heading và danh sách
        self.dept_container = CTkFrame(self.dept_tab, fg_color="#FFFFFF", corner_radius=10)
        self.dept_container.pack(padx=10, pady=10, fill="both", expand=True)

        # Heading
        heading_frame = CTkFrame(self.dept_container, fg_color="#D3D3D3", corner_radius=0)
        heading_frame.pack(fill="x", padx=5, pady=(5, 0))
        
        # Tạo các cột heading với chiều rộng điều chỉnh
        CTkLabel(heading_frame, text="Mã khoa", font=("Helvetica", 12, "bold"), text_color="black", width=150, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Tên khoa", font=("Helvetica", 12, "bold"), text_color="black", width=200, anchor="center").pack(side="left", padx=5)  # Giảm từ 450 xuống 400
        CTkLabel(heading_frame, text="Tên viết tắt", font=("Helvetica", 12, "bold"), text_color="black", width=150, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Mô tả nhiệm vụ", font=("Helvetica", 12, "bold"), text_color="black", width=300, anchor="center").pack(side="left", padx=5)  # Giảm từ 600 xuống 500
        CTkLabel(heading_frame, text="Thao tác", font=("Helvetica", 12, "bold"), text_color="black", width=250, anchor="center").pack(side="left", padx=5)  # Tăng từ 250 lên 350

        # Frame chứa danh sách khoa
        self.dept_list_frame = CTkFrame(self.dept_container, fg_color="transparent")
        self.dept_list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Tải dữ liệu khoa
        self.load_depts()

    def setup_teacher_tab(self):
        # Tiêu đề tab
        header_frame = CTkFrame(self.teacher_tab, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)
        CTkLabel(header_frame, text="Quản lý giáo viên", font=("Helvetica", 18, "bold"), text_color="black").pack(side="left")
        CTkButton(header_frame, text="Thêm giáo viên mới", fg_color="#0085FF", command=self.add_teacher).pack(side="right")

        # Frame chứa heading và danh sách
        self.teacher_container = CTkFrame(self.teacher_tab, fg_color="#FFFFFF", corner_radius=10)
        self.teacher_container.pack(padx=10, pady=10, fill="both", expand=True)

        # Heading
        heading_frame = CTkFrame(self.teacher_container, fg_color="#D3D3D3", corner_radius=0)
        heading_frame.pack(fill="x", padx=5, pady=(5, 0))
        
        # Tạo các cột heading
        CTkLabel(heading_frame, text="Mã giáo viên", font=("Helvetica", 12, "bold"), text_color="black", width=80, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Họ tên", font=("Helvetica", 12, "bold"), text_color="black", width=120, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Ngày sinh", font=("Helvetica", 12, "bold"), text_color="black", width=80, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Điện thoại", font=("Helvetica", 12, "bold"), text_color="black", width=80, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Email", font=("Helvetica", 12, "bold"), text_color="black", width=180, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Khoa", font=("Helvetica", 12, "bold"), text_color="black", width=200, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Bằng cấp", font=("Helvetica", 12, "bold"), text_color="black", width=120, anchor="center").pack(side="left", padx=5)
        # CTkLabel(heading_frame, text="Hệ số", font=("Helvetica", 12, "bold"), text_color="black", width=60, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Thao tác", font=("Helvetica", 12, "bold"), text_color="black", width=100, anchor="center").pack(side="left", padx=5)

        # Frame chứa danh sách giáo viên
        self.teacher_list_frame = CTkFrame(self.teacher_container, fg_color="transparent")
        self.teacher_list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Tải dữ liệu giáo viên
        self.load_teachers()

    def setup_stats_tab(self):
    # Tiêu đề
        header_frame = CTkFrame(self.stats_tab, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)
        CTkLabel(header_frame, text="Thống kê giáo viên", font=("Helvetica", 18, "bold"), text_color="black").pack(side="left")
        
        # Nút hành động
        button_frame = CTkFrame(header_frame, fg_color="transparent")
        button_frame.pack(side="right")
        CTkButton(button_frame, text="Xuất báo cáo", font=("Helvetica", 12), fg_color="#36A2EB", hover_color="#2A82C5", 
                command=self.export_stats).pack(side="left", padx=5)
        CTkButton(button_frame, text="Cập nhật", font=("Helvetica", 12), fg_color="#36A2EB", hover_color="#2A82C5", 
                command=self.refresh_stats).pack(side="left", padx=5)

        # Thống kê tổng quan
        overview_frame = CTkFrame(self.stats_tab, fg_color="transparent")
        overview_frame.pack(fill="x", padx=10, pady=10)
        
        # Tổng số giáo viên
        total_teachers_frame = CTkFrame(overview_frame, fg_color=("#BBDEFB", "#64B5F6"), corner_radius=12, 
                                        border_width=3, border_color="#1976D2", width=200, height=100)
        total_teachers_frame.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        total_teachers_frame.pack_propagate(False)
        self.total_teachers_label = CTkLabel(total_teachers_frame, text="0", font=("Helvetica", 28, "bold"), text_color="#0D47A1")
        self.total_teachers_label.pack(pady=(15, 5))
        CTkLabel(total_teachers_frame, text="Tổng số giáo viên", font=("Helvetica", 14, "bold"), text_color="#0D47A1").pack(pady=(0, 10))

        # Số bằng cấp
        degree_count_frame = CTkFrame(overview_frame, fg_color=("#C8E6C9", "#81C784"), corner_radius=12, 
                                    border_width=3, border_color="#388E3C", width=200, height=100)
        degree_count_frame.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        degree_count_frame.pack_propagate(False)
        self.degree_count_label = CTkLabel(degree_count_frame, text="0", font=("Helvetica", 28, "bold"), text_color="#1B5E20")
        self.degree_count_label.pack(pady=(15, 5))
        CTkLabel(degree_count_frame, text="Số bằng cấp", font=("Helvetica", 14, "bold"), text_color="#1B5E20").pack(pady=(0, 10))

        # Số khoa
        total_depts_frame = CTkFrame(overview_frame, fg_color=("#FFECB3", "#FFB300"), corner_radius=12, 
                                    border_width=3, border_color="#F57C00", width=200, height=100)
        total_depts_frame.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        total_depts_frame.pack_propagate(False)
        self.total_depts_label = CTkLabel(total_depts_frame, text="0", font=("Helvetica", 28, "bold"), text_color="#E65100")
        self.total_depts_label.pack(pady=(15, 5))
        CTkLabel(total_depts_frame, text="Số khoa", font=("Helvetica", 14, "bold"), text_color="#E65100").pack(pady=(0, 10))

        # Tab điều hướng
        tab_frame = CTkFrame(self.stats_tab, fg_color="#FFFFFF", corner_radius=10)
        tab_frame.pack(fill="x", padx=10, pady=10)
        
        CTkButton(tab_frame, text="Thống kê theo độ tuổi", font=("Helvetica", 14), fg_color="#36A2EB", hover_color="#2A82C5", 
                command=self.show_age_chart).pack(side="left", padx=5, pady=5, fill="x", expand=True)
        CTkButton(tab_frame, text="Thống kê theo bằng cấp", font=("Helvetica", 14), fg_color="#FF6384", hover_color="#E55773", 
                command=self.show_degree_chart).pack(side="left", padx=5, pady=5, fill="x", expand=True)
        CTkButton(tab_frame, text="Thống kê theo khoa", font=("Helvetica", 14), fg_color="#FFCE56", hover_color="#E5B74C", 
                command=self.show_dept_chart).pack(side="left", padx=5, pady=5, fill="x", expand=True)

        # Frame chứa biểu đồ và bảng
        self.chart_frame = CTkFrame(self.stats_tab, fg_color="#FFFFFF", corner_radius=10)
        self.chart_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Khởi tạo tab đầu tiên và cập nhật nhãn
        self.update_labels()
        self.show_age_chart()

    def clear_chart_frame(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

    def show_age_chart(self):
        self.clear_chart_frame()
        
        age_labels, age_data = self.get_age_distribution()
        if not age_labels or not age_data:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu độ tuổi để hiển thị.")
            return

        total = sum(age_data)
        ratios = [f"{(count/total*100):.1f}%" if total > 0 else "0.0%" for count in age_data]

        # Frame chính
        main_frame = CTkFrame(self.chart_frame, fg_color="transparent") 
        main_frame.pack(fill="both", expand=True)

        # Frame tiêu đề
        title_frame = CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(pady=(5,10))
        CTkLabel(title_frame, text="Phân bố độ tuổi giáo viên", 
                font=("Helvetica", 16, "bold"), 
                text_color="#0D47A1").pack()

        # Frame chứa biểu đồ và bảng
        content_frame = CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        
        # Chia frame thành 2 cột với tỷ lệ 7:3
        content_frame.grid_columnconfigure(0, weight=7)  # Biểu đồ chiếm 70%
        content_frame.grid_columnconfigure(1, weight=3)  # Bảng chiếm 30%

        # Frame biểu đồ với viền và nền trắng 
        chart_container = CTkFrame(content_frame, fg_color="#FFFFFF", corner_radius=10, border_width=1, border_color="#E0E0E0")
        chart_container.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Vẽ biểu đồ
        fig, ax = plt.subplots(figsize=(8, 4))  # Điều chỉnh kích thước biểu đồ
        bars = ax.bar(age_labels, age_data, color=["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"])

        # Thêm giá trị và tỉ lệ phần trăm lên đỉnh của mỗi cột
        for bar, ratio in zip(bars, ratios):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}\n{ratio}',
                    ha='center', va='bottom')

        ax.set_xlabel("Nhóm tuổi", fontsize=10)
        ax.set_ylabel("Số giáo viên", fontsize=10) 
        ax.set_ylim(0, max(age_data) + 1 if age_data else 1)
        plt.xticks(rotation=0)
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Frame bảng thống kê chi tiết
        table_container = CTkFrame(content_frame, fg_color="#FFFFFF", corner_radius=10, border_width=1, border_color="#E0E0E0")
        table_container.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Tiêu đề bảng
        CTkLabel(table_container, 
                text="Chi tiết thống kê", 
                font=("Helvetica", 14, "bold"),
                text_color="#0D47A1").pack(pady=5)

        # Tạo frame riêng cho bảng với chiều cao cố định
        tree_frame = CTkFrame(table_container, fg_color="transparent", height=150)  # Chiều cao cố định
        tree_frame.pack(fill="x", padx=5, pady=5)
        tree_frame.pack_propagate(False)  # Ngăn frame tự co giãn

        # Style cho bảng
        style = ttk.Style()
        style.configure("Stats.Treeview", font=("Helvetica", 10), rowheight=25)
        style.configure("Stats.Treeview.Heading", font=("Helvetica", 10, "bold"))
        
        # Tạo bảng
        tree = ttk.Treeview(tree_frame, columns=("Age", "Count", "Ratio"), 
                        show="headings", style="Stats.Treeview", height=5)
        
        # Định dạng cột
        tree.heading("Age", text="Độ tuổi")
        tree.heading("Count", text="Số lượng") 
        tree.heading("Ratio", text="Tỷ lệ")
        
        tree.column("Age", width=80, anchor="center")
        tree.column("Count", width=80, anchor="center")
        tree.column("Ratio", width=80, anchor="center")
        
        tree.pack(fill="both", expand=True)

        # Thêm dữ liệu vào bảng
        for label, count, ratio in zip(age_labels, age_data, ratios):
            tree.insert("", "end", values=(label, count, ratio))

    def show_degree_chart(self):
        self.clear_chart_frame()
        
        degree_labels, degree_data = self.get_degree_distribution()
        if not degree_labels or not degree_data:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu bằng cấp để hiển thị.")
            return

        total = sum(degree_data)
        ratios = [f"{(count/total*100):.1f}%" if total > 0 else "0.0%" for count in degree_data]

        # Frame chính
        main_frame = CTkFrame(self.chart_frame, fg_color="transparent") 
        main_frame.pack(fill="both", expand=True)

        # Frame tiêu đề
        title_frame = CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(pady=(5,10))
        CTkLabel(title_frame, text="Phân bố bằng cấp giáo viên", 
                font=("Helvetica", 16, "bold"), 
                text_color="#0D47A1").pack()

        # Frame chứa biểu đồ và bảng
        content_frame = CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        
        content_frame.grid_columnconfigure(0, weight=7)
        content_frame.grid_columnconfigure(1, weight=3)

        # Frame biểu đồ
        chart_container = CTkFrame(content_frame, fg_color="#FFFFFF", corner_radius=10, border_width=1, border_color="#E0E0E0")
        chart_container.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Vẽ biểu đồ
        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.bar(degree_labels, degree_data, color=["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0"])

        # Thêm giá trị và tỉ lệ lên đỉnh cột
        for bar, ratio in zip(bars, ratios):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}\n{ratio}',
                    ha='center', va='bottom')

        ax.set_xlabel("Bằng cấp", fontsize=10)
        ax.set_ylabel("Số giáo viên", fontsize=10)
        ax.set_ylim(0, max(degree_data) + 1 if degree_data else 1)
        plt.xticks(rotation=15)
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Frame bảng thống kê
        table_container = CTkFrame(content_frame, fg_color="#FFFFFF", corner_radius=10, border_width=1, border_color="#E0E0E0")
        table_container.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        CTkLabel(table_container, text="Chi tiết thống kê", 
                font=("Helvetica", 14, "bold"),
                text_color="#0D47A1").pack(pady=5)

        tree_frame = CTkFrame(table_container, fg_color="transparent", height=150)
        tree_frame.pack(fill="x", padx=5, pady=5)
        tree_frame.pack_propagate(False)

        style = ttk.Style()
        style.configure("Stats.Treeview", font=("Helvetica", 10), rowheight=25)
        style.configure("Stats.Treeview.Heading", font=("Helvetica", 10, "bold"))
        
        tree = ttk.Treeview(tree_frame, columns=("Degree", "Count", "Ratio"), 
                        show="headings", style="Stats.Treeview", height=5)
        
        tree.heading("Degree", text="Bằng cấp")
        tree.heading("Count", text="Số lượng")
        tree.heading("Ratio", text="Tỷ lệ")
        
        tree.column("Degree", width=80, anchor="center")
        tree.column("Count", width=80, anchor="center")
        tree.column("Ratio", width=80, anchor="center")
        
        tree.pack(fill="both", expand=True)

        for label, count, ratio in zip(degree_labels, degree_data, ratios):
            tree.insert("", "end", values=(label, count, ratio))

    def show_dept_chart(self):
        self.clear_chart_frame()
        
        dept_labels, dept_data = self.get_dept_distribution()
        if not dept_labels or not dept_data:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu khoa để hiển thị.")
            return

        total = sum(dept_data)
        ratios = [f"{(count/total*100):.1f}%" if total > 0 else "0.0%" for count in dept_data]

        # Frame chính
        main_frame = CTkFrame(self.chart_frame, fg_color="transparent") 
        main_frame.pack(fill="both", expand=True)

        # Frame tiêu đề
        title_frame = CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(pady=(5,10))
        CTkLabel(title_frame, text="Phân bố giáo viên theo khoa", 
                font=("Helvetica", 16, "bold"), 
                text_color="#0D47A1").pack()

        # Frame chứa biểu đồ và bảng
        content_frame = CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        
        content_frame.grid_columnconfigure(0, weight=7)
        content_frame.grid_columnconfigure(1, weight=3)

        # Frame biểu đồ
        chart_container = CTkFrame(content_frame, fg_color="#FFFFFF", corner_radius=10, border_width=1, border_color="#E0E0E0")
        chart_container.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Vẽ biểu đồ
        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.bar(dept_labels, dept_data, color=["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"])

        # Thêm giá trị và tỉ lệ lên đỉnh cột
        for bar, ratio in zip(bars, ratios):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}\n{ratio}',
                    ha='center', va='bottom')

        ax.set_xlabel("Khoa", fontsize=10)
        ax.set_ylabel("Số giáo viên", fontsize=10)
        ax.set_ylim(0, max(dept_data) + 1 if dept_data else 1)
        plt.xticks(rotation=15)
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Frame bảng thống kê
        table_container = CTkFrame(content_frame, fg_color="#FFFFFF", corner_radius=10, border_width=1, border_color="#E0E0E0")
        table_container.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        CTkLabel(table_container, text="Chi tiết thống kê", 
                font=("Helvetica", 14, "bold"),
                text_color="#0D47A1").pack(pady=5)

        tree_frame = CTkFrame(table_container, fg_color="transparent", height=150)
        tree_frame.pack(fill="x", padx=5, pady=5)
        tree_frame.pack_propagate(False)

        style = ttk.Style()
        style.configure("Stats.Treeview", font=("Helvetica", 10), rowheight=25)
        style.configure("Stats.Treeview.Heading", font=("Helvetica", 10, "bold"))
        
        tree = ttk.Treeview(tree_frame, columns=("Dept", "Count", "Ratio"), 
                        show="headings", style="Stats.Treeview", height=5)
        
        tree.heading("Dept", text="Khoa")
        tree.heading("Count", text="Số lượng")
        tree.heading("Ratio", text="Tỷ lệ")
        
        tree.column("Dept", width=80, anchor="center")
        tree.column("Count", width=80, anchor="center")
        tree.column("Ratio", width=80, anchor="center")
        
        tree.pack(fill="both", expand=True)

        for label, count, ratio in zip(dept_labels, dept_data, ratios):
            tree.insert("", "end", values=(label, count, ratio))

    def export_stats(self):
        import pandas as pd
        
        age_labels, age_data = self.get_age_distribution()
        degree_labels, degree_data = self.get_degree_distribution()
        
        # Lấy dữ liệu khoa với tên đầy đủ
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
            dept_labels = []
            dept_data = []
            for row in cursor.fetchall():
                dept_name, count = row
                dept_labels.append(dept_name)
                dept_data.append(count)
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu khoa: {e}")
            return
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        
        try:
            # Tạo các DataFrame
            age_df = pd.DataFrame({
                "Độ tuổi": age_labels,
                "Số lượng": age_data,
                "Tỷ lệ (%)": [f"{(count/sum(age_data)*100):.1f}" if sum(age_data) > 0 else "0.0" for count in age_data]
            })
            degree_df = pd.DataFrame({
                "Bằng cấp": degree_labels,
                "Số lượng": degree_data,
                "Tỷ lệ (%)": [f"{(count/sum(degree_data)*100):.1f}" if sum(degree_data) > 0 else "0.0" for count in degree_data]
            })
            dept_df = pd.DataFrame({
                "Khoa": dept_labels,
                "Số lượng": dept_data,
                "Tỷ lệ (%)": [f"{(count/sum(dept_data)*100):.1f}" if sum(dept_data) > 0 else "0.0" for count in dept_data]
            })

            # Xuất ra Excel
            with pd.ExcelWriter("teacher_statistics.xlsx", engine="xlsxwriter") as writer:
                age_df.to_excel(writer, sheet_name="Age_Distribution", index=False)
                degree_df.to_excel(writer, sheet_name="Degree_Distribution", index=False)
                dept_df.to_excel(writer, sheet_name="Dept_Distribution", index=False)
            
            messagebox.showinfo("Thành công", "Báo cáo đã được xuất ra file: teacher_statistics.xlsx")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất báo cáo: {e}")

    def refresh_stats(self):
        self.update_labels()
        self.show_age_chart()

    def update_labels(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            # Tổng số giáo viên
            cursor.execute("SELECT COUNT(*) FROM teachers")
            total_teachers = cursor.fetchall()[0][0]
            self.total_teachers_label.configure(text=str(total_teachers))
            
            # Số lượng bằng cấp
            cursor.execute("SELECT COUNT(*) FROM degrees")
            degree_count = cursor.fetchall()[0][0]
            self.degree_count_label.configure(text=str(degree_count))
            
            # Số khoa
            cursor.execute("SELECT COUNT(*) FROM departments")
            total_depts = cursor.fetchall()[0][0]
            self.total_depts_label.configure(text=str(total_depts))
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu thống kê: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    from tkcalendar import DateEntry

    def setup_semester_tab(self):
        # Header with title and add button
        header_frame = CTkFrame(self.semester_tab, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)
        CTkLabel(header_frame, text="Quản lý kỳ học", font=("Helvetica", 18, "bold"), text_color="black").pack(side="left")
        CTkButton(header_frame, text="Thêm kỳ học mới", fg_color="#0085FF", command=self.add_semester).pack(side="right")

        # Main container
        self.semester_container = CTkFrame(self.semester_tab, fg_color="#FFFFFF", corner_radius=10)
        self.semester_container.pack(padx=10, pady=10, fill="both", expand=True)

        # Heading row
        heading_frame = CTkFrame(self.semester_container, fg_color="#D3D3D3", corner_radius=0)
        heading_frame.pack(fill="x", padx=5, pady=(5, 0))
        
        # Column headers (giống tab Học phần)
        CTkLabel(heading_frame, text="Mã kỳ", font=("Helvetica", 14, "bold"), text_color="black", width=150, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Tên kỳ", font=("Helvetica", 14, "bold"), text_color="black", width=200, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Năm học", font=("Helvetica", 14, "bold"), text_color="black", width=150, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Ngày bắt đầu", font=("Helvetica", 14, "bold"), text_color="black", width=200, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Ngày kết thúc", font=("Helvetica", 14, "bold"), text_color="black", width=200, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Thao tác", font=("Helvetica", 14, "bold"), text_color="black", width=150, anchor="center").pack(side="left", padx=5)

        # List frame
        self.semester_list_frame = CTkFrame(self.semester_container, fg_color="transparent")
        self.semester_list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Load semester data
        self.load_semesters()


    def setup_class_stats_tab(self):
        # Tiêu đề
        ctk.CTkLabel(self.class_stats_tab, text="Thống kê lớp học phần", font=("Helvetica", 18, "bold"), text_color="black").pack(pady=10)

        # Frame bộ lọc 
        filter_frame = ctk.CTkFrame(self.class_stats_tab, fg_color="#F0F0F0", corner_radius=10)
        filter_frame.pack(padx=10, pady=10, fill="x")
        ctk.CTkLabel(filter_frame, text="Năm học:", font=("Helvetica", 14), text_color="black").pack(side="left", padx=5)
        self.stats_year_combobox = ctk.CTkComboBox(filter_frame, width=200, values=self.get_academic_years(), command=self.update_class_stats)
        self.stats_year_combobox.pack(side="left", padx=5)
        self.stats_year_combobox.set("2025-2026")

        # Frame nút điều hướng
        button_frame = ctk.CTkFrame(self.class_stats_tab, fg_color="transparent")
        button_frame.pack(pady=5)
        ctk.CTkButton(button_frame, text="Biểu đồ", fg_color="#FF6384", hover_color="#E55773", command=self.show_class_stats_chart).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Bảng", fg_color="#36A2EB", hover_color="#2A82C5", command=self.show_class_stats_table).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Xuất Excel", fg_color="#FFCE56", hover_color="#E5B74C", command=self.export_excel).pack(side="left", padx=5)

        # Frame tổng quan với 4 ô thẻ thông tin
        overview_frame = ctk.CTkFrame(self.class_stats_tab, fg_color="transparent")
        overview_frame.pack(fill="x", padx=10, pady=10)

        # Tổng số lớp
        total_classes_card = ctk.CTkFrame(overview_frame, fg_color=("#BBDEFB", "#64B5F6"), corner_radius=12, border_width=3, border_color="#1976D2")
        total_classes_card.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        self.total_classes_label = ctk.CTkLabel(total_classes_card, text="0", font=("Helvetica", 28, "bold"), text_color="#0D47A1")
        self.total_classes_label.pack(pady=(15, 5))
        ctk.CTkLabel(total_classes_card, text="Tổng số lớp", font=("Helvetica", 14, "bold"), text_color="#0D47A1").pack(pady=(0, 10))

        # Tổng số học phần
        total_modules_card = ctk.CTkFrame(overview_frame, fg_color=("#C8E6C9", "#81C784"), corner_radius=12, border_width=3, border_color="#388E3C")
        total_modules_card.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        self.total_modules_label = ctk.CTkLabel(total_modules_card, text="0 học phần", font=("Helvetica", 28, "bold"), text_color="#1B5E20")
        self.total_modules_label.pack(pady=(15, 5))
        ctk.CTkLabel(total_modules_card, text="Học phần", font=("Helvetica", 14, "bold"), text_color="#1B5E20").pack(pady=(0, 10))

        # Tổng sinh viên
        total_students_card = ctk.CTkFrame(overview_frame, fg_color=("#FFECB3", "#FFB300"), corner_radius=12, border_width=3, border_color="#F57C00")
        total_students_card.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        self.total_students_label = ctk.CTkLabel(total_students_card, text="0", font=("Helvetica", 28, "bold"), text_color="#E65100")
        self.total_students_label.pack(pady=(15, 5))
        ctk.CTkLabel(total_students_card, text="Tổng sinh viên", font=("Helvetica", 14, "bold"), text_color="#E65100").pack(pady=(0, 10))

        # Trung bình sinh viên/lớp
        avg_card = ctk.CTkFrame(overview_frame, fg_color=("#E1BEE7", "#BA68C8"), corner_radius=12, border_width=3, border_color="#7B1FA2")
        avg_card.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        self.avg_per_class_label = ctk.CTkLabel(avg_card, text="0", font=("Helvetica", 28, "bold"), text_color="#4A148C")
        self.avg_per_class_label.pack(pady=(15, 5))
        ctk.CTkLabel(avg_card, text="TB SV/Lớp", font=("Helvetica", 14, "bold"), text_color="#4A148C").pack(pady=(0, 10))

        # Frame nội dung (biểu đồ và bảng)
        self.class_stats_frame = ctk.CTkFrame(self.class_stats_tab, fg_color="#FFFFFF", corner_radius=10)
        self.class_stats_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Cập nhật dữ liệu mặc định - hiển thị biểu đồ
        self.update_class_stats()

    def setup_module_tab(self):
        # Header with title and add button
        header_frame = CTkFrame(self.module_tab, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)
        CTkLabel(header_frame, text="Quản lý học phần", font=("Helvetica", 18, "bold"), text_color="black").pack(side="left")
        CTkButton(header_frame, text="Thêm học phần mới", fg_color="#0085FF", command=self.add_module).pack(side="right")

        # Main container
        self.module_container = CTkFrame(self.module_tab, fg_color="#FFFFFF", corner_radius=10)
        self.module_container.pack(padx=10, pady=10, fill="both", expand=True)

        # Heading row
        heading_frame = CTkFrame(self.module_container, fg_color="#D3D3D3", corner_radius=0)
        heading_frame.pack(fill="x", padx=5, pady=(5, 0))
        
        # Column headers (tăng cỡ chữ và chiều rộng cột)
        CTkLabel(heading_frame, text="Mã học phần", font=("Helvetica", 14, "bold"), text_color="black", width=80, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Tên học phần", font=("Helvetica", 14, "bold"), text_color="black", width=300, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Số tín chỉ", font=("Helvetica", 14, "bold"), text_color="black", width=100, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Hệ số học phần", font=("Helvetica", 14, "bold"), text_color="black", width=100, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Số tiết", font=("Helvetica", 14, "bold"), text_color="black", width=100, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Khoa", font=("Helvetica", 14, "bold"), text_color="black", width=100, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Thao tác", font=("Helvetica", 14, "bold"), text_color="black", width=150, anchor="center").pack(side="left", padx=5)

        # List frame
        self.module_list_frame = CTkFrame(self.module_container, fg_color="transparent")
        self.module_list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Load module data
        self.load_modules()

    
    def setup_class_tab(self):
        # Header with title and add button
        header_frame = CTkFrame(self.class_tab, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)
        CTkLabel(header_frame, text="Quản lý lớp học phần", font=("Helvetica", 18, "bold"), text_color="black").pack(side="left")
        CTkButton(header_frame, text="Thêm lớp học phần", fg_color="#0085FF", command=self.add_classes).pack(side="right")

        # Filter frame (các combobox lọc)
        filter_frame = CTkFrame(self.class_tab, fg_color="transparent")
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Filter by Semester
        semester_filter_frame = CTkFrame(filter_frame, fg_color="transparent")
        semester_filter_frame.pack(side="left", padx=(0, 10))
        CTkLabel(semester_filter_frame, text="Kỳ học:", font=("Helvetica", 12), text_color="black").pack(side="left", padx=(0, 5))
        semesters = self.get_semesters()  # Lấy danh sách semester_id từ CSDL
        self.semester_filter = CTkComboBox(semester_filter_frame, values=["Tất cả"] + semesters, width=150, command=lambda value: [print(f"Debug: Bấm vào 'Kỳ học', giá trị chọn: {value}"), self.filter_classes(value)])
        self.semester_filter.pack(side="left")
        self.semester_filter.set("Tất cả")

        # Filter by Module
        module_filter_frame = CTkFrame(filter_frame, fg_color="transparent")
        module_filter_frame.pack(side="left", padx=(0, 10))
        CTkLabel(module_filter_frame, text="Học phần:", font=("Helvetica", 12), text_color="black").pack(side="left", padx=(0, 5))
        modules = [module.split(":")[1].strip() for module in self.get_modules()]  # Lấy danh sách module_name
        self.module_filter = CTkComboBox(module_filter_frame, values=["Tất cả"] + modules, width=200, command=lambda value: [print(f"Debug: Bấm vào 'Học phần', giá trị chọn: {value}"), self.filter_classes(value)])
        self.module_filter.pack(side="left")
        self.module_filter.set("Tất cả")

        # Filter by Assignment Status
        status_filter_frame = CTkFrame(filter_frame, fg_color="transparent")
        status_filter_frame.pack(side="left", padx=(0, 10))
        CTkLabel(status_filter_frame, text="Trạng thái:", font=("Helvetica", 12), text_color="black").pack(side="left", padx=(0, 5))
        self.status_filter = CTkComboBox(status_filter_frame, values=["Tất cả", "Đã phân công", "Chưa phân công"], width=150, command=lambda value: [print(f"Debug: Bấm vào 'Trạng thái', giá trị chọn: {value}"), self.filter_classes(value)])
        self.status_filter.pack(side="left")
        self.status_filter.set("Tất cả")

        # Main container
        self.class_container = CTkFrame(self.class_tab, fg_color="#FFFFFF", corner_radius=10)
        self.class_container.pack(padx=10, pady=10, fill="both", expand=True)

        # Heading row
        heading_frame = CTkFrame(self.class_container, fg_color="#D3D3D3", corner_radius=0)
        heading_frame.pack(fill="x", padx=5, pady=(5, 0))
        
        # Column headers
        CTkLabel(heading_frame, text="Kỳ học", font=("Helvetica", 14, "bold"), text_color="black", width=70, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Học phần", font=("Helvetica", 14, "bold"), text_color="black", width=150, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Mã lớp", font=("Helvetica", 14, "bold"), text_color="black", width=70, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Tên lớp", font=("Helvetica", 14, "bold"), text_color="black", width=220, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Số sinh viên", font=("Helvetica", 14, "bold"), text_color="black", width=100, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Số SV thực tế", font=("Helvetica", 14, "bold"), text_color="black", width=120, anchor="center").pack(side="left", padx=5)  # Thêm cột mới
        CTkLabel(heading_frame, text="Giảng viên", font=("Helvetica", 14, "bold"), text_color="black", width=150, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Thao tác", font=("Helvetica", 14, "bold"), text_color="black", width=200, anchor="center").pack(side="left", padx=5)

        # List frame (dùng CTkScrollableFrame)
        self.class_list_frame = CTkScrollableFrame(self.class_container, fg_color="transparent")
        self.class_list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Load class data
        self.load_classes()

    

    def setup_teacher_coefficient_tab(self):
        self.teacher_coefficient_tab.configure(fg_color="#FFFFFF")
        main_frame = CTkFrame(self.teacher_coefficient_tab, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header frame
        header_frame = CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)
        CTkLabel(header_frame, text="Hệ số giáo viên", font=("Helvetica", 18, "bold"), text_color="black").pack(side="left")
        CTkButton(header_frame, text="Đặt lại thành mặc định", fg_color="#0085FF", command=self.reset_to_default_coefficient_table).pack(side="right")

        # Filter frame
        filter_frame = CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        year_label = CTkLabel(filter_frame, text="Năm học:", font=("Helvetica", 12, "bold"))
        year_label.pack(side="left", padx=5)
        self.coefficient_year_filter = CTkComboBox(filter_frame, values=[f"{y}-{y+1}" for y in range(2020, 2030)], width=150, command=self.load_teacher_coefficients)
        self.coefficient_year_filter.pack(side="left", padx=5)
        self.coefficient_year_filter.set(f"{datetime.now().year}-{datetime.now().year + 1}")

        # List frame
        self.coefficient_list_frame = CTkFrame(main_frame, fg_color="transparent")
        self.coefficient_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Tải dữ liệu hiện có khi khởi tạo
        self.load_teacher_coefficients()



    def setup_teaching_rate_tab(self):
    # Header
        header_frame = CTkFrame(self.teaching_rate_tab, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)
        CTkLabel(header_frame, text="Định mức tiền theo tiết", font=("Helvetica", 18, "bold"), text_color="black").pack(side="left")
        # CTkButton(header_frame, text="Thêm định mức mới", fg_color="#0085FF", command=self.add_teaching_rate).pack(side="right")

        # Main container
        self.rate_container = CTkFrame(self.teaching_rate_tab, fg_color="#FFFFFF", corner_radius=10)
        self.rate_container.pack(padx=10, pady=10, fill="both", expand=True)

        # Heading
        heading_frame = CTkFrame(self.rate_container, fg_color="#D3D3D3", corner_radius=0)
        heading_frame.pack(fill="x", padx=5, pady=(5, 0))
        CTkLabel(heading_frame, text="STT", font=("Helvetica", 14, "bold"), text_color="black", width=100, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Năm học", font=("Helvetica", 14, "bold"), text_color="black", width=150, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Số tiền theo tiết (VNĐ)", font=("Helvetica", 14, "bold"), text_color="black", width=200, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Ngày thiết lập", font=("Helvetica", 14, "bold"), text_color="black", width=300, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Thao tác", font=("Helvetica", 14, "bold"), text_color="black", width=150, anchor="center").pack(side="left", padx=5)

        # Scrollable list frame
        self.rate_list_frame = CTkScrollableFrame(self.rate_container, fg_color="transparent")
        self.rate_list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Load all data
        self.load_teaching_rates()

    def setup_class_coefficient_tab(self):
        # Header
        header_frame = CTkFrame(self.class_coefficient_tab, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)
        CTkLabel(header_frame, text="Hệ số lớp", font=("Helvetica", 18, "bold"), text_color="black").pack(side="left")

        # Filter and Setup button
        filter_frame = CTkFrame(self.class_coefficient_tab, fg_color="transparent")
        filter_frame.pack(fill="x", padx=10, pady=5)
        CTkLabel(filter_frame, text="Năm học:", font=("Helvetica", 12), text_color="black").pack(side="left", padx=(0, 5))
        years = [f"{y}-{y+1}" for y in range(2020, 2030)]
        self.coeff_year_filter = CTkComboBox(filter_frame, values=years, width=150, command=self.load_class_coefficients)
        self.coeff_year_filter.pack(side="left", padx=5)
        CTkButton(filter_frame, text="Thiết lập", fg_color="#0085FF", command=self.setup_standard_range).pack(side="left", padx=5)

        # Main container
        self.coeff_container = CTkFrame(self.class_coefficient_tab, fg_color="#FFFFFF", corner_radius=10)
        self.coeff_container.pack(padx=10, pady=10, fill="both", expand=True)

        # Heading
        heading_frame = CTkFrame(self.coeff_container, fg_color="#D3D3D3", corner_radius=0)
        heading_frame.pack(fill="x", padx=5, pady=(5, 0))
        CTkLabel(heading_frame, text="STT", font=("Helvetica", 14, "bold"), text_color="black", width=160, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Khoảng số sinh viên", font=("Helvetica", 14, "bold"), text_color="black", width=400, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Hệ số", font=("Helvetica", 14, "bold"), text_color="black", width=250, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Ghi chú", font=("Helvetica", 14, "bold"), text_color="black", width=200, anchor="center").pack(side="left", padx=5)

        # Scrollable list frame
        self.coeff_list_frame = CTkScrollableFrame(self.coeff_container, fg_color="transparent")
        self.coeff_list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Load data
        self.load_class_coefficients()

    def setup_salary_calc_tab(self):
        self.salary_calc_tab.configure(fg_color="#FFFFFF")
        main_frame = CTkFrame(self.salary_calc_tab, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.salary_calc_tab.grid_rowconfigure(0, weight=1)
        self.salary_calc_tab.grid_columnconfigure(0, weight=1)

        header_frame = CTkFrame(main_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        CTkLabel(header_frame, text="Tính tiền dạy", font=("Helvetica", 18, "bold"), text_color="black").grid(row=0, column=0, sticky="w")

        filter_frame = CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=10)
        filter_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        years = self.get_academic_years_with_semesters()
        year_label = CTkLabel(filter_frame, text="Năm học:", font=("Helvetica", 12, "bold"))
        year_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.year_filter = CTkComboBox(filter_frame, values=["Chọn năm học"] + years, width=150, command=self.update_semester_options)
        self.year_filter.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.year_filter.set("Chọn năm học")

        semester_label = CTkLabel(filter_frame, text="Kỳ học:", font=("Helvetica", 12, "bold"))
        semester_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.semester_filter = CTkComboBox(filter_frame, values=["Chọn kỳ học", "Kỳ 1", "Kỳ 2", "Kỳ 3"], width=150)
        self.semester_filter.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.semester_filter.set("Chọn kỳ học")

        depts = self.get_dept_names()
        dept_label = CTkLabel(filter_frame, text="Khoa:", font=("Helvetica", 12, "bold"))
        dept_label.grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.dept_filter = CTkComboBox(filter_frame, values=["Chọn khoa"] + ["Tất cả khoa"] + depts, width=150, command=self.update_teacher_options)
        self.dept_filter.grid(row=0, column=5, padx=5, pady=5, sticky="w")
        self.dept_filter.set("Chọn khoa")

        teacher_label = CTkLabel(filter_frame, text="Giảng viên:", font=("Helvetica", 12, "bold"))
        teacher_label.grid(row=0, column=6, padx=5, pady=5, sticky="w")
        self.teacher_filter = CTkComboBox(filter_frame, values=["Chọn giảng viên"], width=200)
        self.teacher_filter.grid(row=0, column=7, padx=5, pady=5, sticky="w")
        self.teacher_filter.set("Chọn giảng viên")

        calc_button = CTkButton(filter_frame, text="Tính tiền dạy", fg_color="#0085FF", width=80, command=self.calculate_salary_display)
        calc_button.grid(row=0, column=8, padx=5, pady=5, sticky="w")
        
        reset_button = CTkButton(filter_frame, text="Reset", fg_color="#6C757D", width=40, command=self.reset_salary_calc)
        reset_button.grid(row=0, column=9, padx=5, pady=5, sticky="w")

        content_frame = CTkFrame(main_frame, fg_color="transparent")
        content_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Frame thông tin giáo viên - Tăng height lên 200 
        teacher_info_frame = CTkFrame(content_frame, fg_color="#cce7ff", corner_radius=10, height=250)
        teacher_info_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        teacher_info_frame.grid_propagate(False)
        content_frame.grid_columnconfigure(0, weight=1, uniform="group1")
        content_frame.grid_rowconfigure(0, weight=0)

        CTkLabel(teacher_info_frame, text="THÔNG TIN GIẢNG VIÊN", 
                font=("Helvetica", 16, "bold"), text_color="#0D47A1").grid(row=0, column=0, 
                columnspan=2, padx=20, pady=(15,10), sticky="w")

        self.salary_calc_teacher_name_title = CTkLabel(teacher_info_frame, text="Họ và tên:", 
                                                    font=("Helvetica", 14))
        self.salary_calc_teacher_name_title.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        self.salary_calc_teacher_name_value = CTkLabel(teacher_info_frame, text="", 
                                                    font=("Helvetica", 14), wraplength=200)
        self.salary_calc_teacher_name_value.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.salary_calc_teacher_id_title = CTkLabel(teacher_info_frame, text="Mã giảng viên:", 
                                                    font=("Helvetica", 14))
        self.salary_calc_teacher_id_title.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        self.salary_calc_teacher_id_value = CTkLabel(teacher_info_frame, text="", 
                                                    font=("Helvetica", 14), wraplength=200)
        self.salary_calc_teacher_id_value.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.salary_calc_degree_title = CTkLabel(teacher_info_frame, text="Học vị:", 
                                                font=("Helvetica", 14))
        self.salary_calc_degree_title.grid(row=3, column=0, padx=20, pady=5, sticky="w")
        self.salary_calc_degree_value = CTkLabel(teacher_info_frame, text="", 
                                                font=("Helvetica", 14), wraplength=200)
        self.salary_calc_degree_value.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        self.salary_calc_dept_title = CTkLabel(teacher_info_frame, text="Khoa/Bộ môn:", 
                                            font=("Helvetica", 14))
        self.salary_calc_dept_title.grid(row=4, column=0, padx=20, pady=5, sticky="w")
        self.salary_calc_dept_value = CTkLabel(teacher_info_frame, text="", 
                                            font=("Helvetica", 14), wraplength=200)
        self.salary_calc_dept_value.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Frame thông tin thanh toán - Tăng height lên 200
        calc_info_frame = CTkFrame(content_frame, fg_color="#cce7ff", corner_radius=10, height=250)
        calc_info_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        calc_info_frame.grid_propagate(False)
        content_frame.grid_columnconfigure(1, weight=1, uniform="group1")
        content_frame.grid_rowconfigure(0, weight=0)

        CTkLabel(calc_info_frame, text="THÔNG TIN THANH TOÁN", 
                font=("Helvetica", 16, "bold"), text_color="#0D47A1").grid(row=0, column=0, 
                columnspan=2, padx=20, pady=(15,10), sticky="w")

        self.salary_calc_teacher_coeff_title = CTkLabel(calc_info_frame, text="Hệ số giáo viên:", 
                                                    font=("Helvetica", 14))
        self.salary_calc_teacher_coeff_title.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        self.salary_calc_teacher_coeff_value = CTkLabel(calc_info_frame, text="", 
                                                    font=("Helvetica", 14), wraplength=200)
        self.salary_calc_teacher_coeff_value.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.salary_calc_rate_title = CTkLabel(calc_info_frame, text="Tiền dạy một tiết:", 
                                            font=("Helvetica", 14))
        self.salary_calc_rate_title.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        self.salary_calc_rate_value = CTkLabel(calc_info_frame, text="", 
                                            font=("Helvetica", 14), wraplength=200)
        self.salary_calc_rate_value.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.salary_calc_period_title = CTkLabel(calc_info_frame, text="Kỳ/Năm học:", 
                                                font=("Helvetica", 14))
        self.salary_calc_period_title.grid(row=3, column=0, padx=20, pady=5, sticky="w")
        self.salary_calc_period_value = CTkLabel(calc_info_frame, text="", 
                                                font=("Helvetica", 14), wraplength=200)
        self.salary_calc_period_value.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Frame cho bảng tính lương 
        self.salary_table_frame = CTkScrollableFrame(main_frame, fg_color="#FFFFFF", corner_radius=10, height=400)
        self.salary_table_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        main_frame.grid_rowconfigure(3, weight=2)

        self.save_button = None

    def switch_tab(self, tab_name):
        print(f"Debug: Chuyển sang tab {tab_name}")
        # Ẩn tab hiện tại
        if self.current_tab:
            self.current_tab.pack_forget()
        
        tab_mapping = {
            "Bằng cấp": self.degree_tab,
            "Khoa": self.dept_tab,
            "Giáo viên": self.teacher_tab,
            "Học phần": self.module_tab,
            "Kỳ học": self.semester_tab,
            "Lớp học": self.class_tab,
            "Thống kê giáo viên": self.stats_tab,
            "Thống kê lớp": self.class_stats_tab,
            "Định mức tiền theo tiết": self.teaching_rate_tab,
            "Hệ số giáo viên": self.teacher_coefficient_tab,
            "Hệ số lớp": self.class_coefficient_tab,
            "Tính tiền dạy": self.salary_calc_tab,
            "Báo cáo": self.report_tab,
            "Phân công": self.assignment_tab
        }
        
        self.current_tab = tab_mapping.get(tab_name)
        if self.current_tab:
            if tab_name == "Tính tiền dạy":
                # Kiểm tra xem widget có tồn tại không
                if not hasattr(self, 'salary_calc_teacher_coeff_value') or self.salary_calc_teacher_coeff_value is None:
                    print("Debug: Tái tạo tab Tính tiền dạy")
                    for widget in self.current_tab.winfo_children():
                        widget.destroy()
                    self.setup_salary_calc_tab()
            self.current_tab.pack(fill="both", expand=True)
        else:
            messagebox.showerror("Lỗi", f"Tab {tab_name} không tồn tại!")

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
            cursor.execute("SELECT module_id, module_name FROM course_modules ORDER BY module_id")
            modules = [f"{row[0]}: {row[1]}" for row in cursor.fetchall()]
            return modules
        except mysql.connector.Error:
            return []
        finally:
            cursor.close()
            conn.close()

    def filter_classes(self, value=None):
        print(f"Debug: filter_classes được gọi với giá trị: {value}")
        # Clear existing items in class_list_frame
        for widget in self.class_list_frame.winfo_children():
            widget.destroy()

        # Cập nhật giá trị combobox tương ứng
        if value == "Tất cả":
            self.semester_filter.set("Tất cả")
            self.module_filter.set("Tất cả")
            self.status_filter.set("Tất cả")
        elif value in self.get_semesters():  # Nếu value là semester_id
            self.semester_filter.set(value)
        elif value in [m.split(":")[1].strip() for m in self.get_modules()]:  # Nếu value là module_name
            self.module_filter.set(value)
        elif value in ["Đã phân công", "Chưa phân công"]:  # Nếu value là trạng thái
            self.status_filter.set(value)

        self.load_classes()

    import random

    def add_degree(self):
        add_window = CTkToplevel(self.window)
        add_window.title("Thêm bằng cấp")
        add_window.resizable(False, False)

        # Set window size and center
        window_width = 450
        window_height = 250
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x_position = int((screen_width - window_width) / 2)
        y_position = int((screen_height - window_height) / 2)
        add_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Make window modal
        add_window.transient(self.window)
        add_window.grab_set()

        # Form frame
        form_frame = CTkFrame(add_window, fg_color="#F0F0F0", corner_radius=10)
        form_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Title
        CTkLabel(form_frame, text="Thêm bằng cấp", font=("Helvetica", 16, "bold"), text_color="black").pack(pady=5)

        # Frame for Degree Name
        name_frame = CTkFrame(form_frame, fg_color="transparent")
        name_frame.pack(fill="x", pady=2)
        CTkLabel(name_frame, text="Tên bằng cấp:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
        degree_name_entry = CTkEntry(name_frame, width=260, placeholder_text="VD: Cử nhân CNTT")
        degree_name_entry.pack(side="left")

        # Frame for Abbreviation
        abbr_frame = CTkFrame(form_frame, fg_color="transparent")
        abbr_frame.pack(fill="x", pady=2)
        CTkLabel(abbr_frame, text="Tên viết tắt:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
        degree_abbr_entry = CTkEntry(abbr_frame, width=260, placeholder_text="VD: CN (≤5 ký tự)")
        degree_abbr_entry.pack(side="left")

        # Frame for Coefficient
        coeff_frame = CTkFrame(form_frame, fg_color="transparent")
        coeff_frame.pack(fill="x", pady=2)
        CTkLabel(coeff_frame, text="Hệ số:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
        degree_coeff_entry = CTkEntry(coeff_frame, width=260, placeholder_text="VD: 1.5")
        degree_coeff_entry.pack(side="left")

        # Buttons
        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        CTkButton(button_frame, text="Lưu", fg_color="#0085FF", width=100).pack(side="left", padx=5)
        CTkButton(button_frame, text="Hủy", fg_color="#6C757D", width=100, command=add_window.destroy).pack(side="left", padx=5)

        def save_degree():
            degree_name = degree_name_entry.get().strip()
            degree_abbr = degree_abbr_entry.get().strip()
            degree_coeff = degree_coeff_entry.get().strip()

            if not all([degree_name, degree_abbr, degree_coeff]):
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
                return

            if not degree_coeff.replace('.', '', 1).isdigit() or float(degree_coeff) <= 0:
                messagebox.showerror("Lỗi", "Hệ số phải là số dương!")
                return

            if len(degree_abbr) > 5:
                messagebox.showerror("Lỗi", "Tên viết tắt không được vượt quá 5 ký tự!")
                return

            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                # Kiểm tra trùng tên và tên viết tắt
                cursor.execute("SELECT degree_id FROM degrees WHERE degree_name = %s OR degree_abbr = %s", (degree_name, degree_abbr))
                if cursor.fetchone():
                    messagebox.showerror("Lỗi", "Tên bằng cấp hoặc tên viết tắt đã tồn tại!")
                    return

                # Tự động tạo mã bằng cấp (DEGxxxxx với 5 số ngẫu nhiên)
                while True:
                    random_num = random.randint(0, 99999)
                    degree_id = f"DEG{str(random_num).zfill(5)}"
                    cursor.execute("SELECT degree_id FROM degrees WHERE degree_id = %s", (degree_id,))
                    if not cursor.fetchone():
                        break

                cursor.execute("""
                    INSERT INTO degrees (degree_id, degree_name, degree_abbr, coefficient)
                    VALUES (%s, %s, %s, %s)
                """, (degree_id, degree_name, degree_abbr, float(degree_coeff)))
                conn.commit()
                messagebox.showinfo("Thành công", f"Thêm bằng cấp {degree_name} với mã {degree_id} thành công!")
                self.load_degrees()
                add_window.destroy()
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể thêm bằng cấp: {e}")
            finally:
                cursor.close()
                conn.close()

        # Bind save function to "Lưu" button
        button_frame.winfo_children()[0].configure(command=save_degree)

    def edit_degree(self, degree_id):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT degree_id, degree_name, degree_abbr, coefficient
                FROM degrees
                WHERE degree_id = %s
            """, (degree_id,))
            degree_data = cursor.fetchone()
            if not degree_data:
                messagebox.showerror("Lỗi", "Không tìm thấy bằng cấp!")
                return

            degree_id, degree_name, degree_abbr, coefficient = degree_data

            # Create popup window
            edit_window = CTkToplevel(self.window)
            edit_window.title("Sửa bằng cấp")
            edit_window.resizable(False, False)

            # Set window size and center
            window_width = 450
            window_height = 250
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            x_position = int((screen_width - window_width) / 2)
            y_position = int((screen_height - window_height) / 2)
            edit_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

            # Make window modal
            edit_window.transient(self.window)
            edit_window.grab_set()

            # Form frame
            form_frame = CTkFrame(edit_window, fg_color="#F0F0F0", corner_radius=10)
            form_frame.pack(padx=20, pady=10, fill="both", expand=True)

            # Title
            CTkLabel(form_frame, text="Sửa bằng cấp", font=("Helvetica", 16, "bold"), text_color="black").pack(pady=5)

            # Frame for Degree ID (display only, not editable)
            id_frame = CTkFrame(form_frame, fg_color="transparent")
            id_frame.pack(fill="x", pady=2)
            CTkLabel(id_frame, text="Mã bằng cấp:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
            degree_id_label = CTkLabel(id_frame, text=degree_id, width=260, anchor="w")
            degree_id_label.pack(side="left")

            # Frame for Degree Name
            name_frame = CTkFrame(form_frame, fg_color="transparent")
            name_frame.pack(fill="x", pady=2)
            CTkLabel(name_frame, text="Tên bằng cấp:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
            degree_name_entry = CTkEntry(name_frame, width=260, placeholder_text="VD: Cử nhân CNTT")
            degree_name_entry.insert(0, degree_name)
            degree_name_entry.pack(side="left")

            # Frame for Abbreviation
            abbr_frame = CTkFrame(form_frame, fg_color="transparent")
            abbr_frame.pack(fill="x", pady=2)
            CTkLabel(abbr_frame, text="Tên viết tắt:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
            degree_abbr_entry = CTkEntry(abbr_frame, width=260, placeholder_text="VD: CN (≤5 ký tự)")
            degree_abbr_entry.insert(0, degree_abbr)
            degree_abbr_entry.pack(side="left")

            # Frame for Coefficient
            coeff_frame = CTkFrame(form_frame, fg_color="transparent")
            coeff_frame.pack(fill="x", pady=2)
            CTkLabel(coeff_frame, text="Hệ số:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
            degree_coeff_entry = CTkEntry(coeff_frame, width=260, placeholder_text="VD: 1.5")
            degree_coeff_entry.insert(0, str(coefficient))
            degree_coeff_entry.pack(side="left")

            # Buttons
            button_frame = CTkFrame(form_frame, fg_color="transparent")
            button_frame.pack(pady=10)
            CTkButton(button_frame, text="Lưu", fg_color="#0085FF", width=100).pack(side="left", padx=5)
            CTkButton(button_frame, text="Hủy", fg_color="#6C757D", width=100, command=edit_window.destroy).pack(side="left", padx=5)

            def save_degree():
                new_degree_name = degree_name_entry.get().strip()
                new_degree_abbr = degree_abbr_entry.get().strip()
                new_degree_coeff = degree_coeff_entry.get().strip()

                if not all([new_degree_name, new_degree_abbr, new_degree_coeff]):
                    messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
                    return

                if not new_degree_coeff.replace('.', '', 1).isdigit() or float(new_degree_coeff) <= 0:
                    messagebox.showerror("Lỗi", "Hệ số phải là số dương!")
                    return

                if len(new_degree_abbr) > 5:
                    messagebox.showerror("Lỗi", "Tên viết tắt không được vượt quá 5 ký tự!")
                    return

                try:
                    conn = mysql.connector.connect(**DB_CONFIG)
                    cursor = conn.cursor()
                    # Kiểm tra trùng tên và tên viết tắt (ngoại trừ bản ghi hiện tại)
                    cursor.execute("""
                        SELECT degree_id FROM degrees
                        WHERE (degree_name = %s OR degree_abbr = %s) AND degree_id != %s
                    """, (new_degree_name, new_degree_abbr, degree_id))
                    if cursor.fetchone():
                        messagebox.showerror("Lỗi", "Tên bằng cấp hoặc tên viết tắt đã tồn tại!")
                        return

                    cursor.execute("""
                        UPDATE degrees
                        SET degree_name = %s, degree_abbr = %s, coefficient = %s
                        WHERE degree_id = %s
                    """, (new_degree_name, new_degree_abbr, float(new_degree_coeff), degree_id))
                    conn.commit()
                    messagebox.showinfo("Thành công", f"Cập nhật bằng cấp {new_degree_name} thành công!")
                    self.load_degrees()
                    edit_window.destroy()
                except mysql.connector.Error as e:
                    messagebox.showerror("Lỗi", f"Không thể cập nhật bằng cấp: {e}")
                finally:
                    cursor.close()
                    conn.close()

            # Bind save function to "Lưu" button
            button_frame.winfo_children()[0].configure(command=save_degree)

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu bằng cấp: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


    def delete_degree(self, degree_id):
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Kiểm tra liên quan đến giáo viên
            cursor.execute("SELECT 1 FROM teachers WHERE degree_id = %s LIMIT 1", (degree_id,))
            if cursor.fetchone():
                messagebox.showerror("Lỗi", "Không thể xóa bằng cấp vì có giáo viên đang sử dụng!", parent=self.window)
                return

            # Xác nhận xóa
            if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa bằng cấp {degree_id}?", parent=self.window):
                cursor.execute("DELETE FROM degrees WHERE degree_id = %s", (degree_id,))
                conn.commit()
                messagebox.showinfo("Thành công", f"Xóa bằng cấp {degree_id} thành công", parent=self.window)
                self.load_degrees()
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể xóa bằng cấp: {e}", parent=self.window)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def load_degrees(self):
        # Xóa các widget cũ trong frame
        for widget in self.degree_list_frame.winfo_children():
            widget.destroy()

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT degree_id, degree_name, degree_abbr FROM degrees")
            rows = cursor.fetchall()
            if not rows:
                CTkLabel(self.degree_list_frame, text="Không có dữ liệu bằng cấp", font=("Helvetica", 14), text_color="gray").pack(pady=20, expand=True)
            else:
                for row in rows:
                    degree_id, name, abbr = row
                    # Tạo frame cho từng dòng
                    degree_row_frame = CTkFrame(self.degree_list_frame, fg_color="#F0F0F0", corner_radius=5)
                    degree_row_frame.pack(fill="x", padx=0, pady=2)

                    # Thay idx bằng degree_id
                    CTkLabel(degree_row_frame, text=degree_id, font=("Helvetica", 12), text_color="black", width=160, anchor="center").pack(side="left", padx=5)
                    CTkLabel(degree_row_frame, text=name, font=("Helvetica", 12), text_color="black", width=400, anchor="center").pack(side="left", padx=5)
                    CTkLabel(degree_row_frame, text=abbr, font=("Helvetica", 12), text_color="black", width=250, anchor="center").pack(side="left", padx=5)

                    # Frame chứa các nút Sửa/Xóa
                    button_frame = CTkFrame(degree_row_frame, fg_color="transparent", width=200)
                    button_frame.pack(side="left", padx=35)
                    CTkButton(button_frame, text="Sửa", fg_color="#FFC107", width=60, command=lambda d_id=degree_id: self.edit_degree(d_id)).pack(side="left", padx=2)
                    CTkButton(button_frame, text="Xóa", fg_color="#F44336", width=60, command=lambda d_id=degree_id: self.delete_degree(d_id)).pack(side="left", padx=2)
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu bằng cấp: {e}")
        finally:
            cursor.close()
            conn.close()

    def on_degree_select(self, event):
        # Xác định vùng click
        region = self.degree_tree.identify_region(event.x, event.y)
        if region != "cell":
            return

        # Xác định dòng được chọn
        selected_item = self.degree_tree.selection()
        if not selected_item:
            return

        # Lấy thông tin dòng
        item = self.degree_tree.item(selected_item)
        degree_id = self.degree_tree.item(selected_item, "tags")[0]  # Lấy degree_id từ tags

        # Xác định cột được click
        column = self.degree_tree.identify_column(event.x)
        if column == "#5":  # Cột "Thao tác" (cột thứ 5)
            # Xác định vị trí chính xác trong cột
            x_relative = event.x - self.degree_tree.winfo_rootx() - self.degree_tree.column("#5")["width"] * 4  # Điều chỉnh vị trí x
            if 0 <= x_relative <= 40:  # Vùng "Sửa"
                self.edit_degree(degree_id)
            elif 40 < x_relative <= 80:  # Vùng "Xóa"
                self.delete_degree(degree_id)

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
        add_window = CTkToplevel(self.window)
        add_window.title("Thêm khoa")
        add_window.resizable(False, False)

        # Set window size and center
        window_width = 450
        window_height = 250
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x_position = int((screen_width - window_width) / 2)
        y_position = int((screen_height - window_height) / 2)
        add_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Make window modal
        add_window.transient(self.window)
        add_window.grab_set()

        # Form frame
        form_frame = CTkFrame(add_window, fg_color="#F0F0F0", corner_radius=10)
        form_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Title
        CTkLabel(form_frame, text="Thêm khoa", font=("Helvetica", 16, "bold"), text_color="black").pack(pady=5)

        # Frame for Dept Name
        name_frame = CTkFrame(form_frame, fg_color="transparent")
        name_frame.pack(fill="x", pady=2)
        CTkLabel(name_frame, text="Tên khoa:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
        dept_name_entry = CTkEntry(name_frame, width=260, placeholder_text="VD: Công nghệ thông tin")
        dept_name_entry.pack(side="left")

        # Frame for Abbreviation
        abbr_frame = CTkFrame(form_frame, fg_color="transparent")
        abbr_frame.pack(fill="x", pady=2)
        CTkLabel(abbr_frame, text="Tên viết tắt:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
        dept_abbr_entry = CTkEntry(abbr_frame, width=260, placeholder_text="VD: CNTT (≤5 ký tự)")
        dept_abbr_entry.pack(side="left")

        # Frame for Description
        desc_frame = CTkFrame(form_frame, fg_color="transparent")
        desc_frame.pack(fill="x", pady=2)
        CTkLabel(desc_frame, text="Mô tả nhiệm vụ:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
        dept_desc_entry = CTkEntry(desc_frame, width=260, placeholder_text="VD: Quản lý CNTT")
        dept_desc_entry.pack(side="left")

        # Buttons
        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        CTkButton(button_frame, text="Lưu", fg_color="#0085FF", width=100).pack(side="left", padx=5)
        CTkButton(button_frame, text="Hủy", fg_color="#6C757D", width=100, command=add_window.destroy).pack(side="left", padx=5)

        def save_dept():
            dept_name = dept_name_entry.get().strip()
            dept_abbr = dept_abbr_entry.get().strip()
            dept_desc = dept_desc_entry.get().strip()

            if not all([dept_name, dept_abbr, dept_desc]):
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
                return

            if len(dept_abbr) > 5:
                messagebox.showerror("Lỗi", "Tên viết tắt không được vượt quá 5 ký tự!")
                return

            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                # Kiểm tra trùng tên và tên viết tắt
                cursor.execute("SELECT dept_id FROM departments WHERE dept_name = %s OR dept_abbr = %s", (dept_name, dept_abbr))
                if cursor.fetchone():
                    messagebox.showerror("Lỗi", "Tên khoa hoặc tên viết tắt đã tồn tại!")
                    return

                # Tự động tạo mã khoa (DEPTxxxx với 4 số ngẫu nhiên)
                while True:
                    random_num = random.randint(0, 9999)
                    dept_id = f"DEPT{str(random_num).zfill(4)}"
                    cursor.execute("SELECT dept_id FROM departments WHERE dept_id = %s", (dept_id,))
                    if not cursor.fetchone():
                        break

                cursor.execute("""
                    INSERT INTO departments (dept_id, dept_name, dept_abbr, description)
                    VALUES (%s, %s, %s, %s)
                """, (dept_id, dept_name, dept_abbr, dept_desc))
                conn.commit()
                messagebox.showinfo("Thành công", f"Thêm khoa {dept_name} với mã {dept_id} thành công!")
                self.load_depts()
                add_window.destroy()
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể thêm khoa: {e}")
            finally:
                cursor.close()
                conn.close()

        # Bind save function to "Lưu" button
        button_frame.winfo_children()[0].configure(command=save_dept)

    def edit_dept(self, dept_id):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT dept_id, dept_name, dept_abbr, description
                FROM departments
                WHERE dept_id = %s
            """, (dept_id,))
            dept_data = cursor.fetchone()
            if not dept_data:
                messagebox.showerror("Lỗi", "Không tìm thấy khoa!")
                return

            dept_id, dept_name, dept_abbr, description = dept_data

            # Create popup window
            edit_window = CTkToplevel(self.window)
            edit_window.title("Sửa khoa")
            edit_window.resizable(False, False)

            # Set window size and center
            window_width = 450
            window_height = 250
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            x_position = int((screen_width - window_width) / 2)
            y_position = int((screen_height - window_height) / 2)
            edit_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

            # Make window modal
            edit_window.transient(self.window)
            edit_window.grab_set()

            # Form frame
            form_frame = CTkFrame(edit_window, fg_color="#F0F0F0", corner_radius=10)
            form_frame.pack(padx=20, pady=10, fill="both", expand=True)

            # Title
            CTkLabel(form_frame, text="Sửa khoa", font=("Helvetica", 16, "bold"), text_color="black").pack(pady=5)

            # Frame for Dept ID (display only, not editable)
            id_frame = CTkFrame(form_frame, fg_color="transparent")
            id_frame.pack(fill="x", pady=2)
            CTkLabel(id_frame, text="Mã khoa:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
            dept_id_label = CTkLabel(id_frame, text=dept_id, width=260, anchor="w")
            dept_id_label.pack(side="left")

            # Frame for Dept Name
            name_frame = CTkFrame(form_frame, fg_color="transparent")
            name_frame.pack(fill="x", pady=2)
            CTkLabel(name_frame, text="Tên khoa:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
            dept_name_entry = CTkEntry(name_frame, width=260, placeholder_text="VD: Công nghệ thông tin")
            dept_name_entry.insert(0, dept_name)
            dept_name_entry.pack(side="left")

            # Frame for Abbreviation
            abbr_frame = CTkFrame(form_frame, fg_color="transparent")
            abbr_frame.pack(fill="x", pady=2)
            CTkLabel(abbr_frame, text="Tên viết tắt:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
            dept_abbr_entry = CTkEntry(abbr_frame, width=260, placeholder_text="VD: CNTT (≤5 ký tự)")
            dept_abbr_entry.insert(0, dept_abbr)
            dept_abbr_entry.pack(side="left")

            # Frame for Description
            desc_frame = CTkFrame(form_frame, fg_color="transparent")
            desc_frame.pack(fill="x", pady=2)
            CTkLabel(desc_frame, text="Mô tả nhiệm vụ:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
            dept_desc_entry = CTkEntry(desc_frame, width=260, placeholder_text="VD: Quản lý CNTT")
            dept_desc_entry.insert(0, description)
            dept_desc_entry.pack(side="left")

            # Buttons
            button_frame = CTkFrame(form_frame, fg_color="transparent")
            button_frame.pack(pady=10)
            CTkButton(button_frame, text="Lưu", fg_color="#0085FF", width=100).pack(side="left", padx=5)
            CTkButton(button_frame, text="Hủy", fg_color="#6C757D", width=100, command=edit_window.destroy).pack(side="left", padx=5)

            def save_dept():
                new_dept_name = dept_name_entry.get().strip()
                new_dept_abbr = dept_abbr_entry.get().strip()
                new_dept_desc = dept_desc_entry.get().strip()

                if not all([new_dept_name, new_dept_abbr, new_dept_desc]):
                    messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
                    return

                if len(new_dept_abbr) > 5:
                    messagebox.showerror("Lỗi", "Tên viết tắt không được vượt quá 5 ký tự!")
                    return

                try:
                    conn = mysql.connector.connect(**DB_CONFIG)
                    cursor = conn.cursor()
                    # Kiểm tra trùng tên và tên viết tắt (ngoại trừ bản ghi hiện tại)
                    cursor.execute("""
                        SELECT dept_id FROM departments
                        WHERE (dept_name = %s OR dept_abbr = %s) AND dept_id != %s
                    """, (new_dept_name, new_dept_abbr, dept_id))
                    if cursor.fetchone():
                        messagebox.showerror("Lỗi", "Tên khoa hoặc tên viết tắt đã tồn tại!")
                        return

                    cursor.execute("""
                        UPDATE departments
                        SET dept_name = %s, dept_abbr = %s, description = %s
                        WHERE dept_id = %s
                    """, (new_dept_name, new_dept_abbr, new_dept_desc, dept_id))
                    conn.commit()
                    messagebox.showinfo("Thành công", f"Cập nhật khoa {new_dept_name} thành công!")
                    self.load_depts()
                    edit_window.destroy()
                except mysql.connector.Error as e:
                    messagebox.showerror("Lỗi", f"Không thể cập nhật khoa: {e}")
                finally:
                    cursor.close()
                    conn.close()

            # Bind save function to "Lưu" button
            button_frame.winfo_children()[0].configure(command=save_dept)

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu khoa: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


    def delete_dept(self, dept_id):
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Kiểm tra liên quan đến giáo viên
            cursor.execute("SELECT 1 FROM teachers WHERE dept_id = %s LIMIT 1", (dept_id,))
            if cursor.fetchone():
                messagebox.showerror("Lỗi", "Không thể xóa khoa vì có giáo viên thuộc khoa này!", parent=self.window)
                return

            # Xác nhận xóa
            if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa khoa {dept_id}?", parent=self.window):
                cursor.execute("DELETE FROM departments WHERE dept_id = %s", (dept_id,))
                conn.commit()
                messagebox.showinfo("Thành công", f"Xóa khoa {dept_id} thành công", parent=self.window)
                self.load_depts()
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể xóa khoa: {e}", parent=self.window)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def load_depts(self):
        # Xóa các widget cũ trong frame
        for widget in self.dept_list_frame.winfo_children():
            widget.destroy()

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            # Lấy tất cả khoa
            query = "SELECT dept_id, dept_name, dept_abbr, dept_description FROM departments"
            cursor.execute(query)

            rows = cursor.fetchall()
            if not rows:
                CTkLabel(self.dept_list_frame, text="Không có dữ liệu khoa", font=("Helvetica", 14), text_color="gray").pack(pady=20, expand=True)
            else:
                for idx, row in enumerate(rows, start=1):
                    dept_id, name, abbr, description = row
                    # Tạo frame cho từng dòng
                    dept_row_frame = CTkFrame(self.dept_list_frame, fg_color="#F0F0F0", corner_radius=5)
                    dept_row_frame.pack(fill="x", padx=0, pady=2)

                    # Căn chỉnh các cột với chiều rộng đồng bộ với heading
                    CTkLabel(dept_row_frame, text=dept_id, font=("Helvetica", 12), text_color="black", width=150, anchor="center").pack(side="left", padx=5)
                    CTkLabel(dept_row_frame, text=name, font=("Helvetica", 12), text_color="black", width=200, anchor="center").pack(side="left", padx=5)  # Giảm từ 450 xuống 400
                    CTkLabel(dept_row_frame, text=abbr, font=("Helvetica", 12), text_color="black", width=150, anchor="center").pack(side="left", padx=5)
                    CTkLabel(dept_row_frame, text=description if description else "N/A", font=("Helvetica", 12), text_color="black", width=300, anchor="center").pack(side="left", padx=5)  # Giảm từ 600 xuống 500
                    # Frame chứa các nút Sửa/Xóa
                    button_frame = CTkFrame(dept_row_frame, fg_color="transparent", width=250)  # Tăng từ 250 lên 350
                    button_frame.pack(side="left", padx=60)
                    CTkButton(button_frame, text="Sửa", fg_color="#FFC107", width=60, command=lambda d_id=dept_id: self.edit_dept(d_id)).pack(side="left", padx=2)
                    CTkButton(button_frame, text="Xóa", fg_color="#F44336", width=60, command=lambda d_id=dept_id: self.delete_dept(d_id)).pack(side="left", padx=2)
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

    def update_teacher_coefficient(self, degree_combobox, teacher_coeff, window):
        degree = degree_combobox.get().strip()
        if not degree or degree == "Không có bằng cấp" or degree == "Lỗi tải bằng cấp":
            teacher_coeff.delete(0, "end")
            teacher_coeff.insert(0, "1.0")  # Giá trị mặc định nếu không có bằng cấp
            return
        degree_id = degree.split(":")[0].strip()
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT coefficient FROM degrees WHERE degree_id = %s", (degree_id,))
            result = cursor.fetchone()
            teacher_coeff.delete(0, "end")
            if result:
                teacher_coeff.insert(0, str(result[0]))
            else:
                teacher_coeff.insert(0, "1.0")  # Giá trị mặc định nếu không tìm thấy
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải hệ số: {e}", parent=window)
        finally:
            cursor.close()
            conn.close()


    def add_teacher(self):
    # Tạo cửa sổ pop-up
        add_window = CTkToplevel(self.window)
        add_window.title("Thêm giáo viên mới")
        add_window.geometry("500x400")
        add_window.resizable(False, False)

        # Căn giữa cửa sổ popup
        self.window.update_idletasks()
        x = self.window.winfo_x()
        y = self.window.winfo_y()
        w = self.window.winfo_width()
        h = self.window.winfo_height()
        add_window.geometry(f"+{x + w//2 - 250}+{y + h//2 - 200}")

        # Đè lên cửa sổ chính
        add_window.transient(self.window)
        add_window.grab_set()

        # Frame chính
        main_frame = CTkFrame(add_window, fg_color="transparent")
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Tiêu đề
        CTkLabel(main_frame, text="THÊM GIÁO VIÊN MỚI", font=("Helvetica", 18, "bold")).pack(pady=(5, 15))

        # Frame nhập liệu
        form_frame = CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="both", expand=True)

        def create_row(label, widget, row):
            CTkLabel(form_frame, text=label, anchor="w", font=("Helvetica", 12)).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 10))
            widget.grid(row=row, column=1, sticky="ew", pady=5)

        form_frame.columnconfigure(1, weight=1)

        # Họ tên
        teacher_name = CTkEntry(form_frame, placeholder_text="Họ tên")
        create_row("Họ tên:", teacher_name, 0)

        # Ngày sinh + nút lịch
        date_frame = CTkFrame(form_frame, fg_color="transparent")
        date_of_birth = CTkEntry(date_frame, placeholder_text="YYYY-MM-DD")
        date_of_birth.pack(side="left", fill="x", expand=True)
        CTkButton(date_frame, text="📅", width=30, fg_color="#0085FF", hover_color="#005BB5", 
                command=lambda: self.open_calendar(date_of_birth)).pack(side="right")
        create_row("Ngày sinh:", date_frame, 1)

        # Điện thoại
        phone = CTkEntry(form_frame, placeholder_text="Số điện thoại")
        create_row("Điện thoại:", phone, 2)

        # Email
        email = CTkEntry(form_frame, placeholder_text="Email")
        create_row("Email:", email, 3)

        # Khoa
        dept_combobox = CTkComboBox(form_frame, values=self.get_departments())
        dept_combobox.set(self.get_departments()[0] if self.get_departments() else "")
        create_row("Khoa:", dept_combobox, 4)

        # Bằng cấp
        degree_combobox = CTkComboBox(form_frame, values=self.get_degrees())
        degree_combobox.set(self.get_degrees()[0] if self.get_degrees() else "")
        create_row("Bằng cấp:", degree_combobox, 5)

        # Hàm lưu giáo viên
        def save_teacher(window):
            name = teacher_name.get().strip()
            dob_str = date_of_birth.get().strip()
            phone_num = phone.get().strip()
            email_addr = email.get().strip()
            dept_info = dept_combobox.get().strip()
            degree_info = degree_combobox.get().strip()

            if not all([name, dept_info, degree_info]):
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin bắt buộc (Họ tên, Khoa, Bằng cấp)", parent=window)
                return

            dob_date = None
            if dob_str:
                try:
                    dob_date = datetime.strptime(dob_str, '%Y-%m-%d').date()
                    if dob_date > datetime.now().date():
                        messagebox.showerror("Lỗi", "Ngày sinh không được trong tương lai!", parent=window)
                        return
                except ValueError:
                    messagebox.showerror("Lỗi", "Ngày sinh không hợp lệ (YYYY-MM-DD)!", parent=window)
                    return

            if phone_num and not re.match(r"^\d{10,15}$", phone_num):
                messagebox.showerror("Lỗi", "Số điện thoại phải từ 10 đến 15 chữ số!", parent=window)
                return

            if email_addr and not re.match(r"[^@]+@[^@]+\.[^@]+", email_addr):
                messagebox.showerror("Lỗi", "Email không hợp lệ!", parent=window)
                return

            dept_id = dept_info.split(":")[0].strip()
            degree_id = degree_info.split(":")[0].strip()

            conn = None
            cursor = None
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()

                # Lấy hệ số từ bảng degrees
                cursor.execute("SELECT coefficient FROM degrees WHERE degree_id = %s", (degree_id,))
                result = cursor.fetchone()
                if not result:
                    messagebox.showerror("Lỗi", "Không tìm thấy bằng cấp!", parent=window)
                    return
                teacher_coefficient = result[0]

                # Kiểm tra email trùng lặp
                if email_addr:
                    cursor.execute("SELECT teacher_id FROM teachers WHERE email = %s", (email_addr,))
                    if cursor.fetchone():
                        messagebox.showerror("Lỗi", "Email đã tồn tại!", parent=window)
                        return

                # Tạo mã giáo viên ngẫu nhiên
                import random
                max_attempts = 100
                for _ in range(max_attempts):
                    random_num = random.randint(0, 99999)
                    teacher_id = f"TCH{str(random_num).zfill(5)}"
                    cursor.execute("SELECT teacher_id FROM teachers WHERE teacher_id = %s", (teacher_id,))
                    if not cursor.fetchone():
                        break
                else:
                    messagebox.showerror("Lỗi", "Không thể tạo mã giáo viên duy nhất sau nhiều lần thử!", parent=window)
                    return

                # Thêm giáo viên
                cursor.execute(
                    "INSERT INTO teachers (teacher_id, full_name, date_of_birth, phone, email, dept_id, degree_id, teacher_coefficient) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (teacher_id, name, dob_date, phone_num or None, email_addr or None, dept_id, degree_id, teacher_coefficient)
                )
                conn.commit()
                messagebox.showinfo("Thành công", f"Thêm giáo viên thành công với mã {teacher_id}", parent=window)
                self.load_teachers()
                window.destroy()
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể thêm giáo viên: {e}", parent=window)
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

        # Nút Thêm và Hủy
        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=6, column=0, columnspan=2, pady=(10, 0))

        CTkButton(button_frame, text="Thêm", width=120, fg_color="#007bff", hover_color="#0056b3",
                command=lambda: save_teacher(add_window)).pack(side="left", padx=10)
        CTkButton(button_frame, text="Hủy", width=120, fg_color="#6c757d", hover_color="#5a6268",
                command=add_window.destroy).pack(side="left", padx=10)

        
    def edit_teacher(self, teacher_id):
        # Tạo cửa sổ pop-up
        edit_window = CTkToplevel(self.window)
        edit_window.title("Sửa thông tin giáo viên")
        edit_window.geometry("500x400")
        edit_window.resizable(False, False)

        # Căn giữa pop-up
        self.window.update_idletasks()
        x = self.window.winfo_x()
        y = self.window.winfo_y()
        w = self.window.winfo_width()
        h = self.window.winfo_height()
        edit_window.geometry(f"+{x + w//2 - 250}+{y + h//2 - 200}")

        # Đè lên cửa sổ chính
        edit_window.transient(self.window)
        edit_window.grab_set()

        # Frame chính
        main_frame = CTkFrame(edit_window, fg_color="transparent")
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Tiêu đề
        CTkLabel(main_frame, text="SỬA THÔNG TIN GIÁO VIÊN", font=("Helvetica", 18, "bold")).pack(pady=(5, 15))

        # Frame nhập liệu
        form_frame = CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="both", expand=True)

        def create_row(label, widget, row):
            CTkLabel(form_frame, text=label, anchor="w", font=("Helvetica", 12)).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 10))
            widget.grid(row=row, column=1, sticky="ew", pady=5)

        form_frame.columnconfigure(1, weight=1)

        # Lấy thông tin giáo viên hiện tại
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT full_name, date_of_birth, phone, email, dept_id, degree_id "
                "FROM teachers WHERE teacher_id = %s",
                (teacher_id,)
            )
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Lỗi", "Không tìm thấy giáo viên!", parent=edit_window)
                edit_window.destroy()
                return
            current_name, current_dob, current_phone, current_email, current_dept_id, current_degree_id = result
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải thông tin giáo viên: {e}", parent=edit_window)
            edit_window.destroy()
            return
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        # Họ tên
        teacher_name = CTkEntry(form_frame, placeholder_text="Họ tên")
        teacher_name.insert(0, current_name)
        create_row("Họ tên:", teacher_name, 0)

        # Ngày sinh + nút lịch
        date_frame = CTkFrame(form_frame, fg_color="transparent")
        date_of_birth = CTkEntry(date_frame, placeholder_text="YYYY-MM-DD")
        if current_dob:
            date_of_birth.insert(0, current_dob.strftime('%Y-%m-%d'))
        date_of_birth.pack(side="left", fill="x", expand=True)
        CTkButton(date_frame, text="📅", width=30, fg_color="#0085FF", hover_color="#005BB5", 
                command=lambda: self.open_calendar(date_of_birth)).pack(side="right")
        create_row("Ngày sinh:", date_frame, 1)

        # Điện thoại
        phone = CTkEntry(form_frame, placeholder_text="Số điện thoại")
        if current_phone:
            phone.insert(0, current_phone)
        create_row("Điện thoại:", phone, 2)

        # Email
        email = CTkEntry(form_frame, placeholder_text="Email")
        if current_email:
            email.insert(0, current_email)
        create_row("Email:", email, 3)

        # Khoa
        dept_combobox = CTkComboBox(form_frame, values=self.get_departments())
        dept_values = self.get_departments()
        for dept in dept_values:
            if dept.startswith(current_dept_id):
                dept_combobox.set(dept)
                break
        else:
            dept_combobox.set(dept_values[0] if dept_values else "")
        create_row("Khoa:", dept_combobox, 4)

        # Bằng cấp
        degree_combobox = CTkComboBox(form_frame, values=self.get_degrees())
        degree_values = self.get_degrees()
        for degree in degree_values:
            if degree.startswith(current_degree_id):
                degree_combobox.set(degree)
                break
        else:
            degree_combobox.set(degree_values[0] if degree_values else "")
        create_row("Bằng cấp:", degree_combobox, 5)

        # Hàm lưu giáo viên
        def save_teacher(window):
            name = teacher_name.get().strip()
            dob_str = date_of_birth.get().strip()
            phone_num = phone.get().strip()
            email_addr = email.get().strip()
            dept_info = dept_combobox.get().strip()
            degree_info = degree_combobox.get().strip()

            if not all([name, dept_info, degree_info]):
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin bắt buộc (Họ tên, Khoa, Bằng cấp)", parent=window)
                return

            dob_date = None
            if dob_str:
                try:
                    dob_date = datetime.strptime(dob_str, '%Y-%m-%d').date()
                    if dob_date > datetime.now().date():
                        messagebox.showerror("Lỗi", "Ngày sinh không được trong tương lai!", parent=window)
                        return
                except ValueError:
                    messagebox.showerror("Lỗi", "Ngày sinh không hợp lệ (YYYY-MM-DD)!", parent=window)
                    return

            if phone_num and not re.match(r"^\d{10,15}$", phone_num):
                messagebox.showerror("Lỗi", "Số điện thoại phải từ 10 đến 15 chữ số!", parent=window)
                return

            if email_addr and not re.match(r"[^@]+@[^@]+\.[^@]+", email_addr):
                messagebox.showerror("Lỗi", "Email không hợp lệ!", parent=window)
                return

            dept_id = dept_info.split(":")[0].strip()
            degree_id = degree_info.split(":")[0].strip()

            conn = None
            cursor = None
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()

                # Kiểm tra email trùng lặp (trừ chính giáo viên hiện tại)
                if email_addr:
                    cursor.execute(
                        "SELECT teacher_id FROM teachers WHERE email = %s AND teacher_id != %s",
                        (email_addr, teacher_id)
                    )
                    if cursor.fetchone():
                        messagebox.showerror("Lỗi", "Email đã tồn tại!", parent=window)
                        return

                # Lấy hệ số từ bảng degrees
                cursor.execute("SELECT coefficient FROM degrees WHERE degree_id = %s", (degree_id,))
                result = cursor.fetchone()
                if not result:
                    messagebox.showerror("Lỗi", "Không tìm thấy bằng cấp!", parent=window)
                    return
                teacher_coefficient = result[0]

                # Cập nhật giáo viên
                cursor.execute(
                    "UPDATE teachers SET full_name = %s, date_of_birth = %s, phone = %s, email = %s, "
                    "dept_id = %s, degree_id = %s, teacher_coefficient = %s WHERE teacher_id = %s",
                    (name, dob_date, phone_num or None, email_addr or None, dept_id, degree_id, teacher_coefficient, teacher_id)
                )
                conn.commit()
                messagebox.showinfo("Thành công", f"Cập nhật giáo viên {teacher_id} thành công", parent=window)
                self.load_teachers()
                window.destroy()
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể cập nhật giáo viên: {e}", parent=window)
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

        # Nút Lưu và Hủy
        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=6, column=0, columnspan=2, pady=(10, 0))

        CTkButton(button_frame, text="Lưu", width=120, fg_color="#007bff", hover_color="#0056b3",
                command=lambda: save_teacher(edit_window)).pack(side="left", padx=10)
        CTkButton(button_frame, text="Hủy", width=120, fg_color="#6c757d", hover_color="#5a6268",
                command=edit_window.destroy).pack(side="left", padx=10)

    def delete_teacher(self, teacher_id):
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Kiểm tra liên quan đến assignments
            cursor.execute("SELECT 1 FROM assignments WHERE teacher_id = %s LIMIT 1", (teacher_id,))
            if cursor.fetchone():
                messagebox.showerror("Lỗi", "Không thể xóa giáo viên vì đã được phân công!", parent=self.window)
                return

            # Xác nhận xóa
            if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa giáo viên {teacher_id}?", parent=self.window):
                cursor.execute("DELETE FROM teachers WHERE teacher_id = %s", (teacher_id,))
                conn.commit()
                messagebox.showinfo("Thành công", f"Xóa giáo viên {teacher_id} thành công", parent=self.window)
                self.load_teachers()
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể xóa giáo viên: {e}", parent=self.window)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def load_teachers(self):
        # Xóa các widget cũ trong frame
        for widget in self.teacher_list_frame.winfo_children():
            widget.destroy()

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            query = """
                SELECT t.teacher_id, t.full_name, t.date_of_birth, t.phone, t.email, d.dept_name, deg.degree_name
                FROM teachers t
                JOIN departments d ON t.dept_id = d.dept_id
                JOIN degrees deg ON t.degree_id = deg.degree_id
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            if not rows:
                CTkLabel(self.teacher_list_frame, text="Không có dữ liệu giáo viên", font=("Helvetica", 14), text_color="gray").pack(pady=20, expand=True)
            else:
                for idx, row in enumerate(rows, start=1):
                    teacher_id, name, dob, phone, email, dept_name, degree_name = row
                    # Tạo frame cho từng dòng
                    teacher_row_frame = CTkFrame(self.teacher_list_frame, fg_color="#F0F0F0", corner_radius=5)
                    teacher_row_frame.pack(fill="x", padx=0, pady=2)

                    # Căn chỉnh các cột với chiều rộng đồng bộ với heading
                    CTkLabel(teacher_row_frame, text=teacher_id, font=("Helvetica", 12), text_color="black", width=80, anchor="center").pack(side="left", padx=5)
                    CTkLabel(teacher_row_frame, text=name, font=("Helvetica", 12), text_color="black", width=120, anchor="center").pack(side="left", padx=5)
                    CTkLabel(teacher_row_frame, text=dob.strftime('%Y-%m-%d') if dob else "N/A", font=("Helvetica", 12), text_color="black", width=80, anchor="center").pack(side="left", padx=5)
                    CTkLabel(teacher_row_frame, text=phone if phone else "N/A", font=("Helvetica", 12), text_color="black", width=80, anchor="center").pack(side="left", padx=5)
                    CTkLabel(teacher_row_frame, text=email if email else "N/A", font=("Helvetica", 12), text_color="black", width=180, anchor="center").pack(side="left", padx=5)
                    CTkLabel(teacher_row_frame, text=dept_name, font=("Helvetica", 12), text_color="black", width=200, anchor="center").pack(side="left", padx=5)
                    CTkLabel(teacher_row_frame, text=degree_name, font=("Helvetica", 12), text_color="black", width=120, anchor="center").pack(side="left", padx=5)

                    # Frame chứa các nút Sửa/Xóa
                    button_frame = CTkFrame(teacher_row_frame, fg_color="transparent", width=100)
                    button_frame.pack(side="left", padx=20)
                    CTkButton(button_frame, text="Sửa", fg_color="#FFC107", width=30, command=lambda t_id=teacher_id: self.edit_teacher(t_id)).pack(side="left", padx=2)
                    CTkButton(button_frame, text="Xóa", fg_color="#F44336", width=30, command=lambda t_id=teacher_id: self.delete_teacher(t_id)).pack(side="left", padx=2)
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
    # Create popup window
        add_window = CTkToplevel(self.window)
        add_window.title("Thêm học phần mới")
        add_window.resizable(False, False)

        # Set window size
        window_width = 450
        window_height = 350
        add_window.geometry(f"{window_width}x{window_height}")

        # Center the window on the screen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x_position = int((screen_width - window_width) / 2)
        y_position = int((screen_height - window_height) / 2)
        add_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Make window modal
        add_window.transient(self.window)
        add_window.grab_set()

        # Form frame
        form_frame = CTkFrame(add_window, fg_color="#F0F0F0", corner_radius=10)
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Title
        CTkLabel(form_frame, text="Thêm học phần mới", font=("Helvetica", 16, "bold"), text_color="black").pack(pady=10)

        # Module Name
        name_frame = CTkFrame(form_frame, fg_color="transparent")
        name_frame.pack(fill="x", pady=5)
        CTkLabel(name_frame, text="Tên học phần:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
        module_name_entry = CTkEntry(name_frame, placeholder_text="Tên học phần", width=300)
        module_name_entry.pack(side="left", fill="x", expand=True)

        # Credits (Combobox từ 1-12)
        credits_frame = CTkFrame(form_frame, fg_color="transparent")
        credits_frame.pack(fill="x", pady=5)
        CTkLabel(credits_frame, text="Số tín chỉ:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
        credits_combobox = CTkComboBox(credits_frame, values=[str(i) for i in range(1, 13)], width=300)
        credits_combobox.pack(side="left", fill="x", expand=True)
        credits_combobox.set("1")

        # Coefficient
        coefficient_frame = CTkFrame(form_frame, fg_color="transparent")
        coefficient_frame.pack(fill="x", pady=5)
        CTkLabel(coefficient_frame, text="Hệ số học phần:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
        coefficient_entry = CTkEntry(coefficient_frame, placeholder_text="Hệ số (ví dụ: 1.5)", width=300)
        coefficient_entry.pack(side="left", fill="x", expand=True)

        # # Periods
        # periods_frame = CTkFrame(form_frame, fg_color="transparent")
        # periods_frame.pack(fill="x", pady=5)
        # CTkLabel(periods_frame, text="Số tiết:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
        # periods_entry = CTkEntry(periods_frame, placeholder_text="Số tiết", width=300)
        # periods_entry.pack(side="left", fill="x", expand=True)

        # Department
        dept_frame = CTkFrame(form_frame, fg_color="transparent")
        dept_frame.pack(fill="x", pady=5)
        CTkLabel(dept_frame, text="Khoa:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
        departments = self.get_departments()
        dept_combobox = CTkComboBox(dept_frame, width=300, values=departments)
        dept_combobox.pack(side="left", fill="x", expand=True)
        if departments and departments[0] not in ["Không có khoa", "Lỗi tải khoa"]:
            dept_combobox.set(departments[0])
        else:
            dept_combobox.set(departments[0])

        # Buttons
        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=20)
        CTkButton(button_frame, text="Thêm", fg_color="#0085FF", width=100).pack(side="left", padx=5)
        CTkButton(button_frame, text="Hủy", fg_color="#6C757D", width=100, command=lambda: add_window.destroy()).pack(side="left", padx=5)

        # Save function
        def save_module():
            name = module_name_entry.get().strip()
            credits = credits_combobox.get().strip()
            coefficient = coefficient_entry.get().strip()
            # periods = periods_entry.get().strip()
            dept = dept_combobox.get().strip()

            # Validation
            if not all([name, credits, coefficient, dept]):
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!", parent=add_window)
                return

            try:
                credits = int(credits)
                # Tự động tính số tiết = tín chỉ * 15
                periods = credits * 15
            except ValueError:
                messagebox.showerror("Lỗi", "Số tín chỉ phải là số nguyên!", parent=add_window)
                return

            try:
                coefficient = float(coefficient)
                if coefficient < 1.0 or coefficient > 1.5:
                    messagebox.showerror("Lỗi", "Hệ số học phần phải từ 1.0 đến 1.5!", parent=add_window)
                    return
            except ValueError:
                messagebox.showerror("Lỗi", "Hệ số phải là số thực!", parent=add_window)
                return

            try:
                periods = int(periods)
                if periods <= 0:
                    messagebox.showerror("Lỗi", "Số tiết phải lớn hơn 0!", parent=add_window)
                    return
            except ValueError:
                messagebox.showerror("Lỗi", "Số tiết phải là số nguyên!", parent=add_window)
                return

            dept_id = dept.split(":")[0].strip()

            # Check for duplicate module name
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("SELECT module_id FROM course_modules WHERE module_name = %s", (name,))
                if cursor.fetchone():
                    messagebox.showerror("Lỗi", "Tên học phần đã tồn tại!", parent=add_window)
                    return

                # Generate module ID
                cursor.execute("SELECT module_id FROM course_modules ORDER BY CAST(SUBSTRING(module_id, 4) AS UNSIGNED) DESC LIMIT 1")
                result = cursor.fetchone()
                if result:
                    last_id = result[0]
                    last_num = int(last_id[3:])
                    new_num = last_num + 1
                else:
                    new_num = 1
                module_id = f"MOD{str(new_num).zfill(5)}"

                # Insert new module with dept_id
                cursor.execute("INSERT INTO course_modules (module_id, module_name, credits, coefficient, periods, dept_id) VALUES (%s, %s, %s, %s, %s, %s)",
                            (module_id, name, credits, coefficient, periods, dept_id))
                conn.commit()
                messagebox.showinfo("Thành công", f"Thêm học phần thành công với mã {module_id}", parent=add_window)
                self.load_modules()
                self.module_list_frame.update_idletasks()
                add_window.destroy()
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể thêm học phần: {e}", parent=add_window)
            finally:
                cursor.close()
                conn.close()

        # Bind save function to "Thêm" button
        button_frame.winfo_children()[0].configure(command=save_module)

    def edit_module(self, module_id):
        # Load module data into the edit form
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT module_id, module_name, credits, coefficient, periods, dept_id
                FROM course_modules
                WHERE module_id = %s
            """, (module_id,))
            module_data = cursor.fetchone()
            if not module_data:
                messagebox.showerror("Lỗi", "Không tìm thấy học phần!")
                return

            module_id, name, credits, coefficient, periods, dept_id = module_data

            # Create popup window
            edit_window = CTkToplevel(self.window)
            edit_window.title("Sửa học phần")
            edit_window.resizable(False, False)

            # Set window size
            window_width = 450
            window_height = 350
            edit_window.geometry(f"{window_width}x{window_height}")

            # Center the window on the screen
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            x_position = int((screen_width - window_width) / 2)
            y_position = int((screen_height - window_height) / 2)
            edit_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

            # Make window modal
            edit_window.transient(self.window)
            edit_window.grab_set()

            # Form frame
            form_frame = CTkFrame(edit_window, fg_color="#F0F0F0", corner_radius=10)
            form_frame.pack(padx=20, pady=20, fill="both", expand=True)

            # Title
            CTkLabel(form_frame, text="Sửa học phần", font=("Helvetica", 16, "bold"), text_color="black").pack(pady=10)

            # Module Name
            name_frame = CTkFrame(form_frame, fg_color="transparent")
            name_frame.pack(fill="x", pady=5)
            CTkLabel(name_frame, text="Tên học phần:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
            module_name_entry = CTkEntry(name_frame, width=300)
            module_name_entry.pack(side="left", fill="x", expand=True)
            module_name_entry.insert(0, name)

            # Credits (Combobox từ 1-12)
            credits_frame = CTkFrame(form_frame, fg_color="transparent")
            credits_frame.pack(fill="x", pady=5)
            CTkLabel(credits_frame, text="Số tín chỉ:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
            credits_combobox = CTkComboBox(credits_frame, values=[str(i) for i in range(1, 13)], width=300)
            credits_combobox.pack(side="left", fill="x", expand=True)
            credits_combobox.set(str(credits))

            # Coefficient
            coefficient_frame = CTkFrame(form_frame, fg_color="transparent")
            coefficient_frame.pack(fill="x", pady=5)
            CTkLabel(coefficient_frame, text="Hệ số học phần:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
            coefficient_entry = CTkEntry(coefficient_frame, width=300)
            coefficient_entry.pack(side="left", fill="x", expand=True)
            coefficient_entry.insert(0, coefficient)

            # Periods
            # periods_frame = CTkFrame(form_frame, fg_color="transparent")
            # periods_frame.pack(fill="x", pady=5)
            # CTkLabel(periods_frame, text="Số tiết:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
            # periods_entry = CTkEntry(periods_frame, width=300)
            # periods_entry.pack(side="left", fill="x", expand=True)
            # periods_entry.insert(0, periods)

            # Department
            dept_frame = CTkFrame(form_frame, fg_color="transparent")
            dept_frame.pack(fill="x", pady=5)
            CTkLabel(dept_frame, text="Khoa:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
            departments = self.get_departments()
            dept_combobox = CTkComboBox(dept_frame, width=300, values=departments)
            dept_combobox.pack(side="left", fill="x", expand=True)
            for dept in departments:
                if dept.startswith(dept_id):
                    dept_combobox.set(dept)
                    break
            else:
                dept_combobox.set(departments[0] if departments else "Không có khoa")

            # Buttons
            button_frame = CTkFrame(form_frame, fg_color="transparent")
            button_frame.pack(pady=20)
            CTkButton(button_frame, text="Lưu", fg_color="#0085FF", width=100).pack(side="left", padx=5)
            CTkButton(button_frame, text="Hủy", fg_color="#6C757D", width=100, command=lambda: edit_window.destroy()).pack(side="left", padx=5)

            # Save function
            def save_module():
                new_name = module_name_entry.get().strip()
                new_credits = credits_combobox.get().strip()
                new_coefficient = coefficient_entry.get().strip()
                # new_periods = periods_entry.get().strip()
                new_dept = dept_combobox.get().strip()

                if not all([new_name, new_credits, new_coefficient, new_dept]):
                    messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!", parent=edit_window)
                    return

                try:
                    new_credits = int(new_credits)
                    # Tự động tính số tiết = tín chỉ * 15
                    new_periods = new_credits * 15
                except ValueError:
                    messagebox.showerror("Lỗi", "Số tín chỉ phải là số nguyên!", parent=edit_window)
                    return

                try:
                    new_coefficient = float(new_coefficient)
                    if new_coefficient < 1.0 or new_coefficient > 1.5:
                        messagebox.showerror("Lỗi", "Hệ số học phần phải từ 1.0 đến 1.5!", parent=edit_window)
                        return
                except ValueError:
                    messagebox.showerror("Lỗi", "Hệ số phải là số thực!", parent=edit_window)
                    return

                try:
                    new_periods = int(new_periods)
                    if new_periods <= 0:
                        messagebox.showerror("Lỗi", "Số tiết phải lớn hơn 0!", parent=edit_window)
                        return
                except ValueError:
                    messagebox.showerror("Lỗi", "Số tiết phải là số nguyên!", parent=edit_window)
                    return

                new_dept_id = new_dept.split(":")[0].strip()

                try:
                    conn = mysql.connector.connect(**DB_CONFIG)
                    cursor = conn.cursor()
                    cursor.execute("SELECT module_id FROM course_modules WHERE module_name = %s AND module_id != %s", (new_name, module_id))
                    if cursor.fetchone():
                        messagebox.showerror("Lỗi", "Tên học phần đã tồn tại!", parent=edit_window)
                        return

                    cursor.execute("UPDATE course_modules SET module_name = %s, credits = %s, coefficient = %s, periods = %s, dept_id = %s WHERE module_id = %s",
                                (new_name, new_credits, new_coefficient, new_periods, new_dept_id, module_id))
                    conn.commit()
                    messagebox.showinfo("Thành công", "Cập nhật học phần thành công!", parent=edit_window)
                    self.load_modules()
                    self.module_list_frame.update_idletasks()
                    edit_window.destroy()
                except mysql.connector.Error as e:
                    messagebox.showerror("Lỗi", f"Không thể cập nhật học phần: {e}", parent=edit_window)
                finally:
                    cursor.close()
                    conn.close()

            # Bind save function to "Lưu" button
            button_frame.winfo_children()[0].configure(command=save_module)

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu học phần: {e}")
        finally:
            cursor.close()
            conn.close()

    def delete_module(self, module_id):
        # Hiện hộp thoại xác nhận trước khi xóa
        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa học phần này?"):
            return
    
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
    
            # Kiểm tra xem có lớp học nào đang sử dụng học phần này không
            cursor.execute("SELECT 1 FROM classes WHERE module_id = %s LIMIT 1", (module_id,))
            if cursor.fetchone():
                messagebox.showerror("Lỗi", "Không thể xóa học phần vì đã có lớp học được tạo!")
                return
    
            # Thực hiện xóa học phần
            cursor.execute("DELETE FROM course_modules WHERE module_id = %s", (module_id,))
            conn.commit()
            
            messagebox.showinfo("Thành công", "Xóa học phần thành công!")
            self.load_modules()
            self.module_list_frame.update_idletasks()
            
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể xóa học phần: {e}")
        finally:
            cursor.close()
            conn.close()

    def load_modules(self):
        # Clear existing items in module_list_frame
        for widget in self.module_list_frame.winfo_children():
            widget.destroy()

        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            # Xóa điều kiện WHERE để lấy tất cả học phần
            query = """
                SELECT cm.module_id, cm.module_name, cm.credits, cm.coefficient, cm.periods, d.dept_abbr
                FROM course_modules cm
                LEFT JOIN departments d ON cm.dept_id = d.dept_id
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            if not rows:
                CTkLabel(self.module_list_frame, text="Không có dữ liệu học phần", 
                        font=("Helvetica", 14), text_color="gray").pack(pady=10)
                return

            # Create a row for each module
            for row in rows:
                module_id, name, credits, coefficient, periods, dept_abbr = row

                # Row frame for each module
                row_frame = CTkFrame(self.module_list_frame, fg_color="#F5F5F5", corner_radius=0)
                row_frame.pack(fill="x", pady=2)

                # Data labels
                CTkLabel(row_frame, text=module_id, font=("Helvetica", 12), 
                        text_color="black", width=80, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=name, font=("Helvetica", 12),
                        text_color="black", width=300, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=str(credits), font=("Helvetica", 12),
                        text_color="black", width=100, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=str(coefficient), font=("Helvetica", 12),
                        text_color="black", width=100, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=str(periods), font=("Helvetica", 12),
                        text_color="black", width=100, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=dept_abbr if dept_abbr else "N/A", font=("Helvetica", 12),
                        text_color="black", width=150, anchor="center").pack(side="left", padx=5)

                # Actions frame
                actions_frame = CTkFrame(row_frame, fg_color="transparent", width=150)
                actions_frame.pack(side="left", padx=5)

                # Edit button
                CTkButton(actions_frame, text="Sửa", width=30, fg_color="#FFC107", hover_color="#E0A800", 
                        command=lambda m_id=module_id: self.edit_module(m_id)).pack(side="left", padx=2)

                # Delete button
                CTkButton(actions_frame, text="Xóa", width=30, fg_color="#F44336", hover_color="#D32F2F", 
                        command=lambda m_id=module_id: self.delete_module(m_id)).pack(side="left", padx=2)

            # Force refresh
            self.module_list_frame.update_idletasks()
            
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu học phần: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


    def add_classes(self):
        # Create popup window
        add_window = CTkToplevel(self.window)
        add_window.title("Thêm lớp học phần")
        add_window.resizable(False, False)

        # Set window size
        window_width = 500
        window_height = 350
        add_window.geometry(f"{window_width}x{window_height}")

        # Center the window
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x_position = int((screen_width - window_width) / 2)
        y_position = int((screen_height - window_height) / 2)
        add_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Make modal
        add_window.transient(self.window)
        add_window.grab_set()

        form_frame = CTkFrame(add_window, fg_color="#F0F0F0", corner_radius=10)
        form_frame.pack(padx=20, pady=10, fill="both", expand=True)

        CTkLabel(form_frame, text="Thêm lớp học phần", font=("Helvetica", 16, "bold"), text_color="black").pack(pady=5)

        # Semester Combobox
        semester_frame = CTkFrame(form_frame, fg_color="transparent")
        semester_frame.pack(fill="x", pady=2)
        CTkLabel(semester_frame, text="Học kỳ:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
        semester_combobox = CTkComboBox(semester_frame, values=self.get_semesters(), width=260, height=32)
        semester_combobox.pack(side="left")
        if self.get_semesters():
            semester_combobox.set(self.get_semesters()[0])

        # Module Combobox
        module_frame = CTkFrame(form_frame, fg_color="transparent")
        module_frame.pack(fill="x", pady=2)
        CTkLabel(module_frame, text="Học phần:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
        modules = self.get_modules()
        module_dict = {module.split(":")[1].strip(): module.split(":")[0].strip() for module in modules}
        module_names = list(module_dict.keys())
        module_combobox = CTkComboBox(module_frame, values=module_names, width=260, height=32)
        module_combobox.pack(side="left")
        if module_names:
            module_combobox.set(module_names[0])

        # Number of Classes
        num_classes_frame = CTkFrame(form_frame, fg_color="transparent")
        num_classes_frame.pack(fill="x", pady=2)
        CTkLabel(num_classes_frame, text="Số lớp:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
        num_classes_combobox = CTkComboBox(num_classes_frame, values=[str(i) for i in range(1, 9)], width=260, height=32)
        num_classes_combobox.pack(side="left")
        num_classes_combobox.set("1")

        # Number of Students
        num_students_frame = CTkFrame(form_frame, fg_color="transparent")
        num_students_frame.pack(fill="x", pady=2)
        CTkLabel(num_students_frame, text="Số sinh viên:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
        num_students_entry = CTkEntry(num_students_frame, placeholder_text="Số sinh viên", width=260, height=32)
        num_students_entry.pack(side="left")

        # Buttons
        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        create_button = CTkButton(button_frame, text="Tạo", fg_color="#0085FF", width=100)
        create_button.pack(side="left", padx=5)
        CTkButton(button_frame, text="Hủy", fg_color="#6C757D", width=100, command=lambda: add_window.destroy()).pack(side="left", padx=5)

        # Save function
        def save_classes():
            semester_id = semester_combobox.get().strip()
            module_name = module_combobox.get().strip()
            num_classes_str = num_classes_combobox.get()
            num_students = num_students_entry.get().strip()

            if not all([semester_id, module_name, num_classes_str, num_students]):
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!", parent=add_window)
                return

            try:
                num_classes = int(num_classes_str)
                if not (1 <= num_classes <= 8):
                    raise ValueError
            except ValueError:
                messagebox.showerror("Lỗi", "Số lớp phải từ 1 đến 8!", parent=add_window)
                return

            try:
                num_students = int(num_students)
                if num_students < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Lỗi", "Số sinh viên phải là số nguyên >= 0!", parent=add_window)
                return

            module_id = module_dict.get(module_name)
            if not module_id:
                messagebox.showerror("Lỗi", "Học phần không hợp lệ!", parent=add_window)
                return

            conn = cursor = None
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()

                # Kiểm tra số lớp hiện tại
                cursor.execute("SELECT class_id FROM classes WHERE semester_id = %s AND module_id = %s", (semester_id, module_id))
                existing_classes = cursor.fetchall()
                current_count = len(existing_classes)

                if current_count + num_classes > 8:
                    messagebox.showerror("Lỗi", f"Tối đa 8 lớp/học phần/kỳ! Hiện có {current_count} lớp.", parent=add_window)
                    return

                # Lấy chi tiết học phần + viết tắt khoa
                cursor.execute("""
                    SELECT cm.module_name, cm.credits, d.dept_abbr
                    FROM course_modules cm
                    JOIN departments d ON cm.dept_id = d.dept_id
                    WHERE cm.module_id = %s
                """, (module_id,))
                module_info = cursor.fetchone()
                if not module_info:
                    messagebox.showerror("Lỗi", "Không tìm thấy thông tin học phần!", parent=add_window)
                    return
                module_name_db, credits, dept_abbr = module_info

                # Lấy năm học đầy đủ từ semester
                cursor.execute("SELECT year FROM semesters WHERE semester_id = %s", (semester_id,))
                year_result = cursor.fetchone()
                if not year_result:
                    messagebox.showerror("Lỗi", "Không tìm thấy kỳ học!", parent=add_window)
                    return
                full_year = year_result[0]

                # Lấy tất cả class_id hiện có
                cursor.execute("SELECT class_id FROM classes")
                all_class_ids = {row[0] for row in cursor.fetchall()}

                # Tạo danh sách lớp
                class_names = []
                for i in range(num_classes):
                    group_num = i + 1
                    group_str = f"N{str(group_num).zfill(2)}"
                    class_name = f"{dept_abbr}{module_id}-LT-{credits}-{full_year}({group_str})"

                    if len(class_name) > 50:
                        messagebox.showerror("Lỗi", f"Tên lớp '{class_name}' quá dài!", parent=add_window)
                        return

                    # Sinh class_id
                    found_valid_id = False
                    for _ in range(1000):
                        class_id_candidate = f"CLS{random.randint(0, 99999):05}"
                        if class_id_candidate not in all_class_ids:
                            all_class_ids.add(class_id_candidate)
                            found_valid_id = True
                            break
                    if not found_valid_id:
                        messagebox.showerror("Lỗi", "Không tạo được mã lớp mới!", parent=add_window)
                        return

                    class_names.append((class_name, class_id_candidate, group_num))

                if not messagebox.askyesno("Xác nhận", f"Tạo {num_classes} lớp học phần:\n" + "\n".join(n[0] for n in class_names), parent=add_window):
                    return

                for class_name, class_id, _ in class_names:
                    cursor.execute("""
                        INSERT INTO classes (class_id, semester_id, module_id, class_name, num_students)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (class_id, semester_id, module_id, class_name, num_students))
                conn.commit()
                messagebox.showinfo("Thành công", f"Đã tạo {num_classes} lớp học phần!", parent=add_window)

                # Làm mới giao diện
                self.semester_filter.set("Tất cả")
                self.module_filter.set("Tất cả")
                self.status_filter.set("Tất cả")
                self.load_classes()
                self.class_list_frame.update_idletasks()
                add_window.destroy()

            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể tạo lớp học phần: {e}", parent=add_window)
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

        # Gắn hàm tạo vào nút
        create_button.configure(command=save_classes)


    def edit_class(self, class_id):
    # Load class data
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.semester_id, c.module_id, c.class_name, c.num_students
                FROM classes c
                WHERE c.class_id = %s
            """, (class_id,))
            class_data = cursor.fetchone()
            if not class_data:
                messagebox.showerror("Lỗi", "Không tìm thấy lớp học!")
                return

            semester_id, module_id, class_name, num_students = class_data

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu lớp học: {e}")
            return
        finally:
            cursor.close()
            conn.close()

        # Create popup window
        edit_window = CTkToplevel(self.window)
        edit_window.title("Sửa thông tin lớp")
        edit_window.resizable(False, False)

        # Set window size
        window_width = 500
        window_height = 350
        edit_window.geometry(f"{window_width}x{window_height}")

        # Center the window on the screen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x_position = int((screen_width - window_width) / 2)
        y_position = int((screen_height - window_height) / 2)
        edit_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Make window modal
        edit_window.transient(self.window)
        edit_window.grab_set()

        # Form frame
        form_frame = CTkFrame(edit_window, fg_color="#F0F0F0", corner_radius=10)
        form_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Title
        CTkLabel(form_frame, text="Sửa thông tin lớp", font=("Helvetica", 16, "bold"), text_color="black").pack(pady=5)

        # Semester Combobox
        semester_frame = CTkFrame(form_frame, fg_color="transparent")
        semester_frame.pack(fill="x", pady=2)
        CTkLabel(semester_frame, text="Học kỳ:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
        semester_combobox = CTkComboBox(semester_frame, values=self.get_semesters(), width=260, height=32)
        semester_combobox.pack(side="left")
        semester_combobox.set(semester_id)

        # Module Combobox (hiển thị module_name, giá trị là module_id)
        module_frame = CTkFrame(form_frame, fg_color="transparent")
        module_frame.pack(fill="x", pady=2)
        CTkLabel(module_frame, text="Học phần:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))

        # Lấy danh sách học phần
        modules = self.get_modules()  # modules có định dạng ["MOD29934: Lập trình Python", ...]
        module_dict = {module.split(":")[1].strip(): module.split(":")[0].strip() for module in modules}  # {module_name: module_id}
        module_names = list(module_dict.keys())  # Danh sách tên học phần để hiển thị

        module_combobox = CTkComboBox(module_frame, values=module_names, width=260, height=32)
        module_combobox.pack(side="left")
        # Tìm module_name tương ứng với module_id
        for name, id in module_dict.items():
            if id == module_id:
                module_combobox.set(name)
                break

        # Class Name
        name_frame = CTkFrame(form_frame, fg_color="transparent")
        name_frame.pack(fill="x", pady=2)
        CTkLabel(name_frame, text="Tên lớp:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
        class_name_entry = CTkEntry(name_frame, placeholder_text="Tên lớp", width=260, height=32)
        class_name_entry.pack(side="left")
        class_name_entry.insert(0, class_name)

        # Number of Students
        num_students_frame = CTkFrame(form_frame, fg_color="transparent")
        num_students_frame.pack(fill="x", pady=2)
        CTkLabel(num_students_frame, text="Số sinh viên:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
        num_students_entry = CTkEntry(num_students_frame, placeholder_text="Số sinh viên", width=260, height=32)
        num_students_entry.pack(side="left")
        num_students_entry.insert(0, str(num_students))

        # Buttons
        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        CTkButton(button_frame, text="Lưu", fg_color="#0085FF", width=100).pack(side="left", padx=5)
        CTkButton(button_frame, text="Hủy", fg_color="#6C757D", width=100, command=lambda: edit_window.destroy()).pack(side="left", padx=5)

        # Save function
        def save_class():
            new_semester_id = semester_combobox.get().strip()
            new_module_name = module_combobox.get().strip()
            new_class_name = class_name_entry.get().strip()
            new_num_students = num_students_entry.get().strip()

            # Lấy module_id từ module_name
            new_module_id = module_dict.get(new_module_name)
            if not new_module_id:
                messagebox.showerror("Lỗi", "Học phần không hợp lệ!", parent=edit_window)
                return

            # Validation
            if not all([new_semester_id, new_module_id, new_class_name, new_num_students]):
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!", parent=edit_window)
                return

            try:
                new_num_students = int(new_num_students)
                if new_num_students < 0:
                    messagebox.showerror("Lỗi", "Số sinh viên phải lớn hơn hoặc bằng 0!", parent=edit_window)
                    return
            except ValueError:
                messagebox.showerror("Lỗi", "Số sinh viên phải là số nguyên!", parent=edit_window)
                return

            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()

                # Update class
                cursor.execute("UPDATE classes SET semester_id = %s, module_id = %s, class_name = %s, num_students = %s WHERE class_id = %s",
                            (new_semester_id, new_module_id, new_class_name, new_num_students, class_id))
                conn.commit()
                messagebox.showinfo("Thành công", "Cập nhật thông tin lớp thành công!", parent=edit_window)
                self.load_classes()
                self.class_list_frame.update_idletasks()
                edit_window.destroy()
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể cập nhật lớp học: {e}", parent=edit_window)
            finally:
                cursor.close()
                conn.close()

        # Bind save function to "Lưu" button
        button_frame.winfo_children()[0].configure(command=save_class)

    def delete_class(self, class_id):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa lớp học phần này không?\nLưu ý: Nếu lớp đã được phân công giảng viên, dữ liệu lương liên quan cũng sẽ bị xóa."):
            conn = None
            cursor = None
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()

                # Xóa dữ liệu lương liên quan (sẽ tự động xóa nhờ ràng buộc ON DELETE CASCADE trong bảng salaries)
                # Xóa phân công (sẽ tự động xóa nhờ ràng buộc ON DELETE CASCADE trong bảng assignments)
                # Xóa lớp học phần
                cursor.execute("DELETE FROM classes WHERE class_id = %s", (class_id,))
                conn.commit()
                messagebox.showinfo("Thành công", "Xóa lớp học phần thành công!")
                self.load_classes()
                self.class_list_frame.update_idletasks()
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể xóa lớp học phần: {e}")
            finally:
                cursor.close()
                conn.close()

    def load_classes(self):
        # Clear existing items in class_list_frame
        for widget in self.class_list_frame.winfo_children():
            widget.destroy()

        # Lấy giá trị hiện tại từ combobox
        semester_filter = self.semester_filter.get()
        module_filter = self.module_filter.get()
        status_filter = self.status_filter.get()

        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Kiểm tra dữ liệu trong các bảng liên quan
            cursor.execute("SELECT semester_id FROM semesters")
            available_semesters = [row[0] for row in cursor.fetchall()]
            print(f"Debug: Available semesters: {available_semesters}")

            cursor.execute("SELECT module_id, module_name FROM course_modules")
            module_data = cursor.fetchall()
            available_modules = {row[1].strip(): row[0] for row in module_data}
            print(f"Debug: Available modules: {[row[1] for row in module_data]}")

            # Debug: Kiểm tra dữ liệu trong bảng class_enrollments
            cursor.execute("SELECT class_id, enrolled_students FROM class_enrollments")
            enrollments = cursor.fetchall()
            print(f"Debug: Data in class_enrollments: {enrollments}")

            query = """
                SELECT c.semester_id, m.module_name, c.class_id, c.class_name, c.num_students, 
                    COALESCE(ce.enrolled_students, 0) as enrolled_students, t.full_name
                FROM classes c
                JOIN semesters s ON c.semester_id = s.semester_id
                JOIN course_modules m ON c.module_id = m.module_id
                LEFT JOIN class_enrollments ce ON c.class_id = ce.class_id 
                LEFT JOIN assignments a ON c.class_id = a.class_id
                LEFT JOIN teachers t ON a.teacher_id = t.teacher_id
                WHERE 1=1
            """
            params = []

            print(f"Debug: Filter values - Semester: {semester_filter}, Module: {module_filter}, Status: {status_filter}")

            if semester_filter != "Tất cả":
                if semester_filter in available_semesters:
                    query += " AND c.semester_id = %s"
                    params.append(semester_filter)
                else:
                    CTkLabel(self.class_list_frame, text=f"Không có dữ liệu lớp học cho kỳ học {semester_filter}", font=("Helvetica", 14), text_color="gray").pack(pady=10)
                    print(f"Debug: No data for semester {semester_filter}")
                    return

            if module_filter != "Tất cả":
                if module_filter.strip() in available_modules:
                    query += " AND m.module_name = %s"
                    params.append(module_filter.strip())
                else:
                    CTkLabel(self.class_list_frame, text=f"Không có dữ liệu lớp học cho học phần {module_filter}", font=("Helvetica", 14), text_color="gray").pack(pady=10)
                    print(f"Debug: No data for module {module_filter}")
                    return

            if status_filter == "Đã phân công":
                query += " AND a.teacher_id IS NOT NULL"
            elif status_filter == "Chưa phân công":
                query += " AND a.teacher_id IS NULL"

            print(f"Debug: Executing query: {query} with params: {params}")
            cursor.execute(query, params)
            rows = cursor.fetchall()

            print(f"Debug: Number of rows fetched: {len(rows)}")
            print(f"Debug: Fetched rows: {rows}")

            if not rows:
                CTkLabel(self.class_list_frame, text="Không có dữ liệu lớp học", font=("Helvetica", 14), text_color="gray").pack(pady=10)
                print("Debug: No data found")
                return

            # Create a row for each class
            for idx, row in enumerate(rows):
                semester_id, module_name, class_id, class_name, num_students, enrolled_students, teacher_name = row
                print(f"Debug: Row {idx+1} - Class ID: {class_id}, Enrolled Students: {enrolled_students}")

                # Row frame for each class
                row_frame = CTkFrame(self.class_list_frame, fg_color="#F5F5F5" if idx % 2 else "#FFFFFF", corner_radius=0)
                row_frame.pack(fill="x", pady=2)

                # Data labels
                CTkLabel(row_frame, text=semester_id, font=("Helvetica", 12), text_color="black", width=70, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=module_name, font=("Helvetica", 12), text_color="black", width=150, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=class_id, font=("Helvetica", 12), text_color="black", width=70, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=class_name, font=("Helvetica", 12), text_color="black", width=220, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=str(num_students), font=("Helvetica", 12), text_color="black", width=100, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=str(enrolled_students) if enrolled_students is not None else "0", font=("Helvetica", 12), text_color="black", width=120, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=teacher_name if teacher_name else "Chưa phân công", font=("Helvetica", 12), text_color="black", width=150, anchor="center").pack(side="left", padx=5)

                # Actions frame
                actions_frame = CTkFrame(row_frame, fg_color="transparent", width=200)
                actions_frame.pack(side="left", padx=5)

                CTkButton(actions_frame, text="Sửa", width=80, fg_color="#FFC107", hover_color="#E0A800", 
                        command=lambda c_id=class_id: self.edit_class(c_id)).pack(side="left", padx=2)

                CTkButton(actions_frame, text="Xóa", width=80, fg_color="#F44336", hover_color="#D32F2F", 
                        command=lambda c_id=class_id: self.delete_class(c_id)).pack(side="left", padx=2)

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu lớp học: {e}")
            print(f"Debug: Database error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        # Làm mới giao diện
        print("Debug: Refreshing class_list_frame")
        self.class_list_frame.update_idletasks()

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
        # Làm trống các trường text
        self.teacher_name.delete(0, END)
        self.teacher_name.configure(placeholder_text="Họ tên")
        
        # Đặt ngày sinh về ngày hiện tại (26/05/2025)
        current_date = datetime.now().strftime('%Y-%m-%d')  # Lấy ngày hiện tại theo định dạng YYYY-MM-DD
        self.date_of_birth.delete(0, END)
        self.date_of_birth.insert(0, current_date)
        
        self.phone.delete(0, END)
        self.phone.configure(placeholder_text="Điện thoại")
        
        self.email.delete(0, END)
        self.email.configure(placeholder_text="Email")
        
        # Đặt combobox khoa về giá trị đầu tiên
        departments = self.get_departments()
        self.dept_combobox.set(departments[0] if departments else "")
        
        # Đặt combobox bằng cấp về "Thạc sĩ" (giả định là giá trị có degree_name là "Thạc sĩ")
        degrees = self.get_degrees()
        selected_degree = ""
        for degree in degrees:
            if "Thạc sĩ" in degree:
                selected_degree = degree
                break
        if not selected_degree and degrees:
            selected_degree = degrees[0]  # Nếu không tìm thấy "Thạc sĩ", lấy giá trị đầu tiên
        self.degree_combobox.set(selected_degree)
        self.update_teacher_coefficient(None)  # Cập nhật hệ số dựa trên bằng cấp "Thạc sĩ"
        
        # Bỏ chọn dòng trong bảng teacher_tree
        for item in self.teacher_tree.selection():
            self.teacher_tree.selection_remove(item)
    

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
        # Create popup window
        add_window = CTkToplevel(self.window)
        add_window.title("Thêm kỳ học mới")
        add_window.resizable(False, False)

        # Set window size
        window_width = 450
        window_height = 300
        add_window.geometry(f"{window_width}x{window_height}")

        # Center the window on the screen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x_position = int((screen_width - window_width) / 2)
        y_position = int((screen_height - window_height) / 2)
        add_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Make window modal
        add_window.transient(self.window)
        add_window.grab_set()

        # Form frame
        form_frame = CTkFrame(add_window, fg_color="#F0F0F0", corner_radius=10)
        form_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Title
        CTkLabel(form_frame, text="Thêm kỳ học mới", font=("Helvetica", 16, "bold"), text_color="black").pack(pady=5)

        # Semester Name (Combobox: Kỳ 1, Kỳ 2, ..., Kỳ 5)
        name_frame = CTkFrame(form_frame, fg_color="transparent")
        name_frame.pack(fill="x", pady=2)
        CTkLabel(name_frame, text="Tên kỳ:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
        semester_name_combobox = CTkComboBox(name_frame, values=["Học kỳ 1", "Học kỳ 2", "Học kỳ 3", "Học kỳ 4", "Học kỳ 5"], width=240, height=32)  # Giảm width từ 300 xuống 260
        semester_name_combobox.pack(side="left")
        semester_name_combobox.set("Học kỳ 1")

        # Academic Year (Combobox: 10 năm trước đến hiện tại)
        year_frame = CTkFrame(form_frame, fg_color="transparent")
        year_frame.pack(fill="x", pady=2)
        CTkLabel(year_frame, text="Năm học:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
        current_year = 2020  # Bắt đầu từ 2010
        academic_years = [f"{y}-{y+1}" for y in range(current_year, 2031)]  # Kết thúc ở 2040
        semester_year_combobox = CTkComboBox(year_frame, values=academic_years, width=240, height=32)
        semester_year_combobox.pack(side="left")
        semester_year_combobox.set("2025-2026")  # Giá trị mặc định

        # Start Date (Calendar)
        start_date_frame = CTkFrame(form_frame, fg_color="transparent")
        start_date_frame.pack(fill="x", pady=2)
        CTkLabel(start_date_frame, text="Ngày bắt đầu:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
        start_date_entry = CTkEntry(start_date_frame, placeholder_text="YYYY-MM-DD", width=210, height=32)  # Giảm width từ 270 xuống 210
        start_date_entry.pack(side="left")
        start_date_entry.insert(0, "2025-01-01")
        calendar_button_start = CTkButton(start_date_frame, text="📅", width=30, height=32, fg_color="#4A4A4A", hover_color="#666666",
                                        command=lambda: self.open_calendar(start_date_entry))
        calendar_button_start.pack(side="left", padx=5)

        # End Date (Calendar)
        end_date_frame = CTkFrame(form_frame, fg_color="transparent")
        end_date_frame.pack(fill="x", pady=2)
        CTkLabel(end_date_frame, text="Ngày kết thúc:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
        end_date_entry = CTkEntry(end_date_frame, placeholder_text="YYYY-MM-DD", width=210, height=32)  # Giảm width từ 270 xuống 210
        end_date_entry.pack(side="left")
        end_date_entry.insert(0, "2025-12-31")
        calendar_button_end = CTkButton(end_date_frame, text="📅", width=30, height=32, fg_color="#4A4A4A", hover_color="#666666",
                                        command=lambda: self.open_calendar(end_date_entry))
        calendar_button_end.pack(side="left", padx=5)

        # Buttons
        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        CTkButton(button_frame, text="Thêm", fg_color="#0085FF", width=100).pack(side="left", padx=5)
        CTkButton(button_frame, text="Hủy", fg_color="#6C757D", width=100, command=lambda: add_window.destroy()).pack(side="left", padx=5)

        # Save function
        def save_semester():
            semester_name = semester_name_combobox.get().strip()
            year = semester_year_combobox.get().strip()
            start_date_str = start_date_entry.get().strip()
            end_date_str = end_date_entry.get().strip()

            # Validation: Check if all fields are filled
            if not all([semester_name, year, start_date_str, end_date_str]):
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!", parent=add_window)
                return

            # Parse dates
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                messagebox.showerror("Lỗi", "Ngày tháng không hợp lệ. Vui lòng nhập theo định dạng YYYY-MM-DD!", parent=add_window)
                return

            # Validation: Start date must be before end date
            if start_date >= end_date:
                messagebox.showerror("Lỗi", "Ngày bắt đầu phải trước ngày kết thúc!", parent=add_window)
                return

            # Validation: Dates must belong to the academic year
            try:
                start_year, end_year = map(int, year.split('-'))
            except ValueError:
                messagebox.showerror("Lỗi", "Năm học không hợp lệ!", parent=add_window)
                return

            if start_date.year != start_year:
                messagebox.showerror("Lỗi", f"Ngày bắt đầu phải thuộc năm {start_year}!", parent=add_window)
                return
            if end_date.year not in [start_year, end_year]:
                messagebox.showerror("Lỗi", f"Ngày kết thúc phải thuộc năm {start_year} hoặc {end_year}!", parent=add_window)
                return

            # Validation: Check for overlapping semesters
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT semester_id FROM semesters
                    WHERE (start_date <= %s AND end_date >= %s)
                    OR (start_date <= %s AND end_date >= %s)
                    OR (%s <= start_date AND %s >= end_date)
                """, (end_date, start_date, end_date, start_date, start_date, end_date))
                if cursor.fetchone():
                    messagebox.showerror("Lỗi", "Thời gian kỳ học này trùng với một kỳ học khác!", parent=add_window)
                    return

                # Generate semester ID
                semester_num = semester_name.split()[-1]  # Lấy số kỳ từ "Kỳ 1", "Kỳ 2", ...
                year_suffix = year[-2:]  # Lấy 2 số cuối của năm
                semester_id = f"HK{semester_num}-{year_suffix}"

                # Check if semester ID already exists
                cursor.execute("SELECT semester_id FROM semesters WHERE semester_id = %s", (semester_id,))
                if cursor.fetchone():
                    messagebox.showerror("Lỗi", f"Kỳ học {semester_id} đã tồn tại!", parent=add_window)
                    return

                # Insert new semester
                cursor.execute("INSERT INTO semesters (semester_id, semester_name, year, start_date, end_date) VALUES (%s, %s, %s, %s, %s)",
                            (semester_id, semester_name, year, start_date, end_date))
                conn.commit()
                messagebox.showinfo("Thành công", f"Thêm kỳ học thành công với mã {semester_id}", parent=add_window)
                self.load_semesters()
                self.semester_list_frame.update_idletasks()
                add_window.destroy()
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể thêm kỳ học: {e}", parent=add_window)
            finally:
                cursor.close()
                conn.close()

        # Bind save function to "Thêm" button
        button_frame.winfo_children()[0].configure(command=save_semester)

    def edit_semester(self, semester_id):
        # Load semester data
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT semester_id, semester_name, year, start_date, end_date
                FROM semesters
                WHERE semester_id = %s
            """, (semester_id,))
            semester_data = cursor.fetchone()
            if not semester_data:
                messagebox.showerror("Lỗi", "Không tìm thấy kỳ học!")
                return

            _, semester_name, year, start_date, end_date = semester_data

            # Create popup window
            edit_window = CTkToplevel(self.window)
            edit_window.title("Sửa kỳ học")
            edit_window.resizable(False, False)

            # Set window size
            window_width = 450
            window_height = 300
            edit_window.geometry(f"{window_width}x{window_height}")

            # Center the window on the screen
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            x_position = int((screen_width - window_width) / 2)
            y_position = int((screen_height - window_height) / 2)
            edit_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

            # Make window modal
            edit_window.transient(self.window)
            edit_window.grab_set()

            # Form frame
            form_frame = CTkFrame(edit_window, fg_color="#F0F0F0", corner_radius=10)
            form_frame.pack(padx=20, pady=10, fill="both", expand=True)

            # Title
            CTkLabel(form_frame, text="Sửa kỳ học", font=("Helvetica", 16, "bold"), text_color="black").pack(pady=5)

            # Semester Name (Combobox: Kỳ 1, Kỳ 2, ..., Kỳ 5)
            name_frame = CTkFrame(form_frame, fg_color="transparent")
            name_frame.pack(fill="x", pady=2)
            CTkLabel(name_frame, text="Tên kỳ:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
            semester_name_combobox = CTkComboBox(name_frame, values=["Học kỳ 1", "Học kỳ 2", "Học kỳ 3", "Học kỳ 4", "Học kỳ 5"], width=240, height=32)  # Giảm width từ 300 xuống 260
            semester_name_combobox.pack(side="left")
            semester_name_combobox.set(semester_name)

            # Academic Year (Combobox: 10 năm trước đến hiện tại)
            year_frame = CTkFrame(form_frame, fg_color="transparent")
            year_frame.pack(fill="x", pady=2)
            CTkLabel(year_frame, text="Năm học:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
            current_year = 2020  # Bắt đầu từ 2010
            academic_years = [f"{y}-{y+1}" for y in range(current_year, 2031)]  # Kết thúc ở 2040
            semester_year_combobox = CTkComboBox(year_frame, values=academic_years, width=240, height=32)
            semester_year_combobox.pack(side="left")
            semester_year_combobox.set(year)  # Set giá trị hiện tại của kỳ học

            # Start Date (Calendar)
            start_date_frame = CTkFrame(form_frame, fg_color="transparent")
            start_date_frame.pack(fill="x", pady=2)
            CTkLabel(start_date_frame, text="Ngày bắt đầu:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
            start_date_entry = CTkEntry(start_date_frame, placeholder_text="YYYY-MM-DD", width=210, height=32)  # Giảm width từ 270 xuống 210
            start_date_entry.pack(side="left")
            start_date_entry.insert(0, start_date.strftime('%Y-%m-%d'))
            calendar_button_start = CTkButton(start_date_frame, text="📅", width=30, height=32, fg_color="#4A4A4A", hover_color="#666666",
                                            command=lambda: self.open_calendar(start_date_entry))
            calendar_button_start.pack(side="left", padx=5)

            # End Date (Calendar)
            end_date_frame = CTkFrame(form_frame, fg_color="transparent")
            end_date_frame.pack(fill="x", pady=2)
            CTkLabel(end_date_frame, text="Ngày kết thúc:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
            end_date_entry = CTkEntry(end_date_frame, placeholder_text="YYYY-MM-DD", width=210, height=32)  # Giảm width từ 270 xuống 210
            end_date_entry.pack(side="left")
            end_date_entry.insert(0, end_date.strftime('%Y-%m-%d'))
            calendar_button_end = CTkButton(end_date_frame, text="📅", width=30, height=32, fg_color="#4A4A4A", hover_color="#666666",
                                            command=lambda: self.open_calendar(end_date_entry))
            calendar_button_end.pack(side="left", padx=5)

            # Buttons
            button_frame = CTkFrame(form_frame, fg_color="transparent")
            button_frame.pack(pady=10)
            CTkButton(button_frame, text="Lưu", fg_color="#0085FF", width=100).pack(side="left", padx=5)
            CTkButton(button_frame, text="Hủy", fg_color="#6C757D", width=100, command=lambda: edit_window.destroy()).pack(side="left", padx=5)

            # Save function
            def save_semester():
                new_semester_name = semester_name_combobox.get().strip() 
                new_year = semester_year_combobox.get().strip()
                new_start_date_str = start_date_entry.get().strip()
                new_end_date_str = end_date_entry.get().strip()

                try:
                    conn = mysql.connector.connect(**DB_CONFIG)
                    cursor = conn.cursor()

                    # 1. Kiểm tra tồn tại semester_id mới
                    semester_num = new_semester_name.split()[-1]  # Lấy số từ "Học kỳ X"
                    year_suffix = new_year[-2:]  # 2 số cuối của năm
                    new_semester_id = f"HK{semester_num}-{year_suffix}"

                    # 2. Kiểm tra trùng lặp 
                    if new_semester_id != semester_id:
                        cursor.execute("""
                            SELECT 1 FROM semesters 
                            WHERE semester_id = %s
                        """, (new_semester_id,))
                        if cursor.fetchone():
                            messagebox.showerror("Lỗi", "Mã kỳ học mới đã tồn tại!", parent=edit_window)
                            return

                    # 3. Thêm semester_id mới trước
                    cursor.execute("""
                        INSERT INTO semesters (semester_id, semester_name, year, start_date, end_date)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (new_semester_id, new_semester_name, new_year, new_start_date_str, new_end_date_str))

                    # 4. Cập nhật classes về semester_id mới
                    cursor.execute("""
                        UPDATE classes 
                        SET semester_id = %s
                        WHERE semester_id = %s
                    """, (new_semester_id, semester_id))

                    # 5. Xóa semester_id cũ
                    if new_semester_id != semester_id:
                        cursor.execute("DELETE FROM semesters WHERE semester_id = %s", (semester_id,))

                    conn.commit()
                    messagebox.showinfo("Thành công", "Cập nhật học kỳ thành công!", parent=edit_window)
                    self.load_semesters()
                    edit_window.destroy()

                except mysql.connector.Error as e:
                    conn.rollback()
                    messagebox.showerror("Lỗi", f"Không thể cập nhật kỳ học: {e}", parent=edit_window)
                finally:
                    cursor.close()
                    conn.close()


            # Bind save function to "Lưu" button
            button_frame.winfo_children()[0].configure(command=save_semester)

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu kỳ học: {e}")
        finally:
            cursor.close()
            conn.close()

    def delete_semester(self, semester_id):
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
                self.load_semesters()
                self.semester_list_frame.update_idletasks()
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể xóa kỳ học: {str(e)}")
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

    def load_semesters(self):
        # Clear existing items in semester_list_frame
        for widget in self.semester_list_frame.winfo_children():
            widget.destroy()

        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            query = """
                SELECT semester_id, semester_name, year, start_date, end_date
                FROM semesters
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            if not rows:
                CTkLabel(self.semester_list_frame, text="Không có dữ liệu kỳ học", font=("Helvetica", 14), text_color="gray").pack(pady=10)
                return

            # Create a row for each semester
            for row in rows:
                semester_id, semester_name, year, start_date, end_date = row

                # Row frame for each semester
                row_frame = CTkFrame(self.semester_list_frame, fg_color="#F5F5F5", corner_radius=0)
                row_frame.pack(fill="x", pady=2)

                # Data labels (khớp với heading)
                CTkLabel(row_frame, text=semester_id, font=("Helvetica", 12), text_color="black", width=150, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=semester_name, font=("Helvetica", 12), text_color="black", width=200, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=year, font=("Helvetica", 12), text_color="black", width=150, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=start_date.strftime('%Y-%m-%d'), font=("Helvetica", 12), text_color="black", width=200, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=end_date.strftime('%Y-%m-%d'), font=("Helvetica", 12), text_color="black", width=200, anchor="center").pack(side="left", padx=5)

                # Actions frame
                actions_frame = CTkFrame(row_frame, fg_color="transparent", width=150)
                actions_frame.pack(side="left", padx=5)

                # Edit button
                CTkButton(actions_frame, text="Sửa", width=50, fg_color="#FFC107", hover_color="#E0A800", 
                        command=lambda s_id=semester_id: self.edit_semester(s_id)).pack(side="left", padx=5)

                # Delete button
                CTkButton(actions_frame, text="Xóa", width=50, fg_color="#F44336", hover_color="#D32F2F", 
                        command=lambda s_id=semester_id: self.delete_semester(s_id)).pack(side="left", padx=5)

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu kỳ học: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        # Làm mới giao diện
        self.semester_list_frame.update_idletasks()
        
    
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
            cursor.execute("SELECT semester_id FROM semesters ORDER BY semester_id")
            semesters = [row[0] for row in cursor.fetchall()]
            return semesters
        except mysql.connector.Error:
            return []
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


    def assign_teacher(self, class_id):
        # Lấy thông tin lớp học để xác định khoa của học phần
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.dept_id, a.teacher_id
                FROM classes c
                JOIN course_modules m ON c.module_id = m.module_id
                LEFT JOIN assignments a ON c.class_id = a.class_id
                WHERE c.class_id = %s
            """, (class_id,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Lỗi", "Không tìm thấy lớp học!", parent=self.window)
                return
            dept_id, current_teacher = result

            # Lấy danh sách giảng viên thuộc khoa của học phần
            cursor.execute("SELECT teacher_id, full_name FROM teachers WHERE dept_id = %s", (dept_id,))
            teachers = [f"{row[0]}: {row[1]}" for row in cursor.fetchall()]

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {e}", parent=self.window)
            return
        finally:
            cursor.close()
            conn.close()

        # Create popup window
        assign_window = CTkToplevel(self.window)
        assign_window.title("Phân công giảng viên")
        assign_window.resizable(False, False)

        # Set window size
        window_width = 500
        window_height = 350
        assign_window.geometry(f"{window_width}x{window_height}")

        # Center the window on the screen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x_position = int((screen_width - window_width) / 2)
        y_position = int((screen_height - window_height) / 2)
        assign_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Make window modal
        assign_window.transient(self.window)
        assign_window.grab_set()

        # Form frame
        form_frame = CTkFrame(assign_window, fg_color="#F0F0F0", corner_radius=10)
        form_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Title
        CTkLabel(form_frame, text="Phân công giảng viên", font=("Helvetica", 16, "bold"), text_color="black").pack(pady=5)

        # Teacher Combobox
        teacher_frame = CTkFrame(form_frame, fg_color="transparent")
        teacher_frame.pack(fill="x", pady=2)
        CTkLabel(teacher_frame, text="Giảng viên:", font=("Helvetica", 12), text_color="black", width=120, anchor="w").pack(side="left", padx=(0, 5))
        teacher_combobox = CTkComboBox(teacher_frame, values=teachers, width=260, height=32)
        teacher_combobox.pack(side="left")
        if current_teacher:
            for teacher in teachers:
                if teacher.startswith(current_teacher):
                    teacher_combobox.set(teacher)
                    break
        elif teachers:
            teacher_combobox.set(teachers[0])

        # Buttons
        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        CTkButton(button_frame, text="Phân công", fg_color="#0085FF", width=100).pack(side="left", padx=5)
        CTkButton(button_frame, text="Hủy", fg_color="#6C757D", width=100, command=lambda: assign_window.destroy()).pack(side="left", padx=5)

        # Save function
        def save_assignment():
            selected_teacher = teacher_combobox.get().strip()
            if not selected_teacher:
                messagebox.showerror("Lỗi", "Vui lòng chọn giảng viên!", parent=assign_window)
                return

            teacher_id = selected_teacher.split(":")[0].strip()

            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()

                # Check if class is already assigned
                cursor.execute("SELECT assignment_id FROM assignments WHERE class_id = %s", (class_id,))
                existing_assignment = cursor.fetchone()

                if existing_assignment:
                    # Update existing assignment
                    cursor.execute("UPDATE assignments SET teacher_id = %s, assigned_at = CURRENT_TIMESTAMP WHERE class_id = %s",
                                (teacher_id, class_id))
                else:
                    # Generate assignment ID
                    cursor.execute("SELECT assignment_id FROM assignments ORDER BY CAST(SUBSTRING(assignment_id, 4) AS UNSIGNED) DESC LIMIT 1")
                    result = cursor.fetchone()
                    if result:
                        last_id = result[0]
                        last_num = int(last_id[3:])
                        new_num = last_num + 1
                    else:
                        new_num = 1
                    assignment_id = f"ASN{str(new_num).zfill(5)}"

                    # Insert new assignment
                    cursor.execute("INSERT INTO assignments (assignment_id, class_id, teacher_id) VALUES (%s, %s, %s)",
                                (assignment_id, class_id, teacher_id))

                conn.commit()
                messagebox.showinfo("Thành công", "Phân công giảng viên thành công!", parent=assign_window)
                self.load_classes()
                self.class_list_frame.update_idletasks()
                assign_window.destroy()
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể phân công giảng viên: {e}", parent=assign_window)
            finally:
                cursor.close()
                conn.close()

        # Bind save function to "Phân công" button
        button_frame.winfo_children()[0].configure(command=save_assignment)

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
            plt.xticks(rotation=0, ha="right")

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
        year = self.stats_year_combobox.get().strip()
        if not year:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn năm học!")
            return

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Lấy danh sách học kỳ trong năm
            cursor.execute("SELECT semester_name FROM semesters WHERE year = %s ORDER BY semester_name", (year,))
            semesters = [row[0] for row in cursor.fetchall()]

            # Kiểm tra xem có dữ liệu không
            cursor.execute("""
                SELECT COUNT(*)
                FROM classes c
                JOIN semesters s ON c.semester_id = s.semester_id
                JOIN course_modules cm ON c.module_id = cm.module_id
                WHERE s.year = %s
            """, (year,))
            has_data = cursor.fetchone()[0] > 0

            if not has_data:
                messagebox.showwarning("Cảnh báo", f"Không có dữ liệu để xuất trong năm học {year}!")
                return

            # Lấy dữ liệu thống kê
            cursor.execute("""
                SELECT 
                    cm.module_name,
                    s.semester_name,
                    COUNT(c.class_id) as class_count,
                    SUM(c.num_students) as total_students
                FROM course_modules cm
                LEFT JOIN classes c ON cm.module_id = c.module_id
                LEFT JOIN semesters s ON c.semester_id = s.semester_id
                WHERE s.year = %s
                GROUP BY cm.module_name, s.semester_name
                ORDER BY cm.module_name, s.semester_name
            """, (year,))
            rows = cursor.fetchall()

            # Tạo DataFrame cho pivot table
            df = pd.DataFrame(rows, columns=['Học phần', 'Kỳ học', 'Số lớp', 'Số sinh viên'])
            pivot_df = pd.pivot_table(
                df,
                values='Số lớp',
                index=['Học phần'],
                columns=['Kỳ học'],
                fill_value=0,
                aggfunc='sum'
            )

            # Tính tổng số lớp và sinh viên
            total_classes = df.groupby('Học phần')['Số lớp'].sum()
            total_students = df.groupby('Học phần')['Số sinh viên'].sum()
            avg_students = total_students / total_classes

            # Gộp các DataFrame
            result_df = pd.DataFrame({
                'Tổng số lớp': total_classes,
                'Tổng sinh viên': total_students,
                'TB SV/lớp': avg_students.round(1)
            })

            # Kết hợp pivot table với các cột tổng
            final_df = pd.concat([pivot_df, result_df], axis=1)

            # Thêm hàng tổng cộng
            sums = final_df.sum()
            sums['TB SV/lớp'] = (final_df['Tổng sinh viên'].sum() / final_df['Tổng số lớp'].sum()).round(1)
            final_df.loc['TỔNG CỘNG'] = sums

            # Xuất Excel
            output_file = f"Class_Stats_Report_{year}.xlsx"
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                final_df.to_excel(writer, sheet_name='Statistics')
                
                # Định dạng
                workbook = writer.book
                worksheet = writer.sheets['Statistics']
                
                # Format cho header
                header_format = workbook.add_format({
                    'bold': True,
                    'align': 'center',
                    'valign': 'vcenter',
                    'bg_color': '#D3D3D3'
                })
                
                # Format cho số liệu
                number_format = workbook.add_format({
                    'align': 'center',
                    'valign': 'vcenter'
                })

                # Áp dụng format
                for col_num, value in enumerate(final_df.columns.values):
                    worksheet.write(0, col_num + 1, value, header_format)
                    worksheet.set_column(col_num + 1, col_num + 1, 15)

                # Format cho cột học phần
                worksheet.set_column(0, 0, 30)

            messagebox.showinfo("Thành công", f"Báo cáo đã được xuất: {output_file}")

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {e}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất file Excel: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


    def show_class_stats_table(self):
        for widget in self.class_stats_frame.winfo_children():
            widget.destroy()

        data = self.get_class_stats_data()
        if not data:
            ctk.CTkLabel(self.class_stats_frame, text="Không có dữ liệu lớp học trong năm học này.", 
                         font=("Helvetica", 14), text_color="gray").pack(pady=10)
            self.clear_summary_labels()
            return

        self.update_summary_labels(data)
        self.show_table(data)

    def show_class_stats_chart(self):
        for widget in self.class_stats_frame.winfo_children():
            widget.destroy()

        data = self.get_class_stats_data()
        if not data or data["total_classes"] == 0:
            ctk.CTkLabel(self.class_stats_frame, text="Không có dữ liệu lớp học trong năm học này.", 
                        font=("Helvetica", 14), text_color="gray").pack(pady=10)
            self.clear_summary_labels()
            return

        self.update_summary_labels(data)
        self.show_charts(data)


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
                btn = CTkButton(self.submenu_frames[main_item], text=f"{item}", font=("Helvetica", 14), fg_color="transparent",
                                text_color="#DDEEFF", hover_color="#5A9BFF", anchor="w",
                                command=lambda x=item: self.switch_tab(x))
                btn.place(relx=0.15, rely=0, y=-button_height)  # Lùi vào 15% từ lề trái, bỏ relwidth để không mở rộng
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

    def open_calendar(self, entry_field):
        # Tạo cửa sổ lịch
        calendar_window = CTkToplevel(self.window)
        calendar_window.title("Chọn ngày")
        calendar_window.resizable(False, False)

        # Đè lên cửa sổ chính
        calendar_window.transient(self.window)
        calendar_window.grab_set()

        # Tạo lịch
        cal = Calendar(calendar_window, selectmode="day", date_pattern="yyyy-mm-dd", font=("Helvetica", 12))
        cal.pack(padx=10, pady=10)

        # Căn giữa cửa sổ lịch so với cửa sổ chính
        self.window.update_idletasks()  # Cập nhật kích thước cửa sổ chính
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        window_x = self.window.winfo_x()
        window_y = self.window.winfo_y()
        cal_width = calendar_window.winfo_reqwidth()
        cal_height = calendar_window.winfo_reqheight()
        pos_x = window_x + (window_width // 2) - (cal_width // 2)
        pos_y = window_y + (window_height // 2) - (cal_height // 2)
        calendar_window.geometry(f"+{pos_x}+{pos_y}")

        # Hàm chọn ngày
        def select_date():
            selected_date = cal.get_date()
            entry_field.delete(0, "end")
            entry_field.insert(0, selected_date)
            calendar_window.destroy()

        # Nút chọn ngày
        CTkButton(calendar_window, text="Chọn", fg_color="#0085FF", hover_color="#005BB5", width=100, height=30, font=("Helvetica", 12, "bold"), command=select_date).pack(pady=5)


    def get_class_stats_data(self):
        year = self.stats_year_combobox.get().strip()
        if not year:
            return None

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Lấy danh sách các học kỳ trong năm học
            cursor.execute("""
                SELECT semester_id, semester_name 
                FROM semesters 
                WHERE year = %s
                ORDER BY semester_id
            """, (year,))
            semesters = [row[0] for row in cursor.fetchall()]

            # Truy vấn chính
            cursor.execute("""
                SELECT 
                    cm.module_name,
                    s.semester_id,
                    COUNT(c.class_id) as class_count,
                    COALESCE(SUM(ce.enrolled_students), 0) as total_enrolled,
                    COALESCE(AVG(ce.enrolled_students), 0) as avg_enrolled
                FROM classes c
                JOIN semesters s ON c.semester_id = s.semester_id
                JOIN course_modules cm ON c.module_id = cm.module_id
                LEFT JOIN class_enrollments ce ON c.class_id = ce.class_id
                WHERE s.year = %s
                GROUP BY cm.module_name, s.semester_id
                ORDER BY cm.module_name, s.semester_id
            """, (year,))
            pivot_data = cursor.fetchall()

            # Tổng số lớp và sinh viên
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT c.class_id) as total_classes,
                    COUNT(DISTINCT cm.module_id) as total_modules,
                    COALESCE(SUM(ce.enrolled_students), 0) as total_enrolled,
                    COALESCE(AVG(ce.enrolled_students), 0) as avg_enrolled
                FROM classes c
                JOIN semesters s ON c.semester_id = s.semester_id
                JOIN course_modules cm ON c.module_id = cm.module_id
                LEFT JOIN class_enrollments ce ON c.class_id = ce.class_id
                WHERE s.year = %s
            """, (year,))
            summary = cursor.fetchone()

            # Top 5 học phần có nhiều sinh viên nhất
            cursor.execute("""
                SELECT 
                    cm.module_name,
                    COALESCE(SUM(ce.enrolled_students), 0) as total_enrolled
                FROM classes c
                JOIN semesters s ON c.semester_id = s.semester_id
                JOIN course_modules cm ON c.module_id = cm.module_id
                LEFT JOIN class_enrollments ce ON c.class_id = ce.class_id
                WHERE s.year = %s
                GROUP BY cm.module_name
                ORDER BY total_enrolled DESC
                LIMIT 5
            """, (year,))
            top_modules = cursor.fetchall()

            return {
                "semesters": semesters,
                "pivot_data": pivot_data,
                "total_classes": summary[0] if summary else 0,
                "total_modules": summary[1] if summary else 0,
                "total_students": int(summary[2]) if summary else 0,
                "avg_students": round(float(summary[3]), 1) if summary else 0,
                "top_modules": top_modules
            }

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu thống kê: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


    def show_class_stats_all(self):
        for widget in self.class_stats_frame.winfo_children():
            widget.destroy()

        data = self.get_class_stats_data()
        if not data:
            ctk.CTkLabel(self.class_stats_frame, text="Không có dữ liệu lớp học trong năm học này.", 
                         font=("Helvetica", 14), text_color="gray").pack(pady=10)
            self.clear_summary_labels()
            return

        self.update_summary_labels(data)
        self.show_charts(data)
        self.show_table(data)
    
    def update_class_stats(self, event=None):
        # Mặc định hiển thị biểu đồ khi vào tab hoặc thay đổi năm
        self.show_class_stats_chart()

    def update_stat_labels(self, data):
        """Cập nhật các nhãn thống kê"""
        self.total_classes_label.configure(text=str(data["total_classes"]))
        self.total_modules_label.configure(text=f"{data['total_modules']}")
        self.total_students_label.configure(text=str(data["total_students"]))
        self.avg_students_label.configure(text=f"TB {data['avg_students']} SV/lớp")
        self.sem1_classes_label.configure(text=str(data["sem1_count"]))
        self.sem1_percentage_label.configure(text=f"{data['sem1_percentage']}%")
        self.sem2_classes_label.configure(text=str(data["sem2_count"]))
        self.sem2_percentage_label.configure(text=f"{data['sem2_percentage']}%")


    def show_charts(self, data):
        chart_frame = ctk.CTkFrame(self.class_stats_frame, fg_color="white")
        chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Tính toán số lớp theo học phần
        module_counts = {}
        for row in data["pivot_data"]:
            module_name = row[0]  # module_name
            class_count = row[2]  # class_count
            if module_name not in module_counts:
                module_counts[module_name] = 0
            module_counts[module_name] += class_count

        # Biểu đồ số lớp theo kỳ học
        fig1, ax1 = plt.subplots(figsize=(10, 3))
        pivot_counts = {}
        for row in data["pivot_data"]:
            sem_name = row[1]  # semester_name
            class_count = row[2]  # class_count
            if sem_name not in pivot_counts:
                pivot_counts[sem_name] = 0
            pivot_counts[sem_name] += class_count

        x = np.arange(len(data["semesters"]))
        ax1.bar(x, [pivot_counts.get(sem, 0) for sem in data["semesters"]], color='#36A2EB')
        ax1.set_xlabel('Kỳ học', fontsize=10)
        ax1.set_ylabel('Số lớp', fontsize=10)
        ax1.set_xticks(x)
        ax1.set_xticklabels(data["semesters"], rotation=0, ha='center', fontsize=10)
        ax1.set_title(f'Số lớp theo kỳ học ({self.stats_year_combobox.get()})', fontsize=12, pad=15)
        plt.tight_layout()

        canvas1 = FigureCanvasTkAgg(fig1, master=chart_frame)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="x", expand=True, pady=5)

        # Biểu đồ top 5 học phần
        fig2, ax2 = plt.subplots(figsize=(10, 3))
        module_names = [row[0] for row in data["top_modules"]]
        total_students = [row[1] for row in data["top_modules"]]
        
        ax2.bar(module_names, total_students, color='#FF6384')
        ax2.set_xlabel('Học phần', fontsize=10)
        ax2.set_ylabel('Tổng sinh viên', fontsize=10)
        ax2.set_xticks(range(len(module_names)))
        ax2.set_xticklabels(module_names, rotation=0, ha='right', fontsize=10)
        ax2.set_title(f'Top 5 học phần nhiều SV nhất ({self.stats_year_combobox.get()})', fontsize=12)
        plt.tight_layout()

        canvas2 = FigureCanvasTkAgg(fig2, master=chart_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="x", expand=True, pady=5)
            
    def update_summary_labels(self, data):
        """Cập nhật các nhãn thống kê"""
        # Cập nhật tổng số lớp
        self.total_classes_label.configure(text=str(data["total_classes"]) if data["total_classes"] is not None else "0")
        
        # Cập nhật tổng số học phần
        self.total_modules_label.configure(text=f"{data['total_modules']}" if data["total_modules"] is not None else "0")
        
        # Cập nhật tổng số sinh viên
        self.total_students_label.configure(text=str(data["total_students"]) if data["total_students"] is not None else "0")
        
        # Cập nhật trung bình sinh viên/lớp  
        self.avg_per_class_label.configure(text=str(data["avg_students"]) if data["avg_students"] is not None else "0")

    def clear_summary_labels(self):
        """Xóa hoặc đặt lại các nhãn thống kê về giá trị mặc định"""
        self.total_classes_label.configure(text="0")
        self.total_modules_label.configure(text="0")
        self.total_students_label.configure(text="0")
        self.avg_per_class_label.configure(text="0")

    def show_table(self, data):
        # Kiểm tra dữ liệu trước khi tạo bảng
        if not data or not data["pivot_data"]:
            ctk.CTkLabel(self.class_stats_frame, text="Không có dữ liệu", 
                        font=("Helvetica", 14), text_color="gray").pack(pady=20)
            return

        table_frame = ctk.CTkFrame(self.class_stats_frame, fg_color="#FFFFFF", corner_radius=10)
        table_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Tính toán số cột và chiều rộng
        num_semesters = len(data["semesters"])
        if num_semesters == 0:  # Thêm kiểm tra này
            num_semesters = 1  # Đặt giá trị mặc định để tránh chia cho 0

        # Tính chiều rộng mỗi cột
        total_width = 1100  # Tổng chiều rộng có sẵn
        col_widths = {
            "module": int(total_width * 0.25),  # 25% cho cột học phần
            "semester": int((total_width * 0.45) / num_semesters),  # 45% chia đều cho các kỳ
            "summary": int((total_width * 0.30) / 3)  # 30% chia đều cho 3 cột tổng
        }

        # Frame tiêu đề
        heading_frame = ctk.CTkFrame(table_frame, fg_color="#D3D3D3", corner_radius=0, height=40)
        heading_frame.pack(fill="x", padx=5, pady=(5,0))
        heading_frame.pack_propagate(False)

        # Tạo tiêu đề
        ctk.CTkLabel(heading_frame, text="Học phần", 
                    font=("Helvetica", 12, "bold"), width=col_widths["module"],
                    anchor="center").pack(side="left")
                    
        for sem in data["semesters"]:
            ctk.CTkLabel(heading_frame, text=f"Số lớp {sem}",
                        font=("Helvetica", 12, "bold"), width=col_widths["semester"],
                        anchor="center").pack(side="left")
                        
        summary_headers = ["Tổng số lớp", "Tổng sinh viên", "TB SV/lớp"]
        for header in summary_headers:
            ctk.CTkLabel(heading_frame, text=header,
                        font=("Helvetica", 12, "bold"), width=col_widths["summary"],
                        anchor="center").pack(side="left")

        # Frame cho dữ liệu
        data_frame = ctk.CTkScrollableFrame(table_frame, fg_color="transparent") 
        data_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Tạo pivot_dict từ pivot_data
        pivot_dict = {}
        grand_total_classes = 0
        grand_total_students = 0
        semester_totals = {sem: 0 for sem in data["semesters"]}  # Khởi tạo tổng theo kỳ

        for row in data["pivot_data"]:
            module_name = row[0]
            sem_name = row[1]
            class_count = row[2]
            total_students = row[3]

            if module_name not in pivot_dict:
                pivot_dict[module_name] = {
                    "semesters": {sem: 0 for sem in data["semesters"]},
                    "total_students": 0,
                    "total_classes": 0
                }
            pivot_dict[module_name]["semesters"][sem_name] = class_count
            pivot_dict[module_name]["total_students"] += total_students
            pivot_dict[module_name]["total_classes"] += class_count
            
            # Cập nhật tổng theo kỳ
            semester_totals[sem_name] += class_count
            grand_total_classes += class_count
            grand_total_students += total_students

        # Hiển thị dữ liệu từng dòng
        for module_name, stats in pivot_dict.items():
            row_frame = ctk.CTkFrame(data_frame, fg_color="#F5F5F5", corner_radius=0, height=35)
            row_frame.pack(fill="x", pady=1)
            row_frame.pack_propagate(False)

            # Tên học phần
            ctk.CTkLabel(row_frame, text=module_name,
                        font=("Helvetica", 12), width=col_widths["module"],
                        anchor="center").pack(side="left")
                        
            # Số lớp theo kỳ
            for sem in data["semesters"]:
                ctk.CTkLabel(row_frame, text=str(stats["semesters"].get(sem, 0)),
                            font=("Helvetica", 12), width=col_widths["semester"],
                            anchor="center").pack(side="left")

            # Các cột tổng
            summary_values = [
                stats["total_classes"],
                stats["total_students"],
                f"{stats['total_students']/stats['total_classes']:.1f}" if stats["total_classes"] > 0 else "0"
            ]
            for value in summary_values:
                ctk.CTkLabel(row_frame, text=str(value),
                            font=("Helvetica", 12), width=col_widths["summary"],
                            anchor="center").pack(side="left")

        # Thêm dòng tổng cộng
        total_frame = ctk.CTkFrame(data_frame, fg_color="#E0E0E0", corner_radius=0, height=35)
        total_frame.pack(fill="x", pady=1)
        total_frame.pack_propagate(False)

        # Label "TỔNG CỘNG"
        ctk.CTkLabel(total_frame, text="TỔNG CỘNG",
                    font=("Helvetica", 12, "bold"), width=col_widths["module"],
                    anchor="center").pack(side="left")

        # Tổng theo từng kỳ
        for sem in data["semesters"]:
            ctk.CTkLabel(total_frame, text=str(semester_totals[sem]),
                        font=("Helvetica", 12, "bold"), width=col_widths["semester"],
                        anchor="center").pack(side="left")

        # Tổng các cột cuối
        avg_per_class = grand_total_students / grand_total_classes if grand_total_classes > 0 else 0
        summary_totals = [
            grand_total_classes,
            grand_total_students,
            f"{avg_per_class:.1f}"
        ]
        for value in summary_totals:
            ctk.CTkLabel(total_frame, text=str(value),
                        font=("Helvetica", 12, "bold"), width=col_widths["summary"],
                        anchor="center").pack(side="left")

    
            
    def refresh_data_realtime(self):
        # Làm mới dữ liệu và cập nhật giao diện
        self.update_class_stats()
        messagebox.showinfo("Thành công", "Dữ liệu đã được cập nhật theo thời gian thực!")

    def get_dept_ids(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT dept_id FROM departments")
            dept_ids = [row[0] for row in cursor.fetchall()]
            return dept_ids
        except mysql.connector.Error:
            return ['DEPT2321']  # Giá trị mặc định nếu lỗi
        finally:
            cursor.close()
            conn.close()

    def get_filtered_modules(self, dept_id=None):
        """Lấy danh sách học phần theo khoa"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            if dept_id:
                query = """
                    SELECT module_id, module_name 
                    FROM course_modules 
                    WHERE dept_id = %s
                    ORDER BY module_name
                """
                cursor.execute(query, (dept_id,))
            else:
                query = """
                    SELECT module_id, module_name 
                    FROM course_modules
                    ORDER BY module_name
                """
                cursor.execute(query)
                
            modules = [f"{row[0]}: {row[1]}" for row in cursor.fetchall()]
            return modules if modules else ["Không có học phần"]
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách học phần: {e}")
            return ["Lỗi tải học phần"]
        finally:
            cursor.close()
            conn.close()

    def add_teacher_coefficient(self):
        year = self.coefficient_year_filter.get().strip()
        if not year:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn năm học")
            return

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM teacher_coefficients WHERE year = %s", (year,))
            if cursor.fetchone()[0] > 0:
                messagebox.showwarning("Cảnh báo", f"Đã có dữ liệu hệ số cho năm học {year}!")
                return

            # Thêm mặc định với kiểm tra degree_id
            default_coefficients = [
                ('DEG82838', 1.3),  # Đại học
                ('DEG12238', 1.5),  # Thạc sĩ
                ('DEG34993', 1.7),  # Tiến sĩ
                ('DEG21434', 2.0),  # Phó giáo sư
                ('DEG92138', 2.5)   # Giáo sư
            ]
            for degree_id, coefficient in default_coefficients:
                cursor.execute("SELECT COUNT(*) FROM degrees WHERE degree_id = %s", (degree_id,))
                if cursor.fetchone()[0] == 0:
                    messagebox.showerror("Lỗi", f"degree_id {degree_id} không tồn tại trong bảng degrees!")
                    return
                cursor.execute("INSERT INTO teacher_coefficients (degree_id, year, coefficient) VALUES (%s, %s, %s)",
                            (degree_id, year, coefficient))
            conn.commit()
            messagebox.showinfo("Thành công", f"Đã thêm hệ số mặc định cho năm học {year}!")
            self.load_teacher_coefficients()
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể thêm hệ số mặc định: {e}")
        finally:
            cursor.close()
            conn.close()

    def edit_teacher_coefficient(self, degree_id, degree_name, current_coeff, year):
        edit_window = CTkToplevel(self.window)
        edit_window.title("Sửa hệ số giáo viên")
        edit_window.geometry("400x250")
        edit_window.resizable(False, False)
        edit_window.transient(self.window)
        edit_window.grab_set()

        form_frame = CTkFrame(edit_window, fg_color="#F0F0F0", corner_radius=10)
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        CTkLabel(form_frame, text="Sửa hệ số giáo viên", font=("Helvetica", 16, "bold"), text_color="black").pack(pady=10)

        # Degree field (disabled)
        degree_row = CTkFrame(form_frame, fg_color="transparent")
        degree_row.pack(fill="x", pady=2)
        CTkLabel(degree_row, text="Bằng cấp:", font=("Helvetica", 12), width=100, anchor="e").pack(side="left", padx=(0, 5))
        degree_var = CTkEntry(degree_row, width=250)
        degree_var.pack(side="left", pady=5)
        degree_var.insert(0, f"{degree_name} (ID: {degree_id})")
        degree_var.configure(state="disabled")

        # Year field (disabled)
        year_row = CTkFrame(form_frame, fg_color="transparent")
        year_row.pack(fill="x", pady=2)
        CTkLabel(year_row, text="Năm học:", font=("Helvetica", 12), width=100, anchor="e").pack(side="left", padx=(0, 5))
        year_var = CTkEntry(year_row, width=250)
        year_var.pack(side="left", pady=5)
        year_var.insert(0, year)
        year_var.configure(state="disabled")

        # Coefficient field
        coeff_row = CTkFrame(form_frame, fg_color="transparent")
        coeff_row.pack(fill="x", pady=2)
        CTkLabel(coeff_row, text="Hệ số:", font=("Helvetica", 12), width=100, anchor="e").pack(side="left", padx=(0, 5))
        coeff_var = CTkEntry(coeff_row, width=250)
        coeff_var.pack(side="left", pady=5)
        coeff_var.insert(0, str(current_coeff))

        def save_coefficient():
            coeff = coeff_var.get().strip()
            try:
                coeff = float(coeff)
                if coeff < 1.0:
                    messagebox.showerror("Lỗi", "Hệ số phải lớn hơn 1.0!", parent=edit_window)
                    return
            except ValueError:
                messagebox.showerror("Lỗi", "Hệ số phải là số hợp lệ!", parent=edit_window)
                return

            if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn cập nhật hệ số cho năm {year}?"):
                try:
                    conn = mysql.connector.connect(**DB_CONFIG)
                    cursor = conn.cursor()
                    # Kiểm tra bản ghi hiện tại
                    cursor.execute("""
                        SELECT coefficient FROM teacher_coefficients 
                        WHERE degree_id = %s AND year = %s
                    """, (degree_id, year))
                    existing_coeff = cursor.fetchone()

                    if existing_coeff:
                        cursor.execute("""
                            UPDATE teacher_coefficients 
                            SET coefficient = %s 
                            WHERE degree_id = %s AND year = %s
                        """, (coeff, degree_id, year))
                    else:
                        cursor.execute("""
                            INSERT INTO teacher_coefficients (year, degree_id, coefficient)
                            VALUES (%s, %s, %s)
                        """, (year, degree_id, coeff))
                    conn.commit()

                    # Kiểm tra toàn bộ dữ liệu sau khi cập nhật
                    cursor.execute("""
                        SELECT year, coefficient FROM teacher_coefficients 
                        WHERE degree_id = %s ORDER BY year
                    """, (degree_id,))
                    all_coeffs_after = cursor.fetchall()
                    print(f"Debug [10:46 AM, 14/06/2025] - Updated coefficient for degree_id: {degree_id}, year: {year}, new_coeff: {coeff}, existing: {existing_coeff}, all_coeffs_after: {all_coeffs_after}")
                    messagebox.showinfo("Thành công", f"Cập nhật hệ số cho năm {year} thành công!")
                    self.load_teacher_coefficients()
                    edit_window.destroy()
                except mysql.connector.Error as e:
                    messagebox.showerror("Lỗi", f"Không thể lưu hệ số: {e}", parent=edit_window)
                finally:
                    cursor.close()
                    conn.close()

        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        CTkButton(button_frame, text="Lưu", fg_color="#0085FF", command=save_coefficient, width=100).pack(side="left", padx=5)
        CTkButton(button_frame, text="Hủy", fg_color="#6C757D", command=edit_window.destroy, width=100).pack(side="left", padx=5)

    def delete_teacher_coefficient(self, degree_id, degree_name, year):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            # Kiểm tra xem có đang sử dụng trong phân công không
            cursor.execute("""
                SELECT 1 
                FROM teachers t 
                WHERE t.degree_id = %s 
                LIMIT 1
            """, (degree_id,))
            if cursor.fetchone():
                messagebox.showwarning("Cảnh báo", f"Bằng cấp {degree_name} đang được sử dụng trong phân công. Xóa có thể ảnh hưởng đến dữ liệu!")
                if not messagebox.askyesno("Xác nhận", f"Bạn vẫn muốn xóa hệ số của {degree_name} trong năm {year}?"):
                    return
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể kiểm tra phân công: {e}")
            return
        finally:
            cursor.close()
            conn.close()

        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa hệ số của {degree_name} trong năm {year}?"):
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM teacher_coefficients WHERE degree_id = %s AND year = %s", (degree_id, year))
                conn.commit()
                messagebox.showinfo("Thành công", "Xóa hệ số thành công!")
                self.load_teacher_coefficients()
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể xóa hệ số: {e}")
            finally:
                cursor.close()
                conn.close()
    def load_teacher_coefficients(self, event=None):
        year = self.coefficient_year_filter.get().strip()
        if not year:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn năm học")
            return

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Lấy tất cả bằng cấp và hệ số từ teacher_coefficients cho năm học
            cursor.execute("""
                SELECT d.degree_name, tc.coefficient, d.degree_id, tc.coefficient IS NOT NULL AS has_custom_coeff
                FROM degrees d
                LEFT JOIN teacher_coefficients tc ON d.degree_id = tc.degree_id AND tc.year = %s
                ORDER BY d.degree_name
            """, (year,))
            rows = cursor.fetchall()

            # Clear previous data
            for widget in self.coefficient_list_frame.winfo_children():
                widget.destroy()

            if not rows:
                CTkLabel(self.coefficient_list_frame, text="Không có dữ liệu bằng cấp", font=("Helvetica", 12), text_color="gray").pack(pady=10)
                return

            # Heading
            heading_frame = CTkFrame(self.coefficient_list_frame, fg_color="#D3D3D3", corner_radius=0)
            heading_frame.pack(fill="x", padx=5, pady=(5, 0))
            CTkLabel(heading_frame, text="STT", font=("Helvetica", 12, "bold"), width=50, anchor="center").pack(side="left", padx=5)
            CTkLabel(heading_frame, text="Bằng cấp", font=("Helvetica", 12, "bold"), width=500, anchor="center").pack(side="left", padx=5)
            CTkLabel(heading_frame, text="Hệ số", font=("Helvetica", 12, "bold"), width=100, anchor="center").pack(side="left", padx=5)
            CTkLabel(heading_frame, text="Trạng thái", font=("Helvetica", 12, "bold"), width=200, anchor="center").pack(side="left", padx=5)
            CTkLabel(heading_frame, text="Thao tác", font=("Helvetica", 12, "bold"), width=200, anchor="center").pack(side="left", padx=5)

            # Populate table
            for idx, (degree_name, coefficient, degree_id, has_custom_coeff) in enumerate(rows, 1):
                coefficient = coefficient if coefficient is not None else 1.0
                # Xác định trạng thái dựa trên hành động
                if not has_custom_coeff:
                    status = "Chưa thiết lập"  # Ban đầu hoặc sau khi xóa
                else:
                    # Kiểm tra xem hệ số có khớp với mặc định từ degrees không
                    cursor.execute("SELECT coefficient FROM degrees WHERE degree_id = %s", (degree_id,))
                    default_coeff = cursor.fetchone()[0]
                    if coefficient == default_coeff:
                        status = "Mặc định"  # Sau khi đặt lại thành mặc định
                    else:
                        status = "Đã thiết lập"  # Sau khi sửa và khác mặc định

                row_frame = CTkFrame(self.coefficient_list_frame, fg_color="#F5F5F5" if idx % 2 else "#FFFFFF")
                row_frame.pack(fill="x", pady=2)
                CTkLabel(row_frame, text=str(idx), font=("Helvetica", 12), width=50, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=degree_name, font=("Helvetica", 12), width=500, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=f"{coefficient:.1f}", font=("Helvetica", 12), width=100, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=status, font=("Helvetica", 12), width=200, anchor="center").pack(side="left", padx=5)
                action_frame = CTkFrame(row_frame, fg_color="transparent")
                action_frame.pack(side="left", padx=5)
                CTkButton(action_frame, text="Sửa", fg_color="#FFC107", width=80, command=lambda id=degree_id, name=degree_name, coeff=coefficient, y=year: self.edit_teacher_coefficient(id, name, coeff, y)).pack(side="left", padx=2)
                CTkButton(action_frame, text="Xóa", fg_color="#F44336", width=80, command=lambda id=degree_id, name=degree_name, y=year: self.delete_teacher_coefficient(id, name, y)).pack(side="left", padx=2)

                print(f"Debug [02:32 PM, 14/06/2025] - Loaded coefficients for year: {year}, degree: {degree_name}, coefficient: {coefficient}, status: {status}")

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu hệ số: {e}")
        finally:
            cursor.close()
            conn.close()

    def reset_to_default_coefficient_table(self):
        year = self.coefficient_year_filter.get().strip()
        if not year:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn năm học")
            return

        # Hiển thị hộp thoại xác nhận
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn đặt lại thành mặc định cho năm {year}?"):
            return  # Thoát nếu người dùng chọn "Không"

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Lấy tất cả bằng cấp từ degrees
            cursor.execute("SELECT degree_id, degree_name, coefficient FROM degrees ORDER BY degree_name")
            degrees = cursor.fetchall()

            # Chỉ đặt lại cho year được chọn
            affected_rows = 0
            for degree_id, degree_name, default_coeff in degrees:
                cursor.execute("""
                    INSERT INTO teacher_coefficients (year, degree_id, coefficient)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE coefficient = VALUES(coefficient)
                """, (year, degree_id, default_coeff))
                affected_rows += 1
            conn.commit()

            # Kiểm tra lại dữ liệu sau khi đặt lại
            cursor.execute("SELECT degree_id, year, coefficient FROM teacher_coefficients WHERE year = %s", (year,))
            updated_rows = cursor.fetchall()
            print(f"Debug [10:46 AM, 14/06/2025] - Reset to default for year: {year}, affected rows: {affected_rows}, updated rows: {updated_rows}")

            # Cập nhật giao diện
            self.load_teacher_coefficients()

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể đặt lại thành mặc định: {e}")
        finally:
            cursor.close()
            conn.close()

    def load_teaching_rates(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            # Lấy danh sách năm học từ 2020-2021 đến 2029-2030
            years = [f"{y}-{y+1}" for y in range(2020, 2030)]
            existing_rates = {}  # Lưu trữ các năm đã được thiết lập
            cursor.execute("SELECT year, amount_per_period, setup_date FROM teaching_rate")
            for year, amount, setup_date in cursor.fetchall():
                existing_rates[year] = (amount, setup_date)

            # Clear previous data
            for widget in self.rate_list_frame.winfo_children():
                widget.destroy()

            # Populate table for all years
            for idx, year in enumerate(years, 1):
                row_frame = CTkFrame(self.rate_list_frame, fg_color="#F5F5F5" if idx % 2 else "#FFFFFF")
                row_frame.pack(fill="x", pady=2)
                CTkLabel(row_frame, text=str(idx), font=("Helvetica", 12), width=100, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=year, font=("Helvetica", 12), width=150, anchor="center").pack(side="left", padx=5)

                if year in existing_rates:
                    amount, setup_date = existing_rates[year]
                    CTkLabel(row_frame, text=f"{amount:,.0f} ₫", font=("Helvetica", 12), width=200, anchor="center").pack(side="left", padx=5)
                    CTkLabel(row_frame, text=setup_date.strftime("%d/%m/%Y") if setup_date else "Chưa thiết lập", font=("Helvetica", 12), width=300, anchor="center").pack(side="left", padx=5)
                    action_frame = CTkFrame(row_frame, fg_color="transparent")
                    action_frame.pack(side="left", padx=5)
                    CTkButton(action_frame, text="Sửa", fg_color="#FFC107", width=70, command=lambda y=year: self.edit_teaching_rate(y)).pack(side="left", padx=2)
                    CTkButton(action_frame, text="Xóa", fg_color="#F44336", width=70, command=lambda y=year: self.delete_teaching_rate(y)).pack(side="left", padx=2)
                else:
                    CTkLabel(row_frame, text="Chưa thiết lập", font=("Helvetica", 12), width=200, anchor="center").pack(side="left", padx=5)
                    CTkLabel(row_frame, text="Chưa thiết lập", font=("Helvetica", 12), width=300, anchor="center").pack(side="left", padx=5)
                    action_frame = CTkFrame(row_frame, fg_color="transparent")
                    action_frame.pack(side="left", padx=5)
                    CTkButton(action_frame, text="Thêm", fg_color="#0085FF", width=70, command=lambda y=year: self.add_teaching_rate(y)).pack(side="left", padx=40)

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách định mức: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def add_teaching_rate(self, year):
        add_window = CTkToplevel(self.window)
        add_window.title("Thêm định mức tiền theo tiết")
        add_window.geometry("400x250")
        # Đặt cửa sổ ra giữa window app
        app_x = self.window.winfo_rootx()
        app_y = self.window.winfo_rooty()
        app_width = self.window.winfo_width()
        app_height = self.window.winfo_height()
        x = app_x + (app_width // 2) - (400 // 2)
        y = app_y + (app_height // 2) - (250 // 2)
        add_window.geometry(f"+{x}+{y}")
        add_window.resizable(False, False)
        add_window.transient(self.window)
        add_window.grab_set()

        form_frame = CTkFrame(add_window, fg_color="#F0F0F0", corner_radius=10)
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        CTkLabel(form_frame, text="Thêm định mức tiền theo tiết", font=("Helvetica", 16, "bold"), text_color="black").pack(pady=10)

        # Year field (disabled)
        year_row = CTkFrame(form_frame, fg_color="transparent")
        year_row.pack(fill="x", pady=2)
        CTkLabel(year_row, text="Năm học:", font=("Helvetica", 12), width=100, anchor="e").pack(side="left", padx=(0, 5))
        year_var = CTkEntry(year_row, width=250)
        year_var.pack(side="left", pady=5)
        year_var.insert(0, year)
        year_var.configure(state="disabled")

        # Amount field
        amount_row = CTkFrame(form_frame, fg_color="transparent")
        amount_row.pack(fill="x", pady=2)
        CTkLabel(amount_row, text="Số tiền (VNĐ):", font=("Helvetica", 12), width=100, anchor="e").pack(side="left", padx=(0, 5))
        amount_var = CTkEntry(amount_row, width=250, placeholder_text="Nhập số tiền > 0")
        amount_var.pack(side="left", pady=5)

        def save_rate():
            amount = amount_var.get().strip()
            try:
                amount = float(amount)
                if amount <= 0:
                    messagebox.showerror("Lỗi", "Số tiền phải lớn hơn 0!", parent=add_window)
                    return
            except ValueError:
                messagebox.showerror("Lỗi", "Số tiền phải là số hợp lệ!", parent=add_window)
                return

            if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn thêm định mức này?"):
                try:
                    conn = mysql.connector.connect(**DB_CONFIG)
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO teaching_rate (year, amount_per_period, setup_date) VALUES (%s, %s, CURDATE()) ON DUPLICATE KEY UPDATE amount_per_period = %s, setup_date = CURDATE()", (year, amount, amount))
                    conn.commit()
                    messagebox.showinfo("Thành công", "Thêm định mức thành công!")
                    self.load_teaching_rates()
                    add_window.destroy()
                except mysql.connector.Error as e:
                    messagebox.showerror("Lỗi", f"Không thể lưu định mức: {e}", parent=add_window)
                finally:
                    cursor.close()
                    conn.close()

        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        CTkButton(button_frame, text="Lưu", fg_color="#0085FF", command=save_rate, width=100).pack(side="left", padx=5)
        CTkButton(button_frame, text="Hủy", fg_color="#6C757D", command=add_window.destroy, width=100).pack(side="left", padx=5)

    def edit_teaching_rate(self, year):
        edit_window = CTkToplevel(self.window)
        edit_window.title("Sửa định mức tiền theo tiết")
        edit_window.geometry("400x250")
        # Đặt cửa sổ ra giữa window app
        app_x = self.window.winfo_rootx()
        app_y = self.window.winfo_rooty()
        app_width = self.window.winfo_width()
        app_height = self.window.winfo_height()
        x = app_x + (app_width // 2) - (400 // 2)
        y = app_y + (app_height // 2) - (250 // 2)
        edit_window.geometry(f"+{x}+{y}")
        edit_window.resizable(False, False)
        edit_window.transient(self.window)
        edit_window.grab_set()

        form_frame = CTkFrame(edit_window, fg_color="#F0F0F0", corner_radius=10)
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        CTkLabel(form_frame, text="Sửa định mức tiền theo tiết", font=("Helvetica", 16, "bold"), text_color="black").pack(pady=10)

        # Get current data
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT amount_per_period, setup_date FROM teaching_rate WHERE year = %s", (year,))
            rate = cursor.fetchone()
            amount = rate[0] if rate and rate[0] > 0 else 0
            setup_date = rate[1] if rate and rate[1] else None
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {e}", parent=edit_window)
            return
        finally:
            cursor.close()
            conn.close()

        # Year field (disabled)
        year_row = CTkFrame(form_frame, fg_color="transparent")
        year_row.pack(fill="x", pady=2)
        CTkLabel(year_row, text="Năm học:", font=("Helvetica", 12), width=100, anchor="e").pack(side="left", padx=(0, 5))
        year_var = CTkEntry(year_row, width=250)
        year_var.pack(side="left", pady=5)
        year_var.insert(0, year)
        year_var.configure(state="disabled")

        # Amount field
        amount_row = CTkFrame(form_frame, fg_color="transparent")
        amount_row.pack(fill="x", pady=2)
        CTkLabel(amount_row, text="Số tiền (VNĐ):", font=("Helvetica", 12), width=100, anchor="e").pack(side="left", padx=(0, 5))
        amount_var = CTkEntry(amount_row, width=250)
        amount_var.pack(side="left", pady=5)
        amount_var.insert(0, str(amount))

        def save_rate():
            amount = amount_var.get().strip()
            try:
                amount = float(amount)
                if amount < 0:
                    messagebox.showerror("Lỗi", "Số tiền phải lớn hơn hoặc bằng 0!", parent=edit_window)
                    return
            except ValueError:
                messagebox.showerror("Lỗi", "Số tiền phải là số hợp lệ!", parent=edit_window)
                return

            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO teaching_rate (year, amount_per_period, setup_date) VALUES (%s, %s, CURDATE()) ON DUPLICATE KEY UPDATE amount_per_period = %s, setup_date = CURDATE()", (year, amount, amount))
                conn.commit()
                messagebox.showinfo("Thành công", "Cập nhật định mức thành công!")
                self.load_teaching_rates()
                edit_window.destroy()
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể lưu định mức: {e}", parent=edit_window)
            finally:
                cursor.close()
                conn.close()

        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        CTkButton(button_frame, text="Lưu", fg_color="#0085FF", command=save_rate, width=100).pack(side="left", padx=5)
        CTkButton(button_frame, text="Hủy", fg_color="#6C757D", command=edit_window.destroy, width=100).pack(side="left", padx=5)

    def delete_teaching_rate(self, year):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa định mức này?"):
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM teaching_rate WHERE year = %s", (year,))
                conn.commit()
                messagebox.showinfo("Thành công", "Xóa định mức thành công!")
                self.load_teaching_rates()
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể xóa định mức: {e}")
            finally:
                cursor.close()
                conn.close()

    def load_class_coefficients(self, event=None):
        year = self.coeff_year_filter.get().strip()
        if not year:
            return

        ranges = [
            "<20 sinh viên", "20-29 sinh viên", "30-39 sinh viên", "40-49 sinh viên",
            "50-59 sinh viên", "60-69 sinh viên", "70-79 sinh viên", "80-89 sinh viên",
            "90-99 sinh viên", ">=100 sinh viên"
        ]
        coeff_data = {}

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT student_range, coefficient, is_standard FROM class_coefficients WHERE year = %s ORDER BY FIELD(student_range, %s)", (year, ", ".join(f"'{r}'" for r in ranges)))
            rows = cursor.fetchall()
            print(f"Debug: Dữ liệu từ class_coefficients cho year {year}: {rows}")  # Debug để kiểm tra dữ liệu

            for row in rows:
                coeff_data[row[0]] = {'coefficient': float(row[1]), 'is_standard': row[2]}  # Chuyển Decimal thành float

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu hệ số: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

        # Clear previous data
        for widget in self.coeff_list_frame.winfo_children():
            widget.destroy()

        # Populate table
        for idx, range_str in enumerate(ranges, 1):
            row_frame = CTkFrame(self.coeff_list_frame, fg_color="#F5F5F5" if idx % 2 else "#FFFFFF", height=20)
            row_frame.pack(fill="x", pady=2)
            CTkLabel(row_frame, text=str(idx), font=("Helvetica", 12), text_color="black", width=160, anchor="center").pack(side="left", padx=5)
            CTkLabel(row_frame, text=range_str, font=("Helvetica", 12), text_color="black", width=400, anchor="center").pack(side="left", padx=5)
            if range_str in coeff_data:
                coeff = coeff_data[range_str]['coefficient']
                is_standard = coeff_data[range_str]['is_standard']
                CTkLabel(row_frame, text=f"{coeff:.1f}", font=("Helvetica", 12), text_color="black", width=250, anchor="center").pack(side="left", padx=1)
                note = "Khoảng chuẩn ✓" if is_standard else ""
                CTkLabel(row_frame, text=note, font=("Helvetica", 12), text_color="green" if is_standard else "black", width=200, anchor="center").pack(side="left", padx=5)
            else:
                CTkLabel(row_frame, text="Chưa thiết lập", font=("Helvetica", 12), text_color="gray", width=250, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text="", font=("Helvetica", 12), text_color="black", width=200, anchor="center").pack(side="left", padx=5)

    def setup_standard_range(self):
        year = self.coeff_year_filter.get().strip()
        if not year:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn năm học")
            return

        setup_window = CTkToplevel(self.window)
        setup_window.title("Thiết lập khoảng chuẩn")
        setup_window.geometry("400x250")
        # Đặt cửa sổ ra giữa window app
        app_x = self.window.winfo_rootx()
        app_y = self.window.winfo_rooty()
        app_width = self.window.winfo_width()
        app_height = self.window.winfo_height()
        x = app_x + (app_width // 2) - (400 // 2)
        y = app_y + (app_height // 2) - (250 // 2)
        setup_window.geometry(f"+{x}+{y}")
        setup_window.resizable(False, False)
        setup_window.transient(self.window)
        setup_window.grab_set()

        form_frame = CTkFrame(setup_window, fg_color="#F0F0F0", corner_radius=10)
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        CTkLabel(form_frame, text="Chọn khoảng chuẩn", font=("Helvetica", 16, "bold"), text_color="black").pack(pady=10)

        ranges = [
            "<20 sinh viên", "20-29 sinh viên", "30-39 sinh viên", "40-49 sinh viên",
            "50-59 sinh viên", "60-69 sinh viên", "70-79 sinh viên", "80-89 sinh viên",
            "90-99 sinh viên", ">=100 sinh viên"
        ]
        selected_range = CTkComboBox(form_frame, values=ranges, width=350)
        selected_range.pack(pady=5)

        def save_standard():
            range_str = selected_range.get().strip()
            if not range_str:
                messagebox.showerror("Lỗi", "Vui lòng chọn khoảng chuẩn!")
                return

            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                # Xóa dữ liệu cũ của năm học này
                cursor.execute("DELETE FROM class_coefficients WHERE year = %s", (year,))
                conn.commit()

                # Tính toán và chèn dữ liệu mới
                standard_idx = ranges.index(range_str)
                for idx, r in enumerate(ranges):
                    coeff = 0.0
                    if idx < standard_idx:
                        coeff = -0.1 * (standard_idx - idx)
                    elif idx > standard_idx:
                        coeff = 0.1 * (idx - standard_idx)
                    is_std = (idx == standard_idx)
                    cursor.execute("INSERT INTO class_coefficients (year, student_range, coefficient, is_standard) VALUES (%s, %s, %s, %s)",
                                (year, r, coeff, is_std))
                conn.commit()
                messagebox.showinfo("Thành công", f"Đã thiết lập khoảng chuẩn {range_str} cho năm {year}!")
                self.load_class_coefficients()
                setup_window.destroy()
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể lưu thiết lập: {e}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()

        button_frame = CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        CTkButton(button_frame, text="Lưu", fg_color="#0085FF", command=save_standard, width=100).pack(side="left", padx=5)
        CTkButton(button_frame, text="Hủy", fg_color="#6C757D", command=setup_window.destroy, width=100).pack(side="left", padx=5)

    def get_academic_years_with_semesters(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT year FROM semesters ORDER BY year")
            years = [row[0] for row in cursor.fetchall()]
            return years if years else ["2025-2026"]
        except mysql.connector.Error:
            return ["2025-2026"]
        finally:
            cursor.close()
            conn.close()

    def update_semester_options(self, event=None):
        year = self.year_filter.get().strip()
        if year:
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("SELECT semester_name FROM semesters WHERE year = %s ORDER BY semester_name", (year,))
                semesters = [row[0] for row in cursor.fetchall()]
                self.semester_filter.configure(values=semesters if semesters else ["Kỳ 1", "Kỳ 2", "Kỳ 3"])
                self.semester_filter.set(semesters[0] if semesters else "Kỳ 1")
            except mysql.connector.Error:
                self.semester_filter.configure(values=["Kỳ 1", "Kỳ 2", "Kỳ 3"])
                self.semester_filter.set("Kỳ 1")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()
        else:
            self.semester_filter.configure(values=["Kỳ 1", "Kỳ 2", "Kỳ 3"])
            self.semester_filter.set("Kỳ 1")

    def update_teacher_options(self, event=None):
        dept = self.dept_filter.get().strip()
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            if dept == "Chọn khoa" or dept == "Tất cả khoa":
                cursor.execute("SELECT teacher_id, full_name FROM teachers ORDER BY full_name")
            else:
                cursor.execute("SELECT teacher_id, full_name FROM teachers WHERE dept_id = (SELECT dept_id FROM departments WHERE dept_name = %s) ORDER BY full_name", (dept,))
            teachers = cursor.fetchall()
            teacher_list = [f"{row[1]} - {row[0]}" if row[1] and row[0] else "Chọn giảng viên" for row in teachers]
            self.teacher_filter.configure(values=["Chọn giảng viên"] + teacher_list)
            self.teacher_filter.set("Chọn giảng viên" if not teacher_list else teacher_list[0])
        except mysql.connector.Error as e:
            self.teacher_filter.configure(values=["Chọn giảng viên"])
            self.teacher_filter.set("Chọn giảng viên")
        finally:
            cursor.close()
            conn.close()

    def calculate_salary_display(self):
        year = self.year_filter.get().strip()
        semester = self.semester_filter.get().strip()
        teacher_str = self.teacher_filter.get().strip()

        if not teacher_str or teacher_str == "Chọn giảng viên":
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn giảng viên!")
            return

        if year == "Chọn năm học" or semester == "Chọn kỳ học":
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn năm học và kỳ học!")
            return

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Trích xuất teacher_id từ teacher_str
            teacher_parts = teacher_str.split(" - ")
            if len(teacher_parts) < 2:
                messagebox.showerror("Lỗi", "Định dạng giảng viên không hợp lệ!")
                return
            teacher_id = teacher_parts[1].strip()

            # Lấy thông tin giảng viên
            cursor.execute("""
                SELECT t.full_name, t.teacher_id, d.degree_name, dept.dept_name 
                FROM teachers t 
                JOIN degrees d ON t.degree_id = d.degree_id 
                JOIN departments dept ON t.dept_id = dept.dept_id 
                WHERE t.teacher_id = %s
            """, (teacher_id,))
            teacher = cursor.fetchone()
            if not teacher:
                messagebox.showerror("Lỗi", f"Không tìm thấy giảng viên với mã {teacher_id}")
                return
            full_name, teacher_id_db, degree_name, dept_name = teacher

            # Lấy hệ số giáo viên
            cursor.execute("""
                SELECT coefficient 
                FROM teacher_coefficients tc 
                JOIN teachers t ON tc.degree_id = t.degree_id 
                WHERE t.teacher_id = %s AND tc.year = %s
            """, (teacher_id, year))
            teacher_coeff = cursor.fetchone()
            teacher_coefficient = float(teacher_coeff[0]) if teacher_coeff else 1.0

            # Lấy đơn giá
            cursor.execute("SELECT amount_per_period FROM teaching_rate WHERE year = %s", (year,))
            rate = cursor.fetchone()
            amount_per_period = float(rate[0]) if rate else 0.0

            # Lấy semester_id
            cursor.execute("SELECT semester_id FROM semesters WHERE year = %s AND semester_name = %s", (year, semester))
            semester_id = cursor.fetchone()
            if not semester_id:
                messagebox.showerror("Lỗi", "Không tìm thấy kỳ học!")
                return
            semester_id = semester_id[0]

            # Cập nhật giao diện, kiểm tra None và widget tồn tại
            if hasattr(self, 'salary_calc_teacher_name_value') and self.salary_calc_teacher_name_value is not None and self.salary_calc_teacher_name_value.winfo_exists():
                self.salary_calc_teacher_name_value.configure(text=full_name or "Không xác định")
            if hasattr(self, 'salary_calc_teacher_id_value') and self.salary_calc_teacher_id_value is not None and self.salary_calc_teacher_id_value.winfo_exists():
                self.salary_calc_teacher_id_value.configure(text=teacher_id_db or "Không xác định")
            if hasattr(self, 'salary_calc_degree_value') and self.salary_calc_degree_value is not None and self.salary_calc_degree_value.winfo_exists():
                self.salary_calc_degree_value.configure(text=degree_name or "Không xác định")
            if hasattr(self, 'salary_calc_dept_value') and self.salary_calc_dept_value is not None and self.salary_calc_dept_value.winfo_exists():
                self.salary_calc_dept_value.configure(text=dept_name or "Không xác định")
            if hasattr(self, 'salary_calc_teacher_coeff_value') and self.salary_calc_teacher_coeff_value is not None and self.salary_calc_teacher_coeff_value.winfo_exists():
                self.salary_calc_teacher_coeff_value.configure(text=f"{teacher_coefficient:.1f}")
            if hasattr(self, 'salary_calc_rate_value') and self.salary_calc_rate_value is not None and self.salary_calc_rate_value.winfo_exists():
                self.salary_calc_rate_value.configure(text=f"{amount_per_period:,.0f} ₫")
            if hasattr(self, 'salary_calc_period_value') and self.salary_calc_period_value is not None and self.salary_calc_period_value.winfo_exists():
                self.salary_calc_period_value.configure(text=f"{semester} - {year}")

            # Kiểm tra và tải bảng lương
            cursor.execute("""
                SELECT c.class_id, cm.periods, c.num_students, cm.coefficient AS hp_coeff
                FROM assignments a
                JOIN classes c ON a.class_id = c.class_id
                JOIN course_modules cm ON c.module_id = cm.module_id
                WHERE a.teacher_id = %s AND c.semester_id = %s
            """, (teacher_id, semester_id))
            classes = cursor.fetchall()

            if not classes:
                # Xóa dữ liệu cũ và hiển thị thông báo "Không có dữ liệu"
                for widget in self.salary_table_frame.winfo_children():
                    widget.destroy()
                CTkLabel(self.salary_table_frame, text="Không có dữ liệu", font=("Helvetica", 12), text_color="gray").pack(pady=20)
            else:
                self.load_salary_table(teacher_id, semester_id)

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải thông tin: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def load_salary_table(self, teacher_id, semester_id):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            # Thay đổi truy vấn để lấy enrolled_students từ bảng class_enrollments
            cursor.execute("""
                SELECT c.class_id, cm.periods, COALESCE(ce.enrolled_students, 0) as enrolled_students, 
                    cm.coefficient AS hp_coeff
                FROM assignments a
                JOIN classes c ON a.class_id = c.class_id
                JOIN course_modules cm ON c.module_id = cm.module_id
                LEFT JOIN class_enrollments ce ON c.class_id = ce.class_id
                WHERE a.teacher_id = %s AND c.semester_id = %s
            """, (teacher_id, semester_id))
            classes = cursor.fetchall()

            # Clear previous data
            for widget in self.salary_table_frame.winfo_children():
                widget.destroy()

            total_periods = 0
            total_salary = 0.0

            # Heading
            heading_frame = CTkFrame(self.salary_table_frame, fg_color="#D3D3D3", corner_radius=0)
            heading_frame.pack(fill="x", padx=5, pady=(5, 0))
            CTkLabel(heading_frame, text="Mã lớp", font=("Helvetica", 12, "bold"), width=200, anchor="center").pack(side="left", padx=5)
            CTkLabel(heading_frame, text="Số tiết", font=("Helvetica", 12, "bold"), width=80, anchor="center").pack(side="left", padx=5)
            CTkLabel(heading_frame, text="Số SV thực tế", font=("Helvetica", 12, "bold"), width=80, anchor="center").pack(side="left", padx=5)
            CTkLabel(heading_frame, text="Hệ số HP", font=("Helvetica", 12, "bold"), width=130, anchor="center").pack(side="left", padx=5)
            CTkLabel(heading_frame, text="Hệ số lớp", font=("Helvetica", 12, "bold"), width=130, anchor="center").pack(side="left", padx=5)
            CTkLabel(heading_frame, text="Số tiết quy đổi", font=("Helvetica", 12, "bold"), width=150, anchor="center").pack(side="left", padx=5)
            CTkLabel(heading_frame, text="Thành tiền", font=("Helvetica", 12, "bold"), width=240, anchor="center").pack(side="left", padx=5)

            year = self.year_filter.get().strip()
            cursor.execute("SELECT amount_per_period FROM teaching_rate WHERE year = %s", (year,))
            rate = cursor.fetchone()
            amount_per_period = float(rate[0]) if rate else 0.0

            # Lấy hệ số giáo viên
            teacher_coefficient = float(self.salary_calc_teacher_coeff_value.cget("text")) if hasattr(self, 'salary_calc_teacher_coeff_value') else 1.0

            for idx, (class_id, periods, enrolled_students, hp_coeff) in enumerate(classes, 1):
                # Lấy hệ số lớp dựa trên số sinh viên thực tế (enrolled_students)
                student_range = self.get_student_range(enrolled_students)
                cursor.execute("""
                    SELECT coefficient 
                    FROM class_coefficients 
                    WHERE year = %s AND student_range = %s
                """, (year, student_range))
                class_coeff = cursor.fetchone()
                class_coefficient = float(class_coeff[0]) if class_coeff else 0.0

                # Tính toán với enrolled_students
                converted_periods = periods * (hp_coeff + class_coefficient)
                salary = converted_periods * teacher_coefficient * amount_per_period
                total_periods += converted_periods
                total_salary += salary

                row_frame = CTkFrame(self.salary_table_frame, fg_color="#F5F5F5" if idx % 2 else "#FFFFFF")
                row_frame.pack(fill="x", pady=2)
                CTkLabel(row_frame, text=class_id, font=("Helvetica", 12), width=200, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=str(periods), font=("Helvetica", 12), width=80, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=str(enrolled_students), font=("Helvetica", 12), width=80, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=f"{hp_coeff:.1f}", font=("Helvetica", 12), width=130, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=f"{class_coefficient:.1f}", font=("Helvetica", 12), width=130, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=f"{converted_periods:.1f}", font=("Helvetica", 12), width=150, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=f"{salary:,.0f} ₫", font=("Helvetica", 12), width=240, anchor="center").pack(side="left", padx=5)

            # Total row
            total_frame = CTkFrame(self.salary_table_frame, fg_color="#E0E0E0")
            total_frame.pack(fill="x", pady=2)
            CTkLabel(total_frame, text="Tổng cộng:", font=("Helvetica", 12, "bold"), width=270, anchor="center").pack(side="left", padx=200)
            CTkLabel(total_frame, text=f"{total_periods:.1f}", font=("Helvetica", 12, "bold"), width=150, anchor="center").pack(side="left", padx=5)
            CTkLabel(total_frame, text=f"{total_salary:,.0f} ₫", font=("Helvetica", 12, "bold"), width=240, anchor="center").pack(side="left", padx=5)

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải bảng lương: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_student_range(self, num_students):
        ranges = [
            "<20 sinh viên", "20-29 sinh viên", "30-39 sinh viên", "40-49 sinh viên",
            "50-59 sinh viên", "60-69 sinh viên", "70-79 sinh viên", "80-89 sinh viên",
            "90-99 sinh viên", ">=100 sinh viên"
        ]
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
        def load_salary_table(self, teacher_id, semester_id):
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                
                # Thay đổi truy vấn để lấy enrolled_students từ bảng class_enrollments
                cursor.execute("""
                    SELECT c.class_id, cm.periods, COALESCE(ce.enrolled_students, 0) as enrolled_students, 
                        cm.coefficient AS hp_coeff
                    FROM assignments a
                    JOIN classes c ON a.class_id = c.class_id
                    JOIN course_modules cm ON c.module_id = cm.module_id
                    LEFT JOIN class_enrollments ce ON c.class_id = ce.class_id
                    WHERE a.teacher_id = %s AND c.semester_id = %s
                """, (teacher_id, semester_id))
                classes = cursor.fetchall()

                # Clear previous data
                for widget in self.salary_table_frame.winfo_children():
                    widget.destroy()

                total_periods = 0
                total_salary = 0.0

                # Tăng kích thước font và chiều cao cho heading
                heading_frame = CTkFrame(self.salary_table_frame, fg_color="#D3D3D3", corner_radius=0, height=50)
                heading_frame.pack(fill="x", padx=5, pady=(5, 0))
                heading_frame.pack_propagate(False)  # Prevent frame from shrinking

                # Tăng font size và width cho các cột heading
                CTkLabel(heading_frame, text="Mã lớp", font=("Helvetica", 14, "bold"), width=250, anchor="center").pack(side="left", padx=5, pady=10)
                CTkLabel(heading_frame, text="Số tiết", font=("Helvetica", 14, "bold"), width=100, anchor="center").pack(side="left", padx=5, pady=10)
                CTkLabel(heading_frame, text="Số SV thực tế", font=("Helvetica", 14, "bold"), width=100, anchor="center").pack(side="left", padx=5, pady=10)
                CTkLabel(heading_frame, text="Hệ số HP", font=("Helvetica", 14, "bold"), width=150, anchor="center").pack(side="left", padx=5, pady=10)
                CTkLabel(heading_frame, text="Hệ số lớp", font=("Helvetica", 14, "bold"), width=150, anchor="center").pack(side="left", padx=5, pady=10)
                CTkLabel(heading_frame, text="Số tiết quy đổi", font=("Helvetica", 14, "bold"), width=170, anchor="center").pack(side="left", padx=5, pady=10)
                CTkLabel(heading_frame, text="Thành tiền", font=("Helvetica", 14, "bold"), width=280, anchor="center").pack(side="left", padx=5, pady=10)

                year = self.year_filter.get().strip()
                cursor.execute("SELECT amount_per_period FROM teaching_rate WHERE year = %s", (year,))
                rate = cursor.fetchone()
                amount_per_period = float(rate[0]) if rate else 0.0

                teacher_coefficient = float(self.salary_calc_teacher_coeff_value.cget("text")) if hasattr(self, 'salary_calc_teacher_coeff_value') else 1.0

                for idx, (class_id, periods, enrolled_students, hp_coeff) in enumerate(classes, 1):
                    student_range = self.get_student_range(enrolled_students)
                    cursor.execute("""
                        SELECT coefficient 
                        FROM class_coefficients 
                        WHERE year = %s AND student_range = %s
                    """, (year, student_range))
                    class_coeff = cursor.fetchone()
                    class_coefficient = float(class_coeff[0]) if class_coeff else 0.0

                    converted_periods = periods * (hp_coeff + class_coefficient)
                    salary = converted_periods * teacher_coefficient * amount_per_period
                    total_periods += converted_periods
                    total_salary += salary

                    # Tăng chiều cao cho mỗi dòng dữ liệu
                    row_frame = CTkFrame(self.salary_table_frame, fg_color="#F5F5F5" if idx % 2 else "#FFFFFF", height=45)
                    row_frame.pack(fill="x", pady=2)
                    row_frame.pack_propagate(False)  # Prevent frame from shrinking

                    # Tăng font size và width cho các cột dữ liệu
                    CTkLabel(row_frame, text=class_id, font=("Helvetica", 13), width=250, anchor="center").pack(side="left", padx=5, pady=5)
                    CTkLabel(row_frame, text=str(periods), font=("Helvetica", 13), width=100, anchor="center").pack(side="left", padx=5, pady=5)
                    CTkLabel(row_frame, text=str(enrolled_students), font=("Helvetica", 13), width=100, anchor="center").pack(side="left", padx=5, pady=5)
                    CTkLabel(row_frame, text=f"{hp_coeff:.1f}", font=("Helvetica", 13), width=150, anchor="center").pack(side="left", padx=5, pady=5)
                    CTkLabel(row_frame, text=f"{class_coefficient:.1f}", font=("Helvetica", 13), width=150, anchor="center").pack(side="left", padx=5, pady=5)
                    CTkLabel(row_frame, text=f"{converted_periods:.1f}", font=("Helvetica", 13), width=170, anchor="center").pack(side="left", padx=5, pady=5)
                    CTkLabel(row_frame, text=f"{salary:,.0f} ₫", font=("Helvetica", 13), width=280, anchor="center").pack(side="left", padx=5, pady=5)

                # Tăng kích thước cho dòng tổng cộng
                total_frame = CTkFrame(self.salary_table_frame, fg_color="#E0E0E0", height=50)
                total_frame.pack(fill="x", pady=2)
                total_frame.pack_propagate(False)

                CTkLabel(total_frame, text="Tổng cộng:", font=("Helvetica", 14, "bold"), width=600, anchor="center").pack(side="left", padx=200, pady=10)
                CTkLabel(total_frame, text=f"{total_periods:.1f}", font=("Helvetica", 14, "bold"), width=170, anchor="center").pack(side="left", padx=5, pady=10)
                CTkLabel(total_frame, text=f"{total_salary:,.0f} ₫", font=("Helvetica", 14, "bold"), width=280, anchor="center").pack(side="left", padx=5, pady=10)

            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể tải bảng lương: {e}")
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
            

        def get_student_range(self, num_students):
            ranges = [
                "<20 sinh viên", "20-29 sinh viên", "30-39 sinh viên", "40-49 sinh viên",
                "50-59 sinh viên", "60-69 sinh viên", "70-79 sinh viên", "80-89 sinh viên",
                "90-99 sinh viên", ">=100 sinh viên"
            ]
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
        
    def get_dept_names(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT dept_name FROM departments ORDER BY dept_name")
            depts = [row[0] for row in cursor.fetchall()]
            return depts
        except mysql.connector.Error:
            return ["Khoa Công nghệ thông tin"]
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def reset_salary_calc(self):
        # Reset các combobox
        self.year_filter.set("Chọn năm học")
        self.semester_filter.set("Chọn kỳ học")
        self.dept_filter.set("Chọn khoa")
        self.teacher_filter.set("Chọn giảng viên")
        
        # Reset thông tin giảng viên
        if hasattr(self, 'salary_calc_teacher_name_value') and self.salary_calc_teacher_name_value is not None and self.salary_calc_teacher_name_value.winfo_exists():
            self.salary_calc_teacher_name_value.configure(text="")
        if hasattr(self, 'salary_calc_teacher_id_value') and self.salary_calc_teacher_id_value is not None and self.salary_calc_teacher_id_value.winfo_exists():
            self.salary_calc_teacher_id_value.configure(text="")
        if hasattr(self, 'salary_calc_degree_value') and self.salary_calc_degree_value is not None and self.salary_calc_degree_value.winfo_exists():
            self.salary_calc_degree_value.configure(text="")
        if hasattr(self, 'salary_calc_dept_value') and self.salary_calc_dept_value is not None and self.salary_calc_dept_value.winfo_exists():
            self.salary_calc_dept_value.configure(text="")
        if hasattr(self, 'salary_calc_teacher_coeff_value') and self.salary_calc_teacher_coeff_value is not None and self.salary_calc_teacher_coeff_value.winfo_exists():
            self.salary_calc_teacher_coeff_value.configure(text="")
        if hasattr(self, 'salary_calc_rate_value') and self.salary_calc_rate_value is not None and self.salary_calc_rate_value.winfo_exists():
            self.salary_calc_rate_value.configure(text="")
        if hasattr(self, 'salary_calc_period_value') and self.salary_calc_period_value is not None and self.salary_calc_period_value.winfo_exists():
            self.salary_calc_period_value.configure(text="")

        # Xóa bảng lương
        for widget in self.salary_table_frame.winfo_children():
            widget.destroy()

        # Xóa nút Lưu nếu tồn tại
        if self.save_button and self.save_button.winfo_exists():
            self.save_button.destroy()
            self.save_button = None

    def save_salary_data(self):
        # TODO: Phát triển chức năng lưu bảng lương vào CSDL
        messagebox.showinfo("Thông báo", "Chức năng đang được phát triển")

    def update_report_teacher_options(self, event=None):
        dept = self.salary_report_dept_filter.get().strip()
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            if dept == "Chọn khoa":
                cursor.execute("""
                    SELECT t.teacher_id, t.full_name, d.degree_name 
                    FROM teachers t 
                    JOIN degrees d ON t.degree_id = d.degree_id 
                    ORDER BY t.full_name
                """)
            else:
                cursor.execute("""
                    SELECT t.teacher_id, t.full_name, d.degree_name 
                    FROM teachers t 
                    JOIN degrees d ON t.degree_id = d.degree_id 
                    WHERE t.dept_id = (SELECT dept_id FROM departments WHERE dept_name = %s) 
                    ORDER BY t.full_name
                """, (dept,))
            teachers = cursor.fetchall()
            teacher_list = [f"{row[1]} - {row[2]}" if row[1] and row[2] else "Chọn giảng viên" for row in teachers]
            self.salary_report_teacher_filter.configure(values=teacher_list if teacher_list else ["Chọn giảng viên"])
            self.salary_report_teacher_filter.set("Chọn giảng viên")
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách giảng viên: {e}")
        finally:
            cursor.close()
            conn.close()

    def display_salary_report(self):
        year = self.salary_report_year_filter.get().strip()
        teacher_str = self.salary_report_teacher_filter.get().strip()
        
        if year == "Chọn năm" or teacher_str == "Chọn giảng viên":
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn năm và giảng viên!")
            return

        # Tách teacher_str thành tên giảng viên và tên bằng cấp
        try:
            teacher_name, degree_name = teacher_str.split(" - ") if " - " in teacher_str else (None, None)
            if not teacher_name or not degree_name:
                messagebox.showerror("Lỗi", "Định dạng giảng viên không hợp lệ!")
                return

            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Lấy teacher_id dựa trên full_name và degree_name
            cursor.execute("""
                SELECT t.teacher_id
                FROM teachers t
                JOIN degrees d ON t.degree_id = d.degree_id
                WHERE t.full_name = %s AND d.degree_name = %s
            """, (teacher_name, degree_name))
            teacher_id_result = cursor.fetchone()
            if not teacher_id_result:
                messagebox.showerror("Lỗi", f"Không tìm thấy giảng viên với tên {teacher_name} và bằng cấp {degree_name}")
                return
            teacher_id = teacher_id_result[0]

            # Lấy thông tin giảng viên
            cursor.execute("""
                SELECT t.full_name, t.teacher_id, d.degree_name, dept.dept_name 
                FROM teachers t 
                JOIN degrees d ON t.degree_id = d.degree_id 
                JOIN departments dept ON t.dept_id = dept.dept_id 
                WHERE t.teacher_id = %s
            """, (teacher_id,))
            teacher = cursor.fetchone()
            if not teacher:
                messagebox.showerror("Lỗi", f"Không tìm thấy giảng viên với mã {teacher_id}")
                return
            full_name, teacher_id, degree_name, dept_name = teacher

            # Cập nhật thông tin giảng viên
            self.salary_report_teacher_name_value.configure(text=full_name or '-')
            self.salary_report_teacher_id_value.configure(text=teacher_id or '-')
            self.salary_report_teacher_degree_value.configure(text=degree_name or '-')
            self.salary_report_teacher_dept_value.configure(text=dept_name or '-')

            # Xóa bảng cũ
            for widget in self.salary_tables_frame.winfo_children():
                widget.destroy()

            # Lấy danh sách kỳ học trong năm
            cursor.execute("SELECT semester_id, semester_name FROM semesters WHERE year = %s ORDER BY semester_name", (year,))
            semesters = cursor.fetchall()
            if not semesters:
                CTkLabel(
                    self.salary_tables_frame,
                    text="Không có dữ liệu kỳ học trong năm này",
                    font=("Helvetica", 14),
                    text_color="gray"
                ).pack(pady=20)
                self.salary_report_total_salary_label.configure(text="Tổng tiền dạy trong năm: 0 ₫")
                self.salary_report_total_classes_label.configure(text="0")
                self.salary_report_total_periods_label.configure(text="0")
                self.salary_report_total_salary_temp_label.configure(text="0 đ")
                return

            total_year_salary = 0.0
            total_classes = 0
            total_periods = 0.0
            # Lấy teacher_coefficient
            cursor.execute("""
                SELECT tc.coefficient 
                FROM teacher_coefficients tc 
                JOIN teachers t ON tc.degree_id = t.degree_id 
                WHERE t.teacher_id = %s AND tc.year = %s
            """, (teacher_id, year))
            teacher_coeff = cursor.fetchone()
            teacher_coefficient = float(teacher_coeff[0]) if teacher_coeff else 1.0

            # Lấy teaching rate
            cursor.execute("SELECT amount_per_period FROM teaching_rate WHERE year = %s", (year,))
            rate = cursor.fetchone()
            amount_per_period = float(rate[0]) if rate else 0.0

            current_semester = None
            if self.current_semester_var.get():
                current_semester = semesters[0][0] if semesters else None  # Lấy kỳ đầu tiên nếu chọn "Chỉ kỳ hiện tại"

            for semester_id, semester_name in semesters:
                if self.current_semester_var.get() and semester_id != current_semester:
                    continue

                # Lấy dữ liệu lớp học
                cursor.execute("""
                    SELECT c.class_id, cm.periods, c.num_students, cm.coefficient AS hp_coeff
                    FROM assignments a
                    JOIN classes c ON a.class_id = c.class_id
                    JOIN course_modules cm ON c.module_id = cm.module_id
                    WHERE a.teacher_id = %s AND c.semester_id = %s
                """, (teacher_id, semester_id))
                classes = cursor.fetchall()

                if not classes:
                    continue

                # Tạo frame cho kỳ học
                semester_frame = CTkFrame(self.salary_tables_frame, fg_color="#FFFFFF")
                semester_frame.pack(fill="x", pady=10)

                # Tiêu đề kỳ học
                CTkLabel(
                    semester_frame,
                    text=f"Báo cáo kỳ {semester_name}",
                    font=("Helvetica", 14, "bold"),
                    text_color="#333"
                ).pack(anchor="w", pady=5)

                # Bảng lương
                table_frame = CTkFrame(semester_frame, fg_color="#FFFFFF")
                table_frame.pack(fill="x", padx=5)

                # Heading
                heading_frame = CTkFrame(table_frame, fg_color="#D3D3D3")
                heading_frame.pack(fill="x")
                CTkLabel(heading_frame, text="Mã lớp", font=("Helvetica", 12, "bold"), text_color="#333", width=100, anchor="center").pack(side="left", padx=5)
                CTkLabel(heading_frame, text="Số tiết", font=("Helvetica", 12, "bold"), text_color="#333", width=80, anchor="center").pack(side="left", padx=5)
                CTkLabel(heading_frame, text="Số tiết quy đổi", font=("Helvetica", 12, "bold"), text_color="#333", width=120, anchor="center").pack(side="left", padx=5)
                CTkLabel(heading_frame, text="Thành tiền", font=("Helvetica", 12, "bold"), text_color="#333", width=120, anchor="center").pack(side="left", padx=5)

                total_periods_sem = 0
                total_salary = 0.0

                for idx, (class_id, periods, num_students, hp_coeff) in enumerate(classes, 1):
                    total_classes += 1
                    total_periods_sem += periods
                    # Lấy hệ số lớp
                    student_range = self.get_student_range(num_students)
                    cursor.execute("SELECT coefficient FROM class_coefficients WHERE year = %s AND student_range = %s", (year, student_range))
                    class_coeff = cursor.fetchone()
                    class_coefficient = float(class_coeff[0]) if class_coeff else 0.0

                    # Tính toán
                    converted_periods = periods * (hp_coeff + class_coefficient)
                    salary = converted_periods * teacher_coefficient * amount_per_period
                    total_periods += converted_periods
                    total_salary += salary

                    # Hiển thị hàng
                    row_frame = CTkFrame(table_frame, fg_color="#F5F5F5" if idx % 2 else "#FFFFFF")
                    row_frame.pack(fill="x", pady=2)
                    CTkLabel(row_frame, text=class_id, font=("Helvetica", 12), text_color="#333", width=100, anchor="center").pack(side="left", padx=5)
                    CTkLabel(row_frame, text=str(periods), font=("Helvetica", 12), text_color="#333", width=80, anchor="center").pack(side="left", padx=5)
                    CTkLabel(row_frame, text=f"{converted_periods:.1f}", font=("Helvetica", 12), text_color="#333", width=120, anchor="center").pack(side="left", padx=5)
                    CTkLabel(row_frame, text=f"{salary:,.0f} ₫", font=("Helvetica", 12), text_color="#333", width=120, anchor="center").pack(side="left", padx=5)

                # Hàng tổng
                total_frame = CTkFrame(table_frame, fg_color="#E0E0E0")
                total_frame.pack(fill="x", pady=2)
                CTkLabel(total_frame, text=f"Tổng tiền dạy kỳ {semester_name}:", font=("Helvetica", 12, "bold"), text_color="#333", width=300, anchor="center").pack(side="left", padx=5)
                CTkLabel(total_frame, text=f"{total_salary:,.0f} ₫", font=("Helvetica", 12, "bold"), text_color="#333", width=120, anchor="center").pack(side="left", padx=5)

                total_year_salary += total_salary

            # Cập nhật tổng tiền năm và thống kê nhanh
            self.salary_report_total_salary_label.configure(text=f"Tổng tiền dạy trong năm: {total_year_salary:,.0f} ₫")
            self.salary_report_total_classes_label.configure(text=str(total_classes))
            self.salary_report_total_periods_label.configure(text=f"{total_periods:.1f}")
            self.salary_report_total_salary_temp_label.configure(text=f"{total_year_salary:,.0f} đ")

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải báo cáo: {e}")
        finally:
            cursor.close()
            conn.close()

    def export_salary_report(self):
        year = self.report_year_filter.get().strip()
        teacher_str = self.report_teacher_filter.get().strip()
        
        if year == "Chọn năm" or teacher_str == "Chọn giảng viên":
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn năm và giảng viên!")
            return

        try:
            teacher_name, degree_name = teacher_str.split(" - ") if " - " in teacher_str else (None, None)
            if not teacher_name or not degree_name:
                messagebox.showerror("Lỗi", "Định dạng giảng viên không hợp lệ!")
                return

            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Lấy teacher_id
            cursor.execute("""
                SELECT t.teacher_id
                FROM teachers t
                JOIN degrees d ON t.degree_id = d.degree_id
                WHERE t.full_name = %s AND d.degree_name = %s
            """, (teacher_name, degree_name))
            teacher_id_result = cursor.fetchone()
            if not teacher_id_result:
                messagebox.showerror("Lỗi", f"Không tìm thấy giảng viên với tên {teacher_name} và bằng cấp {degree_name}")
                return
            teacher_id = teacher_id_result[0]

            # Lấy thông tin giảng viên
            cursor.execute("""
                SELECT t.full_name, t.teacher_id, d.degree_name, dept.dept_name 
                FROM teachers t 
                JOIN degrees d ON t.degree_id = d.degree_id 
                JOIN departments dept ON t.dept_id = dept.dept_id 
                WHERE t.teacher_id = %s
            """, (teacher_id,))
            teacher = cursor.fetchone()
            if not teacher:
                messagebox.showerror("Lỗi", f"Không tìm thấy giảng viên với mã {teacher_id}")
                return
            full_name, teacher_id, degree_name, dept_name = teacher

            # Lấy teacher_coefficient
            cursor.execute("""
                SELECT tc.coefficient 
                FROM teacher_coefficients tc 
                JOIN teachers t ON tc.degree_id = t.degree_id 
                WHERE t.teacher_id = %s AND tc.year = %s
            """, (teacher_id, year))
            teacher_coeff = cursor.fetchone()
            teacher_coefficient = float(teacher_coeff[0]) if teacher_coeff else 1.0

            # Lấy teaching rate
            cursor.execute("SELECT amount_per_period FROM teaching_rate WHERE year = %s", (year,))
            rate = cursor.fetchone()
            amount_per_period = float(rate[0]) if rate else 0.0

            # Tạo danh sách dữ liệu cho Excel
            data = []
            total_year_salary = 0.0

            # Lấy danh sách kỳ học
            cursor.execute("SELECT semester_id, semester_name FROM semesters WHERE year = %s ORDER BY semester_name", (year,))
            semesters = cursor.fetchall()

            current_semester = None
            if self.current_semester_var.get():
                current_semester = semesters[0][0] if semesters else None  # Lấy kỳ đầu tiên nếu chọn "Chỉ kỳ hiện tại"

            for semester_id, semester_name in semesters:
                if self.current_semester_var.get() and semester_id != current_semester:
                    continue

                cursor.execute("""
                    SELECT c.class_id, cm.periods, c.num_students, cm.coefficient AS hp_coeff
                    FROM assignments a
                    JOIN classes c ON a.class_id = c.class_id
                    JOIN course_modules cm ON c.module_id = cm.module_id
                    WHERE a.teacher_id = %s AND c.semester_id = %s
                """, (teacher_id, semester_id))
                classes = cursor.fetchall()

                total_salary = 0.0
                for class_id, periods, num_students, hp_coeff in classes:
                    student_range = self.get_student_range(num_students)
                    cursor.execute("SELECT coefficient FROM class_coefficients WHERE year = %s AND student_range = %s", (year, student_range))
                    class_coeff = cursor.fetchone()
                    class_coefficient = float(class_coeff[0]) if class_coeff else 0.0

                    converted_periods = periods * (hp_coeff + class_coefficient)
                    salary = converted_periods * teacher_coefficient * amount_per_period
                    total_salary += salary

                    data.append({
                        "Kỳ học": semester_name,
                        "Mã lớp": class_id,
                        "Số tiết": periods,
                        "Số tiết quy đổi": round(converted_periods, 1),
                        "Thành tiền (₫)": round(salary, 0)
                    })

                if classes:
                    data.append({
                        "Kỳ học": f"Tổng tiền kỳ {semester_name}",
                        "Mã lớp": "",
                        "Số tiết": "",
                        "Số tiết quy đổi": "",
                        "Thành tiền (₫)": round(total_salary, 0)
                    })

                total_year_salary += total_salary

            # Xuất Excel
            df = pd.DataFrame(data)
            filename = f"salary_report_{teacher_id}_{year}{'_' + current_semester if self.current_semester_var.get() else ''}.xlsx"
            df.to_excel(filename, index=False)
            messagebox.showinfo("Thành công", f"Báo cáo đã được xuất ra file: {filename}")

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể xuất báo cáo: {e}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi xuất Excel: {e}")
        finally:
            cursor.close()
            conn.close()

    def create_or_load_coefficient_table(self):
        year = self.coefficient_year_filter.get().strip()
        if not year:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn năm học")
            return

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Kiểm tra số lượng bản ghi hiện có cho năm học
            cursor.execute("SELECT COUNT(*) FROM teacher_coefficients WHERE year = %s", (year,))
            count = cursor.fetchone()[0]

            if count > 0:
                if not messagebox.askyesno("Xác nhận", f"Bảng đã chứa {count} bản ghi cho năm {year}. Bạn có muốn ghi đè không?"):
                    return

            # Lấy tất cả bằng cấp từ degrees
            cursor.execute("SELECT degree_id, degree_name, coefficient FROM degrees ORDER BY degree_name")
            degrees = cursor.fetchall()

            # Thêm hoặc cập nhật hệ số mặc định
            for degree_id, degree_name, default_coeff in degrees:
                cursor.execute("""
                    INSERT INTO teacher_coefficients (year, degree_id, coefficient)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE coefficient = VALUES(coefficient)
                """, (year, degree_id, default_coeff))
            conn.commit()

            # Cập nhật giao diện
            self.load_teacher_coefficients()

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tạo hoặc tải bảng: {e}")
        finally:
            cursor.close()
            conn.close()

    def recreate_default_coefficient_table(self):
        year = self.coefficient_year_filter.get().strip()
        if not year:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn năm học")
            return

        # Hiển thị hộp thoại xác nhận
        if not messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn tạo lại bảng mặc định không?"):
            return  # Thoát nếu người dùng chọn "Không"

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Lấy tất cả bằng cấp từ degrees
            cursor.execute("SELECT degree_id, degree_name, coefficient FROM degrees ORDER BY degree_name")
            degrees = cursor.fetchall()

            # Ghi đè dữ liệu cho năm học
            for degree_id, degree_name, default_coeff in degrees:
                cursor.execute("""
                    INSERT INTO teacher_coefficients (year, degree_id, coefficient)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE coefficient = VALUES(coefficient)
                """, (year, degree_id, default_coeff))
            conn.commit()

            # Cập nhật giao diện
            self.load_teacher_coefficients()

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tạo lại bảng: {e}")
        finally:
            cursor.close()
            conn.close()


    def setup_report_tab(self):
        from report_tab import ReportTab
        self.report_tab_content = ReportTab(self.report_tab)
        self.report_tab_content.pack(fill="both", expand=True)


    def setup_assignment_tab(self):
        # Header frame with title and year combobox
        header_frame = CTkFrame(self.assignment_tab, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)
        CTkLabel(header_frame, text="Phân Công Giảng Viên", font=("Helvetica", 18, "bold"), text_color="black").pack(side="left")
        self.year_combobox = CTkComboBox(header_frame, values=self.get_academic_years(), width=150, command=self.reset_and_filter_classes)
        self.year_combobox.pack(side="right")
        self.year_combobox.set("2021-2022")

        # Filter row 1 frame
        filter_row1_frame = CTkFrame(self.assignment_tab, fg_color="transparent")
        filter_row1_frame.pack(fill="x", padx=10, pady=5)

        # Department filter
        dept_filter_frame = CTkFrame(filter_row1_frame, fg_color="transparent")
        dept_filter_frame.pack(side="left", padx=(0, 10))
        CTkLabel(dept_filter_frame, text="Khoa:", font=("Helvetica", 12), text_color="black").pack(side="left", padx=(0, 5))
        self.dept_combobox = CTkComboBox(dept_filter_frame, values=["Chọn khoa"] + self.get_dept_names(), width=200, command=self.update_filters)
        self.dept_combobox.pack(side="left")
        self.dept_combobox.set("Chọn khoa")

        # Teacher filter
        teacher_filter_frame = CTkFrame(filter_row1_frame, fg_color="transparent")
        teacher_filter_frame.pack(side="left", padx=(0, 10))
        CTkLabel(teacher_filter_frame, text="Giáo viên:", font=("Helvetica", 12), text_color="black").pack(side="left", padx=(0, 5))
        self.teacher_combobox = CTkComboBox(teacher_filter_frame, values=["Chọn giảng viên"], width=250)
        self.teacher_combobox.pack(side="left")
        self.teacher_combobox.set("Chọn giảng viên")

        # Filter row 2 frame
        filter_row2_frame = CTkFrame(self.assignment_tab, fg_color="transparent")
        filter_row2_frame.pack(fill="x", padx=10, pady=5)

        # Semester filter
        semester_filter_frame = CTkFrame(filter_row2_frame, fg_color="transparent")
        semester_filter_frame.pack(side="left", padx=(0, 10))
        CTkLabel(semester_filter_frame, text="Kỳ học:", font=("Helvetica", 12), text_color="black").pack(side="left", padx=(0, 5))
        self.semester_combobox = CTkComboBox(semester_filter_frame, values=["Chọn kỳ học"], width=150, command=self.assignment_filter_classes)
        self.semester_combobox.pack(side="left")
        self.semester_combobox.set("Chọn kỳ học")

        # Module filter
        module_filter_frame = CTkFrame(filter_row2_frame, fg_color="transparent")
        module_filter_frame.pack(side="left", padx=(0, 10))
        CTkLabel(module_filter_frame, text="Học phần:", font=("Helvetica", 12), text_color="black").pack(side="left", padx=(0, 5))
        self.module_combobox = CTkComboBox(module_filter_frame, values=["Tất cả"], width=150, command=self.assignment_filter_classes)
        self.module_combobox.pack(side="left")
        self.module_combobox.set("Tất cả")

        # Assignment status filter
        status_filter_frame = CTkFrame(filter_row2_frame, fg_color="transparent")
        status_filter_frame.pack(side="left", padx=(0, 10))
        CTkLabel(status_filter_frame, text="Trạng thái:", font=("Helvetica", 12), text_color="black").pack(side="left", padx=(0, 5))
        self.status_combobox = CTkComboBox(status_filter_frame, values=["Tất cả", "Đã phân công", "Chưa phân công"], width=150, command=self.assignment_filter_classes)
        self.status_combobox.pack(side="left")
        self.status_combobox.set("Tất cả")

        # Assign button (initially hidden) with 30% width
        filter_row2_frame.update_idletasks()
        total_width = filter_row2_frame.winfo_width()
        assign_button_width = int(total_width * 0.3) if total_width > 0 else 150
        self.assign_button = CTkButton(filter_row2_frame, text="Phân công giảng viên", fg_color="#0085FF", command=self.assignment_assign_teacher, state="disabled", width=assign_button_width)
        self.assign_button.pack(side="left", padx=(10, 0))

        # Table frame with scrollbar
        table_frame = CTkFrame(self.assignment_tab, fg_color="#FFFFFF", corner_radius=10)
        table_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Scrollbar
        canvas = tk.Canvas(table_frame)
        scrollbar = ctk.CTkScrollbar(table_frame, orientation="vertical", command=canvas.yview)
        scrollable_frame = CTkFrame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Heading row with fixed total width
        heading_frame = CTkFrame(scrollable_frame, fg_color="#D3D3D3", corner_radius=0)
        heading_frame.pack(fill="x", padx=5, pady=(5, 0))
        
        # Column headers with adjusted widths to match data
        CTkLabel(heading_frame, text="Chọn", font=("Helvetica", 14, "bold"), text_color="black", width=50, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Mã lớp", font=("Helvetica", 14, "bold"), text_color="black", width=100, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Tên lớp", font=("Helvetica", 14, "bold"), text_color="black", width=250, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Học phần", font=("Helvetica", 14, "bold"), text_color="black", width=200, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Kỳ học", font=("Helvetica", 14, "bold"), text_color="black", width=100, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Số SV", font=("Helvetica", 14, "bold"), text_color="black", width=80, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Giảng viên hiện tại", font=("Helvetica", 14, "bold"), text_color="black", width=250, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Thao tác", font=("Helvetica", 14, "bold"), text_color="black", width=150, anchor="center").pack(side="left", padx=5)

        # List frame
        self.assignment_list_frame = CTkFrame(scrollable_frame, fg_color="transparent")
        self.assignment_list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Load initial data
        self.assignment_update_semester_options()
        self.assignment_update_teacher_options()
        self.update_filters()  # Khởi tạo danh sách học phần
        self.assignment_filter_classes()

    def get_teachers_by_dept(self, dept_name):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            if dept_name == "Tất cả khoa":
                cursor.execute("""
                    SELECT t.teacher_id, t.full_name, d.degree_abbr
                    FROM teachers t
                    JOIN degrees d ON t.degree_id = d.degree_id
                    ORDER BY t.full_name
                """)
            else:
                cursor.execute("""
                    SELECT t.teacher_id, t.full_name, d.degree_abbr
                    FROM teachers t
                    JOIN degrees d ON t.degree_id = d.degree_id
                    JOIN departments dept ON t.dept_id = dept.dept_id
                    WHERE dept.dept_name = %s
                    ORDER BY t.full_name
                """, (dept_name,))
            teachers = cursor.fetchall()
            return [f"{row[2]}. {row[1]} ({row[0]})" for row in teachers] if teachers else ["Chọn giảng viên"]
        except mysql.connector.Error:
            return ["Chọn giảng viên"]
        finally:
            cursor.close()
            conn.close()

    def get_semesters_by_year(self, year):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT semester_name FROM semesters WHERE year = %s ORDER BY semester_name", (year,))
            semesters = [row[0] for row in cursor.fetchall()]
            return semesters if semesters else ["Chọn kỳ học"]
        except mysql.connector.Error as e:
            print(f"Error fetching semesters: {e}")  # Thêm debug log
            return ["Chọn kỳ học"]
        finally:
            cursor.close()
            conn.close()
    
    def get_modules_by_semester(self, year, semester):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT cm.module_name
                FROM semesters s
                JOIN classes c ON s.semester_id = c.semester_id
                JOIN course_modules cm ON c.module_id = cm.module_id
                WHERE s.year = %s AND s.semester_name = %s
                ORDER BY cm.module_name
            """, (year, semester))
            modules = [row[0] for row in cursor.fetchall()]
            return modules if modules else []
        except mysql.connector.Error as e:
            print(f"Error fetching modules: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def assignment_update_semester_options(self, event=None):
        year = self.year_combobox.get()
        semesters = self.get_semesters_by_year(year)
        self.semester_combobox.configure(values=["Chọn kỳ học"] + semesters if semesters else ["Chọn kỳ học"])
        self.semester_combobox.set("Chọn kỳ học")
        self.assignment_update_module_options()
        self.assignment_filter_classes()  # Cập nhật bảng khi thay đổi kỳ học

    def assignment_update_teacher_options(self, event=None):
        dept = self.dept_combobox.get()
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            if dept == "Chọn khoa":
                self.teacher_combobox.configure(values=["Chọn giảng viên"])
                self.teacher_combobox.set("Chọn giảng viên")
            else:
                cursor.execute("""
                    SELECT t.teacher_id, t.full_name, d.degree_abbr
                    FROM teachers t
                    JOIN degrees d ON t.degree_id = d.degree_id
                    JOIN departments dept ON t.dept_id = dept.dept_id
                    WHERE dept.dept_name = %s
                    ORDER BY t.full_name
                """, (dept,))
                teachers = cursor.fetchall()
                if teachers:
                    teacher_list = [f"{row[2]}. {row[1]} ({row[0]})" for row in teachers]
                    self.teacher_combobox.configure(values=["Chọn giảng viên"] + teacher_list)
                    self.teacher_combobox.set("Chọn giảng viên")
                else:
                    self.teacher_combobox.configure(values=["Chọn giảng viên", "Không có giáo viên"])
                    self.teacher_combobox.set("Chọn giảng viên")
        except mysql.connector.Error as e:
            print(f"Error fetching teachers: {e}")
            self.teacher_combobox.configure(values=["Chọn giảng viên", f"Lỗi: {str(e)}"])
            self.teacher_combobox.set("Chọn giảng viên")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def assignment_update_module_options(self, event=None):
        year = self.year_combobox.get()
        semester = self.semester_combobox.get()
        try:
            if semester != "Chọn kỳ học":
                modules = self.get_modules_by_semester(year, semester)
                self.module_combobox.configure(values=["Tất cả"] + modules if modules else ["Tất cả"])
                self.module_combobox.set("Tất cả")
            else:
                self.module_combobox.configure(values=["Tất cả"])
                self.module_combobox.set("Tất cả")
        except Exception as e:
            print(f"Error updating module options: {e}")
            self.module_combobox.configure(values=["Tất cả"])
            self.module_combobox.set("Tất cả")

    def toggle_class_selection(self, var, class_id):
        if var.get():
            if class_id not in self.selected_classes:
                self.selected_classes.append(class_id)
        else:
            if class_id in self.selected_classes:
                self.selected_classes.remove(class_id)
        self.update_assign_button()

    def update_assign_button(self):
        if self.selected_classes:
            self.assign_button.configure(state="normal")
        else:
            self.assign_button.configure(state="disabled")

    def assignment_filter_classes(self, event=None):
        year = self.year_combobox.get()
        semester = self.semester_combobox.get()
        module = self.module_combobox.get() 
        dept = self.dept_combobox.get()
        status = self.status_combobox.get()

        for widget in self.assignment_list_frame.winfo_children():
            widget.destroy()

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            query = """
                SELECT c.class_id, c.class_name, cm.module_name, s.semester_name, 
                    COALESCE(ce.enrolled_students, 0) AS enrolled_students,
                    COALESCE(t.full_name, 'Chưa phân công')
                FROM classes c
                JOIN semesters s ON c.semester_id = s.semester_id
                JOIN course_modules cm ON c.module_id = cm.module_id
                LEFT JOIN assignments a ON c.class_id = a.class_id
                LEFT JOIN teachers t ON a.teacher_id = t.teacher_id
                LEFT JOIN class_enrollments ce ON c.class_id = ce.class_id
                JOIN departments d ON cm.dept_id = d.dept_id
                WHERE s.year = %s
            """
            params = [year]

            if semester != "Chọn kỳ học" and semester != "Tất cả":
                query += " AND s.semester_name = %s"
                params.append(semester)
            if module != "Tất cả":
                query += " AND cm.module_name = %s"
                params.append(module)
            if dept != "Chọn khoa" and dept != "Tất cả khoa":
                query += " AND d.dept_name = %s"
                params.append(dept)
            if status == "Đã phân công":
                query += " AND a.class_id IS NOT NULL"
            elif status == "Chưa phân công":
                query += " AND a.class_id IS NULL"

            cursor.execute(query, params)
            classes = cursor.fetchall()

            self.selected_classes = []
            if not classes:
                CTkLabel(self.assignment_list_frame, text="Không có dữ liệu lớp học", font=("Helvetica", 12), text_color="red").pack(pady=10)
            else:
                for idx, (class_id, class_name, module_name, semester_name, enrolled_students, teacher_name) in enumerate(classes, 1):
                    class_row = CTkFrame(self.assignment_list_frame, fg_color="#F5F5F5" if idx % 2 else "#FFFFFF")
                    class_row.pack(fill="x", pady=2)  # Giảm pady từ 2 xuống 1 để các row gần nhau hơn
                    class_row.configure(height=35)  # Thêm height=25 để row nhỏ hơn
                    class_row.pack_propagate(False)

                    # Chỉ hiện checkbox nếu chưa phân công
                    if teacher_name == 'Chưa phân công':
                        check_var = BooleanVar()
                        checkbox = CTkCheckBox(class_row, text="", variable=check_var, width=50, 
                                        command=lambda v=check_var, c=class_id: self.toggle_class_selection(v, c))
                        checkbox.pack(side="left", padx=(10, 2))  # Tăng padding bên trái lên 10
                    else:
                        # Giữ nguyên padding cho empty_frame để đảm bảo căn chỉnh
                        empty_frame = CTkFrame(class_row, width=50, fg_color="transparent")
                        empty_frame.pack(side="left", padx=(10, 2))  # Tăng padding bên trái lên 10
                        empty_frame.pack_propagate(False)

                    CTkLabel(class_row, text=class_id, font=("Helvetica", 12), width=100, anchor="center").pack(side="left", padx=5)
                    CTkLabel(class_row, text=class_name, font=("Helvetica", 12), width=250, anchor="center").pack(side="left", padx=5)
                    CTkLabel(class_row, text=module_name, font=("Helvetica", 12), width=200, anchor="center").pack(side="left", padx=5)
                    CTkLabel(class_row, text=semester_name, font=("Helvetica", 12), width=100, anchor="center").pack(side="left", padx=5)
                    CTkLabel(class_row, text=str(enrolled_students), font=("Helvetica", 12), width=80, anchor="center").pack(side="left", padx=5)
                    CTkLabel(class_row, text=teacher_name, font=("Helvetica", 12), width=250, anchor="center").pack(side="left", padx=5)

                    # Frame chứa nút với thao tác tương ứng
                    action_frame = CTkFrame(class_row, fg_color="transparent")
                    action_frame.pack(side="left", padx=5)

                    # Chỉ hiện nút Sửa nếu đã phân công
                    if teacher_name != 'Chưa phân công':
                        CTkButton(action_frame, text="Sửa", fg_color="#FF6384", width=70,
                                command=lambda c=class_id: self.assignment_edit_assignment(c)).pack(side="left", padx=30)

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu lớp: {e}")
        finally:
            cursor.close()
            conn.close()
        self.update_assign_button()

    def assignment_assign_teacher(self):
        if not self.selected_classes:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một lớp để phân công!")
            return
        teacher = self.teacher_combobox.get()
        if teacher == "Chọn giảng viên":
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn giảng viên!")
            return

        teacher_id = teacher.split("(")[-1].strip(")")
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            for class_id in self.selected_classes:
                # Kiểm tra xem lớp đã được phân công chưa
                cursor.execute("SELECT assignment_id FROM assignments WHERE class_id = %s", (class_id,))
                if cursor.fetchone():
                    messagebox.showwarning("Cảnh báo", f"Lớp {class_id} đã được phân công!")
                    continue
                # Tạo assignment_id mới
                cursor.execute("SELECT MAX(CAST(SUBSTRING(assignment_id, 4) AS UNSIGNED)) FROM assignments")
                max_id = cursor.fetchone()[0]
                new_id = f"ASN{str(max_id + 1).zfill(5)}" if max_id else "ASN00001"
                cursor.execute("INSERT INTO assignments (assignment_id, class_id, teacher_id) VALUES (%s, %s, %s)",
                            (new_id, class_id, teacher_id))
            conn.commit()
            messagebox.showinfo("Thành công", "Phân công giảng viên thành công!")
            self.assignment_filter_classes()
            self.selected_classes = []
            self.assign_button.configure(state="disabled")
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể phân công: {e}")
        finally:
            cursor.close()
            conn.close()

    def assignment_edit_assignment(self, class_id):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            # Lấy thông tin phân công hiện tại
            cursor.execute("""
                SELECT t.teacher_id, t.full_name, d.dept_name 
                FROM assignments a
                JOIN teachers t ON a.teacher_id = t.teacher_id
                JOIN departments d ON t.dept_id = d.dept_id
                WHERE a.class_id = %s
            """, (class_id,))
            current_assignment = cursor.fetchone()
            
            if not current_assignment:
                messagebox.showwarning("Cảnh báo", f"Lớp {class_id} chưa được phân công!")
                return
            
            current_teacher_id, current_teacher_name, dept_name = current_assignment

            # Lấy danh sách giảng viên của khoa
            cursor.execute("""
                SELECT t.teacher_id, t.full_name, d.degree_abbr 
                FROM teachers t
                JOIN degrees d ON t.degree_id = d.degree_id
                JOIN departments dept ON t.dept_id = dept.dept_id
                WHERE dept.dept_name = %s
                ORDER BY t.full_name
            """, (dept_name,))
            teachers = cursor.fetchall()
            teacher_list = [f"{row[2]}. {row[1]} ({row[0]})" for row in teachers]

            # Tạo popup window
            popup = CTkToplevel(self.window)
            popup.title("Sửa phân công giảng viên")
            popup.geometry("400x350")

            # Căn giữa popup
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            x = (screen_width - 400) // 2
            y = (screen_height - 250) // 2
            popup.geometry(f"400x350+{x}+{y}")

            popup.transient(self.window)
            popup.grab_set()

            # Main frame
            frame = CTkFrame(popup, fg_color="#F0F0F0", corner_radius=10)
            frame.pack(padx=20, pady=20, fill="both", expand=True)

            # Title
            CTkLabel(frame, text="Sửa phân công giảng viên", 
                    font=("Helvetica", 16, "bold")).pack(pady=(0,20))

            # Class info
            CTkLabel(frame, text=f"Mã lớp: {class_id}", 
                    font=("Helvetica", 12)).pack(pady=5)
            CTkLabel(frame, text=f"Khoa: {dept_name}", 
                    font=("Helvetica", 12)).pack(pady=5)

            # Teacher selection
            CTkLabel(frame, text="Chọn giảng viên:", 
                    font=("Helvetica", 12)).pack(pady=5)
            
            # Find current teacher in list
            current_teacher = next((t for t in teacher_list 
                                if t.endswith(f"({current_teacher_id})")), teacher_list[0])
            
            teacher_var = StringVar(value=current_teacher)
            teacher_combo = CTkComboBox(frame, values=teacher_list, 
                                    variable=teacher_var, width=300)
            teacher_combo.pack(pady=10)

            # Buttons frame
            button_frame = CTkFrame(frame, fg_color="transparent")
            button_frame.pack(pady=20)

            def save_assignment():
                if not messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn thay đổi phân công này?", parent=popup):
                    return
                    
                new_teacher = teacher_var.get()
                if new_teacher == "Chọn giảng viên":
                    messagebox.showerror("Lỗi", "Vui lòng chọn giảng viên!", parent=popup)
                    return

                new_teacher_id = new_teacher.split("(")[-1].strip(")")
                
                try:
                    conn = mysql.connector.connect(**DB_CONFIG)
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE assignments 
                        SET teacher_id = %s 
                        WHERE class_id = %s
                    """, (new_teacher_id, class_id))
                    conn.commit()
                    messagebox.showinfo("Thành công", 
                                    "Cập nhật phân công thành công!", parent=popup)
                    popup.destroy()
                    self.assignment_filter_classes()
                except mysql.connector.Error as e:
                    messagebox.showerror("Lỗi", 
                                    f"Không thể cập nhật phân công: {e}", parent=popup)
                finally:
                    cursor.close()
                    conn.close()

            # Save button
            CTkButton(button_frame, text="Lưu", fg_color="#0085FF", 
                    width=100, command=save_assignment).pack(side="left", padx=5)
            
            # Cancel button
            CTkButton(button_frame, text="Hủy", fg_color="#FF6384", 
                    width=100, command=popup.destroy).pack(side="left", padx=5)

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải thông tin phân công: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def reset_and_filter_classes(self, event=None):
        year = self.year_combobox.get()
        self.dept_combobox.set("Chọn khoa")
        self.teacher_combobox.set("Chọn giảng viên")
        self.semester_combobox.set("Chọn kỳ học")
        self.module_combobox.set("Tất cả")
        self.status_combobox.set("Tất cả")
        self.assignment_update_semester_options()  # Cập nhật kỳ học dựa trên năm mới
        self.assignment_filter_classes()  # Lọc lại bảng với năm mới
    
    def update_filters(self, event=None):
        dept = self.dept_combobox.get()
        year = self.year_combobox.get()
        semester = self.semester_combobox.get()
        
        # Update teacher options based on department
        self.assignment_update_teacher_options()
        
        # Update module options based on department and semester
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            if dept != "Chọn khoa" and semester != "Chọn kỳ học":
                # Lấy danh sách học phần theo khoa và kỳ học
                cursor.execute("""
                    SELECT DISTINCT cm.module_name
                    FROM course_modules cm
                    JOIN classes c ON cm.module_id = c.module_id
                    JOIN semesters s ON c.semester_id = s.semester_id
                    JOIN departments d ON cm.dept_id = d.dept_id
                    WHERE d.dept_name = %s 
                    AND s.year = %s
                    AND s.semester_name = %s
                    ORDER BY cm.module_name
                """, (dept, year, semester))
                
                modules = [row[0] for row in cursor.fetchall()]
                if modules:
                    self.module_combobox.configure(values=["Tất cả"] + modules)
                else:
                    self.module_combobox.configure(values=["Tất cả"])
            else:
                # Nếu chưa chọn khoa hoặc kỳ học, lấy tất cả học phần
                if dept != "Chọn khoa":
                    cursor.execute("""
                        SELECT DISTINCT cm.module_name
                        FROM course_modules cm
                        JOIN departments d ON cm.dept_id = d.dept_id
                        WHERE d.dept_name = %s
                        ORDER BY cm.module_name
                    """, (dept,))
                else:
                    cursor.execute("""
                        SELECT DISTINCT cm.module_name
                        FROM course_modules cm
                        ORDER BY cm.module_name
                    """)
                    
                modules = [row[0] for row in cursor.fetchall()]
                self.module_combobox.configure(values=["Tất cả"] + modules)

            self.module_combobox.set("Tất cả")
            
        except mysql.connector.Error as e:
            print(f"Error updating modules: {e}")
            self.module_combobox.configure(values=["Tất cả"])
            self.module_combobox.set("Tất cả")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
        
        # Cập nhật lại bảng dữ liệu
        self.assignment_filter_classes()