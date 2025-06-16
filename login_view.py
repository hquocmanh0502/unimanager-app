from tkinter import messagebox, Toplevel
import customtkinter as ctk
from PIL import Image, ImageFilter, ImageEnhance
from auth import verify_user
from teacher_view import TeacherView
from admin_view import AdminView
from accountant_view import AccountantView
import os
import threading
import time

class CustomNotification:
    """Class tạo thông báo tùy chỉnh đẹp mắt"""
    
    def __init__(self, parent, message, notification_type="info", duration=3000):
        self.parent = parent
        self.message = message
        self.notification_type = notification_type
        self.duration = duration
        self.notification_window = None
        self.is_closing = False
        
    def show(self):
        """Hiển thị thông báo"""
        try:
            # Tạo window cho notification
            self.notification_window = ctk.CTkToplevel(self.parent)
            self.notification_window.withdraw()  # Ẩn trước khi setup
            
            # Cấu hình window
            self.setup_window()
            
            # Tạo nội dung
            self.create_content()
            
            # Hiển thị với animation
            self.show_with_animation()
            
            # Tự động ẩn sau duration
            self.parent.after(self.duration, self.hide_with_animation)
        except Exception as e:
            print(f"Error creating notification: {e}")
            # Fallback to simple messagebox
            if self.notification_type == "error":
                messagebox.showerror("Lỗi", self.message)
            elif self.notification_type == "success":
                messagebox.showinfo("Thành công", self.message)
            elif self.notification_type == "warning":
                messagebox.showwarning("Cảnh báo", self.message)
            else:
                messagebox.showinfo("Thông báo", self.message)
    
    def setup_window(self):
        """Cấu hình window notification"""
        self.notification_window.title("")
        self.notification_window.geometry("400x100")
        self.notification_window.resizable(False, False)
        self.notification_window.attributes("-topmost", True)
        self.notification_window.overrideredirect(True)  # Loại bỏ title bar
        
        # Vị trí ở góc phải trên màn hình
        try:
            screen_width = self.notification_window.winfo_screenwidth()
            screen_height = self.notification_window.winfo_screenheight()
            x = screen_width - 420
            y = 20
            self.notification_window.geometry(f"400x100+{x}+{y}")
        except:
            # Fallback position
            self.notification_window.geometry("400x100+100+100")
    
    def create_content(self):
        """Tạo nội dung notification"""
        # Màu sắc theo loại thông báo
        colors = {
            "success": {
                "bg": ["#10b981", "#059669"],
                "text": "white",
                "icon": "✅",
                "progress_bg": "#065f46",
                "progress_fill": "#34d399"
            },
            "error": {
                "bg": ["#ef4444", "#dc2626"],
                "text": "white", 
                "icon": "❌",
                "progress_bg": "#991b1b",
                "progress_fill": "#f87171"
            },
            "warning": {
                "bg": ["#f59e0b", "#d97706"],
                "text": "white",
                "icon": "⚠️",
                "progress_bg": "#92400e",
                "progress_fill": "#fbbf24"
            },
            "info": {
                "bg": ["#3b82f6", "#2563eb"],
                "text": "white",
                "icon": "ℹ️",
                "progress_bg": "#1e40af",
                "progress_fill": "#60a5fa"
            }
        }
        
        color_scheme = colors.get(self.notification_type, colors["info"])
        
        # Main frame
        main_frame = ctk.CTkFrame(
            self.notification_window,
            fg_color=color_scheme["bg"],
            corner_radius=15,
            border_width=0
        )
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Content frame
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Top section với icon và message
        top_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 5))
        
        # Icon
        icon_label = ctk.CTkLabel(
            top_frame,
            text=color_scheme["icon"],
            font=ctk.CTkFont(size=20),
            text_color=color_scheme["text"]
        )
        icon_label.pack(side="left", padx=(0, 10))
        
        # Message
        message_label = ctk.CTkLabel(
            top_frame,
            text=self.message,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=color_scheme["text"],
            wraplength=280,
            justify="left"
        )
        message_label.pack(side="left", fill="both", expand=True)
        
        # Close button
        close_btn = ctk.CTkButton(
            top_frame,
            text="×",
            width=20,
            height=20,
            corner_radius=10,
            fg_color="transparent",
            hover_color="#ffffff20",
            text_color=color_scheme["text"],
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.hide_with_animation
        )
        close_btn.pack(side="right")
        
        # Progress bar với màu solid thay vì RGBA
        try:
            self.progress_bar = ctk.CTkProgressBar(
                content_frame,
                height=3,
                corner_radius=2,
                fg_color=color_scheme["progress_bg"],
                progress_color=color_scheme["progress_fill"]
            )
            self.progress_bar.pack(fill="x", pady=(5, 0))
            self.progress_bar.set(1.0)
            
            # Animate progress bar
            self.animate_progress()
        except Exception as e:
            print(f"Error creating progress bar: {e}")
            # Tạo progress bar đơn giản bằng Frame
            self.create_simple_progress(content_frame, color_scheme)
    
    def create_simple_progress(self, parent, color_scheme):
        """Tạo progress bar đơn giản bằng Frame khi CTkProgressBar lỗi"""
        progress_container = ctk.CTkFrame(
            parent,
            height=4,
            fg_color=color_scheme["progress_bg"]
        )
        progress_container.pack(fill="x", pady=(5, 0))
        progress_container.pack_propagate(False)
        
        self.progress_fill = ctk.CTkFrame(
            progress_container,
            fg_color=color_scheme["progress_fill"]
        )
        self.progress_fill.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
        
        # Animate simple progress
        self.animate_simple_progress()
    
    def animate_progress(self):
        """Animation cho CTkProgressBar"""
        if (not hasattr(self, 'progress_bar') or 
            not self.notification_window or 
            not self.notification_window.winfo_exists() or
            self.is_closing):
            return
            
        try:
            current_progress = self.progress_bar.get()
            new_progress = current_progress - (1.0 / (self.duration / 50))
            
            if new_progress > 0:
                self.progress_bar.set(new_progress)
                self.parent.after(50, self.animate_progress)
        except:
            pass
    
    def animate_simple_progress(self):
        """Animation cho simple progress bar"""
        if (not hasattr(self, 'progress_fill') or 
            not self.notification_window or 
            not self.notification_window.winfo_exists() or
            self.is_closing):
            return
            
        try:
            # Giảm width từ 1.0 về 0
            current_width = self.progress_fill.place_info().get('relwidth', 1.0)
            if isinstance(current_width, str):
                current_width = float(current_width)
            
            new_width = current_width - (1.0 / (self.duration / 50))
            
            if new_width > 0:
                self.progress_fill.place_configure(relwidth=new_width)
                self.parent.after(50, self.animate_simple_progress)
        except:
            pass
    
    def show_with_animation(self):
        """Hiển thị với hiệu ứng slide in"""
        if not self.notification_window:
            return
            
        try:
            self.notification_window.deiconify()
            
            # Start position (off-screen right)
            screen_width = self.notification_window.winfo_screenwidth()
            start_x = screen_width
            end_x = screen_width - 420
            y = 20
            
            # Animation steps
            steps = 15
            step_size = (start_x - end_x) / steps
            
            def animate_step(step):
                if (step <= steps and 
                    self.notification_window and 
                    self.notification_window.winfo_exists() and
                    not self.is_closing):
                    try:
                        current_x = int(start_x - (step_size * step))
                        self.notification_window.geometry(f"400x100+{current_x}+{y}")
                        if step < steps:
                            self.parent.after(20, lambda: animate_step(step + 1))
                    except:
                        pass
            
            animate_step(0)
        except Exception as e:
            print(f"Error in show animation: {e}")
    
    def hide_with_animation(self):
        """Ẩn với hiệu ứng slide out"""
        if (not self.notification_window or 
            not self.notification_window.winfo_exists() or
            self.is_closing):
            return
            
        self.is_closing = True
        
        try:
            # Current position
            screen_width = self.notification_window.winfo_screenwidth()
            start_x = screen_width - 420
            end_x = screen_width
            y = 20
            
            # Animation steps
            steps = 10
            step_size = (end_x - start_x) / steps
            
            def animate_step(step):
                if (step <= steps and 
                    self.notification_window and 
                    self.notification_window.winfo_exists()):
                    try:
                        current_x = int(start_x + (step_size * step))
                        self.notification_window.geometry(f"400x100+{current_x}+{y}")
                        if step == steps:
                            self.notification_window.destroy()
                        else:
                            self.parent.after(15, lambda: animate_step(step + 1))
                    except:
                        if self.notification_window:
                            try:
                                self.notification_window.destroy()
                            except:
                                pass
            
            animate_step(0)
        except Exception as e:
            print(f"Error in hide animation: {e}")
            # Force close
            try:
                if self.notification_window:
                    self.notification_window.destroy()
            except:
                pass

class ModernDialog:
    """Class tạo dialog tùy chỉnh hiện đại với error handling tốt hơn"""
    
    def __init__(self, parent, title, message, dialog_type="info", buttons=None):
        self.parent = parent
        self.title = title
        self.message = message
        self.dialog_type = dialog_type
        self.buttons = buttons or ["OK"]
        self.result = None
        self.dialog_window = None
        
    def show(self):
        """Hiển thị dialog và trả về kết quả"""
        try:
            self.create_dialog()
            if self.dialog_window:
                self.dialog_window.wait_window()
            return self.result
        except Exception as e:
            print(f"Error creating dialog: {e}")
            # Fallback to messagebox
            if self.dialog_type == "error":
                messagebox.showerror(self.title, self.message)
            elif self.dialog_type == "warning":
                messagebox.showwarning(self.title, self.message)
            else:
                messagebox.showinfo(self.title, self.message)
            return "OK"
    
    def create_dialog(self):
        """Tạo dialog window"""
        try:
            # Tạo window
            self.dialog_window = ctk.CTkToplevel(self.parent)
            self.dialog_window.title(self.title)
            self.dialog_window.geometry("450x250")
            self.dialog_window.resizable(False, False)
            self.dialog_window.attributes("-topmost", True)
            self.dialog_window.grab_set()  # Modal dialog
            
            # Center trên parent window
            self.center_dialog()
            
            # Tạo nội dung
            self.create_dialog_content()
        except Exception as e:
            print(f"Error in create_dialog: {e}")
            self.dialog_window = None
    
    def center_dialog(self):
        """Căn giữa dialog trên parent window"""
        try:
            self.dialog_window.update_idletasks()
            
            # Lấy kích thước parent
            parent_x = self.parent.winfo_x()
            parent_y = self.parent.winfo_y()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            
            # Tính toán vị trí center
            dialog_width = 450
            dialog_height = 250
            x = parent_x + (parent_width - dialog_width) // 2
            y = parent_y + (parent_height - dialog_height) // 2
            
            self.dialog_window.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        except Exception as e:
            print(f"Error centering dialog: {e}")
    
    def create_dialog_content(self):
        """Tạo nội dung dialog"""
        # Màu sắc theo loại
        colors = {
            "success": {
                "accent": ["#10b981", "#059669"],
                "icon": "✅",
                "icon_bg": ["#d1fae5", "#065f46"]
            },
            "error": {
                "accent": ["#ef4444", "#dc2626"],
                "icon": "❌",
                "icon_bg": ["#fee2e2", "#991b1b"]
            },
            "warning": {
                "accent": ["#f59e0b", "#d97706"],
                "icon": "⚠️",
                "icon_bg": ["#fef3c7", "#92400e"]
            },
            "info": {
                "accent": ["#3b82f6", "#2563eb"],
                "icon": "ℹ️",
                "icon_bg": ["#dbeafe", "#1e40af"]
            }
        }
        
        color_scheme = colors.get(self.dialog_type, colors["info"])
        
        # Main container
        main_frame = ctk.CTkFrame(
            self.dialog_window,
            fg_color=["white", "#1e293b"],
            corner_radius=0
        )
        main_frame.pack(fill="both", expand=True)
        
        # Header với accent color
        header_frame = ctk.CTkFrame(
            main_frame,
            fg_color=color_scheme["accent"],
            corner_radius=0,
            height=60
        )
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Title trong header
        title_label = ctk.CTkLabel(
            header_frame,
            text=self.title,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        title_label.pack(expand=True)
        
        # Content area
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Icon container
        icon_frame = ctk.CTkFrame(
            content_frame,
            fg_color=color_scheme["icon_bg"],
            corner_radius=50,
            width=60,
            height=60
        )
        icon_frame.pack(pady=(0, 20))
        icon_frame.pack_propagate(False)
        
        # Icon
        icon_label = ctk.CTkLabel(
            icon_frame,
            text=color_scheme["icon"],
            font=ctk.CTkFont(size=28),
            text_color=color_scheme["accent"][0]
        )
        icon_label.pack(expand=True)
        
        # Message
        message_label = ctk.CTkLabel(
            content_frame,
            text=self.message,
            font=ctk.CTkFont(size=14),
            text_color=["#374151", "#e5e7eb"],
            wraplength=350,
            justify="center"
        )
        message_label.pack(pady=(0, 30))
        
        # Buttons
        self.create_dialog_buttons(content_frame, color_scheme)
    
    def create_dialog_buttons(self, parent, color_scheme):
        """Tạo buttons cho dialog"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x")
        
        # Nếu chỉ có 1 button, center nó
        if len(self.buttons) == 1:
            btn = ctk.CTkButton(
                button_frame,
                text=self.buttons[0],
                font=ctk.CTkFont(size=14, weight="bold"),
                height=40,
                width=120,
                corner_radius=20,
                fg_color=color_scheme["accent"],
                hover_color=[color_scheme["accent"][1], color_scheme["accent"][0]],
                command=lambda: self.button_clicked(self.buttons[0])
            )
            btn.pack()
        else:
            # Multiple buttons - pack horizontally
            for i, button_text in enumerate(self.buttons):
                if i == 0:  # Primary button
                    btn = ctk.CTkButton(
                        button_frame,
                        text=button_text,
                        font=ctk.CTkFont(size=14, weight="bold"),
                        height=40,
                        width=100,
                        corner_radius=20,
                        fg_color=color_scheme["accent"],
                        hover_color=[color_scheme["accent"][1], color_scheme["accent"][0]],
                        command=lambda t=button_text: self.button_clicked(t)
                    )
                else:  # Secondary button
                    btn = ctk.CTkButton(
                        button_frame,
                        text=button_text,
                        font=ctk.CTkFont(size=14),
                        height=40,
                        width=100,
                        corner_radius=20,
                        fg_color=["#f3f4f6", "#374151"],
                        hover_color=["#e5e7eb", "#4b5563"],
                        text_color=["#374151", "#e5e7eb"],
                        border_width=1,
                        border_color=["#d1d5db", "#6b7280"],
                        command=lambda t=button_text: self.button_clicked(t)
                    )
                
                btn.pack(side="right" if i == 0 else "left", padx=10)
    
    def button_clicked(self, button_text):
        """Xử lý khi button được click"""
        self.result = button_text
        if self.dialog_window:
            try:
                self.dialog_window.destroy()
            except:
                pass

class LoginPage(object):
    def __init__(self, window):
        # Cấu hình chủ đề
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Màn hình
        self.window = window
        self.window.title("Hệ thống quản lý lương giảng viên")
        self.window.geometry("1400x700")
        self.window.minsize(1000, 700)
        
        # Cấu hình grid cho responsive
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # Biến lưu trữ hình ảnh và trạng thái
        self.bg_img = None
        self.show_password = False
        self.is_loading = False

        # Biến kiểu string
        self.var_email = ctk.StringVar()
        self.var_password = ctk.StringVar()
        self.var_role = ctk.StringVar(value="Giảng viên")

        # Tạo giao diện chính
        self.create_main_layout()
        self.create_left_panel()
        self.create_right_panel()
        
        # Bind sự kiện
        self.bind_events()

    # [Giữ nguyên tất cả các method create_* như trong code trước]
    def create_main_layout(self):
        """Tạo layout chính với hiệu ứng gradient"""
        self.main_container = ctk.CTkFrame(
            self.window, 
            fg_color=["#f8fafc", "#0f172a"],
            corner_radius=0
        )
        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=2)
        self.main_container.grid_columnconfigure(1, weight=3)

    def create_left_panel(self):
        """Tạo panel bên trái với hình nền và thông tin"""
        self.left_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=["#1e40af", "#1e3a8a"],
            corner_radius=0
        )
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 2))
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(1, weight=2)
        self.left_frame.grid_rowconfigure(2, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        self.create_header_section()
        self.create_background_section()
        self.create_footer_section()

    def create_header_section(self):
        """Tạo phần header với logo và tiêu đề"""
        header_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        self.logo_label = ctk.CTkLabel(
            header_frame,
            text="Hệ thống \nQuản lý lương giảng viên",
            font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
            text_color="white"
        )
        self.logo_label.pack(pady=(0, 5))

    def create_background_section(self):
        """Tạo phần hình nền với hiệu ứng"""
        bg_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        bg_frame.grid(row=1, column=0, sticky="nsew", padx=20)
        
        bg_path = "bg1.jpg"
        if os.path.exists(bg_path):
            try:
                pil_image = Image.open(bg_path)
                pil_image = pil_image.filter(ImageFilter.GaussianBlur(radius=1))
                enhancer = ImageEnhance.Brightness(pil_image)
                pil_image = enhancer.enhance(1.1)
                
                self.bg_img = ctk.CTkImage(
                    dark_image=pil_image, 
                    light_image=pil_image
                )
                self.bg_label = ctk.CTkLabel(
                    bg_frame,
                    image=self.bg_img,
                    text=""
                )
                self.bg_label.pack(expand=True, fill="both", pady=20)
            except Exception as e:
                self.create_placeholder_image(bg_frame)
        else:
            self.create_placeholder_image(bg_frame)

    def create_placeholder_image(self, parent):
        """Tạo hình placeholder khi không có hình nền"""
        placeholder_frame = ctk.CTkFrame(
            parent,
            fg_color=["#3b82f6", "#2563eb"],
            corner_radius=20,
            height=300,
            width=300
        )
        placeholder_frame.pack(expand=True, fill="both", pady=20)
        
        ctk.CTkLabel(
            placeholder_frame,
            text="📚\n\nHệ thống\nQuản lý lương\nGiảng viên",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white",
            justify="center"
        ).place(relx=0.5, rely=0.5, anchor="center")

    def create_footer_section(self):
        """Tạo phần footer với thông tin bổ sung"""
        footer_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        footer_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=20)
        
        info_text = "Hệ thống quản lý lương giảng viên\nPhiên bản 2.0"
        ctk.CTkLabel(
            footer_frame,
            text=info_text,
            font=ctk.CTkFont(size=12),
            text_color="#93c5fd",
            justify="center"
        ).pack(expand=True)

    def create_right_panel(self):
        """Tạo panel bên phải với form đăng nhập"""
        self.right_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=["white", "#1e293b"],
            corner_radius=0
        )
        self.right_frame.grid(row=0, column=1, sticky="nsew")
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        self.login_container = ctk.CTkFrame(
            self.right_frame,
            fg_color="transparent"
        )
        self.login_container.place(relx=0.5, rely=0.5, anchor="center")

        self.create_login_form()

    def create_login_form(self):
        """Tạo form đăng nhập với thiết kế hiện đại"""
        title_label = ctk.CTkLabel(
            self.login_container,
            text="Đăng nhập hệ thống",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=["#1e3a8a", "#f1f5f9"]
        )
        title_label.pack(pady=(20, 15))

        desc_label = ctk.CTkLabel(
            self.login_container,
            text="Vui lòng chọn vai trò và nhập thông tin đăng nhập",
            font=ctk.CTkFont(size=16),
            text_color=["#6b7280", "#94a3b8"]
        )
        desc_label.pack(pady=(0, 40))

        form_frame = ctk.CTkFrame(
            self.login_container,
            fg_color=["#f8fafc", "#334155"],
            corner_radius=20,
            border_width=1,
            border_color=["#e2e8f0", "#475569"]
        )
        form_frame.pack(padx=20, pady=20, fill="x")

        content_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        content_frame.pack(padx=50, pady=50, fill="x")

        self.create_role_selection(content_frame)
        self.create_email_input(content_frame)
        self.create_password_input(content_frame)
        self.create_login_button(content_frame)
        self.create_extra_options(content_frame)

    def create_role_selection(self, parent):
        """Tạo phần chọn vai trò"""
        role_label = ctk.CTkLabel(
            parent,
            text="Vai trò đăng nhập",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=["#374151", "#e2e8f0"],
            anchor="w"
        )
        role_label.pack(fill="x", pady=(0, 10))

        self.role_combobox = ctk.CTkComboBox(
            parent,
            values=["Quản trị viên", "Giảng viên", "Kế toán"],
            variable=self.var_role,
            font=ctk.CTkFont(size=16),
            width=400,
            height=50,
            corner_radius=12,
            fg_color=["white", "#475569"],
            border_color=["#d1d5db", "#64748b"],
            button_color=["#1e40af", "#3b82f6"],
            button_hover_color=["#1d4ed8", "#2563eb"],
            text_color=["#111827", "#f1f5f9"],
            dropdown_fg_color=["white", "#475569"],
            dropdown_text_color=["#111827", "#f1f5f9"],
            dropdown_hover_color=["#f3f4f6", "#334155"]
        )
        self.role_combobox.pack(fill="x", pady=(0, 20))

    def create_email_input(self, parent):
        """Tạo ô nhập email/username"""
        email_label = ctk.CTkLabel(
            parent,
            text="Tên đăng nhập hoặc Email",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=["#374151", "#e2e8f0"],
            anchor="w"
        )
        email_label.pack(fill="x", pady=(0, 10))

        self.username_entry = ctk.CTkEntry(
            parent,
            placeholder_text="Nhập email hoặc tên đăng nhập",
            font=ctk.CTkFont(size=16),
            width=400,
            height=50,
            corner_radius=12,
            fg_color=["white", "#475569"],
            border_color=["#d1d5db", "#64748b"],
            placeholder_text_color=["#9ca3af", "#94a3b8"],
            text_color=["#111827", "#f1f5f9"],
            textvariable=self.var_email
        )
        self.username_entry.pack(fill="x", pady=(0, 20))

    def create_password_input(self, parent):
        """Tạo ô nhập mật khẩu với nút show/hide"""
        password_label = ctk.CTkLabel(
            parent,
            text="Mật khẩu",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=["#374151", "#e2e8f0"],
            anchor="w"
        )
        password_label.pack(fill="x", pady=(0, 10))

        password_container = ctk.CTkFrame(parent, fg_color="transparent")
        password_container.pack(fill="x", pady=(0, 20))

        self.password_entry = ctk.CTkEntry(
            password_container,
            placeholder_text="Nhập mật khẩu",
            font=ctk.CTkFont(size=16),
            width=400,
            height=50,
            corner_radius=12,
            fg_color=["white", "#475569"],
            border_color=["#d1d5db", "#64748b"],
            placeholder_text_color=["#9ca3af", "#94a3b8"],
            text_color=["#111827", "#f1f5f9"],
            show="●",
            textvariable=self.var_password
        )
        self.password_entry.pack(side="left", fill="x", expand=True)

        self.toggle_btn = ctk.CTkButton(
            password_container,
            text="👁",
            width=45,
            height=45,
            corner_radius=12,
            fg_color=["#f3f4f6", "#475569"],
            hover_color=["#e5e7eb", "#334155"],
            text_color=["#6b7280", "#94a3b8"],
            font=ctk.CTkFont(size=16),
            command=self.toggle_password
        )
        self.toggle_btn.pack(side="right", padx=(8, 0))

    def create_login_button(self, parent):
        """Tạo nút đăng nhập với hiệu ứng loading"""
        self.login_btn = ctk.CTkButton(
            parent,
            text="Đăng nhập",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=55,
            width=400,
            corner_radius=12,
            fg_color=["#1e40af", "#3b82f6"],
            hover_color=["#1d4ed8", "#2563eb"],
            text_color="white",
            command=self.handle_login
        )
        self.login_btn.pack(fill="x", pady=(10, 20))

    def create_extra_options(self, parent):
        """Tạo các tùy chọn bổ sung"""
        forgot_btn = ctk.CTkButton(
            parent,
            text="Quên mật khẩu?",
            font=ctk.CTkFont(size=12, underline=True),
            fg_color="transparent",
            text_color=["#1e40af", "#60a5fa"],
            hover_color=["#f3f4f6", "#334155"],
            width=100,  
            height=25,
            command=self.forgot_password
        )
        forgot_btn.pack()

    def bind_events(self):
        """Bind các sự kiện"""
        self.window.bind('<Return>', lambda e: self.handle_login())
        self.window.bind('<Escape>', lambda e: self.reset())
        self.window.bind('<Configure>', self.on_window_resize)

    def toggle_password(self):
        """Chuyển đổi hiển thị/ẩn mật khẩu"""
        self.show_password = not self.show_password
        if self.show_password:
            self.password_entry.configure(show="")
            self.toggle_btn.configure(text="🙈", text_color=["#1e40af", "#60a5fa"])
        else:
            self.password_entry.configure(show="●")
            self.toggle_btn.configure(text="👁", text_color=["#6b7280", "#94a3b8"])

    def handle_login(self):
        """Xử lý đăng nhập với loading animation"""
        if self.is_loading:
            return
            
        # Validation với thông báo đẹp
        if not self.var_email.get().strip():
            self.show_error_notification("Vui lòng nhập tên đăng nhập hoặc email!")
            self.username_entry.focus()
            return
            
        if not self.var_password.get().strip():
            self.show_error_notification("Vui lòng nhập mật khẩu!")
            self.password_entry.focus()
            return

        # Hiển thị thông báo bắt đầu xác thực
        self.show_info_notification("Đang xác thực thông tin đăng nhập...")
        
        # Bắt đầu loading
        self.start_loading()
        
        # Chạy xác thực trong thread riêng
        threading.Thread(target=self.authenticate_user, daemon=True).start()

    def start_loading(self):
        """Bắt đầu hiệu ứng loading"""
        self.is_loading = True
        self.login_btn.configure(
            text="Đang xác thực...",
            state="disabled",
            fg_color=["#9ca3af", "#6b7280"]
        )
        self.animate_loading()

    def animate_loading(self):
        """Animation cho loading button"""
        if not self.is_loading:
            return
            
        try:
            current_text = self.login_btn.cget("text")
            if current_text.endswith("..."):
                self.login_btn.configure(text="Đang xác thực")
            elif current_text.endswith(".."):
                self.login_btn.configure(text="Đang xác thực...")
            elif current_text.endswith("."):
                self.login_btn.configure(text="Đang xác thực..")
            else:
                self.login_btn.configure(text="Đang xác thực.")
            
            self.window.after(300, self.animate_loading)
        except:
            pass

    def stop_loading(self):
        """Dừng hiệu ứng loading"""
        self.is_loading = False
        try:
            self.login_btn.configure(
                text="Đăng nhập",
                state="normal",
                fg_color=["#1e40af", "#3b82f6"]
            )
        except:
            pass

    def authenticate_user(self):
        """Xác thực người dùng trong background"""
        try:
            time.sleep(1)  # Giả lập thời gian xử lý
            
            role_map = {
                "Quản trị viên": "Admin",
                "Giảng viên": "Teacher", 
                "Kế toán": "Department"
            }
            selected_role = role_map[self.var_role.get()]
            
            user = verify_user(self.var_email.get().strip(), self.var_password.get())
            self.window.after(0, lambda: self.handle_auth_result(user, selected_role))
            
        except Exception as e:
            error_msg = str(e)
            self.window.after(0, lambda: self.handle_auth_error(error_msg))

    def handle_auth_result(self, user, selected_role):
        """Xử lý kết quả xác thực"""
        self.stop_loading()
        
        if user is None:
            self.show_modern_error(
                "Thông tin đăng nhập không chính xác!\n\n"
                "Vui lòng kiểm tra lại tên đăng nhập và mật khẩu."
            )
            return

        if user['role'] != selected_role:
            self.show_modern_warning(
                f"Quyền truy cập bị từ chối!\n\n"
                f"Tài khoản này không có quyền truy cập vào vai trò {self.var_role.get()}.\n"
                f"Vai trò hiện tại của bạn: {self.get_role_name(user['role'])}"
            )
            return

        # Đăng nhập thành công
        user_name = user.get('name', user.get('email', 'User'))
        role_name = self.var_role.get()
        
        self.show_success_notification(
            f"Chào mừng {user_name}!\nĐăng nhập thành công với vai trò {role_name}"
        )
        
        # Delay một chút để user thấy thông báo thành công
        self.window.after(2000, lambda: self.open_main_app(user))

    def handle_auth_error(self, error_msg):
        """Xử lý lỗi xác thực"""
        self.stop_loading()
        self.show_modern_error(
            f"Lỗi hệ thống!\n\n"
            f"Chi tiết: {error_msg}\n\n"
            f"Vui lòng thử lại hoặc liên hệ quản trị viên."
        )

    def get_role_name(self, role_code):
        """Chuyển đổi role code thành tên hiển thị"""
        role_names = {
            "Admin": "Quản trị viên",
            "Teacher": "Giảng viên",
            "Department": "Kế toán"
        }
        return role_names.get(role_code, role_code)

    def open_main_app(self, user):
        """Mở ứng dụng chính"""
        try:
            self.reset()
            self.window.withdraw()

            new_window = Toplevel(self.window)
            new_window.state('zoomed')
            
            if user['role'] == 'Teacher':
                self.app = TeacherView(new_window, user)
            elif user['role'] == 'Admin':
                self.app = AdminView(new_window, user)
            elif user['role'] == 'Department':
                self.app = AccountantView(new_window, user)
            else:
                raise Exception(f"Vai trò không được hỗ trợ: {user['role']}")
                
        except Exception as e:
            print(f"Error opening main app: {e}")
            new_window.destroy() if 'new_window' in locals() else None
            self.window.deiconify()
            self.show_modern_error(f"Lỗi khi mở ứng dụng chính!\n\nChi tiết: {str(e)}")

    # === NOTIFICATION METHODS ===
    
    def show_success_notification(self, message):
        """Hiển thị thông báo thành công"""
        try:
            notification = CustomNotification(
                self.window, 
                message, 
                "success", 
                duration=3000
            )
            notification.show()
        except Exception as e:
            print(f"Error showing success notification: {e}")
            messagebox.showinfo("Thành công", message)
        
    def show_error_notification(self, message):
        """Hiển thị thông báo lỗi"""
        try:
            notification = CustomNotification(
                self.window, 
                message, 
                "error", 
                duration=4000
            )
            notification.show()
        except Exception as e:
            print(f"Error showing error notification: {e}")
            messagebox.showerror("Lỗi", message)
        
    def show_warning_notification(self, message):
        """Hiển thị thông báo cảnh báo"""
        try:
            notification = CustomNotification(
                self.window, 
                message, 
                "warning", 
                duration=4000
            )
            notification.show()
        except Exception as e:
            print(f"Error showing warning notification: {e}")
            messagebox.showwarning("Cảnh báo", message)
        
    def show_info_notification(self, message):
        """Hiển thị thông báo thông tin"""
        try:
            notification = CustomNotification(
                self.window, 
                message, 
                "info", 
                duration=2000
            )
            notification.show()
        except Exception as e:
            print(f"Error showing info notification: {e}")
            messagebox.showinfo("Thông báo", message)

    def show_modern_error(self, message):
        """Hiển thị dialog lỗi hiện đại"""
        try:
            dialog = ModernDialog(
                self.window,
                "Đăng nhập thất bại",
                message,
                "error",
                ["Thử lại"]
            )
            dialog.show()
        except Exception as e:
            print(f"Error showing modern error dialog: {e}")
            messagebox.showerror("Đăng nhập thất bại", message)
        
    def show_modern_warning(self, message):
        """Hiển thị dialog cảnh báo hiện đại"""
        try:
            dialog = ModernDialog(
                self.window,
                "Cảnh báo quyền truy cập", 
                message,
                "warning",
                ["Đã hiểu"]
            )
            dialog.show()
        except Exception as e:
            print(f"Error showing modern warning dialog: {e}")
            messagebox.showwarning("Cảnh báo quyền truy cập", message)

    def forgot_password(self):
        """Xử lý quên mật khẩu với dialog đẹp"""
        try:
            dialog = ModernDialog(
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
            
            result = dialog.show()
            if result == "Sao chép Email":
                # Copy email to clipboard
                try:
                    self.window.clipboard_clear()
                    self.window.clipboard_append("admin@phenikaa.edu.vn")
                    self.show_info_notification("Đã sao chép email vào clipboard!")
                except:
                    messagebox.showinfo("Thông báo", "Email: admin@phenikaa.edu.vn")
        except Exception as e:
            print(f"Error in forgot_password: {e}")
            messagebox.showinfo(
                "Khôi phục mật khẩu",
                "Liên hệ admin@phenikaa.edu.vn hoặc 024-6291-8088 để khôi phục mật khẩu."
            )

    def reset(self):
        """Reset form về trạng thái ban đầu"""
        self.var_email.set("")
        self.var_password.set("")
        self.var_role.set("Giảng viên")
        self.show_password = False
        try:
            self.password_entry.configure(show="●")
            self.toggle_btn.configure(text="👁", text_color=["#6b7280", "#94a3b8"])
        except:
            pass
        self.stop_loading()

    def show(self):
        """Hiển thị cửa sổ đăng nhập"""
        try:
            self.window.update()
            self.window.deiconify()
        except:
            pass

    def on_window_resize(self, event=None):
        """Xử lý khi cửa sổ thay đổi kích thước"""
        if event and event.widget == self.window:
            try:
                if hasattr(self, 'bg_img') and self.bg_img:
                    window_width = self.window.winfo_width()
                    left_panel_width = window_width * 0.4
                    new_size = min(int(left_panel_width * 0.7), 300)
                    if new_size > 100:
                        self.bg_img.configure(size=(new_size, new_size))
            except:
                pass

if __name__ == '__main__':
    try:
        window = ctk.CTk()
        if os.path.exists("icon.ico"):
            window.iconbitmap("icon.ico")
        app = LoginPage(window)
        window.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Lỗi", f"Không thể khởi động ứng dụng: {e}")