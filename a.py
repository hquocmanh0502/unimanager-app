import customtkinter as ctk
import tkinter as tk
from PIL import Image
import os
from typing import Optional, List, Dict
from customtkinter import CTkImage

class ModernNavbar(ctk.CTkFrame):
    def __init__(self, parent, menu_items=None, logout_callback=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Configuration
        self.settings = {
            "theme": {
                "primary": "#1E3A8A",
                "secondary": "#2A4B8D",
                "hover": "#4A78E0",
                "text": "white",
                "text_secondary": "#b0bec5",
                "logout": "#DC3545",
                "logout_hover": "#B02A37"
            },
            "sizes": {
                "expanded": 250
            }
        }
        
        # State
        self.active_dropdown = None
        self.account_panel_visible = False
        self.menu_frames = []
        self.submenu_visible = {}
        self.logout_callback = logout_callback  # Lưu hàm logout
        
        # Menu items
        self.menu_items = menu_items or self.get_default_menu_items()
        for item in self.menu_items:
            if item.get("submenu"):
                self.submenu_visible[item["label"]] = False
        
        # Setup
        self.configure(fg_color=self.settings["theme"]["primary"], width=self.settings["sizes"]["expanded"])
        self.setup_ui()
        
    def get_default_menu_items(self):
        """Return default menu items if none are provided."""
        return [
            {
                "label": "Quản lý giáo viên",
                "icon": "👨",
                "submenu": [
                    {"label": "Bằng cấp", "command": lambda: print("Default: Bằng cấp clicked")},
                    {"label": "Khoa", "command": lambda: print("Default: Khoa clicked")},
                    {"label": "Giáo viên", "command": lambda: print("Default: Giáo viên clicked")}
                ]
            },
            {
                "label": "Quản lý lớp học phần",
                "icon": "📚",
                "submenu": [
                    {"label": "Học phần", "command": lambda: print("Default: Học phần clicked")},
                    {"label": "Kỳ học", "command": lambda: print("Default: Kỳ học clicked")},
                    {"label": "Lớp học", "command": lambda: print("Default: Lớp học clicked")}
                ]
            },
            {
                "label": "Thống kê",
                "icon": "📊",
                "submenu": [
                    {"label": "Thống kê giáo viên", "command": lambda: print("Default: Thống kê giáo viên clicked")},
                    {"label": "Thống kê lớp", "command": lambda: print("Default: Thống kê lớp clicked")}
                ]
            },
            {
                "label": "Tiền dạy",
                "icon": "💰",
                "submenu": [
                    {"label": "Định mức tiền theo tiết", "command": lambda: print("Default: Định mức tiền theo tiết clicked")},
                    {"label": "Hệ số giáo viên", "command": lambda: print("Default: Hệ số giáo viên clicked")},
                    {"label": "Hệ số lớp", "command": lambda: print("Default: Hệ số lớp clicked")},
                    {"label": "Tính tiền dạy", "command": lambda: print("Default: Tính tiền dạy clicked")}
                ]
            },
            {
                "label": "Báo cáo",
                "icon": "📈",
                "submenu": [
                    {"label": "Tiền dạy theo năm", "command": lambda: print("Default: Tiền dạy theo năm clicked")},
                    {"label": "Tổng tiền dạy", "command": lambda: print("Default: Tổng tiền dạy clicked")}
                ]
            }
        ]
        
    def setup_ui(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.main_container.pack(fill="both", expand=True)
        
        self.create_header()
        self.create_menu()
        self.create_footer()
        
    def create_header(self):
        self.header = ctk.CTkFrame(self.main_container, fg_color="transparent", height=80)
        self.header.pack(fill="x", pady=(10, 0))
        
        self.logo_frame = ctk.CTkFrame(self.header, fg_color="transparent", width=150, height=50)
        self.logo_frame.pack(expand=True)
        
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(script_dir, "logo.png")
            if os.path.exists(logo_path):
                logo_image = Image.open(logo_path)
                self.logo = CTkImage(light_image=logo_image, dark_image=logo_image, size=(115, 75))
                self.logo_label = ctk.CTkLabel(self.logo_frame, image=self.logo, text="")
            else:
                self.logo_label = ctk.CTkLabel(self.logo_frame, text="[Logo Placeholder]", font=ctk.CTkFont(size=14, weight="bold"))
        except Exception as e:
            print(f"Error loading logo: {e}")
            self.logo_label = ctk.CTkLabel(self.logo_frame, text="[Logo Placeholder]", font=ctk.CTkFont(size=14, weight="bold"))
        self.logo_label.pack(pady=(10, 15))
        
    def create_menu(self):
        self.menu_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.menu_container.pack(fill="both", expand=True, pady=10)
        
        for item in self.menu_items:
            self.create_menu_item(item)
            
    def create_menu_item(self, item: Dict):
        btn_frame = ctk.CTkFrame(self.menu_container, fg_color="transparent", corner_radius=5, height=40)
        btn_frame.pack(fill="x", pady=2)
        self.menu_frames.append(btn_frame)
        
        icon_label = ctk.CTkLabel(btn_frame, text=item["icon"], font=ctk.CTkFont(size=16), text_color="white")
        icon_label.pack(side="left", padx=10)
        
        text_label = ctk.CTkLabel(btn_frame, text=item["label"], anchor="w", font=ctk.CTkFont(size=18, weight="bold"), text_color="white")
        text_label.pack(side="left", fill="x", expand=True)
        
        if item.get("submenu"):
            arrow = ctk.CTkLabel(btn_frame, text="▶" if not self.submenu_visible[item["label"]] else "▼", font=ctk.CTkFont(size=12))
            arrow.pack(side="right", padx=10)
            
            submenu = ctk.CTkFrame(self.menu_container, fg_color=self.settings["theme"]["secondary"], corner_radius=5)
            btn_frame.submenu = submenu
            btn_frame.arrow = arrow
            
            for sub_item in item["submenu"]:
                sub_btn = ctk.CTkButton(submenu, text=sub_item["label"], command=sub_item.get("command"),
                                       fg_color="transparent", hover_color=self.settings["theme"]["hover"], anchor="w",
                                       font=ctk.CTkFont(size=14), cursor="hand2")
                sub_btn.pack(fill="x", padx=5, pady=2)
            
            def toggle_submenu(event=None):
                if self.active_dropdown and self.active_dropdown != btn_frame:
                    self.active_dropdown.submenu.pack_forget()
                    self.active_dropdown.arrow.configure(text="▶")
                    self.submenu_visible[self.active_dropdown.label] = False
                if self.submenu_visible[item["label"]]:
                    submenu.pack_forget()
                    arrow.configure(text="▶")
                    self.submenu_visible[item["label"]] = False
                    self.active_dropdown = None
                else:
                    submenu.pack(fill="x", padx=20, pady=(0, 5), after=btn_frame)
                    arrow.configure(text="▼")
                    self.submenu_visible[item["label"]] = True
                    self.active_dropdown = btn_frame
                    btn_frame.label = item["label"]
            
            for widget in [btn_frame, text_label, icon_label, arrow]:
                widget.bind("<Button-1>", toggle_submenu)
                widget.configure(cursor="hand2")
        
        def on_enter(e):
            btn_frame.configure(fg_color=self.settings["theme"]["hover"])
        def on_leave(e):
            btn_frame.configure(fg_color="transparent")
            
        for widget in [btn_frame, text_label, icon_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
        
    def create_footer(self):
        self.footer = ctk.CTkFrame(self.main_container, fg_color=self.settings["theme"]["secondary"], corner_radius=10, height=80)
        self.footer.pack(fill="x", pady=10, padx=5)
        
        self.avatar_frame = ctk.CTkFrame(self.footer, width=40, height=40, corner_radius=20)
        self.avatar_frame.pack(side="left", padx=10, pady=10)
        
        try:
            avatar_path = os.path.join(os.path.dirname(__file__), "avatar.png")
            if os.path.exists(avatar_path):
                avatar_img = Image.open(avatar_path)
                self.avatar = CTkImage(light_image=avatar_img, dark_image=avatar_img, size=(40, 40))
                avatar_label = ctk.CTkLabel(self.avatar_frame, image=self.avatar, text="")
            else:
                avatar_label = ctk.CTkLabel(self.avatar_frame, text="US", font=ctk.CTkFont(size=16, weight="bold"))
        except Exception as e:
            print(f"Error loading avatar: {e}")
            avatar_label = ctk.CTkLabel(self.avatar_frame, text="US", font=ctk.CTkFont(size=16, weight="bold"))
        avatar_label.pack(expand=True)
        
        info_frame = ctk.CTkFrame(self.footer, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, pady=10)
        
        username = ctk.CTkLabel(info_frame, text="User Name", font=ctk.CTkFont(size=14, weight="bold"))
        username.pack(anchor="w")
        
        role = ctk.CTkLabel(info_frame, text="Administrator", font=ctk.CTkFont(size=12), text_color=self.settings["theme"]["text_secondary"])
        role.pack(anchor="w")
        
        account_btn = ctk.CTkButton(self.footer, text="▼", width=30, command=self.toggle_account_panel,
                                  fg_color="transparent", hover_color=self.settings["theme"]["hover"], cursor="hand2")
        account_btn.pack(side="right", padx=10)
        self.account_btn = account_btn
        
        self.account_panel = ctk.CTkFrame(self.main_container, fg_color=self.settings["theme"]["secondary"], corner_radius=10)
        self.account_panel.pack_forget()
        
        profile_btn = ctk.CTkButton(self.account_panel, text="Profile", width=80, command=lambda: print("View Profile"),
                                  fg_color="transparent", hover_color=self.settings["theme"]["hover"], cursor="hand2")
        profile_btn.pack(side="left", padx=5, pady=5)
        
        logout_btn = ctk.CTkButton(self.account_panel, text="Đăng xuất", width=80, command=self.logout_callback,
                                 fg_color=self.settings["theme"]["logout"], hover_color=self.settings["theme"]["logout_hover"],
                                 font=ctk.CTkFont(size=12, weight="bold"), cursor="hand2")
        logout_btn.pack(side="left", padx=5, pady=5)
        
    def toggle_account_panel(self):
        if self.account_panel_visible:
            self.account_panel.pack_forget()
            self.account_btn.configure(text="▼")
            self.account_panel_visible = False
        else:
            self.account_panel.pack(fill="x", padx=5, pady=(0, 5), after=self.footer)
            self.account_btn.configure(text="▲")
            self.account_panel_visible = True
            if self.active_dropdown:
                self.active_dropdown.submenu.pack_forget()
                self.active_dropdown.arrow.configure(text="▶")
                self.submenu_visible[self.active_dropdown.label] = False
                self.active_dropdown = None

class ModernApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Modern Navigation Demo")
        self.geometry("1000x600")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.navbar = ModernNavbar(self, width=250, corner_radius=0)
        self.navbar.grid(row=0, column=0, sticky="nsew")
        
        self.content = ctk.CTkFrame(self, fg_color="#f5f6fa")
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        header_frame = ctk.CTkFrame(self.content, fg_color="#ffffff", corner_radius=10)
        header_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header_frame, text="Dashboard Overview", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=15, padx=20, anchor="w")
        
        content_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        content_frame.grid_columnconfigure((0, 1), weight=1)
        
        for i, title in enumerate(["Active Projects", "Pending Tasks", "Upcoming Events", "Recent Reports"]):
            card = ctk.CTkFrame(content_frame, fg_color="#ffffff", corner_radius=10)
            card.grid(row=i//2, column=i%2, sticky="nsew", padx=10, pady=10)
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
            ctk.CTkLabel(card, text=f"Sample data for {title.lower()}", font=ctk.CTkFont(size=10)).pack(pady=5)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    app = ModernApp()
    app.mainloop()