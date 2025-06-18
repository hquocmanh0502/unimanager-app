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
        self.year = "2024-2025"  # Default year
        self.breadcrumb_labels = []

        # Main frame
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(self.header_frame, text="Báo cáo tiền dạy", font=("Helvetica", 20, "bold"), text_color="#2B3467").pack(side="left")

        # Breadcrumb and Year combobox
        self.breadcrumb_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.breadcrumb_frame.pack(side="right")
        self.update_breadcrumb(["Toàn trường"])
        self.year_combobox_report = ctk.CTkComboBox(self.breadcrumb_frame, values=self.get_academic_years(), width=150, command=self.update_report_data)
        self.year_combobox_report.pack(side="right", padx=5)
        self.year_combobox_report.set(self.year)

        # Initialize content frame
        self.report_content_frame = ctk.CTkFrame(self.main_frame, fg_color="#FFFFFF", corner_radius=10)
        self.report_content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Initial load
        self.update_report_data()

    def get_academic_years(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT year FROM semesters ORDER BY year DESC")
            years = [row[0] for row in cursor.fetchall()]
            return years if years else ["2024-2025"]
        except mysql.connector.Error as e:
            print(f"Error fetching academic years: {e}")
            return ["2024-2025"]
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def update_breadcrumb(self, parts):
        # Clear existing breadcrumb labels
        for label in self.breadcrumb_labels:
            label.destroy()
        self.breadcrumb_labels = []
        # Create new breadcrumb labels in breadcrumb_frame
        for i, part in enumerate(parts):
            if i > 0:
                ctk.CTkLabel(self.breadcrumb_frame, text=" / ", text_color="gray").pack(side="left")
            label = ctk.CTkLabel(self.breadcrumb_frame, text=part, text_color="#2B3467", cursor="hand2")
            label.pack(side="left", padx=2)
            label.bind("<Button-1>", lambda e, p=part, idx=i: self.breadcrumb_click(p, idx))
            self.breadcrumb_labels.append(label)

    def breadcrumb_click(self, part, idx):
        current_parts = ["Toàn trường"]
        if idx == 0:
            self.update_breadcrumb(["Toàn trường"])
        elif idx == 1:
            current_parts.append(part)  # Thêm tên khoa
            self.update_breadcrumb(current_parts)
        elif idx == 2:
            current_parts.extend([self.breadcrumb_labels[1].cget("text"), part])  # Thêm tên khoa và giáo viên
            self.update_breadcrumb(current_parts)
        self.update_report_data()

    def update_report_data(self, event=None):
        self.year = self.year_combobox_report.get()
        breadcrumb_parts = [label.cget("text") for label in self.breadcrumb_labels]

        # Clear existing content in report_content_frame
        for widget in self.report_content_frame.winfo_children():
            widget.destroy()

        if len(breadcrumb_parts) == 1:  # Toàn trường
            self.update_breadcrumb(["Toàn trường"])
            ctk.CTkLabel(self.report_content_frame, text="Báo cáo tiền dạy theo khoa", font=("Helvetica", 18, "bold"), text_color="#2B3467").pack(pady=10)
            self.show_dept_report(self.year)
        elif len(breadcrumb_parts) == 2:  # Khoa
            dept = breadcrumb_parts[1]
            self.update_breadcrumb(["Toàn trường", dept])
            ctk.CTkLabel(self.report_content_frame, text=f"Báo cáo tiền dạy - Khoa {dept}", font=("Helvetica", 18, "bold"), text_color="#2B3467").pack(pady=10)
            self.show_teacher_report(self.year, dept)
        elif len(breadcrumb_parts) == 3:  # Giáo viên
            dept = breadcrumb_parts[1]
            teacher = breadcrumb_parts[2]
            self.update_breadcrumb(["Toàn trường", dept, teacher])
            ctk.CTkLabel(self.report_content_frame, text=f"Báo cáo tiền dạy - {teacher}", font=("Helvetica", 18, "bold"), text_color="#2B3467").pack(pady=10)
            self.show_semester_report(self.year, teacher)

    def show_dept_report(self, year):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.dept_name, 
                       COUNT(DISTINCT t.teacher_id) as teacher_count, 
                       COUNT(c.class_id) as class_count,
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

            total_teachers = 0
            total_classes = 0
            total_converted_periods = 0
            total_salary = 0

            # Heading frame
            heading_frame = ctk.CTkFrame(self.report_content_frame, fg_color="#D3D3D3", corner_radius=0)
            heading_frame.pack(fill="x", pady=(0, 5))
            ctk.CTkLabel(heading_frame, text="STT", width=50, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(heading_frame, text="KHOA", width=150, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(heading_frame, text="SỐ GIÁO VIÊN", width=100, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(heading_frame, text="SỐ LỚP", width=100, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(heading_frame, text="TỔNG SỐ TIẾT QUY ĐỔI", width=150, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(heading_frame, text="TỔNG TIỀN", width=150, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)

            # Main content frame to split 50/50
            content_frame = ctk.CTkFrame(self.report_content_frame, fg_color="transparent")
            content_frame.pack(fill="both", expand=True)

            # Table frame (left 50%)
            table_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            table_frame.pack(side="left", fill="both", expand=True, padx=5)

            for idx, (dept_name, teacher_count, class_count, converted_periods, salary) in enumerate(depts, 1):
                frame = ctk.CTkFrame(table_frame, fg_color="#F0F0F0" if idx % 2 else "#FFFFFF")
                frame.pack(fill="x", pady=2)
                ctk.CTkLabel(frame, text=str(idx), width=50, anchor="center").pack(side="left", padx=5)
                dept_label = ctk.CTkLabel(frame, text=dept_name, width=150, anchor="center", text_color="#2B3467", cursor="hand2")
                dept_label.pack(side="left", padx=5)
                dept_label.bind("<Button-1>", lambda e, d=dept_name: self.breadcrumb_click(d, 1))
                ctk.CTkLabel(frame, text=str(teacher_count), width=100, anchor="center").pack(side="left", padx=5)
                ctk.CTkLabel(frame, text=str(class_count), width=100, anchor="center").pack(side="left", padx=5)
                ctk.CTkLabel(frame, text=str(int(float(converted_periods)) if converted_periods is not None else 0), width=150, anchor="center").pack(side="left", padx=5)
                ctk.CTkLabel(frame, text=f"{int(float(salary)) if salary is not None else 0:,.0f} đ", width=150, anchor="center").pack(side="left", padx=5)

                total_teachers += teacher_count or 0
                total_classes += class_count or 0
                total_converted_periods += int(float(converted_periods)) if converted_periods is not None else 0
                total_salary += int(float(salary)) if salary is not None else 0

            # Total row
            total_frame = ctk.CTkFrame(table_frame, fg_color="#E0E0E0")
            total_frame.pack(fill="x", pady=2)
            ctk.CTkLabel(total_frame, text="Tổng cộng:", width=50, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(total_frame, text="", width=150, anchor="center").pack(side="left", padx=5)  # Placeholder for KHOA
            ctk.CTkLabel(total_frame, text=str(total_teachers), width=100, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(total_frame, text=str(total_classes), width=100, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(total_frame, text=str(total_converted_periods), width=150, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(total_frame, text=f"{total_salary:,.0f} đ", width=150, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)

            # Chart frame (right 50%)
            chart_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            chart_frame.pack(side="right", fill="both", expand=True, padx=5)

            labels = [d[0] for d in depts]
            sizes = [d[4] for d in depts] if depts else []
            sizes = [0 if pd.isna(s) or s == 0 else s for s in sizes]
            if all(s == 0 for s in sizes):
                ctk.CTkLabel(chart_frame, text="Không có dữ liệu để vẽ biểu đồ", font=("Helvetica", 12), text_color="red").pack(expand=True)
            else:
                colors = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"]
                explode = [0.1 if i == 0 else 0 for i in range(len(labels))]

                fig, ax = plt.subplots(figsize=(5, 5))
                ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct=lambda pct: f'{pct:.1f}%' if pct > 0 else '', startangle=90)
                ax.axis('equal')

                canvas = FigureCanvasTkAgg(fig, master=chart_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)

            # Export button
            ctk.CTkButton(self.report_content_frame, text="Xuất Excel", fg_color="#28A745", command=lambda: self.export_dept_report(year)).pack(side="bottom", pady=10)

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

            total_classes = 0
            total_converted_periods = 0
            total_salary = 0

            # Heading frame
            heading_frame = ctk.CTkFrame(self.report_content_frame, fg_color="#D3D3D3", corner_radius=0)
            heading_frame.pack(fill="x", pady=(0, 5))
            ctk.CTkLabel(heading_frame, text="STT", width=50, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(heading_frame, text="GIÁO VIÊN", width=150, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(heading_frame, text="HỌC VỊ", width=100, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(heading_frame, text="SỐ LỚP", width=100, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(heading_frame, text="TỔNG SỐ TIẾT QUY ĐỔI", width=150, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(heading_frame, text="TỔNG TIỀN", width=150, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)

            # Main content frame to split 50/50
            content_frame = ctk.CTkFrame(self.report_content_frame, fg_color="transparent")
            content_frame.pack(fill="both", expand=True)

            # Table frame (left 50%)
            table_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            table_frame.pack(side="left", fill="both", expand=True, padx=5)

            for idx, (teacher_name, degree, class_count, converted_periods, salary) in enumerate(teachers, 1):
                frame = ctk.CTkFrame(table_frame, fg_color="#F0F0F0" if idx % 2 else "#FFFFFF")
                frame.pack(fill="x", pady=2)
                ctk.CTkLabel(frame, text=str(idx), width=50, anchor="center").pack(side="left", padx=5)
                teacher_label = ctk.CTkLabel(frame, text=teacher_name, width=150, anchor="center", text_color="#2B3467", cursor="hand2")
                teacher_label.pack(side="left", padx=5)
                teacher_label.bind("<Button-1>", lambda e, t=teacher_name: self.breadcrumb_click(t, 2))
                ctk.CTkLabel(frame, text=degree, width=100, anchor="center").pack(side="left", padx=5)
                ctk.CTkLabel(frame, text=str(class_count), width=100, anchor="center").pack(side="left", padx=5)
                ctk.CTkLabel(frame, text=str(int(float(converted_periods)) if converted_periods is not None else 0), width=150, anchor="center").pack(side="left", padx=5)
                ctk.CTkLabel(frame, text=f"{int(float(salary)) if salary is not None else 0:,.0f} đ", width=150, anchor="center").pack(side="left", padx=5)

                total_classes += class_count or 0
                total_converted_periods += int(float(converted_periods)) if converted_periods is not None else 0
                total_salary += int(float(salary)) if salary is not None else 0

            # Total row
            total_frame = ctk.CTkFrame(table_frame, fg_color="#E0E0E0")
            total_frame.pack(fill="x", pady=2)
            ctk.CTkLabel(total_frame, text="Tổng cộng:", width=50, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(total_frame, text="", width=150, anchor="center").pack(side="left", padx=5)  # Placeholder for GIÁO VIÊN
            ctk.CTkLabel(total_frame, text="", width=100, anchor="center").pack(side="left", padx=5)  # Placeholder for HỌC VỊ
            ctk.CTkLabel(total_frame, text=str(total_classes), width=100, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(total_frame, text=str(total_converted_periods), width=150, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(total_frame, text=f"{total_salary:,.0f} đ", width=150, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)

            # Chart frame (right 50%)
            chart_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            chart_frame.pack(side="right", fill="both", expand=True, padx=5)

            teacher_names = [t[0] for t in teachers]
            salaries = [t[4] for t in teachers] if teachers else []
            salaries = [0 if pd.isna(s) or s == 0 else s for s in salaries]

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(teacher_names, salaries, color="#36A2EB")
            ax.set_ylabel("Tổng tiền (đ)")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            # Export button
            ctk.CTkButton(self.report_content_frame, text="Xuất Excel", fg_color="#28A745", command=lambda: self.export_teacher_report(year, dept)).pack(side="bottom", pady=10)

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

            total_classes = 0
            total_converted_periods = 0
            total_salary = 0

            # Heading frame
            heading_frame = ctk.CTkFrame(self.report_content_frame, fg_color="#D3D3D3", corner_radius=0)
            heading_frame.pack(fill="x", pady=(0, 5))
            ctk.CTkLabel(heading_frame, text="STT", width=50, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(heading_frame, text="HỌC KỲ", width=150, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(heading_frame, text="SỐ LỚP", width=100, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(heading_frame, text="TỔNG SỐ TIẾT QUY ĐỔI", width=150, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(heading_frame, text="TỔNG TIỀN", width=150, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)

            # Main content frame to split 50/50
            content_frame = ctk.CTkFrame(self.report_content_frame, fg_color="transparent")
            content_frame.pack(fill="both", expand=True)

            # Table frame (left 50%)
            table_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            table_frame.pack(side="left", fill="both", expand=True, padx=5)

            for idx, (semester_name, class_count, converted_periods, salary) in enumerate(semesters, 1):
                frame = ctk.CTkFrame(table_frame, fg_color="#F0F0F0" if idx % 2 else "#FFFFFF")
                frame.pack(fill="x", pady=2)
                ctk.CTkLabel(frame, text=str(idx), width=50, anchor="center").pack(side="left", padx=5)
                ctk.CTkLabel(frame, text=semester_name, width=150, anchor="center").pack(side="left", padx=5)
                ctk.CTkLabel(frame, text=str(class_count), width=100, anchor="center").pack(side="left", padx=5)
                ctk.CTkLabel(frame, text=str(int(float(converted_periods)) if converted_periods is not None else 0), width=150, anchor="center").pack(side="left", padx=5)
                ctk.CTkLabel(frame, text=f"{int(float(salary)) if salary is not None else 0:,.0f} đ", width=150, anchor="center").pack(side="left", padx=5)

                total_classes += class_count or 0
                total_converted_periods += int(float(converted_periods)) if converted_periods is not None else 0
                total_salary += int(float(salary)) if salary is not None else 0

            # Total row
            total_frame = ctk.CTkFrame(table_frame, fg_color="#E0E0E0")
            total_frame.pack(fill="x", pady=2)
            ctk.CTkLabel(total_frame, text="Tổng cộng:", width=50, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(total_frame, text="", width=150, anchor="center").pack(side="left", padx=5)  # Placeholder for HỌC KỲ
            ctk.CTkLabel(total_frame, text=str(total_classes), width=100, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(total_frame, text=str(total_converted_periods), width=150, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(total_frame, text=f"{total_salary:,.0f} đ", width=150, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=5)

            # Chart frame (right 50%)
            chart_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            chart_frame.pack(side="right", fill="both", expand=True, padx=5)

            semester_names = [s[0] for s in semesters]
            salaries = [s[3] for s in semesters] if semesters else []
            salaries = [0 if pd.isna(s) or s == 0 else s for s in salaries]

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(semester_names, salaries, color="#36A2EB")
            ax.set_ylabel("Tổng tiền (đ)")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            # Export button
            ctk.CTkButton(self.report_content_frame, text="Xuất Excel", fg_color="#28A745", command=lambda: self.export_semester_report(year, teacher)).pack(side="bottom", pady=10)

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
                    "TỔNG SỐ TIẾT QUY ĐỔI": converted_periods,
                    "TỔNG TIỀN": salary
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
                    "TỔNG SỐ TIẾT QUY ĐỔI": converted_periods,
                    "TỔNG TIỀN": salary
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
                    "TỔNG SỐ TIẾT QUY ĐỔI": converted_periods,
                    "TỔNG TIỀN": salary
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