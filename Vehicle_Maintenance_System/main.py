import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import mysql.connector
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


def fetch_all(query, params=()):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()


def fetch_one(query, params=()):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params)
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()


def execute_query(query, params=()):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close()
        conn.close()

class VehicleMaintenanceApp:
    def __init__(self, user):
        self.user = user
        self.root = tk.Tk()
        self.root.title("Vehicle Maintenance & Service Tracking System")
        self.root.geometry("1200x720")
        self.root.minsize(1050, 650)
        self.root.configure(bg="#F7F3E8")

        self.current_page = None
        self.selected_vehicle_id = None
        self.selected_service_id = None
        self.client_refresh_job = None

        self.setup_style()
        self.build_layout()
        self.show_dashboard()

    def enable_entry_shortcuts(self, entry):
        """Enable standard Windows keyboard shortcuts for a Tkinter Entry."""

        def select_all(event=None):
            entry.select_range(0, "end")
            entry.icursor("end")
            return "break"

        def copy_text(event=None):
            try:
                entry.event_generate("<<Copy>>")
            except tk.TclError:
                pass
            return "break"

        def paste_text(event=None):
            try:
                entry.event_generate("<<Paste>>")
            except tk.TclError:
                pass
            return "break"

        def cut_text(event=None):
            try:
                entry.event_generate("<<Cut>>")
            except tk.TclError:
                pass
            return "break"

        def undo_text(event=None):
            return "break"

        entry.bind("<Control-a>", select_all)
        entry.bind("<Control-A>", select_all)
        entry.bind("<Control-c>", copy_text)
        entry.bind("<Control-C>", copy_text)
        entry.bind("<Control-v>", paste_text)
        entry.bind("<Control-V>", paste_text)
        entry.bind("<Control-x>", cut_text)
        entry.bind("<Control-X>", cut_text)
        entry.bind("<Control-z>", undo_text)
        entry.bind("<Control-Z>", undo_text)

    def setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Treeview",
            background="white",
            foreground="#23352D",
            rowheight=34,
            fieldbackground="white",
            font=("Segoe UI", 10)
        )
        style.configure(
            "Treeview.Heading",
            background="#E2DED2",
            foreground="#23352D",
            font=("Segoe UI", 10, "bold")
        )
        style.map("Treeview", background=[("selected", "#ECE8DD")])

        style.configure(
            "TCombobox",
            padding=7,
            font=("Segoe UI", 10)
        )

    def build_layout(self):
        """Modern dashboard layout for administrator accounts."""
        self.sidebar = tk.Frame(self.root, bg="#1F4D3A", width=235)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        brand = tk.Frame(self.sidebar, bg="#1F4D3A")
        brand.pack(fill="x", padx=18, pady=(24, 28))
        logo = tk.Label(brand, text="VM", font=("Segoe UI", 20, "bold"),
                        bg="#2E6B50", fg="white", width=3, pady=5)
        logo.pack(side="left")
        text = tk.Frame(brand, bg="#1F4D3A")
        text.pack(side="left", padx=10)
        tk.Label(text, text="Vehicle Maintenance", font=("Segoe UI", 10, "bold"),
                 bg="#1F4D3A", fg="white").pack(anchor="w")
        tk.Label(text, text="Service Tracking", font=("Segoe UI", 9),
                 bg="#1F4D3A", fg="#DDD8CB").pack(anchor="w")

        tk.Label(self.sidebar, text="MAIN MENU", font=("Segoe UI", 8, "bold"),
                 bg="#1F4D3A", fg="#78847D").pack(anchor="w", padx=22, pady=(0, 8))
        self.nav_button("Dashboard", self.show_dashboard)
        self.nav_button("Vehicles", self.show_vehicles)
        self.nav_button("Maintenance", self.show_maintenance)
        self.nav_button("Service History", self.show_history)

        tk.Frame(self.sidebar, bg="#D8D2C3", height=1).pack(fill="x", padx=20, pady=18)
        tk.Label(self.sidebar, text="ACCOUNT", font=("Segoe UI", 8, "bold"),
                 bg="#1F4D3A", fg="#78847D").pack(anchor="w", padx=22, pady=(0, 8))
        tk.Button(self.sidebar, text="  Logout", anchor="w", font=("Segoe UI", 10, "bold"),
                  bd=0, relief="flat", bg="#1F4D3A", fg="#B8D4C5",
                  activebackground="#17402F", activeforeground="white",
                  padx=20, pady=11, command=self.logout).pack(fill="x", padx=10)

        self.main = tk.Frame(self.root, bg="#F7F3E8")
        self.main.pack(side="left", fill="both", expand=True)

        header = tk.Frame(self.main, bg="white", height=72, highlightthickness=1,
                          highlightbackground="#E6E6E6")
        header.pack(fill="x")
        header.pack_propagate(False)
        self.header_title = tk.Label(header, text="Dashboard", font=("Segoe UI", 18, "bold"),
                                     bg="white", fg="#1F4D3A")
        self.header_title.pack(side="left", padx=28)
        userbox = tk.Frame(header, bg="white")
        userbox.pack(side="right", padx=24)
        tk.Label(userbox, text="Administrator", font=("Segoe UI", 9),
                 bg="white", fg="#78847D").pack(anchor="e")
        tk.Label(userbox, text=self.user.get('full_name', 'User'), font=("Segoe UI", 10, "bold"),
                 bg="white", fg="#1F4D3A").pack(anchor="e")

        self.content = tk.Frame(self.main, bg="#F7F3E8")
        self.content.pack(fill="both", expand=True)


    def build_client_layout(self):
        """Modern simplified navigation for client accounts."""
        for widget in self.sidebar.winfo_children(): widget.destroy()
        self.sidebar.configure(bg="#1F4D3A")
        brand=tk.Frame(self.sidebar,bg="#1F4D3A"); brand.pack(fill="x",padx=18,pady=(24,28))
        tk.Label(brand,text="VM",font=("Segoe UI",20,"bold"),bg="#2E6B50",fg="white",width=3,pady=5).pack(side="left")
        t=tk.Frame(brand,bg="#1F4D3A"); t.pack(side="left",padx=10)
        tk.Label(t,text="Client Portal",font=("Segoe UI",11,"bold"),bg="#1F4D3A",fg="white").pack(anchor="w")
        tk.Label(t,text="Service Tracking",font=("Segoe UI",9),bg="#1F4D3A",fg="#DDD8CB").pack(anchor="w")
        tk.Label(self.sidebar,text="MY ACCOUNT",font=("Segoe UI",8,"bold"),bg="#1F4D3A",fg="#78847D").pack(anchor="w",padx=22,pady=(0,8))
        self.nav_button("My Dashboard", self.show_client_dashboard)
        self.nav_button("My Service History", self.show_client_history)
        tk.Button(self.sidebar,text="  Logout",anchor="w",font=("Segoe UI",10,"bold"),bd=0,relief="flat",bg="#1F4D3A",fg="#B8D4C5",activebackground="#17402F",activeforeground="white",padx=20,pady=11,command=self.logout).pack(side="bottom",fill="x",padx=10,pady=18)


    def schedule_client_refresh(self, page):
        """Refresh the client tracking page automatically so status changes appear quickly."""
        if str(self.user.get("role", "")).strip().lower() != "client":
            return

        def refresh():
            if not self.root.winfo_exists():
                return
            if self.current_page == page:
                if page == "Client Dashboard":
                    self.show_client_dashboard()
                elif page == "My Service History":
                    self.show_client_history()

        self.client_refresh_job = self.root.after(2000, refresh)

    def show_client_dashboard(self):
        self.current_page = "Client Dashboard"
        self.clear_content("My Vehicle & Service Tracking")

        wrapper = tk.Frame(self.content, bg="#F7F3E8")
        wrapper.pack(fill="both", expand=True, padx=28, pady=25)

        tk.Label(
            wrapper, text="My Vehicle & Service Tracking",
            font=("Segoe UI", 23, "bold"),
            bg="#F7F3E8", fg="#23352D"
        ).pack(anchor="w")

        tk.Label(
            wrapper,
            text="View your vehicle information and latest maintenance status.",
            font=("Segoe UI", 10), bg="#F7F3E8", fg="#5F6B64"
        ).pack(anchor="w", pady=(3, 22))

        try:
            owner = self.user.get("full_name", "")
            vehicles = fetch_all(
                """SELECT id, plate_number, brand, model, year, vehicle_type
                   FROM vehicles
                   WHERE LOWER(TRIM(owner_name)) = LOWER(TRIM(%s))
                   ORDER BY id DESC""",
                (owner,)
            )
            service_count = fetch_one(
                """SELECT COUNT(*) AS total
                   FROM maintenance_records m
                   JOIN vehicles v ON v.id = m.vehicle_id
                   WHERE LOWER(TRIM(v.owner_name)) = LOWER(TRIM(%s))""",
                (owner,)
            )["total"]
            active_count = fetch_one(
                """SELECT COUNT(*) AS total
                   FROM maintenance_records m
                   JOIN vehicles v ON v.id = m.vehicle_id
                   WHERE LOWER(TRIM(v.owner_name)) = LOWER(TRIM(%s))
                     AND m.status IN ('Scheduled', 'In Progress')""",
                (owner,)
            )["total"]
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return

        cards = tk.Frame(wrapper, bg="#F7F3E8")
        cards.pack(fill="x")

        self.card(cards, "MY VEHICLES", str(len(vehicles)), "#2E6B50").pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        self.card(cards, "SERVICE RECORDS", str(service_count), "#2E7D32").pack(
            side="left", fill="x", expand=True, padx=8
        )
        self.card(cards, "ACTIVE SERVICES", str(active_count), "#A06A00").pack(
            side="left", fill="x", expand=True, padx=(8, 0)
        )

        panel = tk.Frame(wrapper, bg="white")
        panel.pack(fill="both", expand=True, pady=(22, 0))

        tk.Label(
            panel, text="My Vehicles",
            font=("Segoe UI", 14, "bold"),
            bg="white", fg="#23352D"
        ).pack(anchor="w", padx=20, pady=(18, 10))

        columns = ("plate", "brand", "model", "year", "type")
        tree = ttk.Treeview(panel, columns=columns, show="headings")
        tree.tag_configure("completed", foreground="#2E7D32")
        tree.tag_configure("scheduled", foreground="#2E6B50")
        tree.tag_configure("in_progress", foreground="#A06A00")
        tree.tag_configure("cancelled", foreground="#A33A3A")
        headings = {
            "plate": "Plate Number", "brand": "Brand",
            "model": "Model", "year": "Year", "type": "Vehicle Type"
        }
        widths = {"plate": 150, "brand": 130, "model": 150, "year": 90, "type": 160}

        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="w")

        for row in vehicles:
            tree.insert("", "end", values=(
                row["plate_number"], row["brand"], row["model"],
                row["year"], row["vehicle_type"]
            ))

        tree.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        if not vehicles:
            tk.Label(
                panel,
                text="No vehicle is currently linked to your client account.",
                font=("Segoe UI", 10), bg="white", fg="#9CA3AF"
            ).pack(pady=10)

        self.schedule_client_refresh("Client Dashboard")

    def show_client_history(self):
        self.current_page = "My Service History"
        self.clear_content("My Service History")

        outer = tk.Frame(self.content, bg="#F7F3E8")
        outer.pack(fill="both", expand=True, padx=25, pady=20)

        tk.Label(
            outer, text="My Service History",
            font=("Segoe UI", 20, "bold"),
            bg="#F7F3E8", fg="#23352D"
        ).pack(anchor="w", pady=(0, 5))

        tk.Label(
            outer,
            text="Track maintenance and service updates for your vehicle.",
            font=("Segoe UI", 10), bg="#F7F3E8", fg="#5F6B64"
        ).pack(anchor="w", pady=(0, 8))

        tk.Button(
            outer, text="Refresh Now", command=self.show_client_history,
            bg="#E2DED2", fg="#23352D", bd=0, padx=14, pady=7,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(0, 10))

        try:
            owner = self.user.get("full_name", "")
            records = fetch_all(
                """SELECT m.service_date, v.plate_number, v.brand, v.model,
                          m.service_type, m.description, m.mileage,
                          m.cost, m.status
                   FROM maintenance_records m
                   JOIN vehicles v ON v.id = m.vehicle_id
                   WHERE LOWER(TRIM(v.owner_name)) = LOWER(TRIM(%s))
                   ORDER BY m.service_date DESC, m.id DESC""",
                (owner,)
            )
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return

        panel = tk.Frame(outer, bg="white")
        panel.pack(fill="both", expand=True)

        columns = (
            "date", "plate", "vehicle", "service",
            "description", "mileage", "cost", "status"
        )
        tree = ttk.Treeview(panel, columns=columns, show="headings")
        headings = {
            "date": "Date", "plate": "Plate Number", "vehicle": "Vehicle",
            "service": "Service Type", "description": "Description",
            "mileage": "Mileage", "cost": "Cost", "status": "Status"
        }
        widths = {
            "date": 100, "plate": 120, "vehicle": 160, "service": 150,
            "description": 240, "mileage": 100, "cost": 110, "status": 120
        }

        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="w")

        for row in records:
            status = row["status"] or ""
            tag = status.lower().replace(" ", "_")
            tree.insert("", "end", values=(
                row["service_date"],
                row["plate_number"],
                f'{row["brand"]} {row["model"]}',
                row["service_type"],
                row["description"] or "",
                row["mileage"] or "",
                f'₱{float(row["cost"]):,.2f}',
                status
            ), tags=(tag,))

        tree.pack(fill="both", expand=True, padx=15, pady=15)

        if not records:
            tk.Label(
                panel,
                text="No service records found for your account.",
                font=("Segoe UI", 10), bg="white", fg="#9CA3AF"
            ).pack(pady=10)

        self.schedule_client_refresh("My Service History")

    def nav_button(self, text, command):
        btn=tk.Button(self.sidebar,text=f"  {text}",anchor="w",font=("Segoe UI",10,"bold"),bd=0,relief="flat",bg="#1F4D3A",fg="#E5E5E5",activebackground="#383838",activeforeground="white",padx=18,pady=11,command=command)
        btn.pack(fill="x",padx=10,pady=2)
        return btn


    def clear_content(self, title):
        if self.client_refresh_job is not None:
            try:
                self.root.after_cancel(self.client_refresh_job)
            except tk.TclError:
                pass
            self.client_refresh_job = None
        for widget in self.content.winfo_children():
            widget.destroy()
        self.header_title.config(text=title)

    def card(self, parent, title, value, accent):
        frame=tk.Frame(parent,bg="white",height=112,highlightthickness=1,highlightbackground="#E6E6E6")
        frame.pack_propagate(False)
        tk.Frame(frame,bg=accent,width=5).pack(side="left",fill="y")
        inner=tk.Frame(frame,bg="white"); inner.pack(side="left",fill="both",expand=True,padx=16,pady=14)
        tk.Label(inner,text=title,font=("Segoe UI",8,"bold"),bg="white",fg="#78847D").pack(anchor="w")
        tk.Label(inner,text=value,font=("Segoe UI",21,"bold"),bg="white",fg="#1F4D3A").pack(anchor="w",pady=(7,0))
        return frame

    def show_dashboard(self):
        self.current_page = "Dashboard"
        self.clear_content("Dashboard")

        wrapper = tk.Frame(self.content, bg="#F7F3E8")
        wrapper.pack(fill="both", expand=True, padx=28, pady=25)

        tk.Label(
            wrapper, text="System Overview",
            font=("Segoe UI", 23, "bold"), bg="#F7F3E8", fg="#23352D"
        ).pack(anchor="w")
        tk.Label(
            wrapper, text="Monitor vehicles and maintenance activity.",
            font=("Segoe UI", 10), bg="#F7F3E8", fg="#5F6B64"
        ).pack(anchor="w", pady=(3, 22))

        try:
            vehicle_count = fetch_one("SELECT COUNT(*) AS total FROM vehicles")["total"]
            service_count = fetch_one("SELECT COUNT(*) AS total FROM maintenance_records")["total"]
            expense = fetch_one(
                "SELECT COALESCE(SUM(cost),0) AS total FROM maintenance_records"
            )["total"]
            completed = fetch_one(
                "SELECT COUNT(*) AS total FROM maintenance_records WHERE status='Completed'"
            )["total"]
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return

        cards = tk.Frame(wrapper, bg="#F7F3E8")
        cards.pack(fill="x")

        self.card(cards, "TOTAL VEHICLES", str(vehicle_count), "#2E6B50").pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        self.card(cards, "SERVICE RECORDS", str(service_count), "#2E7D32").pack(
            side="left", fill="x", expand=True, padx=8
        )
        self.card(cards, "TOTAL EXPENSES", f"₱{float(expense):,.2f}", "#A06A00").pack(
            side="left", fill="x", expand=True, padx=8
        )
        self.card(cards, "COMPLETED SERVICES", str(completed), "#6A4C93").pack(
            side="left", fill="x", expand=True, padx=(8, 0)
        )

        panel = tk.Frame(wrapper, bg="white")
        panel.pack(fill="both", expand=True, pady=(22, 0))

        tk.Label(
            panel, text="Recent Maintenance Records",
            font=("Segoe UI", 14, "bold"), bg="white", fg="#23352D"
        ).pack(anchor="w", padx=20, pady=(18, 10))

        columns = ("date", "plate", "service", "cost", "status")
        tree = ttk.Treeview(panel, columns=columns, show="headings", height=8)
        headings = {
            "date": "Date", "plate": "Plate Number",
            "service": "Service Type", "cost": "Cost", "status": "Status"
        }
        widths = {"date": 110, "plate": 130, "service": 220, "cost": 120, "status": 130}
        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="w")

        try:
            rows = fetch_all("""
                SELECT m.service_date, v.plate_number, m.service_type,
                       m.cost, m.status
                FROM maintenance_records m
                JOIN vehicles v ON v.id = m.vehicle_id
                ORDER BY m.service_date DESC, m.id DESC
                LIMIT 8
            """)
            for row in rows:
                tree.insert("", "end", values=(
                    row["service_date"],
                    row["plate_number"],
                    row["service_type"],
                    f"₱{float(row['cost']):,.2f}",
                    row["status"]
                ))
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))

        tree.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def show_vehicles(self):
        self.current_page = "Vehicles"
        self.clear_content("Vehicle Management")

        outer = tk.Frame(self.content, bg="#F7F3E8")
        outer.pack(fill="both", expand=True, padx=25, pady=20)

        toolbar = tk.Frame(outer, bg="#F7F3E8")
        toolbar.pack(fill="x", pady=(0, 12))

        tk.Button(
            toolbar, text="+ Add Vehicle", command=self.add_vehicle,
            bg="#2E6B50", fg="white", bd=0, padx=16, pady=9,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")

        tk.Button(
            toolbar, text="Edit Selected", command=self.edit_vehicle,
            bg="#D98E04", fg="white", bd=0, padx=16, pady=9,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=8)

        tk.Button(
            toolbar, text="Delete Selected", command=self.delete_vehicle,
            bg="#A33A3A", fg="white", bd=0, padx=16, pady=9,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")

        tk.Button(
            toolbar, text="Refresh", command=self.show_vehicles,
            bg="#E2DED2", fg="#23352D", bd=0, padx=16, pady=9,
            font=("Segoe UI", 10)
        ).pack(side="right")

        panel = tk.Frame(outer, bg="white")
        panel.pack(fill="both", expand=True)

        columns = ("id", "plate", "owner", "brand", "model", "year", "type", "contact")
        self.vehicle_tree = ttk.Treeview(panel, columns=columns, show="headings")

        headings = {
            "id": "ID", "plate": "Plate Number", "owner": "Owner",
            "brand": "Brand", "model": "Model", "year": "Year",
            "type": "Type", "contact": "Contact"
        }
        widths = {
            "id": 50, "plate": 120, "owner": 170, "brand": 100,
            "model": 110, "year": 70, "type": 110, "contact": 130
        }

        for col in columns:
            self.vehicle_tree.heading(col, text=headings[col])
            self.vehicle_tree.column(col, width=widths[col], anchor="w")

        self.vehicle_tree.pack(fill="both", expand=True, padx=15, pady=15)
        self.vehicle_tree.bind("<Double-1>", lambda e: self.edit_vehicle())

        try:
            rows = fetch_all("""
                SELECT id, plate_number, owner_name, brand, model,
                       year, vehicle_type, contact_number
                FROM vehicles
                ORDER BY id DESC
            """)
            for row in rows:
                self.vehicle_tree.insert("", "end", values=(
                    row["id"], row["plate_number"], row["owner_name"],
                    row["brand"], row["model"], row["year"],
                    row["vehicle_type"], row["contact_number"] or ""
                ))
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))

    def selected_vehicle(self):
        selection = self.vehicle_tree.selection()
        if not selection:
            messagebox.showwarning("Select Vehicle", "Please select a vehicle first.")
            return None
        values = self.vehicle_tree.item(selection[0], "values")
        return values

    def vehicle_form(self, title, existing=None):
        self.current_page = title
        self.clear_content(title)

        outer = tk.Frame(self.content, bg="#F7F3E8")
        outer.pack(fill="both", expand=True, padx=28, pady=18)

        top = tk.Frame(outer, bg="#F7F3E8")
        top.pack(fill="x", pady=(0, 10))

        tk.Button(
            top, text="← Back to Vehicles", command=self.show_vehicles,
            bg="#E2DED2", fg="#23352D", bd=0, padx=14, pady=8,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")

        tk.Label(
            top, text=title, font=("Segoe UI", 18, "bold"),
            bg="#F7F3E8", fg="#23352D"
        ).pack(side="left", padx=18)

        panel = tk.Frame(outer, bg="white")
        panel.pack(fill="both", expand=True)

        tk.Label(
            panel,
            text="Vehicle Information",
            font=("Segoe UI", 13, "bold"),
            bg="white", fg="#23352D"
        ).pack(anchor="w", padx=28, pady=(20, 2))

        tk.Label(
            panel,
            text="Enter the vehicle details below, then click Save Vehicle.",
            font=("Segoe UI", 9), bg="white", fg="#5F6B64"
        ).pack(anchor="w", padx=28, pady=(0, 12))

        form = tk.Frame(panel, bg="white")
        form.pack(fill="x", padx=28, pady=4)
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        fields = [
            ("Plate Number", "plate"),
            ("Owner Name", "owner"),
            ("Brand", "brand"),
            ("Model", "model"),
            ("Year", "year"),
            ("Vehicle Type", "type"),
            ("Contact Number", "contact")
        ]
        entries = {}

        for index, (label, key) in enumerate(fields):
            row = index // 2
            col = index % 2
            cell = tk.Frame(form, bg="white")
            cell.grid(row=row, column=col, sticky="ew", padx=(0, 12) if col == 0 else (12, 0), pady=(0, 9))

            tk.Label(
                cell, text=label, bg="white", fg="#D8D2C3",
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w", pady=(0, 3))

            entry = tk.Entry(
                cell, font=("Segoe UI", 10), relief="solid", bd=1
            )
            entry.pack(fill="x", ipady=6)
            self.enable_entry_shortcuts(entry)
            entries[key] = entry

        if existing:
            vals = {
                "plate": existing["plate_number"],
                "owner": existing["owner_name"],
                "brand": existing["brand"],
                "model": existing["model"],
                "year": existing["year"],
                "type": existing["vehicle_type"],
                "contact": existing["contact_number"] or ""
            }
            for key, value in vals.items():
                entries[key].insert(0, str(value))

        button_row = tk.Frame(panel, bg="#F7F3E8", height=72)
        button_row.pack(side="bottom", fill="x")
        button_row.pack_propagate(False)

        def save():
            values = {k: e.get().strip() for k, e in entries.items()}

            if not all(values.values()):
                messagebox.showwarning(
                    "Required Fields", "Please complete all vehicle information before saving."
                )
                return

            try:
                if existing:
                    execute_query("""
                        UPDATE vehicles
                        SET plate_number=%s, owner_name=%s, brand=%s,
                            model=%s, year=%s, vehicle_type=%s, contact_number=%s
                        WHERE id=%s
                    """, (
                        values["plate"], values["owner"], values["brand"],
                        values["model"], values["year"], values["type"],
                        values["contact"], existing["id"]
                    ))
                    messagebox.showinfo("Saved", "Vehicle information updated successfully.")
                else:
                    execute_query("""
                        INSERT INTO vehicles
                        (plate_number, owner_name, brand, model, year,
                         vehicle_type, contact_number)
                        VALUES (%s,%s,%s,%s,%s,%s,%s)
                    """, (
                        values["plate"], values["owner"], values["brand"],
                        values["model"], values["year"], values["type"],
                        values["contact"]
                    ))
                    messagebox.showinfo("Saved", "Vehicle added successfully.")

                self.show_vehicles()

            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", str(e))

        tk.Button(
            button_row, text="SAVE VEHICLE", command=save,
            bg="#2E6B50", fg="white", bd=0,
            font=("Segoe UI", 10, "bold"), padx=25, pady=10
        ).pack(side="right", padx=(8, 28), pady=14)

        tk.Button(
            button_row, text="CANCEL", command=self.show_vehicles,
            bg="#E2DED2", fg="#23352D", bd=0,
            font=("Segoe UI", 10, "bold"), padx=25, pady=10
        ).pack(side="right", pady=14)

        entries["plate"].focus_set()

    def add_vehicle(self):
        self.vehicle_form("Add Vehicle")

    def edit_vehicle(self):
        values = self.selected_vehicle()
        if not values:
            return
        try:
            existing = fetch_one(
                "SELECT * FROM vehicles WHERE id=%s", (values[0],)
            )
            self.vehicle_form("Edit Vehicle", existing)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))

    def delete_vehicle(self):
        values = self.selected_vehicle()
        if not values:
            return
        if not messagebox.askyesno(
            "Delete Vehicle",
            f"Delete vehicle {values[1]}?\nIts maintenance records will also be deleted."
        ):
            return
        try:
            execute_query("DELETE FROM vehicles WHERE id=%s", (values[0],))
            self.show_vehicles()
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))

    def show_maintenance(self):
        self.current_page = "Maintenance"
        self.clear_content("Maintenance Records")
        outer=tk.Frame(self.content,bg="#F7F3E8"); outer.pack(fill="both",expand=True,padx=26,pady=22)
        title=tk.Frame(outer,bg="#F7F3E8"); title.pack(fill="x",pady=(0,14))
        tk.Label(title,text="Maintenance Records",font=("Segoe UI",22,"bold"),bg="#F7F3E8",fg="#1F4D3A").pack(anchor="w")
        tk.Label(title,text="Create, manage, and track every vehicle service record.",font=("Segoe UI",10),bg="#F7F3E8",fg="#78847D").pack(anchor="w",pady=(3,0))
        toolbar=tk.Frame(outer,bg="white",highlightthickness=1,highlightbackground="#E6E6E6"); toolbar.pack(fill="x",pady=(0,10),ipady=7)
        tk.Button(toolbar,text="＋ Add Service Record",command=self.add_service,bg="#2E6B50",fg="white",bd=0,padx=15,pady=9,font=("Segoe UI",10,"bold")).pack(side="left",padx=(10,5))
        tk.Button(toolbar,text="Edit Selected",command=self.edit_service,bg="#F59E0B",fg="white",bd=0,padx=15,pady=9,font=("Segoe UI",10,"bold")).pack(side="left",padx=5)
        tk.Button(toolbar,text="Delete Selected",command=self.delete_service,bg="#D64545",fg="white",bd=0,padx=15,pady=9,font=("Segoe UI",10,"bold")).pack(side="left",padx=5)
        tk.Button(toolbar,text="Refresh",command=self.show_maintenance,bg="#F0F0F0",fg="#34495E",bd=0,padx=15,pady=9,font=("Segoe UI",10,"bold")).pack(side="right",padx=10)
        status_var=tk.StringVar(value="Select status")
        status_combo=ttk.Combobox(toolbar,textvariable=status_var,values=["Scheduled","In Progress","Completed","Cancelled"],state="readonly",width=15)
        status_combo.pack(side="right",padx=5)
        def update_selected_status():
            values=self.selected_service()
            if not values:return
            new_status=status_combo.get()
            if new_status not in ("Scheduled","In Progress","Completed","Cancelled"):
                messagebox.showwarning("Status Required","Select a status first."); return
            try:
                execute_query("UPDATE maintenance_records SET status=%s WHERE id=%s",(new_status,values[0]))
                messagebox.showinfo("Status Updated",f"Service record #{values[0]} is now {new_status}.")
                self.show_maintenance()
            except mysql.connector.Error as e: messagebox.showerror("Database Error",str(e))
        tk.Button(toolbar,text="Update Status",command=update_selected_status,bg="#2E8B57",fg="white",bd=0,padx=15,pady=9,font=("Segoe UI",10,"bold")).pack(side="right",padx=5)
        panel=tk.Frame(outer,bg="white",highlightthickness=1,highlightbackground="#E6E6E6"); panel.pack(fill="both",expand=True)
        columns=("id","date","plate","service","description","mileage","cost","status")
        self.service_tree=ttk.Treeview(panel,columns=columns,show="headings")
        headings={"id":"ID","date":"Date","plate":"Plate","service":"Service Type","description":"Description","mileage":"Mileage","cost":"Cost","status":"Status"}
        widths={"id":45,"date":100,"plate":100,"service":155,"description":240,"mileage":95,"cost":110,"status":125}
        for col in columns:self.service_tree.heading(col,text=headings[col]); self.service_tree.column(col,width=widths[col],anchor="w")
        self.service_tree.tag_configure("completed",foreground="#16804A")
        self.service_tree.tag_configure("scheduled",foreground="#2E6B50")
        self.service_tree.tag_configure("in_progress",foreground="#A06A00")
        self.service_tree.tag_configure("cancelled",foreground="#C0392B")
        self.service_tree.pack(fill="both",expand=True,padx=12,pady=12)
        self.service_tree.bind("<Double-1>",lambda e:self.edit_service())
        try:
            rows=fetch_all("""SELECT m.id,m.service_date,v.plate_number,m.service_type,m.description,m.mileage,m.cost,m.status FROM maintenance_records m JOIN vehicles v ON v.id=m.vehicle_id ORDER BY m.service_date DESC,m.id DESC""")
            for row in rows:
                status=row["status"] or ""; tag=status.lower().replace(" ","_")
                self.service_tree.insert("","end",values=(row["id"],row["service_date"],row["plate_number"],row["service_type"],row["description"] or "",row["mileage"] or "",f"₱{float(row['cost']):,.2f}",status),tags=(tag,))
        except mysql.connector.Error as e: messagebox.showerror("Database Error",str(e))


    def selected_service(self):
        selection = self.service_tree.selection()
        if not selection:
            messagebox.showwarning("Select Record", "Please select a service record first.")
            return None
        return self.service_tree.item(selection[0], "values")

    def service_form(self, title, existing=None):
        # Compact embedded form so Save/Cancel are always visible.
        self.current_page = title
        self.clear_content(title)

        outer = tk.Frame(self.content, bg="#F7F3E8")
        outer.pack(fill="both", expand=True, padx=20, pady=12)

        top = tk.Frame(outer, bg="#F7F3E8")
        top.pack(fill="x", pady=(0, 10))

        tk.Button(
            top, text="← Back to Maintenance", command=self.show_maintenance,
            bg="#E2DED2", fg="#23352D", bd=0, padx=14, pady=7,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")

        tk.Label(
            top, text=title, font=("Segoe UI", 18, "bold"),
            bg="#F7F3E8", fg="#23352D"
        ).pack(side="left", padx=18)

        panel = tk.Frame(outer, bg="white")
        panel.pack(fill="both", expand=True)

        form = tk.Frame(panel, bg="white")
        form.pack(fill="both", expand=True, padx=28, pady=14)
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        def field_label(text, row, col, colspan=1):
            tk.Label(
                form, text=text, bg="white", fg="#D8D2C3",
                font=("Segoe UI", 9, "bold")
            ).grid(row=row, column=col, columnspan=colspan,
                   sticky="w", padx=5, pady=(2, 3))

        vehicle_rows = fetch_all(
            "SELECT id, plate_number, owner_name FROM vehicles ORDER BY plate_number"
        )
        vehicle_map = {
            f"{r['plate_number']} - {r['owner_name']}": r["id"]
            for r in vehicle_rows
        }

        field_label("Vehicle", 0, 0, 2)
        vehicle_combo = ttk.Combobox(
            form, values=list(vehicle_map.keys()), state="readonly",
            font=("Segoe UI", 10)
        )
        vehicle_combo.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 7), ipady=3)

        field_label("Service Date (YYYY-MM-DD)", 2, 0)
        field_label("Service Type", 2, 1)

        date_entry = tk.Entry(form, font=("Segoe UI", 10), relief="solid", bd=1)
        date_entry.grid(row=3, column=0, sticky="ew", padx=5, pady=(0, 7), ipady=5)
        self.enable_entry_shortcuts(date_entry)

        service_entry = tk.Entry(form, font=("Segoe UI", 10), relief="solid", bd=1)
        service_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=(0, 7), ipady=5)
        self.enable_entry_shortcuts(service_entry)

        field_label("Mileage", 4, 0)
        field_label("Cost", 4, 1)

        mileage_entry = tk.Entry(form, font=("Segoe UI", 10), relief="solid", bd=1)
        mileage_entry.grid(row=5, column=0, sticky="ew", padx=5, pady=(0, 7), ipady=5)
        self.enable_entry_shortcuts(mileage_entry)

        cost_entry = tk.Entry(form, font=("Segoe UI", 10), relief="solid", bd=1)
        cost_entry.grid(row=5, column=1, sticky="ew", padx=5, pady=(0, 7), ipady=5)
        self.enable_entry_shortcuts(cost_entry)

        field_label("Status", 6, 0)
        field_label("Description", 6, 1)

        status_combo = ttk.Combobox(
            form, values=["Completed", "Scheduled", "In Progress", "Cancelled"],
            state="readonly", font=("Segoe UI", 10)
        )
        status_combo.grid(row=7, column=0, sticky="ew", padx=5, pady=(0, 7), ipady=3)

        description_entry = tk.Entry(form, font=("Segoe UI", 10), relief="solid", bd=1)
        description_entry.grid(row=7, column=1, sticky="ew", padx=5, pady=(0, 7), ipady=5)
        self.enable_entry_shortcuts(description_entry)

        if existing:
            vehicle_match = None
            for text_value, vid in vehicle_map.items():
                if vid == existing["vehicle_id"]:
                    vehicle_match = text_value
                    break
            if vehicle_match:
                vehicle_combo.set(vehicle_match)
            date_entry.insert(0, str(existing["service_date"]))
            service_entry.insert(0, existing["service_type"] or "")
            description_entry.insert(0, existing["description"] or "")
            mileage_entry.insert(0, existing["mileage"] or "")
            cost_entry.insert(0, str(existing["cost"] or ""))
            status_combo.set(existing["status"] or "Scheduled")
        else:
            vehicle_combo.set(list(vehicle_map.keys())[0] if vehicle_map else "")
            date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
            status_combo.set("Scheduled")

        button_row = tk.Frame(form, bg="white")
        button_row.grid(row=8, column=0, columnspan=2, sticky="ew", padx=5, pady=(6, 0))

        def save():
            vehicle_text = vehicle_combo.get().strip()
            if not vehicle_text:
                messagebox.showwarning("Required", "Please select a vehicle.")
                return

            date_text = date_entry.get().strip()
            try:
                datetime.strptime(date_text, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Invalid Date", "Use YYYY-MM-DD, for example 2026-09-21.")
                return

            service_type = service_entry.get().strip()
            status = status_combo.get().strip()
            if not service_type or not status:
                messagebox.showwarning("Required", "Service type and status are required.")
                return

            try:
                cost = float(cost_entry.get().strip() or 0)
            except ValueError:
                messagebox.showwarning("Invalid Cost", "Enter a valid number for cost.")
                return

            vehicle_id = vehicle_map[vehicle_text]
            data = (
                vehicle_id, date_text, service_type,
                description_entry.get().strip(),
                mileage_entry.get().strip(), cost, status
            )

            try:
                if existing:
                    execute_query("""
                        UPDATE maintenance_records
                        SET vehicle_id=%s, service_date=%s, service_type=%s,
                            description=%s, mileage=%s, cost=%s, status=%s
                        WHERE id=%s
                    """, data + (existing["id"],))
                else:
                    execute_query("""
                        INSERT INTO maintenance_records
                        (vehicle_id, service_date, service_type, description,
                         mileage, cost, status)
                        VALUES (%s,%s,%s,%s,%s,%s,%s)
                    """, data)

                messagebox.showinfo("Saved", "Service record saved successfully.")
                self.show_maintenance()

            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", str(e))

        tk.Button(
            button_row, text="SAVE SERVICE RECORD", command=save,
            bg="#2E6B50", fg="white", bd=0,
            font=("Segoe UI", 10, "bold"), padx=25, pady=9
        ).pack(side="left")

        tk.Button(
            button_row, text="CANCEL", command=self.show_maintenance,
            bg="#E2DED2", fg="#23352D", bd=0,
            font=("Segoe UI", 10, "bold"), padx=25, pady=9
        ).pack(side="left", padx=10)

    def add_service(self):
        rows = fetch_one("SELECT COUNT(*) AS total FROM vehicles")
        if rows["total"] == 0:
            messagebox.showinfo(
                "No Vehicles",
                "Add a vehicle first before creating a service record."
            )
            return
        self.service_form("Add Service Record")

    def edit_service(self):
        values = self.selected_service()
        if not values:
            return
        try:
            existing = fetch_one(
                "SELECT * FROM maintenance_records WHERE id=%s", (values[0],)
            )
            self.service_form("Edit Service Record", existing)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))

    def delete_service(self):
        values = self.selected_service()
        if not values:
            return
        if not messagebox.askyesno(
            "Delete Record",
            "Delete the selected maintenance record?"
        ):
            return
        try:
            execute_query("DELETE FROM maintenance_records WHERE id=%s", (values[0],))
            self.show_maintenance()
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))

    def show_history(self):
        self.current_page = "Service History"
        self.clear_content("Service History")

        outer = tk.Frame(self.content, bg="#F7F3E8")
        outer.pack(fill="both", expand=True, padx=25, pady=20)

        top = tk.Frame(outer, bg="#F7F3E8")
        top.pack(fill="x", pady=(0, 15))

        tk.Label(
            top, text="Select Vehicle",
            font=("Segoe UI", 10, "bold"), bg="#F7F3E8", fg="#D8D2C3"
        ).pack(side="left")

        rows = fetch_all(
            "SELECT id, plate_number, owner_name FROM vehicles ORDER BY plate_number"
        )
        vehicle_map = {
            f"{r['plate_number']} - {r['owner_name']}": r["id"] for r in rows
        }

        combo = ttk.Combobox(
            top, values=list(vehicle_map.keys()), state="readonly", width=35
        )
        combo.pack(side="left", padx=12)

        panel = tk.Frame(outer, bg="white")
        panel.pack(fill="both", expand=True)

        columns = ("date", "service", "description", "mileage", "cost", "status")
        tree = ttk.Treeview(panel, columns=columns, show="headings")
        headings = {
            "date": "Date", "service": "Service Type",
            "description": "Description", "mileage": "Mileage",
            "cost": "Cost", "status": "Status"
        }
        widths = {
            "date": 110, "service": 180, "description": 280,
            "mileage": 100, "cost": 120, "status": 120
        }
        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="w")
        tree.pack(fill="both", expand=True, padx=15, pady=15)

        def load_history(event=None):
            for item in tree.get_children():
                tree.delete(item)
            text = combo.get()
            if not text:
                return
            vehicle_id = vehicle_map[text]
            try:
                records = fetch_all("""
                    SELECT service_date, service_type, description,
                           mileage, cost, status
                    FROM maintenance_records
                    WHERE vehicle_id=%s
                    ORDER BY service_date DESC, id DESC
                """, (vehicle_id,))
                for r in records:
                    tree.insert("", "end", values=(
                        r["service_date"], r["service_type"],
                        r["description"] or "", r["mileage"] or "",
                        f"₱{float(r['cost']):,.2f}", r["status"]
                    ))
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", str(e))

        combo.bind("<<ComboboxSelected>>", load_history)

        if list(vehicle_map.keys()):
            combo.current(0)
            load_history()

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            launch_login()

    def run(self):
        self.root.mainloop()

def launch_login():
    login = tk.Tk()
    login.title("Vehicle Maintenance & Service Tracking System")
    login.geometry("900x600")
    login.resizable(False, False)
    login.configure(bg="#23352D")

    left = tk.Frame(login, bg="#23352D", width=430)
    left.pack(side="left", fill="y")
    left.pack_propagate(False)

    tk.Label(
        left, text="VM", font=("Segoe UI", 42, "bold"),
        fg="white", bg="#2E6B50", width=4, pady=5
    ).pack(anchor="w", padx=50, pady=(105, 25))

    tk.Label(
        left, text="Vehicle Maintenance\n& Service Tracking\nSystem",
        font=("Segoe UI", 21, "bold"), fg="white", bg="#23352D",
        justify="left", wraplength=340
    ).pack(anchor="w", padx=35)

    tk.Label(
        left,
        text="Manage vehicles and services, or let clients\ntrack their own maintenance history.",
        font=("Segoe UI", 11), fg="#E2DED2", bg="#23352D",
        justify="left"
    ).pack(anchor="w", padx=50, pady=(20, 0))

    right = tk.Frame(login, bg="#F7F3E8")
    right.pack(side="right", fill="both", expand=True)

    box = tk.Frame(right, bg="white")
    box.pack(fill="both", expand=True, padx=45, pady=65)

    tk.Label(
        box, text="Welcome Back", font=("Segoe UI", 24, "bold"),
        bg="white", fg="#23352D"
    ).pack(anchor="w", padx=35, pady=(42, 5))

    tk.Label(
        box, text="Sign in to continue",
        font=("Segoe UI", 10), bg="white", fg="#5F6B64"
    ).pack(anchor="w", padx=35, pady=(0, 28))

    tk.Label(
        box, text="Username", font=("Segoe UI", 10, "bold"),
        bg="white", fg="#D8D2C3"
    ).pack(anchor="w", padx=35)

    username = tk.Entry(box, font=("Segoe UI", 11), bd=1, relief="solid")
    username.pack(fill="x", padx=35, pady=(7, 18), ipady=9)

    tk.Label(
        box, text="Password", font=("Segoe UI", 10, "bold"),
        bg="white", fg="#D8D2C3"
    ).pack(anchor="w", padx=35)

    password_frame = tk.Frame(box, bg="white")
    password_frame.pack(fill="x", padx=35, pady=(7, 20))

    password = tk.Entry(
        password_frame, font=("Segoe UI", 11),
        bd=1, relief="solid", show="*"
    )
    password.pack(side="left", fill="x", expand=True, ipady=9)

    def enable_login_shortcuts(entry):
        def select_all(event=None):
            entry.select_range(0, "end")
            entry.icursor("end")
            return "break"

        def copy_text(event=None):
            try:
                entry.event_generate("<<Copy>>")
            except tk.TclError:
                pass
            return "break"

        def paste_text(event=None):
            try:
                entry.event_generate("<<Paste>>")
            except tk.TclError:
                pass
            return "break"

        def cut_text(event=None):
            try:
                entry.event_generate("<<Cut>>")
            except tk.TclError:
                pass
            return "break"

        def undo_text(event=None):
            return "break"

        entry.bind("<Control-a>", select_all)
        entry.bind("<Control-A>", select_all)
        entry.bind("<Control-c>", copy_text)
        entry.bind("<Control-C>", copy_text)
        entry.bind("<Control-v>", paste_text)
        entry.bind("<Control-V>", paste_text)
        entry.bind("<Control-x>", cut_text)
        entry.bind("<Control-X>", cut_text)
        entry.bind("<Control-z>", undo_text)
        entry.bind("<Control-Z>", undo_text)

    enable_login_shortcuts(username)
    enable_login_shortcuts(password)

    def toggle():
        if password.cget("show") == "":
            password.config(show="*")
            show.config(text="Show")
        else:
            password.config(show="")
            show.config(text="Hide")

    show = tk.Button(
        password_frame, text="Show", command=toggle,
        bg="white", fg="#2E6B50", bd=0,
        font=("Segoe UI", 9, "bold")
    )
    show.pack(side="right", padx=5)

    def do_login():
        u = username.get().strip()
        p = password.get()
        if not u or not p:
            messagebox.showwarning(
                "Login Required", "Please enter your username and password.", parent=login
            )
            return

        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT id, username, full_name, role
                FROM users
                WHERE username=%s AND password=%s
            """, (u, p))
            user = cur.fetchone()
            cur.close()
            conn.close()

            if user:
                login.destroy()
                app = VehicleMaintenanceApp(user)
                if str(user.get("role", "")).strip().lower() == "client":
                    app.build_client_layout()
                    app.show_client_dashboard()
                app.run()
            else:
                messagebox.showerror(
                    "Login Failed", "Invalid username or password.", parent=login
                )
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e), parent=login)

    tk.Button(
        box, text="SIGN IN", command=do_login,
        font=("Segoe UI", 11, "bold"), bg="#2E6B50", fg="white",
        activebackground="#C65D0E", activeforeground="white",
        bd=0, pady=11
    ).pack(fill="x", padx=35)

    login.bind("<Return>", lambda e: do_login())
    username.focus()
    login.mainloop()


if __name__ == "__main__":
    launch_login()
