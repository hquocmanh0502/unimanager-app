from customtkinter import CTk
from login_view import LoginPage

if __name__ == "__main__":
    root = CTk()
    app = LoginPage(root)
    root.mainloop()