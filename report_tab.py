import customtkinter as ctk
from tkinter import messagebox
import mysql.connector
from db_config import DB_CONFIG
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np

class ReportTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill="both", expand=True, padx=10, pady=10)
        self.year = "2024-2025"
        self.breadcrumb_labels = []
        
        # Set modern theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Main frame with modern styling
        self.main_frame = ctk.CTkFrame(self, fg_color="#F5F7FA", corner_radius=12)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header with modern design
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=60)
        self.header_frame.pack(fill="x", pady=(0, 10))
        
        # Title with icon
        self.title_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(self.title_frame, text="📊", font=("Arial", 24)).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(self.title_frame, text="Báo cáo tiền dạy", 
                    font=("Helvetica", 20, "bold"), text_color="#2B3467").pack(side="left")
        
        # Year combobox with modern styling
        self.control_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.control_frame.pack(side="right", padx=10)
        
        years = [f"{y}-{y+1}" for y in range(2020, 2030)]
        self.year_combobox_report = ctk.CTkComboBox(
            self.control_frame, 
            values=years, 
            width=150, 
            command=self.update_report_data,
            dropdown_fg_color="#FFFFFF",
            button_color="#4B89DC",
            border_color="#4B89DC"
        )
        self.year_combobox_report.pack(side="right", padx=5)
        self.year_combobox_report.set(self.year)
        
        # Breadcrumb frame (moved below heading)
        self.breadcrumb_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.breadcrumb_frame.pack(fill="x", pady=(0, 10))
        self.update_breadcrumb(["Toàn trường"])
        
        # Content frame with card-like design
        self.report_content_frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color="#FFFFFF", 
            corner_radius=12,
            border_width=1,
            border_color="#E0E0E0"
        )
        self.report_content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initial update
        self.update_report_data()

    def update_breadcrumb(self, parts):
        for label in self.breadcrumb_labels:
            label.destroy()
        self.breadcrumb_labels = []
        
        # Add home icon
        home_icon = ctk.CTkLabel(
            self.breadcrumb_frame, 
            text="🏠", 
            text_color="#4B89DC",
            cursor="hand2",
            font=("Arial", 18)
        )
        home_icon.pack(side="left", padx=(0, 8))
        home_icon.bind("<Button-1>", lambda e: self.breadcrumb_click("Toàn trường", 0))
        self.breadcrumb_labels.append(home_icon)
        
        for i, part in enumerate(parts):
            if i == 0 and part == "Toàn trường":
                continue
                
            sep = ctk.CTkLabel(
                self.breadcrumb_frame, 
                text="›", 
                text_color="#7F7F7F",
                font=("Arial", 18)
            )
            sep.pack(side="left", padx=4)
            self.breadcrumb_labels.append(sep)
            
            label = ctk.CTkLabel(
                self.breadcrumb_frame, 
                text=part, 
                text_color="#4B89DC",
                cursor="hand2",
                font=("Helvetica", 14, "bold")
            )
            label.pack(side="left", padx=4)
            label.bind("<Button-1>", lambda e, p=part, idx=i: self.breadcrumb_click(p, idx))
            self.breadcrumb_labels.append(label)

    def breadcrumb_click(self, part, idx):
        current_parts = ["Toàn trường"]
        if idx == 0:  # Bấm vào "Toàn trường"
            self.update_breadcrumb(["Toàn trường"])
            self.update_report_data()
        elif idx == 1:  # Bấm vào khoa (ví dụ: "Khoa Công nghệ Thông tin")
            current_parts.append(part)  # Giữ khoa
            self.update_breadcrumb(current_parts)
            # Gọi show_teacher_report trực tiếp
            for widget in self.report_content_frame.winfo_children():
                widget.destroy()
            title_frame = ctk.CTkFrame(self.report_content_frame, fg_color="transparent")
            title_frame.pack(fill="x", pady=(0, 20))
            ctk.CTkLabel(title_frame, text=f"BÁO CÁO TIỀN DẠY KHOA {part.upper()}", 
                        font=("Helvetica", 20, "bold"), text_color="#2B3467").pack(side="left")
            ctk.CTkLabel(title_frame, text=f"Năm học: {self.year}", 
                        font=("Helvetica", 14), text_color="#666666").pack(side="right")
            self.show_teacher_report(self.year, part)
        elif idx == 2:  # Bấm vào giáo viên
            current_parts.extend([self.breadcrumb_labels[3].cget("text"), part])  # Giữ khoa và thêm giáo viên
            self.update_breadcrumb(current_parts)
            self.update_report_data()

    def update_report_data(self, event=None):
        self.year = self.year_combobox_report.get()
        breadcrumb_parts = [label.cget("text") for label in self.breadcrumb_labels 
                        if label.cget("text") not in ["🏠", "›"]]
        
        for widget in self.report_content_frame.winfo_children():
            widget.destroy()
            
        self.update_breadcrumb(["Toàn trường"])  # Đặt breadcrumb về "Toàn trường"
        title_frame = ctk.CTkFrame(self.report_content_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(title_frame, text="BÁO CÁO TIỀN DẠY THEO KHOA", 
                    font=("Helvetica", 20, "bold"), text_color="#2B3467").pack(side="left")
        ctk.CTkLabel(title_frame, text=f"Năm học: {self.year}", 
                    font=("Helvetica", 14), text_color="#666666").pack(side="right")
        self.show_dept_report(self.year)

    def show_dept_report(self, year):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT semester_id FROM semesters WHERE year = %s", (year,))
            semesters = cursor.fetchall()
            print(f"Debug - Semesters for year {year}: {semesters}")

            cursor.execute("""
                SELECT d.dept_name, 
                    COUNT(DISTINCT t.teacher_id) as teacher_count, 
                    COUNT(c.class_id) as class_count,
                    COALESCE(SUM(cm.periods * (cm.coefficient + COALESCE(cc.coefficient, 0))), 0) as total_converted_periods,
                    COALESCE(SUM(cm.periods * (cm.coefficient + COALESCE(cc.coefficient, 0)) * COALESCE(tc.coefficient, 1) * COALESCE(tr.amount_per_period, 0)), 0) as total_salary
                FROM departments d
                LEFT JOIN teachers t ON d.dept_id = t.dept_id
                LEFT JOIN assignments a ON t.teacher_id = a.teacher_id
                LEFT JOIN classes c ON a.class_id = c.class_id
                LEFT JOIN course_modules cm ON c.module_id = cm.module_id
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
                WHERE c.semester_id IN (SELECT semester_id FROM semesters WHERE year = %s)
                GROUP BY d.dept_name
                ORDER BY d.dept_name
            """, (year, year, year, year))
            depts = cursor.fetchall()
            print(f"Debug - depts for year {year}: {depts}")

            if not depts:
                ctk.CTkLabel(self.report_content_frame, text=f"Không có dữ liệu cho năm {year}",
                            font=("Helvetica", 14), text_color="red").pack(expand=True)
                return

            total_salary = sum(float(d[4] or 0) for d in depts)
            print(f"Debug - total_salary for year {year}: {total_salary}")

            if total_salary == 0:
                ctk.CTkLabel(self.report_content_frame, text=f"Cảnh báo: Tổng tiền = 0 cho năm {year}",
                            font=("Helvetica", 14), text_color="orange").pack(expand=True)

            # Summary cards
            summary_frame = ctk.CTkFrame(self.report_content_frame, fg_color="transparent")
            summary_frame.pack(fill="x", pady=(0, 20))
            
            stats = {
                "Tổng số khoa": len(depts),
                "Tổng số giáo viên": sum(d[1] or 0 for d in depts),
                "Tổng số lớp": sum(d[2] or 0 for d in depts),
                "Tổng tiền": total_salary
            }

            for i, (label, value) in enumerate(stats.items()):
                card = ctk.CTkFrame(summary_frame, fg_color="#4B89DC", corner_radius=10)
                card.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
                
                if label == "Tổng tiền":
                    value_text = f"{int(value):,} đ"
                else:
                    value_text = str(value)
                    
                ctk.CTkLabel(card, text=value_text, 
                            font=("Helvetica", 16, "bold"),
                            text_color="white").pack(pady=(5,0))
                ctk.CTkLabel(card, text=label,
                            font=("Helvetica", 12),
                            text_color="white").pack(pady=(0,5))

            summary_frame.grid_columnconfigure((0,1,2,3), weight=1)

            # Table and chart container
            content_frame = ctk.CTkFrame(self.report_content_frame, fg_color="transparent")
            content_frame.pack(fill="both", expand=True)
            content_frame.grid_columnconfigure(0, weight=7)  # 70% for table
            content_frame.grid_columnconfigure(1, weight=3)  # 30% for chart

            # Table frame
            table_frame = ctk.CTkScrollableFrame(content_frame, fg_color="transparent")
            table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

            # Table header
            header_frame = ctk.CTkFrame(table_frame, fg_color="#2B3467")
            header_frame.pack(fill="x", pady=(0, 5))
            
            headers = ["STT", "KHOA", "SỐ GIÁO VIÊN", "SỐ LỚP", "TIẾT QĐ", "TỔNG TIỀN"]
            col_widths = [50, 200, 70, 70, 70, 100]
            for col, (header, width) in enumerate(zip(headers, col_widths)):
                ctk.CTkLabel(header_frame, text=header, width=width, anchor="center",
                            font=("Helvetica", 11, "bold"), text_color="white").grid(row=0, column=col, padx=5, pady=5)

            # Table rows
            for idx, (dept_name, teacher_count, class_count, converted_periods, salary) in enumerate(depts, 1):
                row = ctk.CTkFrame(table_frame, fg_color="#FFFFFF" if idx % 2 == 0 else "#F0F0F0")
                row.pack(fill="x", pady=1)
                
                ctk.CTkLabel(row, text=str(idx), width=50, anchor="center").grid(row=0, column=0, padx=5, pady=2)
                
                dept_label = ctk.CTkLabel(row, text=dept_name, width=200, anchor="w",
                                        cursor="hand2", text_color="#2B3467")
                dept_label.grid(row=0, column=1, padx=5, pady=2)
                dept_label.bind("<Button-1>", lambda e, d=dept_name: self.handle_dept_click(d))
                
                ctk.CTkLabel(row, text=str(teacher_count), width=70, anchor="center").grid(row=0, column=2, padx=5, pady=2)
                ctk.CTkLabel(row, text=str(class_count), width=70, anchor="center").grid(row=0, column=3, padx=5, pady=2)
                ctk.CTkLabel(row, text=str(int(float(converted_periods)) if converted_periods is not None else 0), 
                            width=70, anchor="center").grid(row=0, column=4, padx=5, pady=2)
                ctk.CTkLabel(row, text=f"{int(float(salary)) if salary is not None else 0:,} đ", 
                            width=100, anchor="center").grid(row=0, column=5, padx=5, pady=2)

            # Total row
            total_frame = ctk.CTkFrame(table_frame, fg_color="#E3F2FD")
            total_frame.pack(fill="x", pady=(5, 0))
            ctk.CTkLabel(total_frame, text="TỔNG CỘNG:", width=50, anchor="center", font=("Helvetica", 11, "bold"), 
                        text_color="#2B3467").grid(row=0, column=0, padx=5, pady=2)
            ctk.CTkLabel(total_frame, text="", width=180).grid(row=0, column=1, padx=5, pady=2)
            ctk.CTkLabel(total_frame, text=str(sum(d[1] or 0 for d in depts)), width=70, anchor="center", 
                        font=("Helvetica", 11, "bold"), text_color="#2B3467").grid(row=0, column=2, padx=5, pady=2)
            ctk.CTkLabel(total_frame, text=str(sum(d[2] or 0 for d in depts)), width=70, anchor="center", 
                        font=("Helvetica", 11, "bold"), text_color="#2B3467").grid(row=0, column=3, padx=5, pady=2)
            ctk.CTkLabel(total_frame, text=str(int(sum(float(d[3] or 0) for d in depts))), width=70, anchor="center", 
                        font=("Helvetica", 11, "bold"), text_color="#2B3467").grid(row=0, column=4, padx=5, pady=2)
            ctk.CTkLabel(total_frame, text=f"{int(sum(float(d[4] or 0) for d in depts)):,} đ", width=100, anchor="center", 
                        font=("Helvetica", 11, "bold"), text_color="#2B3467").grid(row=0, column=5, padx=5, pady=2)

            # Chart frame
            chart_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            chart_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

            dept_names = [d[0] for d in depts]
            salaries = [float(d[4] or 0) for d in depts]

            if sum(salaries) > 0:
                fig, ax = plt.subplots(figsize=(4, 3))
                ax.barh(dept_names, salaries, color="#4B89DC")
                ax.set_title("Tiền dạy theo khoa")
                ax.set_xlabel("Số tiền (đ)")
                plt.tight_layout()
                canvas = FigureCanvasTkAgg(fig, master=chart_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)
            else:
                ctk.CTkLabel(chart_frame, text="Không có dữ liệu để vẽ biểu đồ", font=("Helvetica", 14)).pack(expand=True, fill="both")

            # Export button
            export_btn = ctk.CTkButton(self.report_content_frame,
                                    text="Xuất Excel",
                                    command=lambda: self.export_dept_report(year),
                                    fg_color="#28A745",
                                    hover_color="#218838")
            export_btn.pack(side="bottom", pady=10)

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def show_teacher_report(self, year, dept):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT semester_id FROM semesters WHERE year = %s", (year,))
            semesters = cursor.fetchall()
            print(f"Debug - Semesters for year {year}: {semesters}")

            cursor.execute("""
                SELECT t.full_name, d.degree_name, COUNT(c.class_id) as class_count,
                    COALESCE(SUM(cm.periods * (cm.coefficient + COALESCE(cc.coefficient, 0))), 0) as total_converted_periods,
                    COALESCE(SUM(cm.periods * (cm.coefficient + COALESCE(cc.coefficient, 0)) * COALESCE(tc.coefficient, 1) * COALESCE(tr.amount_per_period, 0)), 0) as total_salary
                FROM teachers t
                JOIN degrees d ON t.degree_id = d.degree_id
                JOIN departments dept ON t.dept_id = dept.dept_id
                LEFT JOIN assignments a ON t.teacher_id = a.teacher_id
                LEFT JOIN classes c ON a.class_id = c.class_id
                LEFT JOIN course_modules cm ON c.module_id = cm.module_id
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
                WHERE dept.dept_name = %s AND c.semester_id IN (SELECT semester_id FROM semesters WHERE year = %s)
                GROUP BY t.teacher_id, t.full_name, d.degree_name
                ORDER BY t.full_name
            """, (year, year, year, dept, year))
            teachers = cursor.fetchall()
            print(f"Debug - teachers for year {year} and dept {dept}: {teachers}")

            if not teachers:
                ctk.CTkLabel(self.report_content_frame, text=f"Không có dữ liệu cho khoa {dept} trong năm {year}",
                            font=("Helvetica", 14), text_color="red").pack(expand=True)
                return

            total_salary = sum(float(t[4] or 0) for t in teachers)
            print(f"Debug - total_salary for year {year} and dept {dept}: {total_salary}")

            if total_salary == 0:
                ctk.CTkLabel(self.report_content_frame, text=f"Cảnh báo: Tổng tiền = 0 cho khoa {dept} trong năm {year}",
                            font=("Helvetica", 14), text_color="orange").pack(expand=True)

            # Summary cards
            summary_frame = ctk.CTkFrame(self.report_content_frame, fg_color="transparent")
            summary_frame.pack(fill="x", pady=(0, 20))
            
            stats = {
                "Tổng số giáo viên": len(teachers),
                "Tổng số lớp": sum(t[2] or 0 for t in teachers),
                "Tổng tiết quy đổi": sum(float(t[3] or 0) for t in teachers),
                "Tổng tiền": total_salary
            }

            for i, (label, value) in enumerate(stats.items()):
                card = ctk.CTkFrame(summary_frame, fg_color="#4B89DC", corner_radius=10)
                card.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
                
                if label == "Tổng tiền":
                    value_text = f"{int(value):,} đ"
                else:
                    value_text = str(int(value))
                    
                ctk.CTkLabel(card, text=value_text, 
                            font=("Helvetica", 16, "bold"),
                            text_color="white").pack(pady=(5,0))
                ctk.CTkLabel(card, text=label,
                            font=("Helvetica", 12),
                            text_color="white").pack(pady=(0,5))

            summary_frame.grid_columnconfigure((0,1,2,3), weight=1)

            # Table and chart container
            content_frame = ctk.CTkFrame(self.report_content_frame, fg_color="transparent")
            content_frame.pack(fill="both", expand=True)
            content_frame.grid_columnconfigure(0, weight=7)  # 70% for table
            content_frame.grid_columnconfigure(1, weight=3)  # 30% for chart

            # Table frame
            table_frame = ctk.CTkScrollableFrame(content_frame, fg_color="transparent")
            table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

            # Table header
            header_frame = ctk.CTkFrame(table_frame, fg_color="#2B3467")
            header_frame.pack(fill="x", pady=(0, 5))
            
            headers = ["STT", "GIÁO VIÊN", "HỌC VỊ", "SỐ LỚP", "TIẾT QĐ", "TỔNG TIỀN"]
            col_widths = [50, 200, 70, 70, 70, 100]
            for col, (header, width) in enumerate(zip(headers, col_widths)):
                ctk.CTkLabel(header_frame, text=header, width=width, anchor="center",
                            font=("Helvetica", 11, "bold"), text_color="white").grid(row=0, column=col, padx=5, pady=5)

            # Table rows
            for idx, (teacher_name, degree, class_count, converted_periods, salary) in enumerate(teachers, 1):
                row = ctk.CTkFrame(table_frame, fg_color="#FFFFFF" if idx % 2 == 0 else "#F0F0F0")
                row.pack(fill="x", pady=1)
                
                ctk.CTkLabel(row, text=str(idx), width=50, anchor="center").grid(row=0, column=0, padx=5, pady=2)
                
                teacher_label = ctk.CTkLabel(row, text=teacher_name, width=200, anchor="w",
                                        cursor="hand2", text_color="#2B3467")
                teacher_label.grid(row=0, column=1, padx=5, pady=2)
                teacher_label.bind("<Button-1>", lambda e, t=teacher_name: self.handle_teacher_click(t))
                
                ctk.CTkLabel(row, text=degree, width=70, anchor="center").grid(row=0, column=2, padx=5, pady=2)
                ctk.CTkLabel(row, text=str(class_count), width=70, anchor="center").grid(row=0, column=3, padx=5, pady=2)
                ctk.CTkLabel(row, text=str(int(float(converted_periods)) if converted_periods is not None else 0), 
                            width=70, anchor="center").grid(row=0, column=4, padx=5, pady=2)
                ctk.CTkLabel(row, text=f"{int(float(salary)) if salary is not None else 0:,} đ", 
                            width=100, anchor="center").grid(row=0, column=5, padx=5, pady=2)

            # Total row
            total_frame = ctk.CTkFrame(table_frame, fg_color="#E3F2FD")
            total_frame.pack(fill="x", pady=(5, 0))
            ctk.CTkLabel(total_frame, text="TỔNG CỘNG:", width=50, anchor="center", font=("Helvetica", 11, "bold"), 
                        text_color="#2B3467").grid(row=0, column=0, padx=5, pady=2)
            ctk.CTkLabel(total_frame, text="", width=180).grid(row=0, column=1, padx=5, pady=2)
            ctk.CTkLabel(total_frame, text="", width=70, anchor="center").grid(row=0, column=2, padx=5, pady=2)
            ctk.CTkLabel(total_frame, text=str(sum(t[2] or 0 for t in teachers)), width=70, anchor="center", 
                        font=("Helvetica", 11, "bold"), text_color="#2B3467").grid(row=0, column=3, padx=5, pady=2)
            ctk.CTkLabel(total_frame, text=str(int(sum(float(t[3] or 0) for t in teachers))), width=70, anchor="center", 
                        font=("Helvetica", 11, "bold"), text_color="#2B3467").grid(row=0, column=4, padx=5, pady=2)
            ctk.CTkLabel(total_frame, text=f"{int(sum(float(t[4] or 0) for t in teachers)):,} đ", width=100, anchor="center", 
                        font=("Helvetica", 11, "bold"), text_color="#2B3467").grid(row=0, column=5, padx=5, pady=2)

            # Chart frame
            chart_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            chart_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

            teacher_names = [t[0] for t in teachers]
            salaries = [float(t[4] or 0) for t in teachers]

            if sum(salaries) > 0:
                fig, ax = plt.subplots(figsize=(4, 3))
                ax.bar(teacher_names, salaries, color="#4B89DC")
                ax.set_title("Tiền dạy theo giáo viên")
                ax.set_ylabel("Số tiền (đ)")
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                canvas = FigureCanvasTkAgg(fig, master=chart_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)
            else:
                ctk.CTkLabel(chart_frame, text="Không có dữ liệu để vẽ biểu đồ", font=("Helvetica", 14)).pack(expand=True, fill="both")

            # Export button
            export_btn = ctk.CTkButton(self.report_content_frame,
                                    text="Xuất Excel",
                                    command=lambda: self.export_teacher_report(year, dept),
                                    fg_color="#28A745",
                                    hover_color="#218838")
            export_btn.pack(side="bottom", pady=10)

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def show_semester_report(self, year, teacher):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            # Debug: Kiểm tra semesters cho year
            cursor.execute("SELECT semester_id FROM semesters WHERE year = %s", (year,))
            semesters = cursor.fetchall()
            print(f"Debug - Semesters for year {year}: {semesters}")

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
                WHERE t.full_name = %s AND s.year = %s
                GROUP BY s.semester_id, s.semester_name
                ORDER BY s.semester_name
            """, (year, year, year, teacher, year))
            semesters = cursor.fetchall()
            print(f"Debug - semesters for year {year} and teacher {teacher}: {semesters}")

            if not semesters:
                ctk.CTkLabel(self.report_content_frame, text=f"Không có dữ liệu cho giáo viên {teacher} trong năm {year}",
                            font=("Helvetica", 14), text_color="red").pack(expand=True)
                return

            total_salary = sum(float(s[3] or 0) for s in semesters)
            print(f"Debug - total_salary for year {year} and teacher {teacher}: {total_salary}")

            if total_salary == 0:
                ctk.CTkLabel(self.report_content_frame, text=f"Cảnh báo: Tổng tiền = 0 cho giáo viên {teacher} trong năm {year}",
                            font=("Helvetica", 14), text_color="orange").pack(expand=True)

            # Summary cards
            summary_frame = ctk.CTkFrame(self.report_content_frame, fg_color="transparent")
            summary_frame.pack(fill="x", pady=(0, 20))
            
            card1 = ctk.CTkFrame(summary_frame, fg_color="#4B89DC", corner_radius=10, height=80)
            card1.pack(side="left", fill="x", expand=True, padx=5)
            ctk.CTkLabel(card1, text=f"{len(semesters)}", font=("Helvetica", 24, "bold"), 
                        text_color="white").pack(pady=(10, 0))
            ctk.CTkLabel(card1, text="Học kỳ", font=("Helvetica", 12), text_color="white").pack()
            
            card2 = ctk.CTkFrame(summary_frame, fg_color="#00B894", corner_radius=10, height=80)
            card2.pack(side="left", fill="x", expand=True, padx=5)
            ctk.CTkLabel(card2, text=f"{sum(s[1] or 0 for s in semesters)}", font=("Helvetica", 24, "bold"), 
                        text_color="white").pack(pady=(10, 0))
            ctk.CTkLabel(card2, text="Lớp học phần", font=("Helvetica", 12), text_color="white").pack()
            
            card3 = ctk.CTkFrame(summary_frame, fg_color="#FD79A8", corner_radius=10, height=80)
            card3.pack(side="left", fill="x", expand=True, padx=5)
            ctk.CTkLabel(card3, text=f"{sum(int(float(s[3])) if s[3] is not None else 0 for s in semesters):,.0f} đ", 
                        font=("Helvetica", 18, "bold"), text_color="white").pack(pady=(10, 0))
            ctk.CTkLabel(card3, text="Tổng tiền", font=("Helvetica", 12), text_color="white").pack()

            # Table and chart container
            content_frame = ctk.CTkFrame(self.report_content_frame, fg_color="transparent")
            content_frame.pack(fill="both", expand=True)
            content_frame.grid_columnconfigure(0, weight=7)  # 70% for table
            content_frame.grid_columnconfigure(1, weight=3)  # 30% for chart

            # Table frame
            table_frame = ctk.CTkScrollableFrame(content_frame, fg_color="transparent")
            table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

            # Table header
            header_frame = ctk.CTkFrame(table_frame, fg_color="#2B3467")
            header_frame.pack(fill="x", pady=(0, 5))
            
            headers = ["STT", "HỌC KỲ", "SỐ LỚP", "TIẾT QĐ", "TỔNG TIỀN"]
            col_widths = [50, 150, 100, 100, 150]
            for col, (header, width) in enumerate(zip(headers, col_widths)):
                ctk.CTkLabel(header_frame, text=header, width=width, anchor="center",
                            font=("Helvetica", 11, "bold"), text_color="white").grid(row=0, column=col, padx=5, pady=5)

            # Table rows
            for idx, (semester_name, class_count, converted_periods, salary) in enumerate(semesters, 1):
                row = ctk.CTkFrame(table_frame, fg_color="#FFFFFF" if idx % 2 == 0 else "#F0F0F0")
                row.pack(fill="x", pady=1)
                
                ctk.CTkLabel(row, text=str(idx), width=50, anchor="center").grid(row=0, column=0, padx=5, pady=2)
                ctk.CTkLabel(row, text=semester_name, width=150, anchor="w").grid(row=0, column=1, padx=5, pady=2)
                ctk.CTkLabel(row, text=str(class_count), width=100, anchor="center").grid(row=0, column=2, padx=5, pady=2)
                ctk.CTkLabel(row, text=str(int(float(converted_periods)) if converted_periods is not None else 0), 
                            width=100, anchor="center").grid(row=0, column=3, padx=5, pady=2)
                ctk.CTkLabel(row, text=f"{int(float(salary)) if salary is not None else 0:,} đ", 
                            width=150, anchor="center").grid(row=0, column=4, padx=5, pady=2)

            # Total row
            total_frame = ctk.CTkFrame(table_frame, fg_color="#E3F2FD")
            total_frame.pack(fill="x", pady=(5, 0))
            ctk.CTkLabel(total_frame, text="TỔNG CỘNG:", width=50, anchor="center", font=("Helvetica", 11, "bold"), 
                        text_color="#2B3467").grid(row=0, column=0, padx=5, pady=2)
            ctk.CTkLabel(total_frame, text="", width=130).grid(row=0, column=1, padx=5, pady=2)
            ctk.CTkLabel(total_frame, text=str(sum(s[1] or 0 for s in semesters)), width=100, anchor="center", 
                        font=("Helvetica", 11, "bold"), text_color="#2B3467").grid(row=0, column=2, padx=5, pady=2)
            ctk.CTkLabel(total_frame, text=str(int(sum(float(s[2] or 0) for s in semesters))), width=100, anchor="center", 
                        font=("Helvetica", 11, "bold"), text_color="#2B3467").grid(row=0, column=3, padx=5, pady=2)
            ctk.CTkLabel(total_frame, text=f"{int(sum(float(s[3] or 0) for s in semesters)):,} đ", width=150, anchor="center", 
                        font=("Helvetica", 11, "bold"), text_color="#2B3467").grid(row=0, column=4, padx=5, pady=2)

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
            export_btn = ctk.CTkButton(self.report_content_frame,
                                    text="Xuất Excel",
                                    command=lambda: self.export_semester_report(year, teacher),
                                    fg_color="#28A745",
                                    hover_color="#218838")
            export_btn.pack(side="bottom", pady=10)

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def export_dept_report(self, year):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.dept_name, COUNT(DISTINCT t.teacher_id) as teacher_count, COUNT(c.class_id) as class_count,
                       COALESCE(SUM(cm.periods * (cm.coefficient + cc.coefficient)), 0) as total_converted_periods,
                       COALESCE(SUM(cm.periods * (cm.coefficient + cc.coefficient) * tc.coefficient * tr.amount_per_period), 0) as total_salary
                FROM departments d
                LEFT JOIN teachers t ON d.dept_id = t.dept_id
                LEFT JOIN assignments a ON t.teacher_id = a.teacher_id
                LEFT JOIN classes c ON a.class_id = c.class_id
                LEFT JOIN course_modules cm ON c.module_id = cm.module_id
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
                WHERE c.semester_id IN (SELECT semester_id FROM semesters WHERE year = %s)
                GROUP BY d.dept_name
            """, (year, year, year, year))
            depts = cursor.fetchall()

            data = []
            for idx, (dept_name, teacher_count, class_count, converted_periods, salary) in enumerate(depts, 1):
                data.append({
                    "STT": idx,
                    "KHOA": dept_name,
                    "SỐ GIÁO VIÊN": teacher_count,
                    "SỐ LỚP": class_count,
                    "TỔNG SỐ TIẾT QUY ĐỔI": int(float(converted_periods)) if converted_periods is not None else 0,
                    "TỔNG TIỀN": int(float(salary)) if salary is not None else 0
                })

            df = pd.DataFrame(data)
            df.to_excel("dept_report.xlsx", index=False)
            messagebox.showinfo("Thành công", "Báo cáo đã được xuất ra file: dept_report.xlsx")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất báo cáo: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def export_teacher_report(self, year, dept):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.full_name, d.degree_name, COUNT(c.class_id) as class_count,
                       COALESCE(SUM(cm.periods * (cm.coefficient + cc.coefficient)), 0) as total_converted_periods,
                       COALESCE(SUM(cm.periods * (cm.coefficient + cc.coefficient) * tc.coefficient * tr.amount_per_period), 0) as total_salary
                FROM teachers t
                JOIN degrees d ON t.degree_id = d.degree_id
                JOIN departments dept ON t.dept_id = dept.dept_id
                LEFT JOIN assignments a ON t.teacher_id = a.teacher_id
                LEFT JOIN classes c ON a.class_id = c.class_id
                LEFT JOIN course_modules cm ON c.module_id = cm.module_id
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
                WHERE dept.dept_name = %s AND c.semester_id IN (SELECT semester_id FROM semesters WHERE year = %s)
                GROUP BY t.teacher_id, t.full_name, d.degree_name
            """, (year, year, year, dept, year))
            teachers = cursor.fetchall()

            data = []
            for idx, (teacher_name, degree, class_count, converted_periods, salary) in enumerate(teachers, 1):
                data.append({
                    "STT": idx,
                    "GIÁO VIÊN": teacher_name,
                    "HỌC VỊ": degree,
                    "SỐ LỚP": class_count,
                    "TỔNG SỐ TIẾT QUY ĐỔI": int(float(converted_periods)) if converted_periods is not None else 0,
                    "TỔNG TIỀN": int(float(salary)) if salary is not None else 0
                })

            df = pd.DataFrame(data)
            df.to_excel("teacher_report.xlsx", index=False)
            messagebox.showinfo("Thành công", "Báo cáo đã được xuất ra file: teacher_report.xlsx")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất báo cáo: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def export_semester_report(self, year, teacher):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.semester_name, COUNT(c.class_id) as class_count,
                       COALESCE(SUM(cm.periods * (cm.coefficient + cc.coefficient)), 0) as total_converted_periods,
                       COALESCE(SUM(cm.periods * (cm.coefficient + cc.coefficient) * tc.coefficient * tr.amount_per_period), 0) as total_salary
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
                WHERE t.full_name = %s AND s.year = %s
                GROUP BY s.semester_id, s.semester_name
            """, (year, year, year, teacher, year))
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
            df.to_excel("semester_report.xlsx", index=False)
            messagebox.showinfo("Thành công", "Báo cáo đã được xuất ra file: semester_report.xlsx")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất báo cáo: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def handle_dept_click(self, dept_name):
        for widget in self.report_content_frame.winfo_children():
            widget.destroy()
        
        self.update_breadcrumb(["Toàn trường", dept_name])
        
        title_frame = ctk.CTkFrame(self.report_content_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(title_frame, text=f"BÁO CÁO TIỀN DẠY KHOA {dept_name.upper()}", 
                    font=("Helvetica", 20, "bold"), text_color="#2B3467").pack(side="left")
        ctk.CTkLabel(title_frame, text=f"Năm học: {self.year}", 
                    font=("Helvetica", 14), text_color="#666666").pack(side="right")
        
        self.show_teacher_report(self.year, dept_name)

    def handle_teacher_click(self, teacher_name):
        for widget in self.report_content_frame.winfo_children():
            widget.destroy()
        
        # Truy vấn dept_name từ cơ sở dữ liệu dựa trên teacher_name
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.dept_name 
                FROM teachers t
                JOIN departments d ON t.dept_id = d.dept_id
                WHERE t.full_name = %s
            """, (teacher_name,))
            result = cursor.fetchone()
            dept_name = result[0] if result else "Unknown Dept"
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể lấy thông tin khoa: {e}")
            dept_name = "Unknown Dept"
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

        self.update_breadcrumb(["Toàn trường", dept_name, teacher_name])  # Cập nhật breadcrumb với dept_name thực tế
        
        title_frame = ctk.CTkFrame(self.report_content_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(title_frame, text=f"BÁO CÁO TIỀN DẠY GIÁO VIÊN {teacher_name.upper()}", 
                    font=("Helvetica", 20, "bold"), text_color="#2B3467").pack(side="left")
        ctk.CTkLabel(title_frame, text=f"Năm học: {self.year}", 
                    font=("Helvetica", 14), text_color="#666666").pack(side="right")
        
        self.show_semester_report(self.year, teacher_name)