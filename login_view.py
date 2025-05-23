from tkinter import messagebox, Toplevel
from customtkinter import *
from PIL import Image
from auth import verify_user
from teacher_view import TeacherView
from department_view import DepartmentView
from accountant_view import AccountantView
import os

class LoginPage(object):
    def __init__(self, window):
        # Màn hình
        self.window = window
        self.window.title("Login Page")
        self.window.config(bg="white")
        self.window.resizable(False, False)

        # Biến lưu trữ hình ảnh để giữ tham chiếu
        self.bg_img = None

        # Kiểm tra sự tồn tại của bg1.jpg
        bg_path = "bg1.jpg"
        if os.path.exists(bg_path):
            try:
                self.bg_img = CTkImage(dark_image=Image.open(bg_path), size=(500, 500))
                bg_lab = CTkLabel(self.window, image=self.bg_img, text="")
                bg_lab.grid(row=0, column=0)
            except Exception as e:
                print(f"Lỗi khi tải hình ảnh {bg_path}: {e}")
        else:
            print(f"Hình ảnh {bg_path} không tồn tại, bỏ qua hiển thị hình nền")

        # Biến kiểu string email, password, role
        self.var_email = StringVar()
        self.var_password = StringVar()
        self.var_role = StringVar(value="Department")

        # Frame đăng nhập
        self.frame1 = CTkFrame(self.window, fg_color="#D9D9D9", bg_color="white", height=350, width=300,
                               corner_radius=20)
        self.frame1.grid(row=0, column=1, padx=40)

        # Tiêu đề
        self.title = CTkLabel(self.frame1, text="Ứng dụng quản lý Đại học", text_color="white", font=("", 30, "bold"),
                              fg_color="#4158D0", corner_radius=32, height=50)
        self.title.grid(row=0, column=0, pady=30, padx=10)

        # Nhập tài khoản
        self.username_entry = CTkEntry(self.frame1, text_color="white", placeholder_text="Tài khoản",
                                       fg_color="black", placeholder_text_color="white",
                                       font=("", 16, "bold"), width=200, corner_radius=15, height=45,
                                       textvariable=self.var_email)
        self.username_entry.grid(row=1, column=0, sticky="nwe", padx=30)

        # Nhập mật khẩu
        self.password_entry = CTkEntry(self.frame1, text_color="white", placeholder_text="Mật khẩu",
                                       fg_color="black", placeholder_text_color="white",
                                       font=("", 16, "bold"), width=200, corner_radius=15, height=45,
                                       show="*", textvariable=self.var_password)
        self.password_entry.grid(row=2, column=0, sticky="nwe", padx=30, pady=20)

        # Combobox chọn vai trò
        self.role_combobox = CTkComboBox(self.frame1, values=["Department", "Teacher", "Accountant"],
                                         variable=self.var_role, font=("", 14, "bold"), width=200,
                                         height=45, corner_radius=15, dropdown_font=("", 14))
        self.role_combobox.grid(row=3, column=0, sticky="nwe", padx=30, pady=10)

        # Button đăng nhập
        self.l_btn = CTkButton(self.frame1, text="Đăng nhập", font=("", 15, "bold"), height=40, width=60,
                               fg_color="#0085FF", cursor="hand2",
                               corner_radius=15, command=self.login)
        self.l_btn.grid(row=4, column=0, pady=20, padx=35)

        # # Nhãn thông tin nhóm
        # self.group_info_label = CTkLabel(self.frame1, text="Nhóm 1\n  GVHD : Trịnh Văn Bình\n",
        #                                  text_color="black", font=("Helvetica", 16, "bold"))
        # self.group_info_label.grid(row=5, column=0, pady=10)

    def login(self):
        if self.var_email.get() == "" or self.var_password.get() == "":
            messagebox.showerror("Lỗi !!", "Vui lòng nhập đầy đủ thông tin")
            return

        # Xác thực người dùng
        user = verify_user(self.var_email.get(), self.var_password.get())

        if user is None:
            messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu")
            return

        # Kiểm tra vai trò được chọn
        selected_role = self.var_role.get()
        if user['role'] != selected_role:
            messagebox.showerror("Lỗi", f"Tài khoản này không có vai trò {selected_role}")
            return

        # Đăng nhập thành công
        messagebox.showinfo("Thông báo", f"Đăng nhập thành công với vai trò {user['role']}")
        self.reset()
        self.window.withdraw()

        # Xử lý theo vai trò
        new_window = Toplevel(self.window)
        if user['role'] == 'Teacher':
            self.app = TeacherView(new_window, user)
        elif user['role'] == 'Department':
            self.app = DepartmentView(new_window, user)
        elif user['role'] == 'Accountant':
            self.app = AccountantView(new_window, user)
        else:
            print(f"Đăng nhập thành công với vai trò {user['role']}. User info: {user}")
            new_window.destroy()

    def reset(self):
        self.var_email.set("")
        self.var_password.set("")
        self.var_role.set("Department")

    def show(self):
        self.window.update()
        self.window.deiconify()

if __name__ == '__main__':
    window = CTk()
    obj = LoginPage(window)
    window.mainloop()