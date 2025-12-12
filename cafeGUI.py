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
    "orders": os.path.join(DATA_DIR, "orders.csv"),
    "items": os.path.join(DATA_DIR, "items.csv")
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
    if not os.path.exists(FILES["orders"]):
        pd.DataFrame(columns=["id", "waiter", "customer", "total", "date", "status"]).to_csv(FILES["orders"], index=False)

    # 4. ITEMS
    if not os.path.exists(FILES["items"]):
        items_data = [
            {"id": "I001", "name": "Chicken", "price": "15000", "category": "Food", "stock": "100"},
            {"id": "I002", "name": "Drink", "price": "5000", "category": "Beverage", "stock": "100"},
            {"id": "I003", "name": "Rice", "price": "5000", "category": "Food", "stock": "100"},
            {"id": "I004", "name": "French Fries", "price": "10000", "category": "Side", "stock": "50"},
            {"id": "I005", "name": "Nugget", "price": "12000", "category": "Side", "stock": "50"},
        ]
        pd.DataFrame(items_data).to_csv(FILES["items"], index=False)

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
class TableMap(ctk.CTkFrame):
    def __init__(self, master, role, command_callback=None):
        super().__init__(master, fg_color="transparent")
        self.role = role
        self.callback = command_callback
        self.tables = [f"Meja {i}" for i in range(1,10)]

        ctk.CTkLabel(self, text="DENAH MEJA CAFE", font=("Arial", 16, "bold")).pack(pady=(0,10))
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack()
        self.refresh_map()
    
    def refresh_map(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()

        df_orders = get_df("orders")
        occupied_tables = []
        
        if not df_orders.empty:
            active = df_orders[df_orders['status'] == 'Pending']
            occupied_tables = active['customer'].unique().tolist()

        for i, table_name in enumerate(self.tables):
            row = i // 3
            col = i % 3
            is_occupied = table_name in occupied_tables

            if is_occupied:
                color = "#C0392B"
                status_text = "Terisi"
            else:
                color = "#27AE60"
                status_text = "Kosong"

            btn = ctk.CTkButton(
                self.grid_frame,
                text=f"{table_name}\n{status_text}",
                fg_color=color, 
                width=100,
                height=80,
                corner_radius=10,
                state="normal",
                command=lambda t=table_name, occ=is_occupied: self.on_click(t, occ)
            )
            btn.grid(row=row, column=col, padx=10, pady=10)

    def on_click(self, table_name, is_occupied):
        if self.callback: self.callback(table_name, is_occupied)



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

class OrderFrame(ctk.CTkFrame):
    def __init__(self, master, username, role):
        super().__init__(master)
        self.username = username
        self.role = role
        self.cart = {} # {item_id: quantity}
        self.selected_table = None
        self.selected_category = "All"

        # Layout
        self.grid_columnconfigure(0, weight=3) # Menu area
        self.grid_columnconfigure(1, weight=1) # Cart area
        self.grid_rowconfigure(0, weight=1)

        # Left: Menu + Table Map
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.table_map = TableMap(self.left_frame, role=role, command_callback=self.select_table)
        self.table_map.pack(fill="x", pady=(0, 20))

        # Kategori dari file CSV
        df_items = get_df("items")
        unique_categories = df_items['category'].dropna().str.strip().str.title().unique()
        self.categories = ["All"] + sorted(unique_categories)

        # Dropdown kategori
        self.category_combo = ctk.CTkComboBox(
            self.left_frame,
            values=self.categories,
            command=self.filter_by_category
        )
        self.category_combo.set("All")
        self.category_combo.pack(pady=(0, 10), padx=5, fill="x")

        self.menu_frame = ctk.CTkScrollableFrame(self.left_frame, label_text="MENU")
        self.menu_frame.pack(fill="both", expand=True)
        
        # Right: Cart
        self.cart_frame = ctk.CTkFrame(self)
        self.cart_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.lbl_table = ctk.CTkLabel(
            self.cart_frame,
            text="Pilih Meja Hijau...",
            font=("Arial", 16, "bold"),
            text_color="orange"
            )
        self.lbl_table.pack(pady=10)

        ctk.CTkLabel(self.cart_frame, text="ORDER SUMMARY", font=("Arial", 18, "bold")).pack(pady=10)
        self.cart_list = ctk.CTkScrollableFrame(self.cart_frame)
        self.cart_list.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.total_label = ctk.CTkLabel(self.cart_frame, text="Total: Rp 0", font=("Arial", 16, "bold"))
        self.total_label.pack(pady=10)
        
        # curr_row = 0
        if role != 'pembeli':
             self.customer_entry = ctk.CTkEntry(self.cart_frame, placeholder_text="Customer Name")
             self.customer_entry.pack(pady=5, padx=10, fill="x")

        ctk.CTkButton(self.cart_frame, text="CHECKOUT", fg_color="green", command=self.checkout).pack(pady=20, fill="x", padx=10)
        
        self.load_menu()

    def filter_by_category(self, choice):
        self.selected_category = choice.strip().title()
        self.load_menu()
        
    def load_menu(self):
        for w in self.menu_frame.winfo_children():
            w.destroy()

        df_items = get_df("items")
        if df_items.empty:
            ctk.CTkLabel(self.menu_frame, text="No items available").pack(pady=20)
            return

        if self.selected_category != "All":
            df_items = df_items[df_items['category'].str.strip().str.lower() == self.selected_category.lower()]

        row, col = 0, 0
        for _, row_data in df_items.iterrows():
            self.create_item_card(row_data).grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            col += 1
            if col > 2: # 3 items per row
                col = 0
                row += 1

    def create_item_card(self, item):
        card = ctk.CTkFrame(self.menu_frame, border_width=1)
        
        ctk.CTkLabel(card, text=item['name'], font=("Arial", 16, "bold")).pack(pady=(10,5))
        ctk.CTkLabel(card, text=f"Rp {item['price']}").pack(pady=5)
        ctk.CTkLabel(card, text=f"[{item['category']}]", font=("Arial", 12), text_color="gray").pack(pady=(0,5))
        ctk.CTkButton(card, text="ADD", width=100, command=lambda: self.add_to_cart(item)).pack(pady=10, padx=10)
        
        return card
    
    def select_table(self, table_name, is_occupied):
        if is_occupied:
            return messagebox.showwarning("Penuh", "Meja sedang dipakai.")
        self.selected_table = table_name
        self.lbl_table.configure(text=f"Selected: {table_name}", text_color="#2ECC71")

    def add_to_cart(self, item):
        if not self.selected_table:
            return messagebox.showwarning("Pilih Meja", "Silahkan klik meja warna HIJAU dahulu")

        item_id = item['id']
        if item_id in self.cart:
            self.cart[item_id]['qty'] += 1
        else:
            self.cart[item_id] = {'name': item['name'], 'price': int(item['price']), 'qty': 1}
        self.update_cart_ui()

    def update_cart_ui(self):
        for w in self.cart_list.winfo_children():
            w.destroy()
        
        total = 0
        for item_id, data in self.cart.items():
            subtotal = data['price'] * data['qty']
            total += subtotal
            
            row = ctk.CTkFrame(self.cart_list, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"{data['name']} x{data['qty']}", font=("Arial", 12)).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"Rp {subtotal}", font=("Arial", 12, "bold")).pack(side="right", padx=5)
        
        self.total_label.configure(text=f"Total: Rp {total}")

    def checkout(self):
        if not self.cart:
            return messagebox.showwarning("Empty", "Cart is empty!")
        
        if not self.selected_table:
            return messagebox.showwarning("Pilih Meja", "Silahkan pilih meja dahulu")
            
        # "customer" = customer_name
        # if self.role != 'pembeli':
        #      customer_name = self.customer_entry.get()
        #      if not customer_name:
        #          return messagebox.showwarning("Missing Info", "Please enter customer name!")

        total = sum(d['price'] * d['qty'] for d in self.cart.values())
        order_id = str(uuid.uuid4())[:8]
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        new_order = {
            "order_id": order_id,
            "waiter": self.username if self.role in ['waiter'] else 'Self',
            "customer": self.selected_table,
            "total": total,
            "date": date,
            "status": "Pending"
        }
        
        df_orders = get_df("orders")
        df_orders = pd.concat([df_orders, pd.DataFrame([new_order])], ignore_index=True)
        save_df("orders", df_orders)
            
        messagebox.showinfo("Success", f"Order {order_id} Placed!\nTotal: Rp {total}")

        self.cart = {}
        self.update_cart_ui()
        # if self.role != 'pembeli': self.customer_entry.delete(0, 'end')

        # except Exception as e:
        #     messagebox.showerror("Error", f"Failed to save order: {e}")

class ManageMenuFrame(ctk.CTkFrame):
    CATEGORIES = ["Promo", "Paket", "Minuman", "Dessert"] # CONTOH TAMBAHIN/EDIT NANTI

    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Kelola Menu", font=("Arial", 20, "bold")).pack(pady=10)

    # Scrollable list menu
        self.menu_list_frame = ctk.CTkScrollableFrame(self)
        self.menu_list_frame.pack(fill="both", expand=True, padx=10, pady=0)

    # Tambah/edit menu
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(fill="both", padx=10, pady=10)
        ctk.CTkLabel(self.form_frame, text="Nama Menu:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_name = ctk.CTkEntry(self.form_frame)
        self.entry_name.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(self.form_frame, text="Harga:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_price = ctk.CTkEntry(self.form_frame)
        self.entry_price.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(self.form_frame, text="Kategori:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.combo_category = ctk.CTkComboBox(self.form_frame, values=self.CATEGORIES)
        self.combo_category.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        self.form_frame.grid_columnconfigure(1, weight=1)

        self.btn_add = ctk.CTkButton(self.form_frame, text="Tambah Menu", fg_color="green", command=self.add_menu)
        self.btn_add.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

        self.selected_item_id = None
        self.load_menu()

    def load_menu(self):
        for w in self.menu_list_frame.winfo_children():
            w.destroy()

        df = get_df("items")
        if df.empty:
            ctk.CTkLabel(self.menu_list_frame, text="Belum ada menu").pack(pady=20)
            return

        for _, row in df.iterrows():
            self.create_menu_card(row).pack(fill="x", padx=10, pady=5)

    def create_menu_card(self, row):
        card = ctk.CTkFrame(self.menu_list_frame, fg_color="#333333", corner_radius=10)
        ctk.CTkLabel(card, text=f"{row['name']} - Rp {row['price']}", font=("Arial", 14, "bold")).pack(side="left", padx=10, pady=5)
        ctk.CTkLabel(card, text=f"[{row['category']}]", font=("Arial", 12), text_color="gray").pack(side="left", padx=5)

        btn_edit = ctk.CTkButton(card, text="Edit", width=60, command=lambda i=row['id']: self.edit_menu(i))
        btn_edit.pack(side="right", padx=5)
        btn_delete = ctk.CTkButton(card, text="Hapus", width=60, fg_color="red", command=lambda i=row['id']: self.delete_menu(i))
        btn_delete.pack(side="right", padx=5)

        return card

    def add_menu(self):
        name = self.entry_name.get().strip()
        price = self.entry_price.get().strip()
        category = self.combo_category.get().strip()

        if not name or not price or not category:
            return messagebox.showwarning("Warning", "Semua field harus diisi!")

        try:
            price = int(price)
        except:
            return messagebox.showwarning("Warning", "Harga harus berupa angka!")

        df = get_df("items")
        new_id = f"I{len(df)+1:03d}" if self.selected_item_id is None else self.selected_item_id

        new_item = {
            "id": new_id,
            "name": name,
            "price": str(price),
            "category": category,
            "stock": "100"  # default stock
        }

        if self.selected_item_id:  # Update menu
            df.loc[df['id'] == self.selected_item_id, ['name','price','category']] = name, str(price), category
            self.selected_item_id = None
            self.btn_add.configure(text="Tambah Menu")
        else:  # Add new menu
            df = pd.concat([df, pd.DataFrame([new_item])], ignore_index=True)

        save_df("items", df)
        self.entry_name.delete(0,'end'); self.entry_price.delete(0,'end'); self.combo_category.set("")
        self.load_menu()

    def edit_menu(self, item_id):
        df = get_df("items")
        row = df[df['id'] == item_id].iloc[0]
        self.entry_name.delete(0,'end'); self.entry_name.insert(0, row['name'])
        self.entry_price.delete(0,'end'); self.entry_price.insert(0, row['price'])
        self.combo_category.set(row['category'])
        self.selected_item_id = item_id
        self.btn_add.configure(text="Update Menu")

    def delete_menu(self, item_id):
        df = get_df("items")
        df = df[df['id'] != item_id]
        save_df("items", df)
        self.load_menu()


class WaiterMapFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="ANTAR PESANAN", font=("Arial", 20, "bold")).pack(pady=10)
        ctk.CTkLabel(self, text="Klik Meja MERAH untuk melihat detail & mengantar makanan.", text_color="gray").pack()
        self.table_map = TableMap(self, role="waiter", command_callback=self.open_table_detail)
        self.table_map.pack(expand=True)

    def open_table_detail(self, table_name, is_occupied):
        if not is_occupied: return messagebox.showinfo("Info", "Meja ini kosong.")
        orders = get_df("orders")
        items = get_df("items")
        if orders.empty: return

        active_order = orders[(orders['customer'] == table_name) & (orders['status'] == "Pending")]
        if active_order.empty: return

        oid = active_order.iloc[0]['id']
        order_items = items[items['order_id'] == oid]
        self.show_popup(table_name, oid, order_items)

    def show_popup(self, table, oid, items_df):
        top = ctk.CTkToplevel(self)
        top.title(f"Detail {table}")
        top.geometry("400x500")
        top.transient(self) # Always on top
        ctk.CTkLabel(top, text=f"Pesanan {table}", font=("Arial", 20, "bold")).pack(pady=20)
        scroll = ctk.CTkScrollableFrame(top)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        txt_list = ""
        for _, row in items_df.iterrows(): txt_list += f"• {row['qty']}x {row['nama']}\n"
        ctk.CTkLabel(scroll, text=txt_list, font=("Arial", 16), justify="left").pack(anchor="w")
        ctk.CTkButton(top, text="ANTAR MAKANAN (SELESAI)", fg_color="green", height=50, command=lambda: self.mark_served(oid, top)).pack(fill="x", padx=20, pady=20)

    def mark_served(self, oid, window):
        df = get_df("orders")
        df.loc[df['id'] == oid, 'status'] = 'Served'
        save_df("orders", df)
        window.destroy()
        messagebox.showinfo("Selesai", "Meja sekarang Kosong (Hijau).")
        self.table_map.refresh_map()

class GraphFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.plot()
    def plot(self):
        df = get_df("orders")
        if df.empty: return
        df['total'] = pd.to_numeric(df['total']); df['date'] = pd.to_datetime(df['date'])
        daily = df.groupby(df['date'].dt.date)['total'].sum()
        
        fig, ax = plt.subplots(figsize=(6,4), dpi=100)
        fig.patch.set_facecolor('#242424'); ax.set_facecolor('#2b2b2b')
        daily.plot(kind='bar', ax=ax, color='#3B8ED0')
        ax.set_title("Pendapatan Harian", color='white')
        ax.tick_params(colors='white'); ax.spines['bottom'].set_color('white'); ax.spines['left'].set_color('white')
        
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True)

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

        if role == 'pembeli':
            self.add_btn(sidebar, "Buat Pesanan", lambda: OrderFrame(content, username, role))
        if role in ['waiter', 'admin', 'owner']:
            self.add_btn(sidebar, "Denah & Antar", lambda: WaiterMapFrame(content))
        if role in ['cashier', 'admin', 'owner']:
            self.add_btn(sidebar, "Proses Pembayaran", lambda: CashierFrame(content))
        if role in ['admin', 'owner']:
            self.add_btn(sidebar, "Grafik Penjualan", lambda: GraphFrame(content))
        if role in ['admin', 'owner']:
            self.add_btn(sidebar, "Menu", lambda: ManageMenuFrame(content))

        ctk.CTkButton(sidebar, text="LOGOUT", fg_color="red", command=self.show_login).pack(side="bottom", pady=20, padx= 10)

    def add_btn(self, parent, text, cmd):
        def wrapper():
            if "active" in self.frames:
                try:
                    self.frames["active"].destroy()
                except:
                    pass
            frame = cmd()
            frame.pack(fill="both", expand=True)
            self.frames["active"] = frame
        ctk.CTkButton(parent, text=text, fg_color="transparent", border_width=1, command=wrapper).pack(pady=5, padx=10, fill="x")

if __name__ == "__main__":                                            # Menjalankan GUI
    app = MainApp()
    app.mainloop()