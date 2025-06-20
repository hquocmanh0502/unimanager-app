import tkinter as tk
from tkinter import ttk

root = tk.Tk()

# Sample data
colors = ["Red", "Green", "Blue"]

# Create combobox
color_combobox = ttk.Combobox(root, values=colors)
color_combobox.set("Select a Color")  # Set default value
color_combobox.pack(pady=20)

# Function to handle selection
def color_selected(event):
    selected_color = color_combobox.get()
    print(f"You selected: {selected_color}")

color_combobox.bind("<<ComboboxSelected>>", color_selected)

root.mainloop()