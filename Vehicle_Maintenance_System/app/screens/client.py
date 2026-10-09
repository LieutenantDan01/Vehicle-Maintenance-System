import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from database.db import fetch_all, fetch_one
from app.ui_helpers import card


class ClientScreensMixin:
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

        tk.Label(wrapper, text="My Vehicle & Service Tracking", font=("Segoe UI", 23, "bold"), bg="#F7F3E8", fg="#23352D").pack(anchor="w")
        tk.Label(wrapper, text="View your vehicle information and latest maintenance status.", font=("Segoe UI", 10), bg="#F7F3E8", fg="#5F6B64").pack(anchor="w", pady=(3, 22))

        try:
            owner = self.user.get("full_name", "")
            vehicles = fetch_all(
                """SELECT id, plate_number, brand, model, year, vehicle_type
                   FROM vehicles
                   WHERE LOWER(TRIM(owner_name)) = LOWER(TRIM(%s))
                   ORDER BY id DESC""",
                (owner,),
            )
            service_count = fetch_one(
                """SELECT COUNT(*) AS total
                   FROM maintenance_records m
                   JOIN vehicles v ON v.id = m.vehicle_id
                   WHERE LOWER(TRIM(v.owner_name)) = LOWER(TRIM(%s))""",
                (owner,),
            )["total"]
            active_count = fetch_one(
                """SELECT COUNT(*) AS total
                   FROM maintenance_records m
                   JOIN vehicles v ON v.id = m.vehicle_id
                   WHERE LOWER(TRIM(v.owner_name)) = LOWER(TRIM(%s))
                     AND m.status IN ('Scheduled', 'In Progress')""",
                (owner,),
            )["total"]
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return

        cards = tk.Frame(wrapper, bg="#F7F3E8")
        cards.pack(fill="x")

        card(cards, "MY VEHICLES", str(len(vehicles)), "#2E6B50").pack(side="left", fill="x", expand=True, padx=(0, 8))
        card(cards, "SERVICE RECORDS", str(service_count), "#2E7D32").pack(side="left", fill="x", expand=True, padx=8)
        card(cards, "ACTIVE SERVICES", str(active_count), "#A06A00").pack(side="left", fill="x", expand=True, padx=(8, 0))

        panel = tk.Frame(wrapper, bg="white")
        panel.pack(fill="both", expand=True, pady=(22, 0))

        tk.Label(panel, text="My Vehicles", font=("Segoe UI", 14, "bold"), bg="white", fg="#23352D").pack(anchor="w", padx=20, pady=(18, 10))

        columns = ("plate", "brand", "model", "year", "type")
        tree = ttk.Treeview(panel, columns=columns, show="headings")
        tree.tag_configure("completed", foreground="#2E7D32")
        tree.tag_configure("scheduled", foreground="#2E6B50")
        tree.tag_configure("in_progress", foreground="#A06A00")
        tree.tag_configure("cancelled", foreground="#A33A3A")
        headings = {
            "plate": "Plate Number",
            "brand": "Brand",
            "model": "Model",
            "year": "Year",
            "type": "Vehicle Type",
        }
        widths = {"plate": 150, "brand": 130, "model": 150, "year": 90, "type": 160}

        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="w")

        for row in vehicles:
            tree.insert("", "end", values=(row["plate_number"], row["brand"], row["model"], row["year"], row["vehicle_type"]))

        tree.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        if not vehicles:
            tk.Label(panel, text="No vehicle is currently linked to your client account.", font=("Segoe UI", 10), bg="white", fg="#9CA3AF").pack(pady=10)

        self.schedule_client_refresh("Client Dashboard")

    def show_client_history(self):
        self.current_page = "My Service History"
        self.clear_content("My Service History")

        outer = tk.Frame(self.content, bg="#F7F3E8")
        outer.pack(fill="both", expand=True, padx=25, pady=20)

        tk.Label(outer, text="My Service History", font=("Segoe UI", 20, "bold"), bg="#F7F3E8", fg="#23352D").pack(anchor="w", pady=(0, 5))
        tk.Label(outer, text="Track maintenance and service updates for your vehicle.", font=("Segoe UI", 10), bg="#F7F3E8", fg="#5F6B64").pack(anchor="w", pady=(0, 8))
        tk.Button(outer, text="Refresh Now", command=self.show_client_history, bg="#E2DED2", fg="#23352D", bd=0, padx=14, pady=7, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 10))

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
                (owner,),
            )
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return

        panel = tk.Frame(outer, bg="white")
        panel.pack(fill="both", expand=True)

        columns = ("date", "plate", "vehicle", "service", "description", "mileage", "cost", "status")
        tree = ttk.Treeview(panel, columns=columns, show="headings")
        headings = {
            "date": "Date",
            "plate": "Plate Number",
            "vehicle": "Vehicle",
            "service": "Service Type",
            "description": "Description",
            "mileage": "Mileage",
            "cost": "Cost",
            "status": "Status",
        }
        widths = {
            "date": 100,
            "plate": 120,
            "vehicle": 160,
            "service": 150,
            "description": 240,
            "mileage": 100,
            "cost": 110,
            "status": 120,
        }

        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="w")

        for row in records:
            status = row["status"] or ""
            tag = status.lower().replace(" ", "_")
            tree.insert(
                "",
                "end",
                values=(
                    row["service_date"],
                    row["plate_number"],
                    f'{row["brand"]} {row["model"]}',
                    row["service_type"],
                    row["description"] or "",
                    row["mileage"] or "",
                    f'₱{float(row["cost"]):,.2f}',
                    status,
                ),
                tags=(tag,),
            )

        tree.pack(fill="both", expand=True, padx=15, pady=15)

        if not records:
            tk.Label(panel, text="No service records found for your account.", font=("Segoe UI", 10), bg="white", fg="#9CA3AF").pack(pady=10)

        self.schedule_client_refresh("My Service History")
