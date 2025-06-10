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
                    print(f"Debug: User dept_id: {self.user['dept_id']}")
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
            "Quản lý giáo viên": False,
            "Quản lý lớp học phần": False,
            "Thống kê": False
        }

        # Dictionary để lưu các button của tab con
        self.submenu_buttons = {
            "Quản lý giáo viên": [],
            "Quản lý lớp học phần": [],
            "Thống kê": []
        }

        # Dictionary để lưu các frame chứa tab con
        self.submenu_frames = {
            "Quản lý giáo viên": None,
            "Quản lý lớp học phần": None,
            "Thống kê": None
        }

        # Dictionary để ánh xạ mục chính với các tab con
        self.submenu_items = {
            "Quản lý giáo viên": ["Bằng cấp", "Khoa", "Giáo viên"],
            "Quản lý lớp học phần": ["Học phần", "Kỳ học", "Lớp học"],  # Xóa "Phân công"
            "Thống kê": ["Thống kê giáo viên", "Thống kê lớp"]
        }

        # Menu sidebar với cơ chế drop down
        # Mục chính: Quản lý giáo viên
        self.teacher_info_button = CTkButton(self.sidebar, text="▶ Quản lý giáo viên", font=("Helvetica", 18, "bold"), fg_color="#2A4B8D",
                                        text_color="white", hover_color="#4A78E0", anchor="w",
                                        command=lambda: self.toggle_submenu("Quản lý giáo viên"))
        self.teacher_info_button.pack(pady=(15, 0), padx=10, fill="x")
        self.submenu_frames["Quản lý giáo viên"] = CTkFrame(self.sidebar, fg_color="transparent", height=0)
        self.submenu_frames["Quản lý giáo viên"].pack(pady=0, padx=5, fill="x")

        # Mục chính: Quản lý lớp học phần
        self.class_management_button = CTkButton(self.sidebar, text="▶ Quản lý lớp học phần", font=("Helvetica", 18, "bold"), fg_color="#2A4B8D",
                                                text_color="white", hover_color="#4A78E0", anchor="w",
                                                command=lambda: self.toggle_submenu("Quản lý lớp học phần"))
        self.class_management_button.pack(pady=(15, 0), padx=10, fill="x")
        self.submenu_frames["Quản lý lớp học phần"] = CTkFrame(self.sidebar, fg_color="transparent", height=0)
        self.submenu_frames["Quản lý lớp học phần"].pack(pady=0, padx=5, fill="x")

        # Mục chính: Thống kê
        self.stats_button = CTkButton(self.sidebar, text="▶ Thống kê", font=("Helvetica", 18, "bold"), fg_color="#2A4B8D",
                                    text_color="white", hover_color="#4A78E0", anchor="w",
                                    command=lambda: self.toggle_submenu("Thống kê"))
        self.stats_button.pack(pady=(15, 0), padx=10, fill="x")
        self.submenu_frames["Thống kê"] = CTkFrame(self.sidebar, fg_color="transparent", height=0)
        self.submenu_frames["Thống kê"].pack(pady=0, padx=5, fill="x")

        # Mục chính: Lương (không có tab con)
        CTkButton(self.sidebar, text="Lương", font=("Helvetica", 18, "bold"), fg_color="#2A4B8D",
                text_color="white", hover_color="#4A78E0", anchor="w",
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
        CTkLabel(heading_frame, text="Mã bằng cấp", font=("Helvetica", 12, "bold"), text_color="black", width=80, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Tên bằng cấp", font=("Helvetica", 12, "bold"), text_color="black", width=400, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Tên viết tắt", font=("Helvetica", 12, "bold"), text_color="black", width=200, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Hệ số", font=("Helvetica", 12, "bold"), text_color="black", width=150, anchor="center").pack(side="left", padx=5)
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
        CTkLabel(heading_frame, text="Email", font=("Helvetica", 12, "bold"), text_color="black", width=120, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Khoa", font=("Helvetica", 12, "bold"), text_color="black", width=200, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Bằng cấp", font=("Helvetica", 12, "bold"), text_color="black", width=120, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Hệ số", font=("Helvetica", 12, "bold"), text_color="black", width=60, anchor="center").pack(side="left", padx=5)
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
        main_frame.pack(fill="both", expand=True, pady=20)

        # Tiêu đề
        CTkLabel(main_frame, text="Phân bố độ tuổi giáo viên", font=("Helvetica", 18, "bold"), text_color="black").pack(pady=5)

        # Frame biểu đồ và bảng
        content_frame = CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)

        # Frame biểu đồ
        chart_container = CTkFrame(content_frame, fg_color="#FFFFFF")
        chart_container.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        # Biểu đồ
        fig, ax = plt.subplots(figsize=(4, 2.5))
        ax.bar(age_labels, age_data, color=["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"])
        ax.set_title("Phân bố độ tuổi", fontsize=12, pad=15)
        ax.set_xlabel("Nhóm tuổi", fontsize=10)
        ax.set_ylabel("Số giáo viên", fontsize=10)
        ax.set_ylim(0, max(age_data) + 1 if age_data else 1)
        plt.xticks(rotation=0, ha="center", fontsize=8)  # Không xoay nhãn
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", expand=True)

        # Frame bảng
        table_container = CTkFrame(content_frame, fg_color="#FFFFFF")
        table_container.pack(side="right", padx=10, pady=10, fill="both", expand=True)

        # Tiêu đề bảng
        CTkLabel(table_container, text="Chi tiết thống kê", font=("Helvetica", 14, "bold"), text_color="black").pack(pady=5)

        # Bảng
        style = ttk.Style()
        style.configure("Stats.Treeview", font=("Helvetica", 10))
        style.configure("Stats.Treeview.Heading", font=("Helvetica", 10, "bold"))
        
        tree = ttk.Treeview(table_container, columns=("Age", "Count", "Ratio"), show="headings", style="Stats.Treeview")
        tree.heading("Age", text="Độ tuổi", anchor="center")
        tree.heading("Count", text="Số lượng", anchor="center")
        tree.heading("Ratio", text="Tỷ lệ", anchor="center")
        tree.column("Age", width=100, anchor="center", stretch=True)
        tree.column("Count", width=80, anchor="center", stretch=True)
        tree.column("Ratio", width=80, anchor="center", stretch=True)
        tree.pack(fill="both", expand=True)

        for label, count, ratio in zip(age_labels, age_data, ratios):
            tree.insert("", "end", values=(label, count, ratio))

    def show_degree_chart(self):
        self.clear_chart_frame()
        
        degree_labels, degree_data = self.get_degree_distribution()
        if not degree_labels or not degree_data:
            messagebox.showwarning("Cảnh báo!", "Không có dữ liệu bằng cấp để xem!")
            return

        total = sum(degree_data)
        ratios = [f"{(count/total*100):.1f}%" if total > 0 else "0.0%" for count in degree_data]

        # Frame chính
        main_frame = CTkFrame(self.chart_frame, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, pady=20)

        # Tiêu đề
        CTkLabel(main_frame, text="Phân bố bằng cấp giáo viên", font=("Helvetica", 18, "bold"), text_color="black").pack(pady=5)

        # Frame biểu đồ và bảng
        content_frame = CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)

        # Frame biểu đồ
        chart_container = CTkFrame(content_frame, fg_color="#FFFFFF")
        chart_container.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        # Biểu đồ
        fig, ax = plt.subplots(figsize=(4, 2.5))
        ax.bar(degree_labels, degree_data, color=["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"])
        ax.set_title("Phân bố bằng cấp", fontsize=12, pad=15)
        ax.set_xlabel("Bằng cấp", fontsize=10)
        ax.set_ylabel("Số giáo viên", fontsize=10)
        ax.set_ylim(0, max(degree_data) + 1 if degree_data else 1)
        plt.xticks(rotation=0, ha="center", fontsize=8)  # Không xoay nhãn
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", expand=True)

        # Frame bảng
        table_container = CTkFrame(content_frame, fg_color="#FFFFFF")
        table_container.pack(side="right", padx=10, pady=10, fill="both", expand=True)

        # Tiêu đề bảng
        CTkLabel(table_container, text="Chi tiết thống kê", font=("Helvetica", 14, "bold"), text_color="black").pack(pady=5)

        # Bảng
        style = ttk.Style()
        style.configure("Stats.Treeview", font=("Helvetica", 10))
        style.configure("Stats.Treeview.Heading", font=("Helvetica", 10, "bold"))
        
        tree = ttk.Treeview(table_container, columns=("Degree", "Count", "Ratio"), show="headings", style="Stats.Treeview")
        tree.heading("Degree", text="Bằng cấp", anchor="center")
        tree.heading("Count", text="Số lượng", anchor="center")
        tree.heading("Ratio", text="Tỷ lệ", anchor="center")
        tree.column("Degree", width=100, anchor="center", stretch=True)
        tree.column("Count", width=80, anchor="center", stretch=True)
        tree.column("Ratio", width=80, anchor="center", stretch=True)
        tree.pack(fill="both", expand=True)

        for label, count, ratio in zip(degree_labels, degree_data, ratios):
            tree.insert("", "end", values=(label, count, ratio))

    def show_dept_chart(self):
        self.clear_chart_frame()
        
        # Lấy cả tên viết tắt và tên đầy đủ
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            query = """
                SELECT d.dept_abbr, d.dept_name, COUNT(t.teacher_id) 
                FROM departments d 
                LEFT JOIN teachers t ON d.dept_id = t.dept_id
                GROUP BY d.dept_id, d.dept_abbr, d.dept_name
            """
            cursor.execute(query)
            dept_abbrs = []  # Tên viết tắt cho biểu đồ
            dept_names = []  # Tên đầy đủ cho bảng
            dept_data = []
            for row in cursor.fetchall():
                dept_abbr, dept_name, count = row
                dept_abbrs.append(dept_abbr)
                dept_names.append(dept_name)
                dept_data.append(count)
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu khoa: {e}")
            return [], []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        if not dept_abbrs or not dept_data:
            messagebox.showwarning("Cảnh báo!", "Không có dữ liệu khoa để xem!")
            return

        total = sum(dept_data)
        ratios = [f"{(count/total*100):.1f}%" if total > 0 else "0.0%" for count in dept_data]

        # Frame chính
        main_frame = CTkFrame(self.chart_frame, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, pady=20)

        # Tiêu đề
        CTkLabel(main_frame, text="Phân bố giáo viên theo khoa", font=("Helvetica", 18, "bold"), text_color="black").pack(pady=5)

        # Frame biểu đồ và bảng
        content_frame = CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)

        # Frame biểu đồ
        chart_container = CTkFrame(content_frame, fg_color="#FFFFFF")
        chart_container.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        # Biểu đồ cột
        fig, ax = plt.subplots(figsize=(4, 2.5))
        ax.bar(dept_abbrs, dept_data, color=["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"])
        ax.set_title("Phân bố theo khoa", fontsize=12, pad=15)
        ax.set_xlabel("Khoa (viết tắt)", fontsize=10)
        ax.set_ylabel("Số giáo viên", fontsize=10)
        ax.set_ylim(0, max(dept_data) + 1 if dept_data else 1)
        plt.xticks(rotation=0, ha="center", fontsize=8)  # Không xoay nhãn
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", expand=True)

        # Frame bảng
        table_container = CTkFrame(content_frame, fg_color="#FFFFFF")
        table_container.pack(side="right", padx=10, pady=10, fill="both", expand=True)

        # Tiêu đề bảng
        CTkLabel(table_container, text="Chi tiết thống kê", font=("Helvetica", 14, "bold"), text_color="black").pack(pady=5)

        # Bảng
        style = ttk.Style()
        style.configure("Stats.Treeview", font=("Helvetica", 10))
        style.configure("Stats.Treeview.Heading", font=("Helvetica", 10, "bold"))
        
        tree = ttk.Treeview(table_container, columns=("Dept", "Count", "Ratio"), show="headings", style="Stats.Treeview")
        tree.heading("Dept", text="Khoa", anchor="center")
        tree.heading("Count", text="Số lượng", anchor="center")
        tree.heading("Ratio", text="Tỷ lệ", anchor="center")
        tree.column("Dept", width=120, anchor="center", stretch=True)
        tree.column("Count", width=80, anchor="center", stretch=True)
        tree.column("Ratio", width=80, anchor="center", stretch=True)
        tree.pack(fill="both", expand=True)

        for name, count, ratio in zip(dept_names, dept_data, ratios):
            tree.insert("", "end", values=(name, count, ratio))

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
        self.assignment_tree.column("Module", width=170, anchor="center")
        self.assignment_tree.column("ID", width=80, anchor="center")
        self.assignment_tree.column("Name", width=170, anchor="center")
        self.assignment_tree.column("Students", width=80, anchor="center")
        self.assignment_tree.column("Teacher", width=200, anchor="center")
        self.assignment_tree.pack(padx=10, pady=10, fill="both", expand=True)
        self.assignment_tree.bind("<<TreeviewSelect>>", self.on_assignment_select)
        self.load_classes_by_semester(None)  # Tải danh sách lớp học phần khi khởi tạo

    def setup_class_stats_tab(self):
    # Tiêu đề
        ctk.CTkLabel(self.class_stats_tab, text="Thống kê lớp học phần", font=("Helvetica", 18, "bold"), text_color="black").pack(pady=10)

        # Frame bộ lọc
        filter_frame = ctk.CTkFrame(self.class_stats_tab, fg_color="#F0F0F0", corner_radius=10)
        filter_frame.pack(padx=10, pady=10, fill="x")
        ctk.CTkLabel(filter_frame, text="Năm học:", font=("Helvetica", 14), text_color="black").pack(side="left", padx=5)
        self.stats_year_combobox = ctk.CTkComboBox(filter_frame, width=200, values=self.get_academic_years(), command=self.update_class_stats)
        self.stats_year_combobox.pack(side="left", padx=5)
        self.stats_year_combobox.set("2025-2026")  # Đặt mặc định là 2025-2026

        # Frame nút điều hướng
        button_frame = ctk.CTkFrame(self.class_stats_tab, fg_color="transparent")
        button_frame.pack(pady=5)
        ctk.CTkButton(button_frame, text="Tất cả", fg_color="#0085FF", hover_color="#005BB5", command=self.show_class_stats_all).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Biểu đồ", fg_color="#FF6384", hover_color="#E55773", command=self.show_class_stats_chart).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Bảng", fg_color="#36A2EB", hover_color="#2A82C5", command=self.show_class_stats_table).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Xuất Excel", fg_color="#FFCE56", hover_color="#E5B74C", command=self.export_excel).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Cập nhật ngay", fg_color="#28A745", hover_color="#218838", command=self.refresh_data_realtime).pack(side="left", padx=5)

        # Frame tổng quan với 4 ô thẻ thông tin
        overview_frame = ctk.CTkFrame(self.class_stats_tab, fg_color="transparent")
        overview_frame.pack(fill="x", padx=10, pady=10)

        # Ô 1: Tổng số lớp học phần
        total_classes_frame = ctk.CTkFrame(overview_frame, fg_color="#BBDEFB", corner_radius=12, border_width=3, border_color="#1976D2", width=200, height=100)
        total_classes_frame.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        total_classes_frame.pack_propagate(False)
        ctk.CTkLabel(total_classes_frame, text="Tổng số lớp học phần", font=("Helvetica", 12, "bold"), text_color="#0D47A1").pack(pady=(5, 0))
        self.total_classes_label = ctk.CTkLabel(total_classes_frame, text="15", font=("Helvetica", 24, "bold"), text_color="#0D47A1")
        self.total_classes_label.pack(pady=(0, 5))
        self.total_modules_label = ctk.CTkLabel(total_classes_frame, text="4 học phần", font=("Helvetica", 12, "bold"), text_color="#0D47A1")
        self.total_modules_label.pack(pady=(0, 5))

        # Ô 2: Tổng số sinh viên (loại bỏ dòng dưới cùng)
        total_students_frame = ctk.CTkFrame(overview_frame, fg_color="#FFECB3", corner_radius=12, border_width=3, border_color="#F57C00", width=200, height=100)
        total_students_frame.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        total_students_frame.pack_propagate(False)
        ctk.CTkLabel(total_students_frame, text="Tổng số sinh viên", font=("Helvetica", 12, "bold"), text_color="#E65100").pack(pady=(5, 0))
        self.total_students_label = ctk.CTkLabel(total_students_frame, text="640", font=("Helvetica", 24, "bold"), text_color="#E65100")
        self.total_students_label.pack(pady=(0, 10))  # Tăng pady để cân đối không gian

        # Ô 3: Trung bình SV/lớp
        avg_students_frame = ctk.CTkFrame(overview_frame, fg_color="#FFCDD2", corner_radius=12, border_width=3, border_color="#D32F2F", width=200, height=100)
        avg_students_frame.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        avg_students_frame.pack_propagate(False)
        ctk.CTkLabel(avg_students_frame, text="Trung bình SV/lớp", font=("Helvetica", 12, "bold"), text_color="#B71C1C").pack(pady=(5, 0))
        self.avg_per_class_label = ctk.CTkLabel(avg_students_frame, text="42.67", font=("Helvetica", 24, "bold"), text_color="#B71C1C")
        self.avg_per_class_label.pack(pady=(0, 5))
        ctk.CTkLabel(avg_students_frame, text=" ", font=("Helvetica", 12, "bold"), text_color="#B71C1C").pack(pady=(0, 5))

        # Ô 4: Môn đông SV nhất (giữ nguyên)
        top_module_frame = ctk.CTkFrame(overview_frame, fg_color="#D1C4E9", corner_radius=12, border_width=3, border_color="#673AB7", width=200, height=100)
        top_module_frame.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        top_module_frame.pack_propagate(False)
        ctk.CTkLabel(top_module_frame, text="Môn đông SV nhất", font=("Helvetica", 12, "bold"), text_color="#311B92").pack(pady=(5, 0))
        self.top_module_label = ctk.CTkLabel(top_module_frame, text="N/A", font=("Helvetica", 24, "bold"), text_color="#311B92")
        self.top_module_label.pack(pady=(0, 5))
        ctk.CTkLabel(top_module_frame, text=" ", font=("Helvetica", 12, "bold"), text_color="#311B92").pack(pady=(0, 5))

        # Frame nội dung (biểu đồ và bảng)
        self.class_stats_frame = ctk.CTkScrollableFrame(self.class_stats_tab, fg_color="#FFFFFF", corner_radius=10)
        self.class_stats_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Cập nhật dữ liệu mặc định
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
        self.semester_filter = CTkComboBox(semester_filter_frame, values=["Tất cả"] + self.get_semesters(), width=150, command=self.filter_classes)
        self.semester_filter.pack(side="left")
        self.semester_filter.set("Tất cả")

        # Filter by Module
        module_filter_frame = CTkFrame(filter_frame, fg_color="transparent")
        module_filter_frame.pack(side="left", padx=(0, 10))
        CTkLabel(module_filter_frame, text="Học phần:", font=("Helvetica", 12), text_color="black").pack(side="left", padx=(0, 5))
        self.module_filter = CTkComboBox(module_filter_frame, values=["Tất cả"] + [module.split(":")[1].strip() for module in self.get_modules()], width=200, command=self.filter_classes)
        self.module_filter.pack(side="left")
        self.module_filter.set("Tất cả")

        # Filter by Assignment Status
        status_filter_frame = CTkFrame(filter_frame, fg_color="transparent")
        status_filter_frame.pack(side="left", padx=(0, 10))
        CTkLabel(status_filter_frame, text="Trạng thái:", font=("Helvetica", 12), text_color="black").pack(side="left", padx=(0, 5))
        self.status_filter = CTkComboBox(status_filter_frame, values=["Tất cả", "Đã phân công", "Chưa phân công"], width=150, command=self.filter_classes)
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
        CTkLabel(heading_frame, text="Giảng viên", font=("Helvetica", 14, "bold"), text_color="black", width=150, anchor="center").pack(side="left", padx=5)
        CTkLabel(heading_frame, text="Thao tác", font=("Helvetica", 14, "bold"), text_color="black", width=200, anchor="center").pack(side="left", padx=5)

        # List frame (dùng CTkScrollableFrame)
        self.class_list_frame = CTkScrollableFrame(self.class_container, fg_color="transparent")
        self.class_list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Load class data
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
            cursor.execute("SELECT module_id, module_name FROM course_modules ORDER BY module_id")
            modules = [f"{row[0]}: {row[1]}" for row in cursor.fetchall()]
            return modules
        except mysql.connector.Error:
            return []
        finally:
            cursor.close()
            conn.close()

    def filter_classes(self, event=None):
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
            cursor.execute("SELECT degree_id, degree_name, degree_abbr, coefficient FROM degrees")
            rows = cursor.fetchall()
            if not rows:
                CTkLabel(self.degree_list_frame, text="Không có dữ liệu bằng cấp", font=("Helvetica", 14), text_color="gray").pack(pady=20, expand=True)
            else:
                for row in rows:
                    degree_id, name, abbr, coeff = row
                    # Tạo frame cho từng dòng
                    degree_row_frame = CTkFrame(self.degree_list_frame, fg_color="#F0F0F0", corner_radius=5)
                    degree_row_frame.pack(fill="x", padx=0, pady=2)

                    # Thay idx bằng degree_id
                    CTkLabel(degree_row_frame, text=degree_id, font=("Helvetica", 12), text_color="black", width=80, anchor="center").pack(side="left", padx=5)
                    CTkLabel(degree_row_frame, text=name, font=("Helvetica", 12), text_color="black", width=400, anchor="center").pack(side="left", padx=5)
                    CTkLabel(degree_row_frame, text=abbr, font=("Helvetica", 12), text_color="black", width=200, anchor="center").pack(side="left", padx=5)
                    CTkLabel(degree_row_frame, text=str(coeff), font=("Helvetica", 12), text_color="black", width=150, anchor="center").pack(side="left", padx=5)

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
                SELECT t.teacher_id, t.full_name, t.date_of_birth, t.phone, t.email, d.dept_name, deg.degree_name, t.teacher_coefficient
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
                    teacher_id, name, dob, phone, email, dept_name, degree_name, coeff = row
                    # Tạo frame cho từng dòng
                    teacher_row_frame = CTkFrame(self.teacher_list_frame, fg_color="#F0F0F0", corner_radius=5)
                    teacher_row_frame.pack(fill="x", padx=0, pady=2)

                    # Căn chỉnh các cột với chiều rộng đồng bộ với heading
                    CTkLabel(teacher_row_frame, text=teacher_id, font=("Helvetica", 12), text_color="black", width=80, anchor="center").pack(side="left", padx=5)
                    CTkLabel(teacher_row_frame, text=name, font=("Helvetica", 12), text_color="black", width=120, anchor="center").pack(side="left", padx=5)
                    CTkLabel(teacher_row_frame, text=dob.strftime('%Y-%m-%d') if dob else "N/A", font=("Helvetica", 12), text_color="black", width=80, anchor="center").pack(side="left", padx=5)
                    CTkLabel(teacher_row_frame, text=phone if phone else "N/A", font=("Helvetica", 12), text_color="black", width=80, anchor="center").pack(side="left", padx=5)
                    CTkLabel(teacher_row_frame, text=email if email else "N/A", font=("Helvetica", 12), text_color="black", width=120, anchor="center").pack(side="left", padx=5)
                    CTkLabel(teacher_row_frame, text=dept_name, font=("Helvetica", 12), text_color="black", width=200, anchor="center").pack(side="left", padx=5)
                    CTkLabel(teacher_row_frame, text=degree_name, font=("Helvetica", 12), text_color="black", width=120, anchor="center").pack(side="left", padx=5)
                    CTkLabel(teacher_row_frame, text=str(coeff), font=("Helvetica", 12), text_color="black", width=60, anchor="center").pack(side="left", padx=5)

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
                    class_name = f"{dept_abbr}{module_id} - LT - {credits} - {full_year} ({group_str})"

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

            cursor.execute("SELECT module_id, module_name FROM course_modules")
            available_modules = {row[1]: row[0] for row in cursor.fetchall()}  # {module_name: module_id}

            query = """
                SELECT c.semester_id, m.module_name, c.class_id, c.class_name, c.num_students, t.full_name
                FROM classes c
                JOIN semesters s ON c.semester_id = s.semester_id
                JOIN course_modules m ON c.module_id = m.module_id
                LEFT JOIN assignments a ON c.class_id = a.class_id
                LEFT JOIN teachers t ON a.teacher_id = t.teacher_id
                WHERE 1=1
            """
            params = []

            if semester_filter != "Tất cả":
                if semester_filter in available_semesters:
                    query += " AND c.semester_id = %s"
                    params.append(semester_filter)
                else:
                    CTkLabel(self.class_list_frame, text="Không có dữ liệu lớp học", font=("Helvetica", 14), text_color="gray").pack(pady=10)
                    return

            if module_filter != "Tất cả":
                # Lọc theo module_name, cần lấy module_id tương ứng
                module_id = available_modules.get(module_filter)
                if module_id:
                    query += " AND c.module_id = %s"
                    params.append(module_id)
                else:
                    CTkLabel(self.class_list_frame, text="Không có dữ liệu lớp học", font=("Helvetica", 14), text_color="gray").pack(pady=10)
                    return

            if status_filter == "Đã phân công":
                query += " AND a.teacher_id IS NOT NULL"
            elif status_filter == "Chưa phân công":
                query += " AND a.teacher_id IS NULL"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            print(f"Debug: Số dòng dữ liệu lấy được: {len(rows)}")  # Debug để kiểm tra số lượng dữ liệu

            if not rows:
                CTkLabel(self.class_list_frame, text="Không có dữ liệu lớp học", font=("Helvetica", 14), text_color="gray").pack(pady=10)
                return

            # Create a row for each class
            for row in rows:
                semester_id, module_name, class_id, class_name, num_students, teacher_name = row

                # Row frame for each class
                row_frame = CTkFrame(self.class_list_frame, fg_color="#F5F5F5", corner_radius=0)
                row_frame.pack(fill="x", pady=2)

                # Data labels
                CTkLabel(row_frame, text=semester_id, font=("Helvetica", 12), text_color="black", width=100, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=module_name, font=("Helvetica", 12), text_color="black", width=200, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=class_id, font=("Helvetica", 12), text_color="black", width=100, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=class_name, font=("Helvetica", 12), text_color="black", width=150, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=str(num_students), font=("Helvetica", 12), text_color="black", width=100, anchor="center").pack(side="left", padx=5)
                CTkLabel(row_frame, text=teacher_name if teacher_name else "Chưa phân công", font=("Helvetica", 12), text_color="black", width=150, anchor="center").pack(side="left", padx=5)

                # Actions frame
                actions_frame = CTkFrame(row_frame, fg_color="transparent", width=200)
                actions_frame.pack(side="left", padx=5)

                # Assign button
                CTkButton(actions_frame, text="Phân công", width=50, fg_color="#00C4B4", hover_color="#009688", 
                        command=lambda c_id=class_id: self.assign_teacher(c_id)).pack(side="left", padx=2)

                # Edit Class button
                CTkButton(actions_frame, text="Sửa", width=50, fg_color="#FFC107", hover_color="#E0A800", 
                        command=lambda c_id=class_id: self.edit_class(c_id)).pack(side="left", padx=2)

                # Delete Class button
                CTkButton(actions_frame, text="Xóa", width=50, fg_color="#F44336", hover_color="#D32F2F", 
                        command=lambda c_id=class_id: self.delete_class(c_id)).pack(side="left", padx=2)

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu lớp học: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        # Làm mới giao diện
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
        data = self.get_class_stats_data()
        if not data:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu để xuất báo cáo!")
            return

        try:
            # Tạo danh sách cột dựa trên semesters thực tế
            semester_cols = {sem: f"Số lớp {sem}" for sem in data["semesters"]}
            rows = []
            for row in data["stats_data"]:
                row_dict = {"Học phần": row["Module"]}
                for sem, count in row["SemesterCounts"].items():
                    row_dict[semester_cols[sem]] = count
                row_dict.update({
                    "Tổng số lớp": row["TotalClasses"],
                    "Tổng sinh viên": row["TotalStudents"],
                    "Trung bình SV/lớp": row["AvgStudents"]
                })
                rows.append(row_dict)

            # Thêm hàng tổng cộng
            total_row = {"Học phần": "Tổng cộng"}
            for sem in data["semesters"]:
                total_row[semester_cols[sem]] = data["sem_counts"].get(sem, 0)
            total_row.update({
                "Tổng số lớp": data["total_classes"],
                "Tổng sinh viên": data["total_students"],
                "Trung bình SV/lớp": data["avg_students"]
            })
            rows.append(total_row)

            # Tạo DataFrame
            df = pd.DataFrame(rows)

            # Xuất file Excel
            year = self.stats_year_combobox.get().strip()
            output_file = f"Class_Stats_Report_{year}.xlsx"
            df.to_excel(output_file, index=False)
            messagebox.showinfo("Thành công", f"Báo cáo đã được xuất: {output_file}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu file Excel: {e}")


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
        if not data:
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

            # Lấy danh sách học kỳ
            cursor.execute("""
                SELECT semester_name, semester_id, year
                FROM semesters 
                WHERE year = %s
                ORDER BY semester_name
            """, (year,))
            semester_data = cursor.fetchall()
            semesters = [row[0] for row in semester_data]
            semester_ids = {row[0]: row[1] for row in semester_data}
            
            if not semesters:
                print(f"Debug: Không tìm thấy kỳ học nào cho năm {year}")
                return None

            # Kiểm tra dữ liệu trong classes - Sửa phần này
            semester_id_list = list(semester_ids.values())
            if semester_id_list:
                # Tạo câu query động dựa trên số lượng semester_id thực tế
                placeholders = ', '.join(['%s'] * len(semester_id_list))
                query = f"""
                    SELECT c.class_id, c.semester_id, c.module_id, c.num_students, cm.dept_id
                    FROM classes c
                    LEFT JOIN course_modules cm ON c.module_id = cm.module_id
                    WHERE c.semester_id IN ({placeholders})
                """
                cursor.execute(query, semester_id_list)
                class_data = cursor.fetchall()
            print(f"Debug: Số lớp trong classes: {len(class_data)}")
            print(f"Debug: Class data with dept_id: {[(row[0], row[1], row[2], row[3], row[4]) for row in class_data]}")

            # Kiểm tra dữ liệu trong course_modules
            cursor.execute("""
                SELECT module_id, dept_id, module_name
                FROM course_modules
            """)
            module_data = cursor.fetchall()
            print(f"Debug: Số module trong course_modules: {len(module_data)}")
            print(f"Debug: Module data: {module_data}")

            # Tổng số lớp, sinh viên, học phần (không lọc dept_id ban đầu)
            cursor.execute("""
                SELECT COUNT(DISTINCT c.class_id) as total_classes, 
                    COUNT(DISTINCT cm.module_id) as total_modules,
                    COALESCE(SUM(c.num_students), 0) as total_students
                FROM classes c
                JOIN semesters s ON c.semester_id = s.semester_id
                JOIN course_modules cm ON c.module_id = cm.module_id
                WHERE s.year = %s
            """, (year,))
            total_result = cursor.fetchone()
            total_classes = total_result[0] if total_result[0] else 0
            total_modules = total_result[1] if total_result[1] else 0
            total_students = total_result[2] if total_result[2] else 0

            if total_classes == 0:
                print(f"Debug: Không có lớp học nào cho năm {year}")
                return None

            # Số lớp theo kỳ (không lọc dept_id ban đầu)
            cursor.execute("""
                SELECT s.semester_name, COUNT(DISTINCT c.class_id)
                FROM classes c
                JOIN semesters s ON c.semester_id = s.semester_id
                JOIN course_modules cm ON c.module_id = cm.module_id
                WHERE s.year = %s
                GROUP BY s.semester_id, s.semester_name
                ORDER BY s.semester_name
            """, (year,))
            sem_data = cursor.fetchall()
            sem_counts = {row[0]: row[1] for row in sem_data}
            print(f"Debug: Kiểm tra lớp theo kỳ: {sem_data}")

            # Dữ liệu bảng pivot (không lọc dept_id ban đầu)
            cursor.execute("""
                SELECT cm.module_name, s.semester_name, COUNT(c.class_id) as class_count,
                    COALESCE(SUM(c.num_students), 0) as total_students
                FROM classes c
                LEFT JOIN semesters s ON c.semester_id = s.semester_id AND s.year = %s
                JOIN course_modules cm ON c.module_id = cm.module_id
                WHERE s.year = %s
                GROUP BY cm.module_id, cm.module_name, s.semester_id, s.semester_name
                ORDER BY cm.module_name, s.semester_name
            """, (year, year))
            pivot_data = cursor.fetchall()
            print(f"Debug: Số dòng pivot_data: {len(pivot_data)}")
            print(f"Debug: Pivot data: {[(row[0], row[1], row[2]) for row in pivot_data]}")

            # Lọc pivot_data theo dept_id của người dùng
            pivot_data_filtered = []
            for module_name, sem_name, class_count, students in pivot_data:
                cursor.execute("""
                    SELECT dept_id
                    FROM course_modules
                    WHERE module_name = %s
                """, (module_name,))
                dept = cursor.fetchone()
                if dept and dept[0] == self.user['dept_id']:
                    pivot_data_filtered.append((module_name, sem_name, class_count, students))
            print(f"Debug: Số dòng pivot_data sau khi lọc dept_id {self.user['dept_id']}: {len(pivot_data_filtered)}")
            print(f"Debug: Pivot data filtered: {[(row[0], row[1], row[2]) for row in pivot_data_filtered]}")

            # Xây dựng stats_data
            stats_data = {}
            for module_name, sem_name, class_count, students in pivot_data_filtered:
                if module_name not in stats_data:
                    stats_data[module_name] = {
                        "Module": module_name,
                        "TotalClasses": 0,
                        "TotalStudents": 0,
                        "SemesterCounts": {sem: 0 for sem in semesters}
                    }
                stats_data[module_name]["SemesterCounts"][sem_name] = class_count
                stats_data[module_name]["TotalClasses"] += class_count
                stats_data[module_name]["TotalStudents"] += students
            stats_data = [row for row in stats_data.values() if row["TotalClasses"] > 0]
            for row in stats_data:
                row["AvgStudents"] = round(row["TotalStudents"] / row["TotalClasses"], 2) if row["TotalClasses"] > 0 else 0

            # Môn đông SV nhất (lọc theo dept_id)
            cursor.execute("""
                SELECT cm.module_name, SUM(c.num_students) as total_students
                FROM classes c
                JOIN semesters s ON c.semester_id = s.semester_id
                JOIN course_modules cm ON c.module_id = cm.module_id
                WHERE s.year = %s AND cm.dept_id = %s
                GROUP BY cm.module_id, cm.module_name
                ORDER BY total_students DESC
                LIMIT 1
            """, (year, self.user['dept_id']))
            top_module_result = cursor.fetchone()
            top_module = top_module_result[0] if top_module_result else "N/A"

            # Top 5 học phần có nhiều SV nhất (lọc theo dept_id)
            cursor.execute("""
                SELECT cm.module_name, SUM(c.num_students) as total_students
                FROM classes c
                JOIN semesters s ON c.semester_id = s.semester_id
                JOIN course_modules cm ON c.module_id = cm.module_id
                WHERE s.year = %s AND cm.dept_id = %s
                GROUP BY cm.module_id, cm.module_name
                ORDER BY total_students DESC
                LIMIT 5
            """, (year, self.user['dept_id']))
            top_modules = [{"Module": row[0], "TotalStudents": row[1]} for row in cursor.fetchall()]

            print(f"Debug: Số kỳ học lấy được: {len(semesters)}")
            print(f"Debug: Số học phần: {len(stats_data)}")
            print(f"Debug: sem_counts: {sem_counts}")

            return {
                "total_classes": total_classes,
                "total_modules": total_modules,
                "total_students": total_students,
                "avg_students": round(total_students / total_classes, 2) if total_classes > 0 else 0,
                "top_module": top_module,
                "semesters": semesters,
                "sem_counts": sem_counts,
                "stats_data": stats_data,
                "top_modules": top_modules,
                "pivot_data": pivot_data  # Thêm pivot_data vào kết quả
            }

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu thống kê: {e}")
            return None
        finally:
            cursor.close()
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
        self.show_class_stats_all()

    def update_stat_labels(self, data):
        """Cập nhật các nhãn thống kê"""
        self.total_classes_label.configure(text=str(data["total_classes"]))
        self.total_modules_label.configure(text=f"{data['total_modules']} học phần")
        self.total_students_label.configure(text=str(data["total_students"]))
        self.avg_students_label.configure(text=f"TB {data['avg_students']} SV/lớp")
        self.sem1_classes_label.configure(text=str(data["sem1_count"]))
        self.sem1_percentage_label.configure(text=f"{data['sem1_percentage']}%")
        self.sem2_classes_label.configure(text=str(data["sem2_count"]))
        self.sem2_percentage_label.configure(text=f"{data['sem2_percentage']}%")


    def show_charts(self, data):
        chart_frame = ctk.CTkFrame(self.class_stats_frame, fg_color="white")
        chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Biểu đồ 1: Bar chart số lớp theo semester_name (sử dụng pivot_data)
        fig1, ax1 = plt.subplots(figsize=(5, 3))
        pivot_counts = {}
        for module_name, sem_name, class_count, _ in data["pivot_data"]:  # Sử dụng pivot_data gốc
            if sem_name not in pivot_counts:
                pivot_counts[sem_name] = 0
            pivot_counts[sem_name] += class_count
        x = np.arange(len(data["semesters"]))
        ax1.bar(x, [pivot_counts.get(sem, 0) for sem in data["semesters"]], color='#36A2EB')
        ax1.set_xlabel('Kỳ học')
        ax1.set_ylabel('Số lớp')
        ax1.set_xticks(x)
        ax1.set_xticklabels(data["semesters"], rotation=0, ha='right', fontsize=8)
        ax1.set_title(f'Số lớp theo kỳ học ({self.stats_year_combobox.get()})')
        plt.tight_layout()

        canvas1 = FigureCanvasTkAgg(fig1, master=chart_frame)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True, pady=5)

        # Biểu đồ 2: Top 5 học phần có nhiều SV nhất
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        top_modules = data["top_modules"]
        module_names = [row["Module"] for row in top_modules]
        total_students = [row["TotalStudents"] for row in top_modules]
        ax2.bar(module_names, total_students, color='#FF6384')
        ax2.set_xlabel('Học phần')
        ax2.set_ylabel('Tổng sinh viên')
        ax2.set_xticks(range(len(module_names)))
        ax2.set_xticklabels(module_names, rotation=0, ha='right', fontsize=8)
        ax2.set_title(f'Top 5 học phần nhiều SV nhất ({self.stats_year_combobox.get()})')
        plt.tight_layout()

        canvas2 = FigureCanvasTkAgg(fig2, master=chart_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True, pady=5)
            
    def update_summary_labels(self, data):
        """Cập nhật các nhãn thống kê"""
        self.total_classes_label.configure(text=str(data["total_classes"]) if data["total_classes"] is not None else "15")
        self.total_modules_label.configure(text=f"{data['total_modules']} học phần" if data["total_modules"] is not None else "4 học phần")
        self.total_students_label.configure(text=str(data["total_students"]) if data["total_students"] is not None else "640")
        self.avg_per_class_label.configure(text=str(data["avg_students"]) if data["avg_students"] is not None else "42.67")
        self.top_module_label.configure(text=data["top_module"] if data["top_module"] else "N/A")

    def clear_summary_labels(self):
        """Xóa hoặc đặt lại các nhãn thống kê về giá trị mặc định"""
        self.total_classes_label.configure(text="0")
        self.total_modules_label.configure(text="0 học phần")
        self.total_students_label.configure(text="0")
        self.avg_per_class_label.configure(text="0")
        self.top_module_label.configure(text="N/A")

    def show_table(self, data):
        table_frame = ctk.CTkFrame(self.class_stats_frame, fg_color="#FFFFFF", corner_radius=10)
        table_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Tạo tiêu đề động
        headers = ["Học phần"] + [f"Số lớp {sem}" for sem in data["semesters"]] + ["Tổng số lớp", "Tổng sinh viên", "Trung bình SV/lớp"]
        widths = [200] + [100] * len(data["semesters"]) + [100, 100, 100]
        heading_frame = ctk.CTkFrame(table_frame, fg_color="#D3D3D3", corner_radius=0)
        heading_frame.pack(fill="x", padx=5, pady=(5, 0))
        for header, width in zip(headers, widths):
            ctk.CTkLabel(heading_frame, text=header, font=("Helvetica", 14, "bold"), text_color="black", 
                        width=width, anchor="center").pack(side="left", padx=5)

        # Hiển thị dữ liệu từ pivot_data (tất cả dữ liệu trước khi lọc)
        pivot_dict = {}
        for module_name, sem_name, class_count, _ in data["pivot_data"]:  # Sử dụng pivot_data gốc
            if module_name not in pivot_dict:
                pivot_dict[module_name] = {sem: 0 for sem in data["semesters"]}
            pivot_dict[module_name][sem_name] = class_count

        for module_name, counts in pivot_dict.items():
            row_frame = ctk.CTkFrame(table_frame, fg_color="#F5F5F5", corner_radius=0)
            row_frame.pack(fill="x", pady=2)
            values = [module_name] + [counts.get(sem, 0) for sem in data["semesters"]] + \
                    [sum(counts.values()), sum(counts.get(sem, 0) * 40 for sem in data["semesters"] if counts.get(sem, 0)),  # Giả định 40 SV/lớp
                    round(sum(counts.get(sem, 0) * 40 for sem in data["semesters"] if counts.get(sem, 0)) / sum(counts.values()) if sum(counts.values()) > 0 else 0, 2)]
            for value, width in zip(values, widths):
                ctk.CTkLabel(row_frame, text=str(value), font=("Helvetica", 12), text_color="black", 
                            width=width, anchor="center").pack(side="left", padx=5)

        # Hàng tổng
        total_frame = ctk.CTkFrame(table_frame, fg_color="#E0E0E0", corner_radius=0)
        total_frame.pack(fill="x", pady=2)
        total_values = ["Tổng cộng"] + [data["sem_counts"].get(sem, 0) for sem in data["semesters"]] + \
                    [data["total_classes"], data["total_students"], data["avg_students"]]
        for value, width in zip(total_values, widths):
            ctk.CTkLabel(total_frame, text=str(value), font=("Helvetica", 12, "bold"), text_color="black", 
                        width=width, anchor="center").pack(side="left", padx=5)

    
            
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