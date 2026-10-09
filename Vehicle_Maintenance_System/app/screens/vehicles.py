import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import mysql.connector
from database.db import fetch_all, fetch_one, execute_query
from app.ui_helpers import enable_entry_shortcuts


VEHICLE_OPTIONS = {
    "2-Wheeler": {
        "brands": ["Honda", "Yamaha", "Suzuki", "Kawasaki", "KTM", "Vespa", "Rusi", "Motorstar", "Kymco", "CFMoto"],
        "types": ["Scooter", "Underbone", "Naked", "Sportbike", "Touring", "Cafe Racer"],
    },
    "4-Wheeler": {
        "brands": ["Honda", "Toyota", "Mitsubishi", "Nissan", "Suzuki", "Isuzu", "Mazda", "Ford", "Chevrolet", "Jeep", "Hyundai", "Kia", "MG"],
        "types": ["Sedan", "Hatchback", "SUV", "CUV", "MPV", "Pickup Truck", "Coupe", "Van"],
    },
}


class VehicleScreensMixin:
    def show_vehicles(self):
        self.current_page = "Vehicles"
        self.clear_content("Vehicle Management")

        outer = tk.Frame(self.content, bg="#F7F3E8")
        outer.pack(fill="both", expand=True, padx=25, pady=20)

        toolbar = tk.Frame(outer, bg="#F7F3E8")
        toolbar.pack(fill="x", pady=(0, 12))

        tk.Button(toolbar, text="+ Add Vehicle", command=self.add_vehicle, bg="#2E6B50", fg="white", bd=0, padx=16, pady=9, font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Button(toolbar, text="Edit Selected", command=self.edit_vehicle, bg="#D98E04", fg="white", bd=0, padx=16, pady=9, font=("Segoe UI", 10, "bold")).pack(side="left", padx=8)
        tk.Button(toolbar, text="Delete Selected", command=self.delete_vehicle, bg="#A33A3A", fg="white", bd=0, padx=16, pady=9, font=("Segoe UI", 10, "bold")).pack(side="left")
        search_var = tk.StringVar()
        tk.Label(toolbar, text="Search", bg="#F7F3E8", fg="#23352D", font=("Segoe UI", 9, "bold")).pack(side="right", padx=(8, 0))
        search_entry = tk.Entry(toolbar, textvariable=search_var, font=("Segoe UI", 10), relief="solid", bd=1, width=24)
        search_entry.pack(side="right", ipady=5, padx=(8, 0))
        enable_entry_shortcuts(search_entry)
        tk.Button(toolbar, text="Refresh", command=self.show_vehicles, bg="#E2DED2", fg="#23352D", bd=0, padx=16, pady=9, font=("Segoe UI", 10)).pack(side="right")

        panel = tk.Frame(outer, bg="white")
        panel.pack(fill="both", expand=True)

        columns = ("id", "plate", "owner", "brand", "model", "year", "type", "contact")
        self.vehicle_tree = ttk.Treeview(panel, columns=columns, show="headings")

        headings = {
            "id": "ID",
            "plate": "Plate Number",
            "owner": "Owner",
            "brand": "Brand",
            "model": "Model",
            "year": "Year",
            "type": "Type",
            "contact": "Contact",
        }
        widths = {
            "id": 50,
            "plate": 120,
            "owner": 170,
            "brand": 100,
            "model": 110,
            "year": 70,
            "type": 110,
            "contact": 130,
        }

        for col in columns:
            self.vehicle_tree.heading(col, text=headings[col])
            self.vehicle_tree.column(col, width=widths[col], anchor="w")

        self.vehicle_tree.pack(fill="both", expand=True, padx=15, pady=15)
        self.vehicle_tree.bind("<Double-1>", lambda e: self.edit_vehicle())

        rows = []

        def render_vehicles(*args):
            query = search_var.get().strip().casefold()
            matching_rows = [
                row for row in rows
                if not query or any(query in str(value or "").casefold() for value in row.values())
            ]
            self.vehicle_tree.delete(*self.vehicle_tree.get_children())
            for display_id, row in enumerate(matching_rows, start=1):
                self.vehicle_tree.insert(
                    "",
                    "end",
                    iid=str(row["id"]),
                    values=(display_id, row["plate_number"], row["owner_name"], row["brand"], row["model"], row["year"], row["vehicle_type"], row["contact_number"] or ""),
                )

        search_var.trace_add("write", render_vehicles)

        try:
            rows = fetch_all(
                """
                SELECT id, plate_number, owner_name, brand, model,
                       year, vehicle_type, contact_number
                FROM vehicles
                ORDER BY id ASC
            """
            )
            render_vehicles()
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))

    def selected_vehicle(self):
        selection = self.vehicle_tree.selection()
        if not selection:
            messagebox.showwarning("Select Vehicle", "Please select a vehicle first.")
            return None
        values = self.vehicle_tree.item(selection[0], "values")
        return (selection[0],) + values[1:]

    def vehicle_form(self, title, existing=None):
        self.current_page = title
        self.clear_content(title)

        outer = tk.Frame(self.content, bg="#F7F3E8")
        outer.pack(fill="both", expand=True, padx=28, pady=18)

        top = tk.Frame(outer, bg="#F7F3E8")
        top.pack(fill="x", pady=(0, 10))

        tk.Button(top, text="← Back to Vehicles", command=self.show_vehicles, bg="#E2DED2", fg="#23352D", bd=0, padx=14, pady=8, font=("Segoe UI", 10, "bold")).pack(side="left")

        panel = tk.Frame(outer, bg="white")
        panel.pack(fill="both", expand=True)

        tk.Label(panel, text="Vehicle Information", font=("Segoe UI", 13, "bold"), bg="white", fg="#23352D").pack(anchor="w", padx=28, pady=(20, 2))
        tk.Label(panel, text="Enter the vehicle details below, then click Save Vehicle.", font=("Segoe UI", 9), bg="white", fg="#5F6B64").pack(anchor="w", padx=28, pady=(0, 12))

        form = tk.Frame(panel, bg="white")
        form.pack(fill="x", padx=28, pady=4)
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        fields = [
            ("Owner Name", "owner", "entry"),
            ("Vehicle Category", "category", "category"),
            ("Brand", "brand", "brand"),
            ("Vehicle Type", "type", "type"),
            ("Model", "model", "entry"),
            ("Year Model", "year", "year"),
            ("Plate Number", "plate", "entry"),
            ("Contact Number", "contact", "contact"),
        ]
        entries = {}

        def update_category_options(event=None):
            category = entries["category"].get()
            options = VEHICLE_OPTIONS.get(category)
            for key, option_key in (("brand", "brands"), ("type", "types")):
                combo = entries[key]
                combo.configure(values=options[option_key] if options else ())
                combo.configure(state="readonly" if options else "disabled")
                if combo.get() not in (options[option_key] if options else ()):
                    combo.set("")
            entries["year"].configure(state="readonly" if options else "disabled")

        for index, (label, key, field_type) in enumerate(fields):
            row = index // 2
            col = index % 2
            cell = tk.Frame(form, bg="white")
            cell.grid(row=row, column=col, sticky="ew", padx=(0, 12) if col == 0 else (12, 0), pady=(0, 9))

            tk.Label(cell, text=label, bg="white", fg="#D8D2C3", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 3))

            if field_type == "category":
                entry = ttk.Combobox(cell, values=tuple(VEHICLE_OPTIONS), state="readonly", font=("Segoe UI", 10))
                entry.bind("<<ComboboxSelected>>", update_category_options)
            elif field_type in ("brand", "type"):
                entry = ttk.Combobox(cell, state="disabled", font=("Segoe UI", 10))
            elif field_type == "year":
                entry = ttk.Combobox(cell, values=tuple(str(year) for year in range(date.today().year, 1959, -1)), state="disabled", font=("Segoe UI", 10))
            else:
                entry = tk.Entry(cell, font=("Segoe UI", 10), relief="solid", bd=1)
                if field_type == "contact":
                    valid_contact = entry.register(lambda proposed: len(proposed) <= 11 and all("0" <= char <= "9" for char in proposed))
                    entry.configure(validate="key", validatecommand=(valid_contact, "%P"))
                enable_entry_shortcuts(entry)
            entry.pack(fill="x", ipady=6)
            entries[key] = entry

        if existing:
            vals = {
                "plate": existing["plate_number"],
                "owner": existing["owner_name"],
                "brand": existing["brand"],
                "model": existing["model"],
                "year": existing["year"],
                "type": existing["vehicle_type"],
                "contact": existing["contact_number"] or "",
            }
            category = next(
                (name for name, options in VEHICLE_OPTIONS.items() if any(value.casefold() == str(vals["type"]).casefold() for value in options["types"])),
                "",
            )
            if category:
                entries["category"].set(category)
                update_category_options()
            for key, value in vals.items():
                if isinstance(entries[key], ttk.Combobox):
                    entries[key].set(str(value))
                else:
                    entries[key].insert(0, str(value))

        button_row = tk.Frame(panel, bg="#F7F3E8", height=72)
        button_row.pack(side="bottom", fill="x")
        button_row.pack_propagate(False)

        def save():
            values = {k: e.get().strip() for k, e in entries.items()}

            if not all(values.values()):
                messagebox.showwarning("Required Fields", "Please complete all vehicle information before saving.")
                return
            if len(values["contact"]) > 11 or not values["contact"].isascii() or not values["contact"].isdigit():
                messagebox.showwarning("Invalid Contact Number", "Contact number must contain no more than 11 digits.")
                return

            try:
                if existing:
                    execute_query(
                        """
                        UPDATE vehicles
                        SET plate_number=%s, owner_name=%s, brand=%s,
                            model=%s, year=%s, vehicle_type=%s, contact_number=%s
                        WHERE id=%s
                    """,
                        (values["plate"], values["owner"], values["brand"], values["model"], values["year"], values["type"], values["contact"], existing["id"]),
                    )
                    messagebox.showinfo("Saved", "Vehicle information updated successfully.")
                else:
                    execute_query(
                        """
                        INSERT INTO vehicles
                        (plate_number, owner_name, brand, model, year,
                         vehicle_type, contact_number)
                        VALUES (%s,%s,%s,%s,%s,%s,%s)
                    """,
                        (values["plate"], values["owner"], values["brand"], values["model"], values["year"], values["type"], values["contact"]),
                    )
                    messagebox.showinfo("Saved", "Vehicle added successfully.")

                self.show_vehicles()

            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", str(e))

        tk.Button(button_row, text="SAVE VEHICLE", command=save, bg="#2E6B50", fg="white", bd=0, font=("Segoe UI", 10, "bold"), padx=25, pady=10).pack(side="right", padx=(8, 28), pady=14)
        tk.Button(button_row, text="CANCEL", command=self.show_vehicles, bg="#E2DED2", fg="#23352D", bd=0, font=("Segoe UI", 10, "bold"), padx=25, pady=10).pack(side="right", pady=14)

        entries["owner"].focus_set()

    def add_vehicle(self):
        self.vehicle_form("Add Vehicle")

    def edit_vehicle(self):
        values = self.selected_vehicle()
        if not values:
            return
        try:
            existing = fetch_one("SELECT * FROM vehicles WHERE id=%s", (values[0],))
            self.vehicle_form("Edit Vehicle", existing)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))

    def delete_vehicle(self):
        values = self.selected_vehicle()
        if not values:
            return
        if not messagebox.askyesno("Delete Vehicle", f"Delete vehicle {values[1]}?\nIts maintenance records will also be deleted."):
            return
        try:
            execute_query("DELETE FROM vehicles WHERE id=%s", (values[0],))
            self.show_vehicles()
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
