# ========================================================================
# LIBRARY
# ========================================================================
import customtkinter as ctk
import pandas as pd
import os
import uuid
from datetime import datetime
from tkinter import messagebox, filedialog
import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import segno
import io
import shutil
# ========================================================================
# CONFIGURASI TAMPILAN
# ========================================================================
ctk.set_appearance_mode("Dark") #untuk mengatur tampilan
ctk.set_default_color_theme("blue") #sama seperti keterangan di atas
# ========================================================================
# DATABASE MANAGER (AUTO REPAIR)
# ========================================================================
DATA_DIR = "data" # folder tempat semua file CSV disimpan
IMAGES_DIR = os.path.join(DATA_DIR, "images") # dictionary yang mengubah nama dataset ke file CSV
FILES = {
    "users": os.path.join(DATA_DIR, "users.csv"),
    "orders": os.path.join(DATA_DIR, "orders.csv"),
    "order_details": os.path.join(DATA_DIR, "order_details.csv"),
    "items": os.path.join(DATA_DIR, "items.csv")
}
def init_db(): # membuat folder database dan menjalankan file CSV
    os.makedirs(DATA_DIR, exist_ok=True) #os.makedirs() → membuat folder beserta subfolder jika perlu.
    os.makedirs(IMAGES_DIR, exist_ok=True) #DATA_DIR → nama folder yang ingin dibuat.
                                                    #exist_ok=True → jika folder sudah ada, tidak menimbulkan error.
    # users
    if not os.path.exists(FILES["users"]): # Mengecek apakah file users.csv sudah ada, jika belum akan membuat file user dahulu
        users_data = [
            {"username": "admin", "password": "123", "role": "admin"},
            {"username": "cashier", "password": "123", "role": "cashier"},
            {"username": "waiter", "password": "123", "role": "waiter"},
            {"username": "owner", "password": "123", "role": "owner"},
        ]
        pd.DataFrame(users_data).to_csv(FILES["users"], index=False) # mengubah list dictionary menjadi DataFrame Pandas lalu
                                                                            # menyimpan DataFrame ke file CSV tanpa kolom index otomatis
    # orders
    if not os.path.exists(FILES["orders"]): #database transaksi
        pd.DataFrame(columns=["order_id", "waiter", "customer", "total", "date", "status", "order_progress", "payment_method"]).to_csv(FILES["orders"], index=False)
    # items
    if not os.path.exists(FILES["items"]):
        items_data = [
            {"id": "I001", "name": "Chicken", "price": "15000", "category": "Food", "stock": "100", "image": ""},
            {"id": "I002", "name": "Drink", "price": "5000", "category": "Beverage", "stock": "100", "image": ""},
            {"id": "I003", "name": "Rice", "price": "5000", "category": "Food", "stock": "100", "image": ""},
            {"id": "I004", "name": "French Fries", "price": "10000", "category": "Side", "stock": "50", "image": ""},
            {"id": "I005", "name": "Nugget", "price": "12000", "category": "Side", "stock": "50", "image": ""},
        ]
        pd.DataFrame(items_data).to_csv(FILES["items"], index=False)
   
    # order_details
    if not os.path.exists(FILES["order_details"]):
        pd.DataFrame(columns=["id", "order_id", "item_id", "name", "qty", "subtotal"]).to_csv(FILES["order_details"], index=False)

def get_df(key):
    try:
        df = pd.read_csv(FILES[key], dtype=str) # Membaca file CSV menjadi DataFrame
        return df
    except Exception as e: # Jika file CSV bermasalah akan muncul teks eror
        print(f"Gagal membaca {key}: {e}")
        return pd.DataFrame()
def save_df(key, df): # Menyimpan DataFrame kembali ke CSV
    df.to_csv(FILES[key], index=False)
# ========================================================================
# TABLE MAP
# ========================================================================
class TableMap(ctk.CTkFrame): # Membuat kelas TableMap yang merupakan frame khusus untuk menampilkan denah meja
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

        if not df_orders.empty and 'status' in df_orders.columns and 'customer' in df_orders.columns:
            active = df_orders[df_orders['order_progress'].isin(['Belum Dibuat', 'Masih Dibuatkan', 'Siap Diantar', 'Sudah Diantar'])]
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
        if self.callback:
            self.callback(table_name, is_occupied)
# ========================================================================
# FITUR
# ========================================================================
class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, callback):
        super().__init__(master)
        box = ctk.CTkFrame(self, width=360, height=420, corner_radius=12)
        box.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(box, text="CAFE KEL 15", font=("Arial", 24, "bold")).pack(pady=25)
        # Input username dan password
        self.entry_u = ctk.CTkEntry(box, placeholder_text="Username"); self.entry_u.pack(pady=8)
        self.entry_p = ctk.CTkEntry(box, placeholder_text="Password", show="*"); self.entry_p.pack(pady=8)
        # memanggil fungsi do_login
        ctk.CTkButton(box, text="LOGIN", command=lambda: self.do_login(callback)).pack(pady=16)
        # Tombol guest
        ctk.CTkButton(box, text="Pelanggan (Guest)", fg_color="transparent", border_width=1, command=lambda: callback("pembeli", "Guest")).pack()

    def do_login(self, cb):
        u, p = self.entry_u.get(), self.entry_p.get() # Ambil input username dan password
        df = get_df("users")
        if df.empty:
            return messagebox.showerror("ERROR", "DATABASE USER KOSONG")
        user = df[(df['username'] == u) & (df['password'] == p)]
        if not user.empty:
            cb(user.iloc[0]['role'], user.iloc[0]['username'])
        else:
            messagebox.showerror("ERROR", "LOGIN GAGAL")

# -----------------------
# OrderFrame 
# -----------------------
class OrderFrame(ctk.CTkFrame):
    def __init__(self, master, username, role):
        super().__init__(master)
        self.username = username
        self.role = role
        self.cart = {}
        self.selected_table = None
        self.selected_category = "All"
        self.image_cache = {} 
        # layout
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.table_map = TableMap(self.left_frame, role=role, command_callback=self.select_table)
        self.table_map.pack(fill="x", pady=(0, 20))

        df_items = get_df("items")
        unique_categories = []
        if not df_items.empty and 'category' in df_items.columns:
            unique_categories = df_items['category'].dropna().str.strip().str.title().unique()
        self.categories = ["All"] + sorted(unique_categories)

        self.category_combo = ctk.CTkComboBox(self.left_frame, values=self.categories, command=self.filter_by_category)
        self.category_combo.set("All"); self.category_combo.pack(pady=(0,10), padx=5, fill="x")

        self.menu_frame = ctk.CTkScrollableFrame(self.left_frame, label_text="MENU")
        self.menu_frame.pack(fill="both", expand=True)
        
        # right cart
        self.cart_frame = ctk.CTkFrame(self)
        self.cart_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.lbl_table = ctk.CTkLabel(self.cart_frame, text="Pilih Meja Hijau...", font=("Arial", 16, "bold"), text_color="orange")
        self.lbl_table.pack(pady=10)

        ctk.CTkLabel(self.cart_frame, text="ORDER SUMMARY", font=("Arial", 18, "bold")).pack(pady=10)
        self.cart_list = ctk.CTkScrollableFrame(self.cart_frame); self.cart_list.pack(fill="both", expand=True, padx=5, pady=5)

        self.total_label = ctk.CTkLabel(self.cart_frame, text="Total: Rp 0", font=("Arial", 16, "bold")); self.total_label.pack(pady=10)

        if role != 'pembeli':
            self.customer_entry = ctk.CTkEntry(self.cart_frame, placeholder_text="Customer Name"); self.customer_entry.pack(pady=5, padx=10, fill="x")

        ctk.CTkButton(self.cart_frame, text="CHECKOUT (Buat Order)", fg_color="green", command=self.checkout).pack(pady=20, fill="x", padx=10)

        self.load_menu()

    def filter_by_category(self, choice):
        self.selected_category = choice.strip().title()
        self.load_menu()

    def load_menu(self):
        for w in self.menu_frame.winfo_children():
            w.destroy()

        df_items = get_df("items")
        if df_items.empty:
            ctk.CTkLabel(self.menu_frame, text="No items available").pack(pady=20); return

        items = df_items
        if self.selected_category != "All":
            items = items[items['category'].str.strip().str.title() == self.selected_category]

        row, col = 0, 0
        for _, row_data in items.iterrows():
            # FIXED 4 COLUMNS
            self.create_item_card(row_data).grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            col += 1
            if col >= 4: 
                col = 0; row += 1

    def create_item_card(self, item):
        card = ctk.CTkFrame(self.menu_frame, border_width=1, corner_radius=8)

        # image (if available)
        img_path = item.get('image', '') if 'image' in item else ''
        if img_path and os.path.exists(img_path):
            try:
                pil = Image.open(img_path).copy()
                pil.thumbnail((140, 100))
                tkimg = ImageTk.PhotoImage(pil)
                # cache to prevent GC
                self.image_cache[item['id']] = tkimg
                lbl_img = ctk.CTkLabel(card, image=tkimg, text="")
                lbl_img.pack(pady=(8,2))
            except Exception as e:
                
                ctk.CTkLabel(card, text="(no image)", font=("Arial", 10)).pack(pady=(8,2))
        else:
            ctk.CTkLabel(card, text="(no image)", font=("Arial", 10)).pack(pady=(8,2))

        ctk.CTkLabel(card, text=item['name'], font=("Arial", 14, "bold")).pack(pady=(6,3))
        ctk.CTkLabel(card, text=f"Rp {item['price']}").pack(pady=2)
        ctk.CTkLabel(card, text=f"[{item['category']}]", font=("Arial", 11), text_color="gray").pack(pady=(0,5))
        ctk.CTkButton(card, text="ADD", width=100, command=lambda: self.add_to_cart(item)).pack(pady=6, padx=10)

        return card

    def select_table(self, table_name, is_occupied):
        if is_occupied: return messagebox.showwarning("Penuh", "Meja sedang dipakai.")
        self.selected_table = table_name
        self.lbl_table.configure(text=f"Selected: {table_name}", text_color="#2ECC71")

    def add_to_cart(self, item):
        if not self.selected_table:
            return messagebox.showwarning("Pilih Meja", "Silahkan klik meja warna HIJAU dahulu")
        item_id = item['id']
        
        # Check stock availability
        df_items = get_df("items")
        item_row = df_items[df_items['id'] == item_id]
        if not item_row.empty:
            current_stock = int(item_row.iloc[0].get('stock', 0))
            current_qty = self.cart.get(item_id, {}).get('qty', 0)
            if current_qty + 1 > current_stock:
                return messagebox.showwarning("Stok Tidak Cukup", f"Stok {item['name']} hanya tersedia {current_stock} unit.")
        
        if item_id in self.cart:
            self.cart[item_id]['qty'] += 1
        else:
            self.cart[item_id] = {'name': item['name'], 'price': int(item['price']), 'qty': 1}
        self.update_cart_ui()

    def remove_from_cart(self, item_id):
        if item_id in self.cart:
            self.cart[item_id]['qty'] -= 1
            if self.cart[item_id]['qty'] <= 0:
                del self.cart[item_id]
            self.update_cart_ui()

    def update_cart_ui(self):
        for w in self.cart_list.winfo_children(): w.destroy()
        total = 0
        for item_id, data in self.cart.items():
            subtotal = data['price'] * data['qty']
            total += subtotal
            
            row = ctk.CTkFrame(self.cart_list, fg_color="#2b2b2b")
            row.pack(fill="x", pady=2)
            
            # Button Remove (-)
            btn_del = ctk.CTkButton(row, text="-", width=30, height=24, fg_color="#C0392B", 
                                    command=lambda i=item_id: self.remove_from_cart(i))
            btn_del.pack(side="left", padx=5, pady=2)

            ctk.CTkLabel(row, text=f"{data['name']} x{data['qty']}", font=("Arial", 12)).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"Rp {subtotal}", font=("Arial", 12, "bold")).pack(side="right", padx=5)
            
        self.total_label.configure(text=f"Total: Rp {total}")

    def checkout(self):
        if not self.cart: return messagebox.showwarning("Empty", "Cart is empty!")
        if not self.selected_table: return messagebox.showwarning("Pilih Meja", "Silahkan pilih meja dahulu")

        # Check stock availability before checkout
        df_items = get_df("items")
        for item_id, data in self.cart.items():
            item_row = df_items[df_items['id'] == item_id]
            if not item_row.empty:
                current_stock = int(item_row.iloc[0].get('stock', 0))
                qty_ordered = data['qty']
                if qty_ordered > current_stock:
                    return messagebox.showwarning("Stok Tidak Cukup", 
                        f"Stok {data['name']} tidak mencukupi.\nTersedia: {current_stock}, Dibutuhkan: {qty_ordered}")

        total = sum(d['price'] * d['qty'] for d in self.cart.values())
        order_id = str(uuid.uuid4())[:8]
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        new_order = {
            "order_id": order_id,
            "waiter": self.username if self.role in ['waiter'] else 'Self',
            "customer": self.selected_table,
            "total": total,
            "date": date,
            "status": "Unpaid",
            "order_progress": "Belum Dibuat",
            "payment_method": ""
        }

        df_orders = get_df("orders")
        df_orders = pd.concat([df_orders, pd.DataFrame([new_order])], ignore_index=True)
        save_df("orders", df_orders)

        # Save Order Details
        details_list = []
        for item_id, data in self.cart.items():
            details_list.append({
                "id": str(uuid.uuid4())[:8],
                "order_id": order_id,
                "item_id": item_id,
                "name": data['name'],
                "qty": data['qty'],
                "subtotal": data['price'] * data['qty']
            })
       
        if details_list:
             df_details = get_df("order_details")
             df_details = pd.concat([df_details, pd.DataFrame(details_list)], ignore_index=True)
             save_df("order_details", df_details)

        messagebox.showinfo("Success", f"Order {order_id} Placed!\nTotal: Rp {total}")

        self.cart = {}
        self.update_cart_ui()
        self.table_map.refresh_map()

# -----------------------
# CashierFrame: proses pembayaran 
# -----------------------
class CashierFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="PROSES PEMBAYARAN", font=("Arial", 20, "bold")).pack(pady=10)
        ctk.CTkLabel(self, text="Pilih order berstatus 'Unpaid' lalu pilih metode pembayaran (Cash/QRIS)", text_color="gray").pack()

        # Daily earnings display
        earnings_frame = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=8)
        earnings_frame.pack(fill="x", padx=10, pady=5)
        self.earnings_label = ctk.CTkLabel(earnings_frame, text="Pendapatan Hari Ini: Rp 0", font=("Arial", 14, "bold"), text_color="#2ECC71")
        self.earnings_label.pack(pady=8)
        self.update_daily_earnings()

        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(btn_frame, text="Refresh", command=self.load_orders).pack(side="left")
        ctk.CTkButton(btn_frame, text="Refresh & Toggle CSV", command=self.load_orders).pack(side="left", padx=8)

        self.load_orders()

    def update_daily_earnings(self):
        """Calculate and display daily earnings from paid orders"""
        df = get_df("orders")
        if df.empty:
            self.earnings_label.configure(text="Pendapatan Hari Ini: Rp 0")
            return
        
        # Filter paid orders from today
        today = datetime.now().date()
        df['date'] = pd.to_datetime(df['date'])
        df['total'] = pd.to_numeric(df['total'], errors='coerce')
        
        paid_today = df[(df['status'] == 'Paid') & (df['date'].dt.date == today)]
        
        if paid_today.empty:
            daily_total = 0
        else:
            daily_total = paid_today['total'].sum()
        
        self.earnings_label.configure(text=f"Pendapatan Hari Ini: Rp {int(daily_total):,}")

    def load_orders(self):
        for w in self.list_frame.winfo_children(): w.destroy()
        self.update_daily_earnings()  # Update daily earnings when refreshing
        df = get_df("orders")
        if df.empty:
            ctk.CTkLabel(self.list_frame, text="Belum ada order").pack(pady=20); return
        pending = df[df['status'] == 'Unpaid']
        if pending.empty:
            ctk.CTkLabel(self.list_frame, text="Tidak ada order Pending").pack(pady=20); return

        df_details = get_df("order_details")

        for _, row in pending.iterrows():
            card = ctk.CTkFrame(self.list_frame, fg_color="#2b2b2b", corner_radius=8)
            card.pack(fill="x", padx=10, pady=6)
           
            
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", padx=10, pady=10, fill="x", expand=True)

            
            ctk.CTkLabel(info_frame, text=f"Order: {row['order_id']} | Meja: {row['customer']}", font=("Arial", 13, "bold"), text_color="white").pack(anchor="w")
           
            # Items
            items_found = False
            if not df_details.empty and 'order_id' in df_details.columns:
                 items = df_details[df_details['order_id'] == row['order_id']]
                 if not items.empty:
                     items_found = True
                     for _, item in items.iterrows():
                         ctk.CTkLabel(info_frame, text=f"- {item['name']} x{item['qty']}", font=("Arial", 11), text_color="#ccc").pack(anchor="w", padx=(10,0))
           
            if not items_found:
                ctk.CTkLabel(info_frame, text="(Detail tidak tersedia / Pesanan Lama)", font=("Arial", 10), text_color="orange").pack(anchor="w", padx=(10,0))

           
            ctk.CTkLabel(info_frame, text=f"Total: Rp {row['total']}", font=("Arial", 13, "bold"), text_color="#2ECC71").pack(anchor="w", pady=(5,0))

            
            ctk.CTkButton(card, text="Bayar", width=120, command=lambda oid=row['order_id']: self.open_payment(oid)).pack(side="right", padx=10, pady=10)

    def open_payment(self, order_id):
        df = get_df("orders")
        order = df[df['order_id'] == order_id]
        if order.empty:
            return messagebox.showerror("Error", "Order tidak ditemukan")
        order = order.iloc[0]
        total = float(order['total'])  # Convert to float for calculations

        popup = ctk.CTkToplevel(self)
        popup.title(f"Pembayaran {order_id}")
        popup.geometry("400x600")
        popup.grab_set()

        ctk.CTkLabel(popup, text="PILIH METODE PEMBAYARAN", font=("Arial", 16, "bold")).pack(pady=15)
        
        ctk.CTkLabel(popup, text=f"Order: {order_id}", font=("Arial", 12)).pack()
        ctk.CTkLabel(popup, text=f"Total: Rp {total}", font=("Arial", 14, "bold"), text_color="lightgreen").pack(pady=10)

        # Payment method selection
        payment_method = tk.StringVar(value="QRIS")
        
        payment_frame = ctk.CTkFrame(popup)
        payment_frame.pack(pady=15, padx=20, fill="x")
        
        ctk.CTkLabel(payment_frame, text="Metode Pembayaran:", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Store total for use in callbacks
        self.payment_total = float(total)
        
        ctk.CTkRadioButton(payment_frame, text="QRIS", variable=payment_method, value="QRIS", 
                          command=lambda: self.update_payment_ui(popup, payment_method, order_id, self.payment_total)).pack(pady=5, padx=20, anchor="w")
        ctk.CTkRadioButton(payment_frame, text="Cash (Tunai)", variable=payment_method, value="Cash", 
                          command=lambda: self.update_payment_ui(popup, payment_method, order_id, self.payment_total)).pack(pady=5, padx=20, anchor="w")

        # Frame for QR code/cash input (will be shown/hidden based on selection)
        self.qr_frame = ctk.CTkFrame(popup)
        self.qr_frame.pack(pady=10, padx=20)
        
        # Cash input variables (will be created in update_payment_ui)
        self.cash_received_entry = None
        self.change_label = None
        self.current_total = total  # Store total for calculate_change
        
        self.qr_label = None
        self.update_payment_ui(popup, payment_method, order_id, total)

        def confirm_payment():
            selected_method = payment_method.get()
            
            # Validate cash payment
            cash_received = None
            change = 0
            if selected_method == "Cash":
                try:
                    cash_received = float(self.cash_received_entry.get().strip())
                    if cash_received < self.payment_total:
                        return messagebox.showerror("Error", f"Uang yang diterima (Rp {cash_received:,.0f}) kurang dari total (Rp {self.payment_total:,.0f})")
                    change = cash_received - self.payment_total
                except ValueError:
                    return messagebox.showerror("Error", "Masukkan jumlah uang yang valid")
            
            df2 = get_df("orders")
           
            if df2[df2['order_id'] == order_id].empty:
                messagebox.showerror("Error", "Order ID tidak ditemukan saat update.")
                return
            
            current_progress = df2.loc[df2['order_id'] == order_id, 'order_progress'].values[0]
            new_progress = current_progress
            if new_progress == 'Belum Dibuat':
                new_progress = 'Masih Dibuatkan'

            df2.loc[df2['order_id'] == order_id, 'status'] = 'Paid'
            df2.loc[df2['order_id'] == order_id, 'order_progress'] = new_progress
            # Store payment method
            if 'payment_method' not in df2.columns:
                df2['payment_method'] = ''
            df2.loc[df2['order_id'] == order_id, 'payment_method'] = selected_method
           
            save_df("orders", df2)

            # ==================== DECREASE STOCK ====================
            # Get order details to decrease stock
            df_details = get_df("order_details")
            df_items = get_df("items")
            
            if not df_details.empty and 'order_id' in df_details.columns:
                order_items = df_details[df_details['order_id'] == order_id]
                if not order_items.empty:
                    for _, order_item in order_items.iterrows():
                        item_id = order_item['item_id']
                        qty_ordered = int(order_item['qty'])
                        
                        # Find the item in items table
                        item_mask = df_items['id'] == item_id
                        if item_mask.any():
                            current_stock = int(df_items.loc[item_mask, 'stock'].values[0])
                            new_stock = max(0, current_stock - qty_ordered)  # Prevent negative stock
                            df_items.loc[item_mask, 'stock'] = str(new_stock)
                    
                    save_df("items", df_items)
            # ========================================================

            # ==================== STRUK ====================
            struk_folder = "struk"
            os.makedirs(struk_folder, exist_ok=True)
            struk_path = os.path.join(struk_folder, f"{order_id}.txt")

            # Ambil detail item untuk order ini
            df_details = get_df("order_details")
            items = pd.DataFrame()
            if not df_details.empty and 'order_id' in df_details.columns:
                items = df_details[df_details['order_id'] == order_id]

            with open(struk_path, "w", encoding="utf-8") as f:
                f.write("========== STRUK PEMBAYARAN ==========\n")
                f.write(f"Order ID : {order_id}\n")
                f.write(f"Tanggal  : {order['date']}\n")
                f.write(f"Meja     : {order['customer']}\n")
                f.write(f"Kasir    : (system)\n")
                f.write("\n-------- DAFTAR PESANAN --------\n")

                if not items.empty:
                    for _, item in items.iterrows():
                        price_per_item = int(item['subtotal']) // int(item['qty'])
                        f.write(f"{item['name']:<20} x{int(item['qty']):2} @Rp {price_per_item:>6} = Rp {int(item['subtotal']):>8}\n")
                else:
                    f.write(" (Detail item tidak tersedia)\n")

                f.write("\n-------------------------------------\n")
                f.write(f"TOTAL    : Rp {int(order['total']):>19}\n")
                f.write("-------------------------------------\n")
                f.write(f"Metode   : {selected_method}\n")
                if selected_method == "Cash" and cash_received is not None:
                    f.write(f"Tunai    : Rp {int(cash_received):>19}\n")
                    f.write(f"Kembali  : Rp {int(change):>19}\n")
                f.write("-------------------------------------\n")
                f.write("Terima kasih telah berkunjung!\n")
                f.write("=====================================\n")

            # Tampilkan struk
            struk_win = ctk.CTkToplevel(self)
            struk_win.title("Struk Pembayaran")
            struk_win.geometry("480x650")
            struk_win.grab_set()
            ctk.CTkLabel(struk_win, text="STRUK PEMBAYARAN", font=("Arial", 16, "bold")).pack(pady=10)
            text_widget = tk.Text(struk_win, wrap="word", font=("Consolas", 11), background="#1e1e1e", foreground="white")
            with open(struk_path, "r", encoding="utf-8") as ff:
                content = ff.read()
            text_widget.insert("1.0", content)
            text_widget.configure(state="disabled")
            text_widget.pack(fill="both", expand=True, padx=15, pady=10)
            ctk.CTkButton(struk_win, text="Tutup", fg_color="red", command=struk_win.destroy).pack(pady=10)

            popup.destroy()
            self.update_daily_earnings()  # Update daily earnings display
            messagebox.showinfo("Success", f"Pembayaran untuk order {order_id} dikonfirmasi.")
            self.load_orders()
        # ==================================================================

        ctk.CTkButton(popup, text="Konfirmasi Pembayaran", fg_color="green", command=confirm_payment).pack(pady=10, fill="x", padx=20)
        ctk.CTkButton(popup, text="Batal / Tutup", fg_color="gray", command=popup.destroy).pack(pady=6, fill="x", padx=20)

    def update_payment_ui(self, popup, payment_method_var, order_id, total):
        # Clear QR frame
        for w in self.qr_frame.winfo_children():
            w.destroy()
        
        method = payment_method_var.get()
        
        if method == "QRIS":
            # Generate QR code
            payload = f"QRIS|ORDER|{order_id}|TOTAL|{total}"
            qr = segno.make(payload)
            buf = io.BytesIO()
            qr.save(buf, kind="png", scale=6)
            buf.seek(0)
            pil_img = Image.open(buf)
            tk_img = ImageTk.PhotoImage(pil_img)
            
            ctk.CTkLabel(self.qr_frame, text="SCAN QRIS UNTUK PEMBAYARAN", font=("Arial", 12, "bold")).pack(pady=5)
            lbl = ctk.CTkLabel(self.qr_frame, image=tk_img, text="")
            lbl.image = tk_img
            lbl.pack(pady=8)
            ctk.CTkLabel(self.qr_frame, text="Setelah customer membayar via e-wallet,\ntekan KONFIRMASI.", font=("Arial", 10), text_color="gray").pack(pady=5)
        else:
            # Cash payment with change calculation
            ctk.CTkLabel(self.qr_frame, text="PEMBAYARAN TUNAI", font=("Arial", 12, "bold"), text_color="#FFD700").pack(pady=10)
            
            # Total amount label
            ctk.CTkLabel(self.qr_frame, text=f"Total Pembayaran: Rp {int(total):,}", font=("Arial", 11, "bold"), text_color="white").pack(pady=5)
            
            # Cash received input
            input_frame = ctk.CTkFrame(self.qr_frame, fg_color="transparent")
            input_frame.pack(pady=10, padx=10, fill="x")
            
            ctk.CTkLabel(input_frame, text="Uang Diterima:", font=("Arial", 11)).pack(side="left", padx=5)
            self.cash_received_entry = ctk.CTkEntry(input_frame, placeholder_text="Masukkan jumlah uang", width=200)
            self.cash_received_entry.pack(side="left", padx=5)
            
            # Store total as instance variable for calculate_change
            self.current_total = float(total)
            
            # Change label (create before binding)
            self.change_label = ctk.CTkLabel(self.qr_frame, text="Kembalian: Rp 0", font=("Arial", 12, "bold"), text_color="#2ECC71")
            self.change_label.pack(pady=5)
            
            # Bind after all widgets are created
            self.cash_received_entry.bind("<KeyRelease>", lambda e: self.calculate_change())
            self.cash_received_entry.bind("<FocusOut>", lambda e: self.calculate_change())
            
            ctk.CTkLabel(self.qr_frame, text="Masukkan jumlah uang yang diterima,\nlalu tekan KONFIRMASI.", font=("Arial", 10), text_color="gray").pack(pady=5)
    
    def calculate_change(self):
        """Calculate and display change when cash received is entered"""
        if hasattr(self, 'change_label') and hasattr(self, 'cash_received_entry') and hasattr(self, 'current_total'):
            if self.change_label and self.cash_received_entry:
                try:
                    cash_text = self.cash_received_entry.get().strip()
                    if not cash_text:
                        self.change_label.configure(text="Kembalian: Rp 0", text_color="#2ECC71")
                        return
                    cash_received = float(cash_text)
                    change = cash_received - self.current_total
                    if change < 0:
                        self.change_label.configure(text=f"Kembalian: Kurang Rp {abs(int(change)):,}", text_color="#E74C3C")
                    else:
                        self.change_label.configure(text=f"Kembalian: Rp {int(change):,}", text_color="#2ECC71")
                except ValueError:
                    self.change_label.configure(text="Kembalian: Rp 0", text_color="#2ECC71")
# -----------------------
# ManageMenuFrame 
# -----------------------
class ManageMenuFrame(ctk.CTkFrame):
    CATEGORIES = ["Promo", "Paket", "Minuman", "Dessert"]

    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Kelola Menu & Stok", font=("Arial", 20, "bold")).pack(pady=10)

        self.menu_list_frame = ctk.CTkScrollableFrame(self)
        self.menu_list_frame.pack(fill="both", expand=True, padx=10, pady=0)

        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(fill="both", padx=10, pady=10)
        
        ctk.CTkLabel(self.form_frame, text="Nama Menu:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_name = ctk.CTkEntry(self.form_frame); self.entry_name.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        
        ctk.CTkLabel(self.form_frame, text="Harga:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_price = ctk.CTkEntry(self.form_frame); self.entry_price.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(self.form_frame, text="Stok Awal:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.entry_stock = ctk.CTkEntry(self.form_frame, placeholder_text="Contoh: 50"); self.entry_stock.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

       
        ctk.CTkLabel(self.form_frame, text="Kategori:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.combo_category = ctk.CTkComboBox(self.form_frame, values=self.CATEGORIES); self.combo_category.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        
        ctk.CTkLabel(self.form_frame, text="Gambar:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        img_btn_frame = ctk.CTkFrame(self.form_frame)
        img_btn_frame.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
        self.img_path_var = tk.StringVar(value="")
        self.btn_choose_img = ctk.CTkButton(img_btn_frame, text="Pilih Gambar...", command=self.choose_image)
        self.btn_choose_img.pack(side="left", padx=(0,8))
        self.lbl_img_preview = ctk.CTkLabel(img_btn_frame, text="(tidak ada)", width=120)
        self.lbl_img_preview.pack(side="left")

        self.form_frame.grid_columnconfigure(1, weight=1)

        self.btn_add = ctk.CTkButton(self.form_frame, text="Tambah Menu", fg_color="green", command=self.add_menu)
        self.btn_add.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")

        self.selected_item_id = None
        self.thumbnail_cache = {}
        self.load_menu()

    def choose_image(self):
        path = filedialog.askopenfilename(title="Pilih gambar menu", filetypes=[("Image files","*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
        if path:
            try:
                ext = os.path.splitext(path)[1]
                dest_name = f"{uuid.uuid4().hex[:8]}{ext}"
                dest_path = os.path.join(IMAGES_DIR, dest_name)
                shutil.copy(path, dest_path)
                self.img_path_var.set(dest_path)
               
                pil = Image.open(dest_path).copy()
                pil.thumbnail((80, 60))
                tkimg = ImageTk.PhotoImage(pil)
                self.thumbnail_cache['preview'] = tkimg
                self.lbl_img_preview.configure(image=tkimg, text="")
                self.lbl_img_preview.image = tkimg
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menyalin gambar: {e}")

    def load_menu(self):
        for w in self.menu_list_frame.winfo_children(): w.destroy()
        df = get_df("items")
        if df.empty:
            ctk.CTkLabel(self.menu_list_frame, text="Belum ada menu").pack(pady=20); return
        for _, row in df.iterrows():
            self.create_menu_card(row).pack(fill="x", padx=10, pady=5)

    def create_menu_card(self, row):
        card = ctk.CTkFrame(self.menu_list_frame, fg_color="#333333", corner_radius=10)
       
        # small thumb
        img_path = row.get('image', '') if 'image' in row else ''
        if img_path and os.path.exists(img_path):
            try:
                pil = Image.open(img_path).copy()
                pil.thumbnail((60,40))
                tkimg = ImageTk.PhotoImage(pil)
                label_img = ctk.CTkLabel(card, image=tkimg, text="")
                label_img.image = tkimg
                label_img.pack(side="left", padx=6, pady=6)
            except:
                pass
       
        # Info Menu
        ctk.CTkLabel(card, text=f"{row['name']}", font=("Arial", 14, "bold")).pack(side="left", padx=(10, 5), pady=5)
       
        # Info Harga & Stok 
        info_text = f"Rp {row['price']} | Stok: {row.get('stock', '0')}"
        ctk.CTkLabel(card, text=info_text, font=("Arial", 12), text_color="yellow").pack(side="left", padx=5)
       
        ctk.CTkLabel(card, text=f"[{row['category']}]", font=("Arial", 12), text_color="gray").pack(side="left", padx=5)
       
        btn_edit = ctk.CTkButton(card, text="Edit", width=60, command=lambda i=row['id']: self.edit_menu(i)); btn_edit.pack(side="right", padx=5)
        btn_delete = ctk.CTkButton(card, text="Hapus", width=60, fg_color="red", command=lambda i=row['id']: self.delete_menu(i)); btn_delete.pack(side="right", padx=5)
        return card

    def add_menu(self):
        name = self.entry_name.get().strip()
        price = self.entry_price.get().strip()
        stock = self.entry_stock.get().strip() # Ambil data stok
        category = self.combo_category.get().strip()
        img_path = self.img_path_var.get().strip()

        if not name or not price or not category or not stock:
            return messagebox.showwarning("Warning", "Semua field (termasuk Stok) harus diisi!")
       
        try:
            price = int(price)
            stock = int(stock) #  stok harus angka
        except:
            return messagebox.showwarning("Warning", "Harga dan Stok harus berupa angka!")

        df = get_df("items")
        new_id = f"I{len(df)+1:03d}" if self.selected_item_id is None else self.selected_item_id
       
        # Simpan stok ke dictionary
        new_item = {
            "id": new_id,
            "name": name,
            "price": str(price),
            "category": category,
            "stock": str(stock), 
            "image": img_path
        }

        if self.selected_item_id:
            # Update data termasuk stok
            df.loc[df['id'] == self.selected_item_id, ['name','price','category','stock','image']] = name, str(price), category, str(stock), img_path
            self.selected_item_id = None
            self.btn_add.configure(text="Tambah Menu")
        else:
            df = pd.concat([df, pd.DataFrame([new_item])], ignore_index=True)
       
        save_df("items", df)
       
        # Reset Form
        self.entry_name.delete(0,'end')
        self.entry_price.delete(0,'end')
        self.entry_stock.delete(0, 'end') 
        self.combo_category.set("")
        self.img_path_var.set("")
        self.lbl_img_preview.configure(image=None, text="(tidak ada)")
       
        self.load_menu()

    def edit_menu(self, item_id):
        df = get_df("items")
        row = df[df['id'] == item_id].iloc[0]
       
        self.entry_name.delete(0,'end'); self.entry_name.insert(0, row['name'])
        self.entry_price.delete(0,'end'); self.entry_price.insert(0, row['price'])
       
        # Isi form stok saat edit
        current_stock = row.get('stock', '0')
        self.entry_stock.delete(0, 'end'); self.entry_stock.insert(0, current_stock)

        self.combo_category.set(row['category'])
        self.img_path_var.set(row.get('image','') or "")
       
        if self.img_path_var.get() and os.path.exists(self.img_path_var.get()):
            pil = Image.open(self.img_path_var.get()).copy(); pil.thumbnail((80,60)); tkimg = ImageTk.PhotoImage(pil)
            self.lbl_img_preview.configure(image=tkimg, text=""); self.lbl_img_preview.image = tkimg
        else:
            self.lbl_img_preview.configure(image=None, text="(tidak ada)")
           
        self.selected_item_id = item_id
        self.btn_add.configure(text="Update Menu & Stok")

    def delete_menu(self, item_id):
        df = get_df("items")
        df = df[df['id'] != item_id]
        save_df("items", df)
        self.load_menu()
# -----------------------
# GraphFrame
# -----------------------
class GraphFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master); self.plot()
    def plot(self):
        df = get_df("orders")
        if df.empty: return
        if 'total' not in df.columns or 'date' not in df.columns:
            return
        df['total'] = pd.to_numeric(df['total']); df['date'] = pd.to_datetime(df['date'])
        daily = df.groupby(df['date'].dt.date)['total'].sum()
        fig, ax = plt.subplots(figsize=(6,4), dpi=100)
        fig.patch.set_facecolor('#242424'); ax.set_facecolor('#2b2b2b')
        daily.plot(kind='bar', ax=ax, color='#3B8ED0')
        ax.set_title("Pendapatan Harian", color='white')
        ax.tick_params(colors='white'); ax.spines['bottom'].set_color('white'); ax.spines['left'].set_color('white')
        canvas = FigureCanvasTkAgg(fig, master=self); canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True)

# -----------------------
# WaiterMapFrame
# -----------------------
class WaiterMapFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
       
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left: Map
        self.left = ctk.CTkFrame(self)
        self.left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
       
        ctk.CTkLabel(self.left, text="DENAH MEJA", font=("Arial", 18, "bold")).pack(pady=15)
        self.map = TableMap(self.left, role="waiter", command_callback=self.on_table_click)
        self.map.pack(expand=True)
       
        ctk.CTkButton(self.left, text="Refresh Map", command=self.map.refresh_map).pack(pady=20)

        # Right: Details
        self.right = ctk.CTkFrame(self)
        self.right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
       
        self.lbl_title = ctk.CTkLabel(self.right, text="Detail Pesanan", font=("Arial", 18, "bold"))
        self.lbl_title.pack(pady=15)
       
        self.details_frame = ctk.CTkScrollableFrame(self.right, label_text="Daftar Item")
        self.details_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Update Status Pesanan
    def update_order_status(self, table_name, new_status):
        df = get_df("orders")
        
        mask = (df['customer'] == table_name) & (df['order_progress'] != 'Selesai')
       
        if df[mask].empty:
            messagebox.showinfo("Info", "Tidak ada order aktif untuk diupdate.")
            return

        #  CEK PEMBAYARAN SEBELUM CLEAR MEJA 
        if new_status == "Selesai":
            
            payment_status = df.loc[mask, 'status'].values[0]
           
            
            if payment_status != "Paid":
                messagebox.showwarning("Ditolak", "Pelanggan BELUM MEMBAYAR!\nHarap hubungi kasir sebelum membersihkan meja.")
                return
        # -----------------------------------------------------

        # Update status di DataFrame
        df.loc[mask, 'order_progress'] = new_status
       
        # Simpan CSV
        save_df("orders", df)
       
        # Refresh Map 
        self.map.refresh_map()
       
        # Refresh Tampilan Detail (Kanan) agar status langsung berubah di layar
        is_occupied = False if new_status == "Selesai" else True
        self.on_table_click(table_name, is_occupied)

        if new_status == "Selesai":
            messagebox.showinfo("Sukses", f"Meja {table_name} berhasil dikosongkan.")
        else:
            messagebox.showinfo("Sukses", f"Status meja {table_name} diubah menjadi: {new_status}")

    def on_table_click(self, table_name, is_occupied):
        self.lbl_title.configure(text=f"Pesanan: {table_name}")
        for w in self.details_frame.winfo_children(): w.destroy()
       
        if not is_occupied:
            ctk.CTkLabel(self.details_frame, text="Meja Kosong / Order Selesai", text_color="gray").pack(pady=20)
            return

        df = get_df("orders")
        if df.empty: return
       
        # Filter active orders for this table
        table_orders = df[ (df['customer'] == table_name) & (df['order_progress'] != 'Selesai')]
       
        if table_orders.empty:
            ctk.CTkLabel(self.details_frame, text="Tidak ada order aktif", text_color="gray").pack(pady=20)
            return
           
        total_all = 0
        df_details = get_df("order_details")
       
        # Aggregate data
        grand_total = 0
        all_items = []

        current_status = table_orders.iloc[0].get('order_progress', 'Belum Dibuat')
        status_paid = table_orders.iloc[0].get('status', 'Unpaid')

        for _, row in table_orders.iterrows():
            grand_total += float(row['total'])
            order_id = row['order_id']
            if not df_details.empty and 'order_id' in df_details.columns:
                items = df_details[df_details['order_id'] == order_id]
                for _, item in items.iterrows():
                    all_items.append(f"- {item['name']} x{item['qty']}")
       
        main_card = ctk.CTkFrame(self.details_frame, fg_color="#333", corner_radius=10)
        main_card.pack(fill="x", pady=10, padx=5)
       
        ctk.CTkLabel(main_card, text=table_name, font=("Arial", 16, "bold"), text_color="#FFD700").pack(pady=(15,5))

        # Tampilkan Status Pembayaran & Progress
        ctk.CTkLabel(main_card, text=f"Bayar: {status_paid}", font=("Arial", 12, "bold"), text_color="#2ECC71" if status_paid=="Paid" else "#E74C3C").pack()
       
        ctk.CTkLabel(main_card, text=f"Progress: {current_status}", font=("Arial", 12, "italic"), text_color="#3498DB").pack(pady=(0, 10))

        # Items List
        item_box = ctk.CTkFrame(main_card, fg_color="transparent")
        item_box.pack(fill="x", padx=15, pady=5)
       
        if not all_items:
            ctk.CTkLabel(item_box, text="(Detail tidak tersedia)", font=("Arial", 11), text_color="gray").pack()
        else:
            for itm in all_items:
                ctk.CTkLabel(item_box, text=itm, font=("Arial", 12), text_color="white").pack(anchor="w")

        ctk.CTkFrame(main_card, height=2, fg_color="gray").pack(fill="x", padx=10, pady=10)

        
        ctk.CTkLabel(main_card, text=f"Total: Rp {int(grand_total)}", font=("Arial", 14, "bold"), text_color="#2ECC71").pack(pady=(0,15))

       
        status_frame = ctk.CTkFrame(main_card, fg_color="transparent")
        status_frame.pack(pady=(5,15), fill="x", padx=10)

        # Tombol Update Status 
        btn_1 = ctk.CTkButton(status_frame, text="Masih Dibuat", width=100, height=30, fg_color="#E67E22", command=lambda: self.update_order_status(table_name, "Masih Dibuatkan"))
        btn_1.grid(row=0, column=0, padx=5, pady=5)

        btn_2 = ctk.CTkButton(status_frame, text="Siap Diantar", width=100, height=30, fg_color="#27AE60", command=lambda: self.update_order_status(table_name, "Siap Diantar"))
        btn_2.grid(row=0, column=1, padx=5, pady=5)

        btn_3 = ctk.CTkButton(status_frame, text="Sudah Diantar", width=100, height=30, fg_color="#2980B9", command=lambda: self.update_order_status(table_name, "Sudah Diantar"))
        btn_3.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        
        ctk.CTkFrame(main_card, height=1, fg_color="gray").pack(fill="x", padx=20, pady=5)
       
        
        btn_text = "SELESAI / CLEAR MEJA"
        btn_color = "#C0392B"
       
        btn_finish = ctk.CTkButton(main_card, text=btn_text, fg_color=btn_color, hover_color="#922B21", command=lambda: self.update_order_status(table_name, "Selesai"))
        btn_finish.pack(pady=10, padx=20, fill="x")

# -----------------------
# MainApp
# -----------------------
class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CAFE KEL 15")
        self.geometry("1100x700")
        init_db()
        self.container = ctk.CTkFrame(self); self.container.pack(fill="both", expand=True)
        self.show_login()

    def show_login(self):
        for w in self.container.winfo_children(): w.destroy()
        LoginFrame(self.container, self.on_login).pack(fill="both", expand=True)

    def on_login(self, role, username):
        for w in self.container.winfo_children(): w.destroy()
        sidebar = ctk.CTkFrame(self.container, width=200, corner_radius=0); sidebar.grid(row=0, column=0, sticky="nsew")
        self.container.grid_columnconfigure(1, weight=1); self.container.grid_rowconfigure(0, weight=1)
        ctk.CTkLabel(sidebar, text="RESTO POS", font=("Arial", 20, "bold")).pack(pady=30)
        ctk.CTkLabel(sidebar, text=f"{role.upper()}", text_color="gray").pack(pady=(0,20))
        content = ctk.CTkFrame(self.container, fg_color="transparent"); content.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
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
        ctk.CTkButton(sidebar, text="LOGOUT", fg_color="red", command=self.show_login).pack(side="bottom", pady=20, padx=10)

    def add_btn(self, parent, text, cmd):
        def wrapper():
            if "active" in self.frames:
                try: self.frames["active"].destroy()
                except: pass
            frame = cmd(); frame.pack(fill="both", expand=True); self.frames["active"] = frame
        ctk.CTkButton(parent, text=text, fg_color="transparent", border_width=1, command=wrapper).pack(pady=5, padx=10, fill="x")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop() 