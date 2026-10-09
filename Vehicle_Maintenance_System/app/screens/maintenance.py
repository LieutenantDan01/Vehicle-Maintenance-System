import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import mysql.connector
from tkcalendar import DateEntry
from database.db import fetch_all, fetch_one, execute_query, ensure_mechanic_column
from app.ui_helpers import enable_entry_shortcuts


class MaintenanceScreensMixin:
    def show_maintenance(self):
        self.current_page = "Maintenance"
        self.clear_content("Maintenance Records")
        outer = tk.Frame(self.content, bg="#F7F3E8")
        outer.pack(fill="both", expand=True, padx=26, pady=22)
        title = tk.Frame(outer, bg="#F7F3E8")
        title.pack(fill="x", pady=(0, 14))
        tk.Label(title, text="Maintenance Records", font=("Segoe UI", 22, "bold"), bg="#F7F3E8", fg="#1F4D3A").pack(anchor="w")
        tk.Label(title, text="Create, manage, and track every vehicle service record.", font=("Segoe UI", 10), bg="#F7F3E8", fg="#78847D").pack(anchor="w", pady=(3, 0))
        toolbar = tk.Frame(outer, bg="white", highlightthickness=1, highlightbackground="#E6E6E6")
        toolbar.pack(fill="x", pady=(0, 10), ipady=7)
        tk.Button(toolbar, text="＋ Add Service Record", command=self.add_service, bg="#2E6B50", fg="white", bd=0, padx=15, pady=9, font=("Segoe UI", 10, "bold")).pack(side="left", padx=(10, 5))
        tk.Button(toolbar, text="Edit Selected", command=self.edit_service, bg="#F59E0B", fg="white", bd=0, padx=15, pady=9, font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)
        tk.Button(toolbar, text="Delete Selected", command=self.delete_service, bg="#D64545", fg="white", bd=0, padx=15, pady=9, font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)
        tk.Button(toolbar, text="Refresh", command=self.show_maintenance, bg="#F0F0F0", fg="#34495E", bd=0, padx=15, pady=9, font=("Segoe UI", 10, "bold")).pack(side="right", padx=10)
        status_var = tk.StringVar(value="Select status")
        status_combo = ttk.Combobox(toolbar, textvariable=status_var, values=["Scheduled", "In Progress", "Completed", "Cancelled"], state="readonly", width=15)
        status_combo.pack(side="right", padx=5)

        def update_selected_status():
            values = self.selected_service()
            if not values:
                return
            new_status = status_combo.get()
            if new_status not in ("Scheduled", "In Progress", "Completed", "Cancelled"):
                messagebox.showwarning("Status Required", "Select a status first.")
                return
            try:
                execute_query("UPDATE maintenance_records SET status=%s WHERE id=%s", (new_status, values[0]))
                messagebox.showinfo("Status Updated", f"Service record #{values[0]} is now {new_status}.")
                self.show_maintenance()
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", str(e))

        tk.Button(toolbar, text="Update Status", command=update_selected_status, bg="#2E8B57", fg="white", bd=0, padx=15, pady=9, font=("Segoe UI", 10, "bold")).pack(side="right", padx=5)
        panel = tk.Frame(outer, bg="white", highlightthickness=1, highlightbackground="#E6E6E6")
        panel.pack(fill="both", expand=True)
        columns = ("id", "date", "plate", "service", "description", "mileage", "cost", "status")
        self.service_tree = ttk.Treeview(panel, columns=columns, show="headings")
        headings = {"id": "ID", "date": "Date", "plate": "Plate", "service": "Service Type", "description": "Description", "mileage": "Mileage", "cost": "Cost", "status": "Status"}
        widths = {"id": 45, "date": 100, "plate": 100, "service": 155, "description": 240, "mileage": 95, "cost": 110, "status": 125}
        for col in columns:
            self.service_tree.heading(col, text=headings[col])
            self.service_tree.column(col, width=widths[col], anchor="w")
        self.service_tree.tag_configure("completed", foreground="#16804A")
        self.service_tree.tag_configure("scheduled", foreground="#2E6B50")
        self.service_tree.tag_configure("in_progress", foreground="#A06A00")
        self.service_tree.tag_configure("cancelled", foreground="#C0392B")
        self.service_tree.pack(fill="both", expand=True, padx=12, pady=12)
        self.service_tree.bind("<Double-1>", lambda e: self.edit_service())
        try:
            ensure_mechanic_column()
            rows = fetch_all("""SELECT m.id,m.service_date,v.plate_number,m.service_type,m.description,m.mileage,m.cost,m.status FROM maintenance_records m JOIN vehicles v ON v.id=m.vehicle_id ORDER BY m.service_date DESC,m.id DESC""")
            for row in rows:
                status = row["status"] or ""
                tag = status.lower().replace(" ", "_")
                self.service_tree.insert("", "end", values=(row["id"], row["service_date"], row["plate_number"], row["service_type"], row["description"] or "", row["mileage"] or "", f"₱{float(row['cost']):,.2f}", status), tags=(tag,))
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))

    def selected_service(self):
        selection = self.service_tree.selection()
        if not selection:
            messagebox.showwarning("Select Record", "Please select a service record first.")
            return None
        return self.service_tree.item(selection[0], "values")

    def service_form(self, title, existing=None):
        self.current_page = title
        self.clear_content(title)

        outer = tk.Frame(self.content, bg="#F7F3E8")
        outer.pack(fill="both", expand=True, padx=20, pady=12)

        top = tk.Frame(outer, bg="#F7F3E8")
        top.pack(fill="x", pady=(0, 10))

        tk.Button(top, text="← Back to Maintenance", command=self.show_maintenance, bg="#E2DED2", fg="#23352D", bd=0, padx=14, pady=7, font=("Segoe UI", 10, "bold")).pack(side="left")

        panel = tk.Frame(outer, bg="white")
        panel.pack(fill="both", expand=True)

        form = tk.Frame(panel, bg="white")
        form.pack(fill="both", expand=True, padx=28, pady=14)
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        def field_label(text, row, col, colspan=1):
            tk.Label(form, text=text, bg="white", fg="#D8D2C3", font=("Segoe UI", 9, "bold")).grid(row=row, column=col, columnspan=colspan, sticky="w", padx=5, pady=(2, 3))

        vehicle_rows = fetch_all("SELECT id, plate_number, owner_name FROM vehicles ORDER BY plate_number")
        vehicle_map = {f"{r['plate_number']} - {r['owner_name']}": r["id"] for r in vehicle_rows}

        field_label("Vehicle", 0, 0, 2)
        vehicle_combo = ttk.Combobox(form, values=list(vehicle_map.keys()), state="readonly", font=("Segoe UI", 10))
        vehicle_combo.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 7), ipady=3)

        field_label("Service Date", 2, 0)
        field_label("Service Type", 2, 1)

        date_entry = DateEntry(form, date_pattern="yyyy-mm-dd", font=("Segoe UI", 10), state="readonly")
        date_entry.grid(row=3, column=0, sticky="ew", padx=5, pady=(0, 7), ipady=5)

        service_entry = tk.Entry(form, font=("Segoe UI", 10), relief="solid", bd=1)
        service_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=(0, 7), ipady=5)
        enable_entry_shortcuts(service_entry)

        field_label("Mileage", 4, 0)
        field_label("Cost", 4, 1)

        mileage_field = tk.Frame(form, bg="white")
        mileage_field.grid(row=5, column=0, sticky="ew", padx=5, pady=(0, 7))
        mileage_entry = tk.Entry(mileage_field, font=("Segoe UI", 10), relief="solid", bd=1)
        mileage_entry.pack(side="left", fill="x", expand=True, ipady=5)
        enable_entry_shortcuts(mileage_entry)
        tk.Label(mileage_field, text="km", bg="#F7F3E8", fg="#5F6B64", font=("Segoe UI", 10, "bold"), padx=10, pady=5).pack(side="left", padx=(6, 0))

        cost_field = tk.Frame(form, bg="white")
        cost_field.grid(row=5, column=1, sticky="ew", padx=5, pady=(0, 7))
        tk.Label(cost_field, text="₱", bg="#F7F3E8", fg="#5F6B64", font=("Segoe UI", 10, "bold"), padx=10, pady=5).pack(side="left", padx=(0, 6))
        cost_entry = tk.Entry(cost_field, font=("Segoe UI", 10), relief="solid", bd=1)
        cost_entry.pack(side="left", fill="x", expand=True, ipady=5)
        enable_entry_shortcuts(cost_entry)

        field_label("Mechanic Name", 6, 0)
        field_label("Status", 6, 1)

        mechanic_entry = tk.Entry(form, font=("Segoe UI", 10), relief="solid", bd=1)
        mechanic_entry.grid(row=7, column=0, sticky="ew", padx=5, pady=(0, 7), ipady=5)
        enable_entry_shortcuts(mechanic_entry)

        status_combo = ttk.Combobox(form, values=["Completed", "Scheduled", "In Progress", "Cancelled"], state="readonly", font=("Segoe UI", 10))
        status_combo.grid(row=7, column=1, sticky="ew", padx=5, pady=(0, 7), ipady=3)

        field_label("Description", 8, 0, 2)
        description_entry = tk.Entry(form, font=("Segoe UI", 10), relief="solid", bd=1)
        description_entry.grid(row=9, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 7), ipady=5)
        enable_entry_shortcuts(description_entry)

        if existing:
            vehicle_match = None
            for text_value, vid in vehicle_map.items():
                if vid == existing["vehicle_id"]:
                    vehicle_match = text_value
                    break
            if vehicle_match:
                vehicle_combo.set(vehicle_match)
            date_entry.set_date(existing["service_date"])
            service_entry.insert(0, existing["service_type"] or "")
            description_entry.insert(0, existing["description"] or "")
            mileage_entry.insert(0, existing["mileage"] or "")
            cost_entry.insert(0, str(existing["cost"] or ""))
            mechanic_entry.insert(0, existing.get("mechanic_name") or "")
            status_combo.set(existing["status"] or "Scheduled")
        else:
            vehicle_combo.set(list(vehicle_map.keys())[0] if vehicle_map else "")
            status_combo.set("Scheduled")

        button_row = tk.Frame(form, bg="white")
        button_row.grid(row=10, column=0, columnspan=2, sticky="ew", padx=5, pady=(6, 0))

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
            mechanic_name = mechanic_entry.get().strip()
            data = (vehicle_id, date_text, service_type, description_entry.get().strip(), mileage_entry.get().strip(), cost, status, mechanic_name)

            try:
                if existing:
                    execute_query(
                        """
                        UPDATE maintenance_records
                        SET vehicle_id=%s, service_date=%s, service_type=%s,
                            description=%s, mileage=%s, cost=%s, status=%s,
                            mechanic_name=%s
                        WHERE id=%s
                    """,
                        data + (existing["id"],),
                    )
                else:
                    execute_query(
                        """
                        INSERT INTO maintenance_records
                        (vehicle_id, service_date, service_type, description,
                         mileage, cost, status, mechanic_name)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                        data,
                    )

                messagebox.showinfo("Saved", "Service record saved successfully.")
                self.show_maintenance()

            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", str(e))

        tk.Button(button_row, text="SAVE SERVICE RECORD", command=save, bg="#2E6B50", fg="white", bd=0, font=("Segoe UI", 10, "bold"), padx=25, pady=9).pack(side="left")
        tk.Button(button_row, text="CANCEL", command=self.show_maintenance, bg="#E2DED2", fg="#23352D", bd=0, font=("Segoe UI", 10, "bold"), padx=25, pady=9).pack(side="left", padx=10)

    def add_service(self):
        rows = fetch_one("SELECT COUNT(*) AS total FROM vehicles")
        if rows["total"] == 0:
            messagebox.showinfo("No Vehicles", "Add a vehicle first before creating a service record.")
            return
        self.service_form("Add Service Record")

    def edit_service(self):
        values = self.selected_service()
        if not values:
            return
        try:
            existing = fetch_one("SELECT * FROM maintenance_records WHERE id=%s", (values[0],))
            self.service_form("Edit Service Record", existing)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))

    def delete_service(self):
        values = self.selected_service()
        if not values:
            return
        if not messagebox.askyesno("Delete Record", "Delete the selected maintenance record?"):
            return
        try:
            execute_query("DELETE FROM maintenance_records WHERE id=%s", (values[0],))
            self.show_maintenance()
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
