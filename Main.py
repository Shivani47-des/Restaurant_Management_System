import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
import os
from datetime import datetime
import webbrowser
from tkinter import filedialog

class AuthSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Management System - Authentication")
        self.root.geometry("1900x1000")
        
        # Set background color
        self.root.configure(bg="#f6f7f9")
        
        # Initialize data files
        self.users_file = "users.json"
        self.tables_file = "tables.json"
        self.orders_file = "orders.json"
        self.menu_file = "menu.json"
        
        # Create files if they don't exist
        self.initialize_data_files()
        
        self.create_auth_gui()
    
    def initialize_data_files(self):
        # Users file
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({"admin": "admin123"}, f)  # Default admin account
        
        # Tables file
        if not os.path.exists(self.tables_file):
            with open(self.tables_file, 'w') as f:
                json.dump({"tables": [{"id": i, "capacity": 4, "reserved": False, "reservation_details": None} for i in range(1, 11)]}, f)
        
        # Orders file
        if not os.path.exists(self.orders_file):
            with open(self.orders_file, 'w') as f:
                json.dump({}, f)
        
        # Menu file
        if not os.path.exists(self.menu_file):
            default_menu = {
                "Burger": 100,
                "Pizza": 200,
                "Pasta": 150,
                "Sandwich": 80,
                "Salad": 90,
                "Soft Drink": 40,
                "Coffee": 60,
                "Tea": 30
            }
            with open(self.menu_file, 'w') as f:
                json.dump(default_menu, f)
    
    def create_auth_gui(self):
        self.clear_window()
        
        self.auth_frame = tk.Frame(self.root, padx=20, pady=20, bg="#e3f2fd")
        self.auth_frame.pack(expand=True)
        
        # Title
        tk.Label(self.auth_frame, text="Restaurant Management System", 
                font=('Arial', 16, 'bold'), bg="#e3f2fd", fg="#1976d2").grid(row=0, column=0, columnspan=2, pady=10)
        
        # Username
        tk.Label(self.auth_frame, text="Username:", bg="#e3f2fd").grid(row=1, column=0, sticky='e', pady=5)
        self.username_entry = tk.Entry(self.auth_frame)
        self.username_entry.grid(row=1, column=1, pady=5)
        self.username_entry.focus()
        
        # Password
        tk.Label(self.auth_frame, text="Password:", bg="#e3f2fd").grid(row=2, column=0, sticky='e', pady=5)
        self.password_entry = tk.Entry(self.auth_frame, show="*")
        self.password_entry.grid(row=2, column=1, pady=5)
        
        # Buttons
        btn_frame = tk.Frame(self.auth_frame, bg="#e3f2fd")
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.login_btn = tk.Button(
            btn_frame, text="Login", command=self.login, width=10,
            bg="#4caf50", fg="white", activebackground="#388e3c", activeforeground="white", font=('Arial', 10, 'bold')
        )
        self.login_btn.pack(side="left", padx=5)
        
        self.signup_btn = tk.Button(
            btn_frame, text="Sign Up", command=self.signup, width=10,
            bg="#ff9800", fg="white", activebackground="#f57c00", activeforeground="white", font=('Arial', 10, 'bold')
        )
        self.signup_btn.pack(side="left", padx=5)
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda event: self.login())
    
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def load_data(self, file):
        try:
            with open(file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_data(self, data, file):
        with open(file, 'w') as f:
            json.dump(data, f, indent=4)
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        users = self.load_data(self.users_file)
        
        if username in users and users[username] == password:
            messagebox.showinfo("Success", "Login successful!")
            self.root.destroy()  # Close auth window
            # Open main application
            main_root = tk.Tk()
            app = RestaurantManagementSystem(main_root)
            if username == "admin":
                app.show_admin_features()
            main_root.mainloop()
        else:
            messagebox.showerror("Error", "Invalid username or password")
    
    def signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return
        
        users = self.load_data(self.users_file)
        
        if username in users:
            messagebox.showerror("Error", "Username already exists")
        else:
            users[username] = password
            self.save_data(users, self.users_file)
            messagebox.showinfo("Success", "Account created successfully! You can now login.")
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.username_entry.focus()

class RestaurantManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Management System - Dashboard")
        self.root.geometry("2000x800")
        
        # Set background color
        self.root.configure(bg="#fff8e1")
        
        # Initialize data files
        self.tables_file = "tables.json"
        self.orders_file = "orders.json"
        self.menu_file = "menu.json"
        self.users_file = "users.json"
        
        # Initialize other attributes
        self.orders = {}
        self.gst_percentage = 18
        self.current_order_id = self.get_last_order_id() + 1
        self.customer_name = tk.StringVar()
        self.customer_contact = tk.StringVar()
        self.customer_email = tk.StringVar()
        self.table_number = tk.StringVar()
        self.table_number.trace_add("write", self.autofill_customer_details_by_table)
        self.is_admin = False
        
        # Initialize UI
        self.create_widgets()
        
        # Load data after UI is set up
        try:
            self.items = self.load_data(self.menu_file)
            self.create_order_tab_content()
            self.create_reservation_tab_content()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize: {str(e)}")
            self.root.destroy()

    def create_widgets(self):
    # Menu Bar
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Export Data", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        self.admin_menu = tk.Menu(menubar, tearoff=0)
        self.admin_menu.add_command(label="Add New Item", command=self.add_new_item)
        self.admin_menu.add_command(label="View Sales", command=self.view_sales)
        self.admin_menu.add_command(label="Order History", command=self.show_order_history)
        self.admin_menu.add_command(label="Table Management", command=self.manage_tables)
        self.admin_menu.add_command(label="User Management", command=self.manage_users, state="disabled")
        menubar.add_cascade(label="Admin", menu=self.admin_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Colorful tabs using tk.Frame
        self.order_tab = tk.Frame(self.notebook, bg="#e8f5e9")          # Light green
        self.reservation_tab = tk.Frame(self.notebook, bg="#e3f2fd")    # Light blue

        self.notebook.add(self.order_tab, text="New Order")
        self.notebook.add(self.reservation_tab, text="Table Reservation")

    # ========== Helper Methods ==========

    def load_data(self, file):
        try:
            with open(file, 'r') as f:
                return json.load(f)
        except:
            return {}

    def save_data(self, data, file):
        with open(file, 'w') as f:
            json.dump(data, f, indent=4)

    def get_last_order_id(self):
        orders = self.load_data(self.orders_file)
        if orders:
            return max(int(k) for k in orders.keys())
        return 0

    @staticmethod
    def convert_to_inr(amount):
        return "₹" + str(amount)

    def show_admin_features(self):
        self.is_admin = True
        for i in range(self.admin_menu.index("end")+1):
            self.admin_menu.entryconfig(i, state="normal")

    # ========== Order Tab Content ==========

    def create_order_tab_content(self):
        main_frame = tk.Frame(self.order_tab, bg="#e8f5e9")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        edit_btn = tk.Button(
            main_frame, text="Edit Existing Order", command=self.edit_order,
            bg="#9575cd", fg="white", activebackground="#673ab7", activeforeground="white", font=('Arial', 10, 'bold')
        )
        edit_btn.pack(pady=10)

        # Left Frame (Customer Details)
        left_frame = tk.LabelFrame(main_frame, text="Customer Details", padx=10, pady=10,
                                bg="#c8e6c9", fg="#2e7d32", font=('Arial', 12, 'bold'))
        left_frame.pack(side="left", fill="y", padx=5, pady=5)

        tk.Label(left_frame, text="Name:", bg="#c8e6c9").grid(row=0, column=0, sticky="e", pady=5)
        tk.Entry(left_frame, textvariable=self.customer_name).grid(row=0, column=1, pady=5)

        tk.Label(left_frame, text="Contact:", bg="#c8e6c9").grid(row=1, column=0, sticky="e", pady=5)
        contact_entry = tk.Entry(left_frame, textvariable=self.customer_contact)
        contact_entry.grid(row=1, column=1, pady=5)
        contact_entry.configure(validate="key")
        contact_entry.configure(validatecommand=(contact_entry.register(self.validate_contact), "%P"))

        tk.Label(left_frame, text="Email:", bg="#c8e6c9").grid(row=2, column=0, sticky="e", pady=5)
        tk.Entry(left_frame, textvariable=self.customer_email).grid(row=2, column=1, pady=5)

        tk.Label(left_frame, text="Table #:", bg="#c8e6c9").grid(row=3, column=0, sticky="e", pady=5)
        tk.Entry(left_frame, textvariable=self.table_number).grid(row=3, column=1, pady=5)

        # Right Frame (Menu and Order)
        right_frame = tk.Frame(main_frame, bg="#e8f5e9")
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # Menu Section
        menu_frame = tk.LabelFrame(right_frame, text="Menu", padx=10, pady=10,
                                bg="#a5d6a7", fg="#2e7d32", font=('Arial', 12, 'bold'))
        menu_frame.pack(fill="both", expand=True)

        headers = ["Item", "Price", "Quantity"]
        for col, header in enumerate(headers):
            tk.Label(menu_frame, text=header, font=('Arial', 10, 'bold'), bg="#a5d6a7", fg="#2e7d32").grid(
                row=0, column=col, padx=5, pady=5)

        canvas = tk.Canvas(menu_frame, bg="#a5d6a7", highlightthickness=0)
        scrollbar = ttk.Scrollbar(menu_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#a5d6a7")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        row = 1
        for item, price in self.items.items():
            item_var = tk.IntVar()
            tk.Label(scrollable_frame, text=item, bg="#a5d6a7").grid(row=row, column=0, padx=5, pady=5, sticky="w")
            tk.Label(scrollable_frame, text=self.convert_to_inr(price), bg="#a5d6a7").grid(row=row, column=1, padx=5, pady=5)
            quantity_entry = tk.Entry(scrollable_frame, width=5)
            quantity_entry.grid(row=row, column=2, padx=5, pady=5)
            quantity_entry.insert(0, "0")
            self.orders[item] = {"var": item_var, "quantity": quantity_entry}
            quantity_entry.bind("<KeyRelease>", lambda event, item=item: self.update_sample_bill(item))
            row += 1

        canvas.grid(row=1, column=0, columnspan=3, sticky="nsew")
        scrollbar.grid(row=1, column=3, sticky="ns")

        menu_frame.grid_rowconfigure(1, weight=1)
        menu_frame.grid_columnconfigure(0, weight=1)

        # Buttons Frame
        buttons_frame = tk.Frame(right_frame, bg="#e8f5e9")
        buttons_frame.pack(fill="x", pady=10)

        tk.Button(
            buttons_frame, text="Generate Bill", command=self.show_bill_popup,
            bg="#66bb6a", fg="white", activebackground="#43a047", activeforeground="white", font=('Arial', 10, 'bold')
        ).pack(side="left", padx=5)
        tk.Button(
            buttons_frame, text="Clear All", command=self.clear_selection,
            bg="#ef5350", fg="white", activebackground="#d32f2f", activeforeground="white", font=('Arial', 10, 'bold')
        ).pack(side="left", padx=5)
        tk.Button(
            buttons_frame, text="Print Bill", command=self.print_bill,
            bg="#42a5f5", fg="white", activebackground="#1976d2", activeforeground="white", font=('Arial', 10, 'bold')
        ).pack(side="left", padx=5)

        # Bill Preview Section
        bill_frame = tk.LabelFrame(right_frame, text="Bill Preview", padx=10, pady=10,
                                bg="#dcedc8", fg="#33691e", font=('Arial', 12, 'bold'))
        bill_frame.pack(fill="both", expand=True)

        self.bill_text = tk.Text(bill_frame, height=10, wrap="word", font=('Courier', 10), bg="#f1f8e9")
        self.bill_text.pack(fill="both", expand=True)
        self.update_sample_bill()

    def edit_order(self):
        order_id = simpledialog.askstring("Edit Order", "Enter Order ID to edit:")
        if not order_id:
            return

        try:
            with open(self.orders_file, "r") as f:
                orders = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load orders: {e}")
            return

        if order_id not in orders:
            messagebox.showerror("Error", "Order ID not found.")
            return

        order_data = orders[order_id]

        # Fill customer details in the form
        self.customer_name.set(order_data.get("customer_name", ""))
        self.customer_contact.set(order_data.get("customer_contact", ""))
        self.customer_email.set(order_data.get("customer_email", ""))
        self.table_number.set(order_data.get("table_number", ""))

        # Clear all current quantities
        for item in self.orders:
            self.orders[item]["quantity"].delete(0, tk.END)
            self.orders[item]["quantity"].insert(0, "0")

        # Fill item quantities from the order
        for item in order_data["items"]:
            name = item["name"]
            qty = item["quantity"]
            if name in self.orders:
                self.orders[name]["quantity"].delete(0, tk.END)
                self.orders[name]["quantity"].insert(0, str(qty))

        self.update_sample_bill()
        messagebox.showinfo("Loaded", f"Order #{order_id} loaded. You can now update quantities and re-generate the bill.")
    


    # ======= auto fetch reserved table ======== 
    def autofill_customer_details_by_table(self, *args):
        table_no = self.table_number.get().strip()
        if not table_no.isdigit():
            return

        tables_data = self.load_data(self.tables_file)
        for table in tables_data["tables"]:
            if str(table["id"]) == table_no and table["reserved"]:
                details = table.get("reservation_details", {})
                self.customer_name.set(details.get("name", ""))
                self.customer_contact.set(details.get("contact", ""))
                return


    # ========== Reservation Tab Content ==========
    def create_reservation_tab_content(self):
        # Main Frame
        main_frame = ttk.Frame(self.reservation_tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def create_reservation_tab_content(self):
    # Main Frame with light blue background
        main_frame = tk.Frame(self.reservation_tab, bg="#e3f2fd")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Left Frame (Reservation Details) with blue shade
        left_frame = tk.LabelFrame(main_frame, text="Reservation Details", padx=10, pady=10,
                                bg="#bbdefb", fg="#0d47a1", font=('Arial', 12, 'bold'))
        left_frame.pack(side="left", fill="y", padx=5, pady=5)

        tk.Label(left_frame, text="Customer Name:", bg="#bbdefb").grid(row=0, column=0, sticky="e", pady=5)
        self.reserve_name = tk.Entry(left_frame)
        self.reserve_name.grid(row=0, column=1, pady=5)

        tk.Label(left_frame, text="Contact:", bg="#bbdefb").grid(row=1, column=0, sticky="e", pady=5)
        self.reserve_contact = tk.Entry(left_frame)
        self.reserve_contact.grid(row=1, column=1, pady=5)

        tk.Label(left_frame, text="Date:", bg="#bbdefb").grid(row=2, column=0, sticky="e", pady=5)
        self.reserve_date = tk.Entry(left_frame)
        self.reserve_date.grid(row=2, column=1, pady=5)
        self.reserve_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(left_frame, text="Time:", bg="#bbdefb").grid(row=3, column=0, sticky="e", pady=5)
        self.reserve_time = tk.Entry(left_frame)
        self.reserve_time.grid(row=3, column=1, pady=5)
        self.reserve_time.insert(0, "19:00")

        tk.Label(left_frame, text="Party Size:", bg="#bbdefb").grid(row=4, column=0, sticky="e", pady=5)
        self.reserve_size = tk.Spinbox(left_frame, from_=1, to=20)
        self.reserve_size.grid(row=4, column=1, pady=5)

        # Right Frame (Table Selection) with lighter blue
        right_frame = tk.Frame(main_frame, bg="#e3f2fd")
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # Table List Section
        table_frame = tk.LabelFrame(right_frame, text="Available Tables", padx=10, pady=10,
                                bg="#90caf9", fg="#0d47a1", font=('Arial', 12, 'bold'))
        table_frame.pack(fill="both", expand=True)

        # Treeview for tables (ttk doesn't support bg/fg, so leave as is)
        self.table_tree = ttk.Treeview(table_frame, columns=("ID", "Capacity", "Status", "Reservation"), 
                                    show="headings", selectmode="browse")
        self.table_tree.heading("ID", text="Table #")
        self.table_tree.heading("Capacity", text="Capacity")
        self.table_tree.heading("Status", text="Status")
        self.table_tree.heading("Reservation", text="Reserved For")
        self.table_tree.column("ID", width=50, anchor="center")
        self.table_tree.column("Capacity", width=70, anchor="center")
        self.table_tree.column("Status", width=80, anchor="center")
        self.table_tree.column("Reservation", width=150)
        self.table_tree.pack(fill="both", expand=True)

        # Buttons Frame with blue background
        buttons_frame = tk.Frame(right_frame, bg="#e3f2fd")
        buttons_frame.pack(fill="x", pady=10)

        tk.Button(buttons_frame, text="Check Availability", command=self.check_table_availability,
                bg="#1976d2", fg="white", activebackground="#0d47a1", activeforeground="white", font=('Arial', 10, 'bold')
        ).pack(side="left", padx=5)
        tk.Button(buttons_frame, text="Make Reservation", command=self.make_reservation,
                bg="#43a047", fg="white", activebackground="#1b5e20", activeforeground="white", font=('Arial', 10, 'bold')
        ).pack(side="left", padx=5)
        tk.Button(buttons_frame, text="Clear", command=self.clear_reservation,
                bg="#fbc02d", fg="white", activebackground="#f57c00", activeforeground="white", font=('Arial', 10, 'bold')
        ).pack(side="left", padx=5)
        tk.Button(buttons_frame, text="Cancel Reservation", command=self.cancel_reservation,
                bg="#e53935", fg="white", activebackground="#b71c1c", activeforeground="white", font=('Arial', 10, 'bold')
        ).pack(side="left", padx=5)

        # Load initial table data
        self.load_table_data()

    def load_table_data(self):
        # Clear existing data
        for item in self.table_tree.get_children():
            self.table_tree.delete(item)
        
        # Load table data
        tables_data = self.load_data(self.tables_file)
        
        # Add tables to treeview
        for table in tables_data["tables"]:
            status = "Reserved" if table["reserved"] else "Available"
            reservation = table.get("reservation_details", {}).get("name", "") if table["reserved"] else ""
            self.table_tree.insert("", "end", values=(
                table["id"], 
                table["capacity"], 
                status,
                reservation
            ))

    def check_table_availability(self):
        try:
            party_size = int(self.reserve_size.get())
            if party_size <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid party size (1-20)")
            return
        
        tables_data = self.load_data(self.tables_file)
        
        available_tables = [table for table in tables_data["tables"] 
                          if not table["reserved"] and table["capacity"] >= party_size]
        
        if available_tables:
            message = f"Available tables for {party_size} people:\n"
            message += "\n".join(f"Table #{table['id']} (Capacity: {table['capacity']})" 
                               for table in available_tables)
            messagebox.showinfo("Available Tables", message)
        else:
            messagebox.showinfo("Available Tables", "No available tables for the requested party size")

    def make_reservation(self):
        name = self.reserve_name.get().strip()
        contact = self.reserve_contact.get().strip()
        date = self.reserve_date.get().strip()
        time = self.reserve_time.get().strip()
        
        try:
            party_size = int(self.reserve_size.get())
            if party_size <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid party size (1-20)")
            return
        
        if not name:
            messagebox.showerror("Error", "Please enter customer name")
            return
        
        if not contact or not contact.isdigit() or len(contact) != 10:
            messagebox.showerror("Error", "Please enter a valid 10-digit contact number")
            return
        
        # Validate date format (simple check)
        if len(date) != 10 or date[4] != '-' or date[7] != '-':
            messagebox.showerror("Error", "Please enter date in YYYY-MM-DD format")
            return
        
        # Validate time format (simple check)
        if len(time) != 5 or time[2] != ':':
            messagebox.showerror("Error", "Please enter time in HH:MM format")
            return
        
        tables_data = self.load_data(self.tables_file)
        
        # Find first available table that fits the party size
        table_to_reserve = None
        for table in tables_data["tables"]:
            if not table["reserved"] and table["capacity"] >= party_size:
                table_to_reserve = table
                break
        
        if not table_to_reserve:
            messagebox.showerror("Error", "No available tables for the requested party size")
            return
        
        # Update table status
        table_to_reserve["reserved"] = True
        table_to_reserve["reservation_details"] = {
            "name": name,
            "contact": contact,
            "date": date,
            "time": time,
            "party_size": party_size
        }
        
        self.save_data(tables_data, self.tables_file)
        
        messagebox.showinfo("Reservation Confirmed", 
                          f"Reservation for {party_size} people confirmed!\n"
                          f"Table #{table_to_reserve['id']} (Capacity: {table_to_reserve['capacity']})\n"
                          f"Name: {name}\nContact: {contact}\n"
                          f"Date: {date} at {time}")
        
        # Update table view and clear form
        self.load_table_data()
        self.clear_reservation()

    def cancel_reservation(self):
        selected_item = self.table_tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a table to cancel reservation")
            return
        
        table_id = self.table_tree.item(selected_item)["values"][0]
        tables_data = self.load_data(self.tables_file)
        
        for table in tables_data["tables"]:
            if table["id"] == table_id and table["reserved"]:
                if messagebox.askyesno("Confirm Cancellation", 
                                      f"Cancel reservation for Table #{table_id}?"):
                    table["reserved"] = False
                    table["reservation_details"] = None
                    self.save_data(tables_data, self.tables_file)
                    self.load_table_data()
                    messagebox.showinfo("Success", f"Reservation for Table #{table_id} cancelled")
                return
        
        messagebox.showerror("Error", "Selected table is not reserved")

    def clear_reservation(self):
        self.reserve_name.delete(0, tk.END)
        self.reserve_contact.delete(0, tk.END)
        self.reserve_date.delete(0, tk.END)
        self.reserve_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.reserve_time.delete(0, tk.END)
        self.reserve_time.insert(0, "19:00")
        self.reserve_size.delete(0, tk.END)
        self.reserve_size.insert(0, "2")

    def update_sample_bill(self, item=None):
        selected_items = []
        total_price = 0

        for item, info in self.orders.items():
            quantity = info["quantity"].get()
            if quantity and quantity != "0":
                selected_items.append({
                    "name": item,
                    "quantity": int(quantity),
                    "price": self.items[item],
                    "total": self.convert_to_inr(self.items[item] * int(quantity))
                })
                total_price += self.items[item] * int(quantity)

        gst_amount = (total_price * self.gst_percentage) / 100
        grand_total = total_price + gst_amount

        bill_content = self.generate_bill_content(selected_items, total_price, gst_amount, grand_total)

        self.bill_text.config(state="normal")
        self.bill_text.delete("1.0", tk.END)
        self.bill_text.insert("1.0", bill_content)
        self.bill_text.config(state="disabled")

    def generate_bill_content(self, selected_items, total_price, gst_amount, grand_total):
        bill = "="*50 + "\n"
        bill += " "*15 + "RESTAURANT BILL\n"
        bill += "="*50 + "\n\n"
        bill += f"Customer Name: {self.customer_name.get()}\n"
        bill += f"Contact: {self.customer_contact.get()}\n"
        bill += f"Email: {self.customer_email.get()}\n"
        bill += f"Table #: {self.table_number.get()}\n"
        bill += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        bill += "-"*50 + "\n"
        bill += "ITEMS ORDERED:\n"
        
        for item in selected_items:
            bill += f"{item['name'].ljust(25)} {str(item['quantity']).rjust(3)} x {self.convert_to_inr(item['price']).rjust(6)} = {item['total'].rjust(8)}\n"
        
        bill += "-"*50 + "\n"
        bill += f"Subtotal: {self.convert_to_inr(total_price).rjust(36)}\n"
        bill += f"GST ({self.gst_percentage}%): {self.convert_to_inr(gst_amount).rjust(30)}\n"
        bill += "-"*50 + "\n"
        bill += f"GRAND TOTAL: {self.convert_to_inr(grand_total).rjust(31)}\n"
        bill += "="*50 + "\n"
        bill += "\nThank you for dining with us!\n"
        
        return bill

    def show_bill_popup(self):
        if not self.customer_name.get().strip():
            messagebox.showwarning("Warning", "Please enter customer name.")
            return

        selected_items = []
        total_price = 0

        for item, info in self.orders.items():
            quantity = info["quantity"].get()
            if quantity and quantity != "0":
                selected_items.append({
                    "name": item,
                    "quantity": int(quantity),
                    "price": self.items[item],
                    "total": self.convert_to_inr(self.items[item] * int(quantity))
                })
                total_price += self.items[item] * int(quantity)

        if not selected_items:
            messagebox.showwarning("Warning", "Please select at least one item.")
            return

        gst_amount = (total_price * self.gst_percentage) / 100
        grand_total = total_price + gst_amount

        # Save the order
        order_data = {
            "customer_name": self.customer_name.get(),
            "customer_contact": self.customer_contact.get(),
            "customer_email": self.customer_email.get(),
            "table_number": self.table_number.get(),
            "order_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": selected_items,
            "subtotal": self.convert_to_inr(total_price),
            "gst_amount": self.convert_to_inr(gst_amount),
            "grand_total": self.convert_to_inr(grand_total)
        }

        # Load existing orders
        try:
            with open(self.orders_file, 'r') as f:
                orders = json.load(f)
        except:
            orders = {}

        # Add new order
        orders[self.current_order_id] = order_data
        self.current_order_id += 1

        # Save back to file
        with open(self.orders_file, 'w') as f:
            json.dump(orders, f, indent=4)
        
        # Show confirmation after saving
        messagebox.showinfo("Success", "Order is placed!")
        self.clear_selection()


        # Show bill
        bill_window = tk.Toplevel(self.root)
        bill_window.title("Final Bill")
        
        bill_text = tk.Text(bill_window, wrap="word", padx=10, pady=10, font=('Courier', 10))
        bill_text.pack(fill="both", expand=True)
        
        bill_content = self.generate_bill_content(selected_items, total_price, gst_amount, grand_total)
        bill_text.insert("1.0", bill_content)
        
        # Make bill read-only
        bill_text.config(state="disabled")
        
        # Print button in bill window
        

    def print_bill(self):
        selected_items = []
        total_price = 0

        for item, info in self.orders.items():
            quantity = info["quantity"].get()
            if quantity and quantity != "0":
                quantity = int(quantity)
                price = self.items[item]
                selected_items.append({
                    "name": item,
                    "quantity": quantity,
                    "price": price,
                    "total": self.convert_to_inr(price * quantity)
                })
                total_price += price * quantity

        if not selected_items:
            messagebox.showwarning("Warning", "No items selected to print.")
            return

        gst_amount = (total_price * self.gst_percentage) / 100
        grand_total = total_price + gst_amount
        
        bill_content = self.generate_bill_content(selected_items, total_price, gst_amount, grand_total)
        messagebox.showinfo("Print Bill", "Bill sent to printer.\n\n" + bill_content)


    def clear_selection(self):
        # Clear item quantities
        for item, info in self.orders.items():
            info["quantity"].delete(0, tk.END)
            info["quantity"].insert(0, "0")
        
        # Clear customer details
        self.customer_name.set("")
        self.customer_contact.set("")
        self.customer_email.set("")
        self.table_number.set("")

        # Update the bill preview
        self.update_sample_bill()

    def view_sales(self):
        orders = self.load_data(self.orders_file)
        if not orders:
            messagebox.showinfo("Sales", "No sales data found.")
            return

        # Aggregate sales data
        total_sales = 0
        item_sales = {}

        for order in orders.values():
            total_sales += order.get("total", 0)
            for item in order.get("items", []):
                name = item["name"]
                qty = item["quantity"]
                price = item.get("price", 0)
                amt = qty * price
                if name not in item_sales:
                    item_sales[name] = {"quantity": 0, "amount": 0}
                item_sales[name]["quantity"] += qty
                item_sales[name]["amount"] += amt

        # Display in a new window
        win = tk.Toplevel(self.root)
        win.title("Sales Report")
        win.geometry("700x500")
        win.configure(bg="#f1f8e9")

        tk.Label(win, text=f"Total Sales: {self.convert_to_inr(total_sales)}", font=("Arial", 14, "bold"), bg="#f1f8e9", fg="#388e3c").pack(pady=10)

        frame = tk.Frame(win, bg="#f1f8e9")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("Item", "Quantity Sold", "Amount")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=150)
        tree.pack(fill="both", expand=True)

        for item, data in item_sales.items():
            tree.insert("", "end", values=(item, data["quantity"], self.convert_to_inr(data["amount"])))

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

   
    def show_order_history(self):
    # Load orders
        orders = self.load_data(self.orders_file)
        if not orders:
            messagebox.showinfo("Order History", "No orders found.")
            return

        # Create a new window
        win = tk.Toplevel(self.root)
        win.title("Order History")
        win.geometry("900x500")
        win.configure(bg="#e3f2fd")

        # Table frame
        frame = tk.Frame(win, bg="#e3f2fd")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("Order ID", "Customer", "Contact", "Table", "Date", "Total", "Items")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100 if col != "Items" else 250)
        tree.pack(fill="both", expand=True)

        # Insert orders
        for oid, order in orders.items():
            # Calculate total if not stored or if it's zero
            order_total = order.get("total", 0)
            if not order_total or order_total == 0:
                order_total = 0
                for item in order.get("items", []):
                    qty = item.get("quantity", 0)
                    price = item.get("price", 0)
                    order_total += qty * price

            items_str = ", ".join([f"{item['name']}({item['quantity']})" for item in order.get("items", [])])
            tree.insert("", "end", values=(
                oid,
                order.get("customer_name", ""),
                order.get("customer_contact", ""),
                order.get("table_number", ""),
                order.get("date", ""),
                self.convert_to_inr(order_total),
                items_str
            ))

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def load_all_orders(self):
        # Clear existing data
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)
        
        # Load order data
        orders = self.load_data(self.orders_file)
        
        # Add orders to treeview
        for order_id, order in sorted(orders.items(), key=lambda x: int(x[0])):
            self.order_tree.insert("", "end", values=(
                order_id,
                order["customer_name"],
                order["customer_contact"],
                order["order_date"],
                order["table_number"],
                order["grand_total"]
            ))

    def search_orders(self):
        search_term = self.search_entry.get().lower()
        if not search_term:
            self.load_all_orders()
            return
        
        # Clear existing data
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)
        
        # Load order data
        orders = self.load_data(self.orders_file)
        
        # Filter orders
        for order_id, order in sorted(orders.items(), key=lambda x: int(x[0])):
            if (search_term in order_id.lower() or
                search_term in order["customer_name"].lower() or
                search_term in order["customer_contact"].lower() or
                search_term in order["table_number"].lower()):
                
                self.order_tree.insert("", "end", values=(
                    order_id,
                    order["customer_name"],
                    order["customer_contact"],
                    order["order_date"],
                    order["table_number"],
                    order["grand_total"]
                ))

    def view_selected_order(self):
        selected_item = self.order_tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select an order")
            return
        
        order_id = self.order_tree.item(selected_item)["values"][0]
        self.show_order_details(order_id)

    def export_selected_order(self):
        selected_item = self.order_tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select an order")
            return
        
        order_id = self.order_tree.item(selected_item)["values"][0]
        orders = self.load_data(self.orders_file)
        order = orders.get(str(order_id))
        
        if not order:
            messagebox.showerror("Error", "Order not found")
            return
        
        # Generate bill content
        bill_content = self.generate_bill_content(
            order["items"],
            float(order["subtotal"].replace("₹", "")),
            float(order["gst_amount"].replace("₹", "")),
            float(order["grand_total"].replace("₹", ""))
        )
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title=f"Save Order #{order_id}"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(bill_content)
                messagebox.showinfo("Success", f"Order #{order_id} exported successfully")
            except:
                messagebox.showerror("Error", "Failed to export order")

    def show_order_details(self, order_id):
        orders = self.load_data(self.orders_file)
        order = orders.get(str(order_id))
        
        if not order:
            messagebox.showerror("Error", f"Order #{order_id} not found")
            return
        
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Order Details - #{order_id}")
        details_window.geometry("600x500")
        
        text = tk.Text(details_window, wrap="word", padx=10, pady=10, font=('Courier', 10))
        text.pack(fill="both", expand=True)
        
        text.insert("1.0", f"Order ID: {order_id}\n")
        text.insert("end", f"Customer: {order['customer_name']}\n")
        text.insert("end", f"Contact: {order['customer_contact']}\n")
        text.insert("end", f"Email: {order.get('customer_email', 'N/A')}\n")
        text.insert("end", f"Table #: {order['table_number']}\n")
        text.insert("end", f"Date: {order['order_date']}\n\n")
        text.insert("end", "Items Ordered:\n")
        
        for item in order["items"]:
            text.insert("end", f"{item['name'].ljust(20)} {str(item['quantity']).rjust(3)} x {self.convert_to_inr(item['price']).rjust(6)} = {item['total'].rjust(8)}\n")
        
        text.insert("end", f"\nSubtotal: {order['subtotal']}\n")
        text.insert("end", f"GST ({self.gst_percentage}%): {order['gst_amount']}\n")
        text.insert("end", f"Grand Total: {order['grand_total']}\n")
        
        text.config(state="disabled")
        
        # Print button
        ttk.Button(details_window, text="Print", command=lambda: self.print_bill_from_order(order),
                  style="Accent.TButton").pack(pady=5)

    def print_bill_from_order(self, order):
        bill_content = self.generate_bill_content(
            order["items"],
            float(order["subtotal"].replace("₹", "")),
            float(order["gst_amount"].replace("₹", "")),
            float(order["grand_total"].replace("₹", ""))
        )
        
        messagebox.showinfo("Print Bill", "Bill sent to printer.\n\n" + bill_content)

    def manage_tables(self):
        table_window = tk.Toplevel(self.root)
        table_window.title("Manage Tables")
        table_window.geometry("700x500")
        
        # Treeview for tables
        tree = ttk.Treeview(table_window, columns=("ID", "Capacity", "Status", "Reservation"), 
                          show="headings", selectmode="browse")
        tree.heading("ID", text="Table #")
        tree.heading("Capacity", text="Capacity")
        tree.heading("Status", text="Status")
        tree.heading("Reservation", text="Reserved For")
        
        tree.column("ID", width=50, anchor="center")
        tree.column("Capacity", width=70, anchor="center")
        tree.column("Status", width=80, anchor="center")
        tree.column("Reservation", width=150)
        
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Load table data
        tables_data = self.load_data(self.tables_file)
        for table in tables_data["tables"]:
            status = "Reserved" if table["reserved"] else "Available"
            reservation = table.get("reservation_details", {}).get("name", "") if table["reserved"] else ""
            tree.insert("", "end", values=(
                table["id"], 
                table["capacity"], 
                status,
                reservation
            ))
        
        # Button frame
        button_frame = ttk.Frame(table_window)
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(button_frame, text="Add Table", command=lambda: self.add_table(tree),
                  style="Accent.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Remove Table", command=lambda: self.remove_table(tree),
                  style="TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Toggle Status", command=lambda: self.toggle_table_status(tree),
                  style="TButton").pack(side="left", padx=5)

    def add_table(self, tree):
        capacity = simpledialog.askinteger("Add Table", "Enter table capacity (2-10):", minvalue=2, maxvalue=10)
        if capacity:
            with open(self.tables_file, 'r') as f:
                tables_data = json.load(f)
            
            new_id = max(table["id"] for table in tables_data["tables"]) + 1
            tables_data["tables"].append({
                "id": new_id, 
                "capacity": capacity, 
                "reserved": False,
                "reservation_details": None
            })
            
            with open(self.tables_file, 'w') as f:
                json.dump(tables_data, f, indent=4)
            
            tree.insert("", "end", values=(new_id, capacity, "Available", ""))
            messagebox.showinfo("Success", f"Table #{new_id} added successfully")

    def remove_table(self, tree):
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a table")
            return
            
        table_id = tree.item(selected_item)["values"][0]
        
        if messagebox.askyesno("Confirm", f"Remove Table #{table_id}?"):
            with open(self.tables_file, 'r') as f:
                tables_data = json.load(f)
            
            tables_data["tables"] = [table for table in tables_data["tables"] if table["id"] != table_id]
            
            with open(self.tables_file, 'w') as f:
                json.dump(tables_data, f, indent=4)
            
            tree.delete(selected_item)
            messagebox.showinfo("Success", f"Table #{table_id} removed successfully")

    def toggle_table_status(self, tree):
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a table")
            return
            
        table_id = tree.item(selected_item)["values"][0]
        
        with open(self.tables_file, 'r') as f:
            tables_data = json.load(f)
        
        for table in tables_data["tables"]:
            if table["id"] == table_id:
                if table["reserved"]:
                    if messagebox.askyesno("Confirm", f"Mark Table #{table_id} as available?"):
                        table["reserved"] = False
                        table["reservation_details"] = None
                        tree.item(selected_item, values=(
                            table_id,
                            table["capacity"],
                            "Available",
                            ""
                        ))
                else:
                    table["reserved"] = True
                    table["reservation_details"] = {
                        "name": "Manual Reservation",
                        "contact": "",
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "time": "00:00",
                        "party_size": 1
                    }
                    tree.item(selected_item, values=(
                        table_id,
                        table["capacity"],
                        "Reserved",
                        "Manual Reservation"
                    ))
                break
        
        with open(self.tables_file, 'w') as f:
            json.dump(tables_data, f, indent=4)

    def manage_users(self):
        users_window = tk.Toplevel(self.root)
        users_window.title("User Management")
        users_window.geometry("600x400")
        
        # Treeview for users
        tree = ttk.Treeview(users_window, columns=("Username", "Password"), show="headings")
        tree.heading("Username", text="Username")
        tree.heading("Password", text="Password (hidden)")
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Load user data
        users = self.load_data(self.users_file)
        for username, password in users.items():
            tree.insert("", "end", values=(username, "*" * len(password)))
        
        # Button frame
        btn_frame = ttk.Frame(users_window)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="Add User", command=lambda: self.add_user(tree),
                  style="Accent.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Remove User", command=lambda: self.remove_user(tree),
                  style="TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Reset Password", command=lambda: self.reset_password(tree),
                  style="TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Close", command=users_window.destroy,
                  style="TButton").pack(side="right", padx=5)

    def add_user(self, tree):
        username = simpledialog.askstring("Add User", "Enter username:")
        if username:
            if username in self.load_data(self.users_file):
                messagebox.showerror("Error", "Username already exists")
                return
                
            password = simpledialog.askstring("Add User", "Enter password:", show="*")
            if password and len(password) >= 6:
                users = self.load_data(self.users_file)
                users[username] = password
                self.save_data(users, self.users_file)
                tree.insert("", "end", values=(username, "*" * len(password)))
                messagebox.showinfo("Success", "User added successfully")
            else:
                messagebox.showerror("Error", "Password must be at least 6 characters")

    def remove_user(self, tree):
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a user")
            return
            
        username = tree.item(selected_item)["values"][0]
        
        if username == "admin":
            messagebox.showerror("Error", "Cannot remove admin account")
            return
            
        if messagebox.askyesno("Confirm", f"Remove user {username}?"):
            users = self.load_data(self.users_file)
            del users[username]
            self.save_data(users, self.users_file)
            tree.delete(selected_item)
            messagebox.showinfo("Success", "User removed successfully")

    def reset_password(self, tree):
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a user")
            return
            
        username = tree.item(selected_item)["values"][0]
        password = simpledialog.askstring("Reset Password", f"Enter new password for {username}:", show="*")
        
        if password and len(password) >= 6:
            users = self.load_data(self.users_file)
            users[username] = password
            self.save_data(users, self.users_file)
            tree.item(selected_item, values=(username, "*" * len(password)))
            messagebox.showinfo("Success", "Password reset successfully")
        else:
            messagebox.showerror("Error", "Password must be at least 6 characters")

    def add_new_item(self):
        new_item = simpledialog.askstring("New Item", "Enter item name:")
        if new_item:
            price = simpledialog.askinteger("Price", f"Enter price for {new_item}:", minvalue=1)
            if price:
                self.items[new_item] = price
                self.save_data(self.items, self.menu_file)
                # Recreate the order tab to show new item
                self.create_order_tab_content()
                messagebox.showinfo("Success", f"{new_item} added to menu!")

    def export_data(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Export Data"
        )
        
        if file_path:
            try:
                data = {
                    "menu": self.load_data(self.menu_file),
                    "tables": self.load_data(self.tables_file),
                    "orders": self.load_data(self.orders_file),
                    "users": self.load_data(self.users_file)
                }
                
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=4)
                
                messagebox.showinfo("Success", "Data exported successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {str(e)}")

    def export_report(self, report):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Save Sales Report"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(report)
                messagebox.showinfo("Success", "Report exported successfully")
            except:
                messagebox.showerror("Error", "Failed to export report")

    def show_user_guide(self):
        guide = """
        Restaurant Management System - User Guide
        
        1. New Order Tab:
           - Enter customer details
           - Select items and quantities
           - Generate and print bills
        
        2. Table Reservation Tab:
           - Check table availability
           - Make new reservations
           - Cancel existing reservations
        
        3. Admin Features (Admin only):
           - Add/remove menu items
           - View sales reports
           - Manage order history
           - Manage tables
           - Manage users
        
        For assistance, contact support@restaurant.com
        """
        
        guide_window = tk.Toplevel(self.root)
        guide_window.title("User Guide")
        
        text = tk.Text(guide_window, wrap="word", padx=10, pady=10)
        text.pack(fill="both", expand=True)
        text.insert("1.0", guide)
        text.config(state="disabled")

    def show_about(self):
        about = """
        Restaurant Management System
        Version 2.0
        
        Developed by:
        Restaurant Solutions Inc.
        
        © 2023 All Rights Reserved
        """
        
        messagebox.showinfo("About", about)

    def validate_contact(self, value):
        if value == "":
            return True
        if len(value) > 10:
            return False
        return value.isdigit()

# Main application flow
if __name__ == "__main__":
    # Create root window
    root = tk.Tk()
    
    # Configure ttk styles
    style = ttk.Style()
    style.configure("TButton", padding=6)
    style.configure("Accent.TButton", background="#4CAF50", foreground="white")
    
    # Run authentication system
    auth_system = AuthSystem(root)
    root.mainloop()
