# Cafe Order Management System
## Overview
This is a cafe order management system built with Python, Tkinter (CustomTkinter), and Pandas. It simulates a McDonald's-like or cafe system where different users (Admin, Cashier, Waiter, Guest) can interact with the system.

## Key Features
- **User Roles**: Supports Admin, Cashier, Waiter, Owner, and Guest.
- **Menu Management**: Loads menu items from `items.csv`.
- **Order System**:
    - Browse menu items (Chicken, Drink, Rice, Fries, Nugget).
    - Add items to a cart.
    - Real-time total calculation.
    - Checkout system (saves orders to `orders.csv`).
- **Data Persistence**: Uses CSV files (`users.csv`, `items.csv`, `orders.csv`) effectively as a database.

## Installation & Usage
1. **Dependencies**:
   Ensure you have the required libraries installed:
   ```bash
   pip install customtkinter pandas matplotlib python-barcode ipython segno
   ```

2. **Run the Application**:
   Execute the main script:
   ```bash
   python cafeGUI.py
   ```

3. **Login Details** (Default):
   - **Admin**: admin / 123
   - **Cashier**: cashier / 123
   - **Waiter**: waiter / 123
   - **Owner**: owner / 123
   - **Guest**: Click "Pelanggan (Guest)" button

## File Structure
- `cafeGUI.py`: Main application code.
- `data/`: Directory where CSV files are stored (automatically created).
    - `users.csv`: User credentials.
    - `items.csv`: Menu items.
    - `orders.csv`: Order history.
