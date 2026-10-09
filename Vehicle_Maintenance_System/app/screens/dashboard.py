import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from database.db import fetch_all, fetch_one


class DashboardScreensMixin:
    def show_dashboard(self):
        self.current_page = "Dashboard"
        self.clear_content("Dashboard")

        wrapper = tk.Frame(self.content, bg="#F7F3E8")
        wrapper.pack(fill="both", expand=True, padx=28, pady=25)

        tk.Label(wrapper, text="System Overview", font=("Segoe UI", 23, "bold"), bg="#F7F3E8", fg="#23352D").pack(anchor="w")
        tk.Label(wrapper, text="Monitor vehicles and maintenance activity.", font=("Segoe UI", 10), bg="#F7F3E8", fg="#5F6B64").pack(anchor="w", pady=(3, 22))

        try:
            vehicle_count = fetch_one("SELECT COUNT(*) AS total FROM vehicles")["total"]
            service_count = fetch_one("SELECT COUNT(*) AS total FROM maintenance_records")["total"]
            expense = fetch_one("SELECT COALESCE(SUM(cost),0) AS total FROM maintenance_records")["total"]
            completed = fetch_one("SELECT COUNT(*) AS total FROM maintenance_records WHERE status='Completed'")["total"]
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return

        cards = tk.Frame(wrapper, bg="#F7F3E8")
        cards.pack(fill="x")

        self.card(cards, "TOTAL VEHICLES", str(vehicle_count), "#2E6B50").pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.card(cards, "SERVICE RECORDS", str(service_count), "#2E7D32").pack(side="left", fill="x", expand=True, padx=8)
        self.card(cards, "TOTAL EXPENSES", f"₱{float(expense):,.2f}", "#A06A00").pack(side="left", fill="x", expand=True, padx=8)
        self.card(cards, "COMPLETED SERVICES", str(completed), "#6A4C93").pack(side="left", fill="x", expand=True, padx=(8, 0))

        panel = tk.Frame(wrapper, bg="white")
        panel.pack(fill="both", expand=True, pady=(22, 0))

        tk.Label(panel, text="Recent Maintenance Records", font=("Segoe UI", 14, "bold"), bg="white", fg="#23352D").pack(anchor="w", padx=20, pady=(18, 10))

        columns = ("date", "plate", "service", "cost", "status")
        tree = ttk.Treeview(panel, columns=columns, show="headings", height=8)
        headings = {
            "date": "Date",
            "plate": "Plate Number",
            "service": "Service Type",
            "cost": "Cost",
            "status": "Status",
        }
        widths = {"date": 110, "plate": 130, "service": 220, "cost": 120, "status": 130}
        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="w")

        try:
            rows = fetch_all(
                """
                SELECT m.service_date, v.plate_number, m.service_type,
                       m.cost, m.status
                FROM maintenance_records m
                JOIN vehicles v ON v.id = m.vehicle_id
                ORDER BY m.service_date DESC, m.id DESC
                LIMIT 8
            """
            )
            for row in rows:
                tree.insert("", "end", values=(row["service_date"], row["plate_number"], row["service_type"], f"₱{float(row['cost']):,.2f}", row["status"]))
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))

        tree.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def show_history(self):
        self.current_page = "Service History"
        self.clear_content("Service History")

        outer = tk.Frame(self.content, bg="#F7F3E8")
        outer.pack(fill="both", expand=True, padx=25, pady=20)

        top = tk.Frame(outer, bg="#F7F3E8")
        top.pack(fill="x", pady=(0, 15))

        tk.Label(top, text="Select Vehicle", font=("Segoe UI", 10, "bold"), bg="#F7F3E8", fg="#D8D2C3").pack(side="left")

        rows = fetch_all("SELECT id, plate_number, owner_name FROM vehicles ORDER BY plate_number")
        vehicle_map = {f"{r['plate_number']} - {r['owner_name']}": r["id"] for r in rows}

        combo = ttk.Combobox(top, values=list(vehicle_map.keys()), state="readonly", width=35)
        combo.pack(side="left", padx=12)

        panel = tk.Frame(outer, bg="white")
        panel.pack(fill="both", expand=True)

        columns = ("date", "service", "description", "mileage", "cost", "status")
        tree = ttk.Treeview(panel, columns=columns, show="headings")
        headings = {
            "date": "Date",
            "service": "Service Type",
            "description": "Description",
            "mileage": "Mileage",
            "cost": "Cost",
            "status": "Status",
        }
        widths = {"date": 110, "service": 180, "description": 280, "mileage": 100, "cost": 120, "status": 120}
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
                records = fetch_all(
                    """
                    SELECT service_date, service_type, description,
                           mileage, cost, status
                    FROM maintenance_records
                    WHERE vehicle_id=%s
                    ORDER BY service_date DESC, id DESC
                """,
                    (vehicle_id,),
                )
                for r in records:
                    tree.insert("", "end", values=(r["service_date"], r["service_type"], r["description"] or "", r["mileage"] or "", f"₱{float(r['cost']):,.2f}", r["status"]))
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", str(e))

        combo.bind("<<ComboboxSelected>>", load_history)

        if list(vehicle_map.keys()):
            combo.current(0)
            load_history()
