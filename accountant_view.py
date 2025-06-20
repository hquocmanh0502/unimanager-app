
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
from report_tab import ReportTab

class AccountantView:
    def __init__(self, window, user):
        self.window = window
        self.user = user
        self.accountant_id = user['user_id']
        self.window.title("Giao diện Kế toán")
        self.window.geometry("1700x700")

        # Khởi tạo accountant_id nếu là tài khoản kế toán
        if self.user['role'] == 'Accountant':
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (self.user['user_id'],))
                result = cursor.fetchone()
                if result:
                    self.user['accountant_id'] = result[0]
                    cursor.execute("SELECT dept_id FROM departments LIMIT 1")
                    dept_result = cursor.fetchone()
                    if dept_result:
                        self.user['dept_id'] = dept_result[0]
                else:
                    messagebox.showerror("Lỗi", "Không tìm thấy tài khoản kế toán tương ứng")
                    self.window.destroy()
                    return
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Không thể tải thông tin tài khoản: {e}")
                self.window.destroy()
                return
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

        # Frame chính
        self.main_frame = CTkFrame(self.window)
        self.main_frame.pack(fill="both", expand=True)

        # Định nghĩa menu_items cho navbar
        self.navbar_menu_items = [
            {
                "label": "Định mức tiền theo tiết",
                "icon": "💸",
                "fg_color": "#3E54AC",
                "hover_color": "#4B67D6",
                "text_color": "white",
                "command": lambda: self.switch_tab("Định mức tiền theo tiết")
            },
            {
                "label": "Hệ số giáo viên",
                "icon": "👨",
                "fg_color": "#3E54AC",
                "hover_color": "#4B67D6",
                "text_color": "white",
                "command": lambda: self.switch_tab("Hệ số giáo viên")
            },
            {
                "label": "Hệ số lớp",
                "icon": "📚",
                "fg_color": "#3E54AC",
                "hover_color": "#4B67D6",
                "text_color": "white",
                "command": lambda: self.switch_tab("Hệ số lớp")
            },
            {
                "label": "Tính tiền dạy",
                "icon": "💰",
                "fg_color": "#3E54AC",
                "hover_color": "#4B67D6",
                "text_color": "white",
                "command": lambda: self.switch_tab("Tính tiền dạy")
            },
            {
                "label": "Báo cáo",
                "icon": "📈",
                "fg_color": "#3E54AC",
                "hover_color": "#4B67D6",
                "text_color": "white",
                "command": lambda: self.switch_tab("Báo cáo")
            }
        ]

        # Tạo navbar với menu_items và logout_callback
        self.navbar = ModernNavbar(self.main_frame, fg_color="#2B3467", menu_items=self.navbar_menu_items, logout_callback=self.logout, user=self.user)
        self.navbar.pack(side="left", fill="y")

        # Cập nhật thông tin người dùng trong footer của navbar
        self.navbar.footer.winfo_children()[1].winfo_children()[0].configure(text=self.user['username'])
        self.navbar.footer.winfo_children()[1].winfo_children()[1].configure(text="Kế toán")

        # Frame chính bên phải chứa nội dung
        self.content_frame = CTkFrame(self.main_frame, fg_color=("#E6F0FA", "#B0C4DE"))
        self.content_frame.pack(side="right", fill="both", expand=True)

        # Frame chứa các tab
        self.tab_frame = CTkFrame(self.content_frame, fg_color="transparent")
        self.tab_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Khởi tạo các tab
        self.teaching_rate_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.teacher_coefficient_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.class_coefficient_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.salary_calc_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)
        self.report_tab = CTkFrame(self.tab_frame, fg_color="#FFFFFF", corner_radius=10)

        # Gọi các hàm setup cho các tab
        self.setup_teaching_rate_tab()
        self.setup_teacher_coefficient_tab()
        self.setup_class_coefficient_tab()
        self.setup_salary_calc_tab()
        self.setup_report_tab()

        # Hiển thị tab mặc định
        self.current_tab = self.teaching_rate_tab
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

    def switch_tab(self, tab_name):
        if self.current_tab:
            self.current_tab.pack_forget()
        if tab_name == "Định mức tiền theo tiết":
            self.current_tab = self.teaching_rate_tab
            print("Debug: Switched to teaching_rate_tab")
        elif tab_name == "Hệ số giáo viên":
            self.current_tab = self.teacher_coefficient_tab
            print("Debug: Switched to teacher_coefficient_tab")
        elif tab_name == "Hệ số lớp":
            self.current_tab = self.class_coefficient_tab
            print("Debug: Switched to class_coefficient_tab")
        elif tab_name == "Tính tiền dạy":
            self.current_tab = self.salary_calc_tab
            print("Debug: Switched to salary_calc_tab")
        elif tab_name == "Báo cáo":
            self.current_tab = self.report_tab
            print("Debug: Switched to report_tab")
        self.current_tab.pack(fill="both", expand=True)
        print(f"Debug: Current tab packed: {self.current_tab}")

    def logout(self):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn đăng xuất?"):
            self.window.destroy()
            import os
            os.system("python login_view.py")

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

    def setup_salary_calc_tab(self):
        print("Debug: Entering setup_salary_calc_tab")
        self.salary_calc_tab.configure(fg_color="#FFFFFF")
        main_frame = CTkFrame(self.salary_calc_tab, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.salary_calc_tab.grid_rowconfigure(0, weight=1)
        self.salary_calc_tab.grid_columnconfigure(0, weight=1)

        # Header
        header_frame = CTkFrame(main_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        CTkLabel(header_frame, text="Tính tiền dạy", font=("Helvetica", 18, "bold"), text_color="black").grid(row=0, column=0, sticky="w")

        # Filter frame
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

        # Content frame
        content_frame = CTkFrame(main_frame, fg_color="transparent")
        content_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Frame thông tin giáo viên
        teacher_info_frame = CTkFrame(content_frame, fg_color="#cce7ff", corner_radius=10, height=250)
        teacher_info_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        teacher_info_frame.grid_propagate(False)
        content_frame.grid_columnconfigure(0, weight=1, uniform="group1")
        content_frame.grid_rowconfigure(0, weight=0)

        CTkLabel(teacher_info_frame, text="THÔNG TIN GIẢNG VIÊN", 
                font=("Helvetica", 16, "bold"), text_color="#0D47A1").grid(row=0, column=0, 
                columnspan=2, padx=20, pady=(15,10), sticky="w")

        CTkLabel(teacher_info_frame, text="Họ và tên:", font=("Helvetica", 14)).grid(row=1, column=0, padx=20, pady=5, sticky="w")
        self.salary_calc_teacher_name_value = CTkLabel(teacher_info_frame, text="", font=("Helvetica", 14), wraplength=200)
        self.salary_calc_teacher_name_value.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        print(f"Debug: Initialized salary_calc_teacher_name_value={self.salary_calc_teacher_name_value}")

        CTkLabel(teacher_info_frame, text="Mã giảng viên:", font=("Helvetica", 14)).grid(row=2, column=0, padx=20, pady=5, sticky="w")
        self.salary_calc_teacher_id_value = CTkLabel(teacher_info_frame, text="", font=("Helvetica", 14), wraplength=200)
        self.salary_calc_teacher_id_value.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        print(f"Debug: Initialized salary_calc_teacher_id_value={self.salary_calc_teacher_id_value}")

        CTkLabel(teacher_info_frame, text="Học vị:", font=("Helvetica", 14)).grid(row=3, column=0, padx=20, pady=5, sticky="w")
        self.salary_calc_degree_value = CTkLabel(teacher_info_frame, text="", font=("Helvetica", 14), wraplength=200)
        self.salary_calc_degree_value.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        print(f"Debug: Initialized salary_calc_degree_value={self.salary_calc_degree_value}")

        CTkLabel(teacher_info_frame, text="Khoa/Bộ môn:", font=("Helvetica", 14)).grid(row=4, column=0, padx=20, pady=5, sticky="w")
        self.salary_calc_dept_value = CTkLabel(teacher_info_frame, text="", font=("Helvetica", 14), wraplength=200)
        self.salary_calc_dept_value.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        print(f"Debug: Initialized salary_calc_dept_value={self.salary_calc_dept_value}")

        # Frame thông tin thanh toán
        calc_info_frame = CTkFrame(content_frame, fg_color="#cce7ff", corner_radius=10, height=250)
        calc_info_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        calc_info_frame.grid_propagate(False)
        content_frame.grid_columnconfigure(1, weight=1, uniform="group1")

        CTkLabel(calc_info_frame, text="THÔNG TIN THANH TOÁN", 
                font=("Helvetica", 16, "bold"), text_color="#0D47A1").grid(row=0, column=0, 
                columnspan=2, padx=20, pady=(15,10), sticky="w")

        CTkLabel(calc_info_frame, text="Hệ số giáo viên:", font=("Helvetica", 14)).grid(row=1, column=0, padx=20, pady=5, sticky="w")
        self.salary_calc_teacher_coeff_value = CTkLabel(calc_info_frame, text="", font=("Helvetica", 14), wraplength=200)
        self.salary_calc_teacher_coeff_value.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        print(f"Debug: Initialized salary_calc_teacher_coeff_value={self.salary_calc_teacher_coeff_value}")

        CTkLabel(calc_info_frame, text="Tiền dạy một tiết:", font=("Helvetica", 14)).grid(row=2, column=0, padx=20, pady=5, sticky="w")
        self.salary_calc_rate_value = CTkLabel(calc_info_frame, text="", font=("Helvetica", 14), wraplength=200)
        self.salary_calc_rate_value.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        print(f"Debug: Initialized salary_calc_rate_value={self.salary_calc_rate_value}")

        CTkLabel(calc_info_frame, text="Kỳ/Năm học:", font=("Helvetica", 14)).grid(row=3, column=0, padx=20, pady=5, sticky="w")
        self.salary_calc_period_value = CTkLabel(calc_info_frame, text="", font=("Helvetica", 14), wraplength=200)
        self.salary_calc_period_value.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        print(f"Debug: Initialized salary_calc_period_value={self.salary_calc_period_value}")

        # Frame cho bảng tính lương
        self.salary_table_frame = CTkScrollableFrame(main_frame, fg_color="#FFFFFF", corner_radius=10, height=400)
        self.salary_table_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        main_frame.grid_rowconfigure(3, weight=2)

        self.save_button = None
        print("Debug: Exiting setup_salary_calc_tab")

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
    # Switch to the "Tính tiền dạy" tab and ensure it is fully rendered
        self.switch_tab("Tính tiền dạy")
        self.window.update_idletasks()  # Force GUI to render all widgets

        # Proceed with fetching and updating data
        year = self.year_filter.get().strip()
        semester = self.semester_filter.get().strip()
        teacher_str = self.teacher_filter.get().strip()

        # Input validation
        if not teacher_str or teacher_str == "Chọn giảng viên":
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn giảng viên!")
            return
        if year == "Chọn năm học" or semester == "Chọn kỳ học":
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn năm học và kỳ học!")
            return

        try:
            # Database connection
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Extract teacher_id
            teacher_parts = teacher_str.split(" - ")
            if len(teacher_parts) < 2:
                messagebox.showerror("Lỗi", "Định dạng giảng viên không hợp lệ!")
                return
            teacher_id = teacher_parts[1].strip()

            # Fetch teacher information
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

            # Fetch teacher coefficient
            cursor.execute("""
                SELECT coefficient 
                FROM teacher_coefficients tc 
                JOIN teachers t ON tc.degree_id = t.degree_id 
                WHERE t.teacher_id = %s AND tc.year = %s
            """, (teacher_id, year))
            teacher_coeff = cursor.fetchone()
            teacher_coefficient = float(teacher_coeff[0]) if teacher_coeff else 1.0

            # Fetch teaching rate
            cursor.execute("SELECT amount_per_period FROM teaching_rate WHERE year = %s", (year,))
            rate = cursor.fetchone()
            amount_per_period = float(rate[0]) if rate else 0.0

            # Fetch semester_id
            cursor.execute("SELECT semester_id FROM semesters WHERE year = %s AND semester_name = %s", (year, semester))
            semester_id = cursor.fetchone()
            if not semester_id:
                messagebox.showerror("Lỗi", "Không tìm thấy kỳ học!")
                return
            semester_id = semester_id[0]

            # Debug information
            print(f"Debug: full_name={full_name}, teacher_id={teacher_id_db}, degree_name={degree_name}, dept_name={dept_name}")
            print(f"Debug: teacher_coefficient={teacher_coefficient}, amount_per_period={amount_per_period}, period={semester} - {year}")

            # Update widgets
            widgets = [
                ('salary_calc_teacher_name_value', full_name or "Không xác định"),
                ('salary_calc_teacher_id_value', teacher_id_db or "Không xác định"),
                ('salary_calc_degree_value', degree_name or "Không xác định"),
                ('salary_calc_dept_value', dept_name or "Không xác định"),
                ('salary_calc_teacher_coeff_value', f"{teacher_coefficient:.1f}"),
                ('salary_calc_rate_value', f"{amount_per_period:,.0f} ₫"),
                ('salary_calc_period_value', f"{semester} - {year}")
            ]

            for attr, value in widgets:
                if hasattr(self, attr) and getattr(self, attr) is not None and getattr(self, attr).winfo_exists():
                    getattr(self, attr).configure(text=value)
                    print(f"Debug: Updated {attr} with value={value}")
                else:
                    print(f"Debug: {attr} không hợp lệ")

            # Load salary table (additional logic omitted for brevity)
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
            
            # Truy vấn lấy enrolled_students từ bảng class_enrollments
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

            # Xóa dữ liệu cũ
            for widget in self.salary_table_frame.winfo_children():
                widget.destroy()

            total_periods = 0
            total_salary = 0.0

            # Tăng kích thước font và chiều cao cho heading
            heading_frame = CTkFrame(self.salary_table_frame, fg_color="#D3D3D3", corner_radius=0, height=50)
            heading_frame.pack(fill="x", padx=5, pady=(5, 0))
            heading_frame.pack_propagate(False)

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

            # Kiểm tra teacher_coefficient
            if (hasattr(self, 'salary_calc_teacher_coeff_value') and 
                self.salary_calc_teacher_coeff_value is not None and 
                self.salary_calc_teacher_coeff_value.winfo_exists()):
                try:
                    teacher_coefficient = float(self.salary_calc_teacher_coeff_value.cget("text"))
                except ValueError:
                    teacher_coefficient = 1.0  # Giá trị mặc định nếu text không hợp lệ
            else:
                teacher_coefficient = 1.0  # Giá trị mặc định nếu widget không tồn tại

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
                row_frame.pack_propagate(False)

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

    def setup_report_tab(self):
        from report_tab import ReportTab
        self.report_tab_content = ReportTab(self.report_tab)
        self.report_tab_content.pack(fill="both", expand=True)

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
    def get_academic_years_with_semesters(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT year FROM semesters ORDER BY year DESC")
            years = [row[0] for row in cursor.fetchall()]
            return years
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách năm học: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def get_dept_names(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT dept_name FROM departments ORDER BY dept_name")
            depts = [row[0] for row in cursor.fetchall()]
            return depts
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách khoa: {e}")
            return []
        finally:
            cursor.close()
            conn.close()