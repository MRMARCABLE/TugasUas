#   ========================================================================
#                                  LIBRARY
#   ========================================================================
import customtkinter as ctk
import pandas as pd
import os
import uuid
import shutil
from datetime import datetime
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from barcode.ean import EAN13
from barcode.writer import ImageWriter
from IPython.display import Image, display
import segno

#   ========================================================================
#                             CONFIGURASI TAMPILAN
#   ========================================================================
ctk.set_appearance_mode("Dark")                                      # membuat seluruh tema UI gelap
ctk.set_default_color_theme("blue")                                  # warna utama

#   ========================================================================
#                        DATABASE MANAGER (AUTO REPAIR)
#   ========================================================================
DATA_DIR = "data"                                                    # folder tempat semua file CSV disimpan
FILES = {                                                            # dictionary yang mengubah nama dataset ke file CSV
    "users": os.path.join(DATA_DIR, "users.csv"),
    # "menu": os.path.join(DATA_DIR, "namafile"),
    # "orders": os.path.join(DATA_DIR, "namafile"),
    # "items": os.path.join(DATA_DIR, "namafile")
}

def init_db():                                                       # membuat folder database dan menjalankan file CSV
    os.makedirs(DATA_DIR, exist_ok=True)                             # membuat folder "data" (nggak eror jika folder sudah terbuat)

    # 1. USERS
    if not os.path.exists(FILES["users"]):                           # Mengecek apakah file users.csv sudah ada, jika belum akan membuat file user dahulu
        users_data = [
            {"username": "admin", "password": "123", "role": "admin"},
            {"username": "cashier", "password": "123", "role": "cashier"},
            {"username": "waiter", "password": "123", "role": "waiter"},
            {"username": "owner", "password": "123", "role": "owner"},
        ]
        pd.DataFrame(users_data).to_csv(FILES["users"], index=False) # mengubah list dictionary menjadi DataFrame Pandas lalu
                                                                     # menyimpan DataFrame ke file CSV tanpa kolom index otomatis

    # 2. MENUS
    # if not os.path.exists(FILES["namafile"]):
    #     menu_data = [

    #     ]

    # 3. ORDERS

    # 4. ITEMS

def get_df(key):
    try:
        df = pd.read_csv(FILES[key], dtype=str)                      # Membaca file CSV sebagai DataFrame dan memastikan semuanya dalam bentuk string
        if key == "orders" and "customer" not in df.columns:           # Anti-crash
            print("Struktur data order salah. Mengembalikan frame kosong aman.")
            return pd.DataFrame(columns=["id", "waiter", "customer", "total", "date", "status"])
        return df
    
    except Exception as e:                                           # Jika file CSV bermasalah akan muncul teks eror
        print(f"Gagal membaca {key}: {e}")
        return pd.DataFrame()
    
def save_df(key, df):                                                # Menyimpan DataFrame kembali ke CSV
    df.to_csv(FILES[key], index=False)

#   ========================================================================
#                                 TABLE MAP
#   ========================================================================
# class TableMap(ctk.CTkFrame):



#   ========================================================================
#                                    FITUR
#   ========================================================================

class LoginFrame(ctk.CTkFrame):                                      # UI khusus untuk login
    def __init__(self, master, callback):
        super().__init__(master)
        box = ctk.CTkFrame(self, width=320, height=450, corner_radius=15)
        box.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(box, text="CAFE GUI", font=("Arial", 24, "bold")).pack(pady=30)
        self.entry_u = ctk.CTkEntry(box, placeholder_text="Username"); self.entry_u.pack(pady=10)
        self.entry_p = ctk.CTkEntry(box, placeholder_text="Password", show="*"); self.entry_p.pack(pady=10)
        ctk.CTkButton(box, text="LOGIN", command=lambda: self.do_login(callback)).pack(pady=20)
        ctk.CTkButton(box, text="Pelanggan (Guest)", fg_color="transparent", border_width=1, command=lambda: callback("pembeli", "Guest")).pack()

    def do_login(self, cb):                                          # Mengecek apakah Username dan Password valid dengan Database
        u, p = self.entry_u.get(), self.entry_p.get()
        df = get_df("users")
        if df.empty: 
            return messagebox.showerror("ERROR", "DATABASE USER KOSONG")
        user = df[(df['username'] == u) & (df['password'] == p)]
        if not user.empty:
            cb(user.iloc[0]['role'], user.iloc[0]['username'])
        else:
            messagebox.showerror("ERROR", "LOGIN GAGAL")

# class OrderFrame(ctk.CTkFrame):

# class WaiterMapFrame(ctk.CTkFrame):

# class GraphFrame(ctk.CTkFrame):

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CAFE GUI")
        self.geometry("1100x700")
        init_db() # FORCE CHECK
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        self.show_login()
    
    def show_login(self):
        for w in self.container.winfo_children():
            w.destroy()
        LoginFrame(self.container, self.on_login).pack(fill="both", expand=True)

    def on_login(self, role, username):
        for w in self.container.winfo_children():
            w.destroy()
        sidebar = ctk.CTkFrame(self.container, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        self.container.grid_columnconfigure(1, weight=1); self.container.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(sidebar, text="RESTO POS", font=("Arial", 20, "bold")).pack(pady=30)
        ctk.CTkLabel(sidebar, text=f"{role.upper()}", text_color="gray").pack(pady=(0, 20))

        content = ctk.CTkFrame(self.container, fg_color="transparent")
        content.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.frames = {}

        if role in ['pembeli', 'cashier', 'waiter']:
            self.add_btn(sidebar, "Buat Pesanan", lambda: OrderFrame(content, username, role))
        if role == 'waiter':
            self.add_btn(sidebar, "Denah & Antar", lambda: WaiterMapFrame(content))
        if role in ['admin', 'owner']:
            self.add_btn(sidebar, "Grafik Penjualan", lambda: GraphFrame(content))

        ctk.CTkButton(sidebar, text="LOGOUT", fg_color="red", command=self.show_login).pack(side="bottom", pady=20, padx= 10)

    def add_btn(self, parent, text, cmd):
        def wrapper():
            for k, v in self.frames.items():
                v.pack_forget()
            frame = cmd(); frame.pack(fill="both", expand=True); self.frames["active"] = frame
        ctk.CTkButton(parent, text=text, fg_color="transparent", border_width=1, command=wrapper).pack(pady=5, padx=10, fill="x")

if __name__ == "__main__":                                            # Menjalankan GUI
    app = MainApp()
    app.mainloop()