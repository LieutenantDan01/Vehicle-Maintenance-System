import tkinter as tk
from tkinter import ttk, messagebox

import mysql.connector

from database.db import get_connection
from app.ui_helpers import (
    configure_style,
    nav_button,
)

from app.screens.client import ClientScreensMixin
from app.screens.dashboard import DashboardScreensMixin
from app.screens.vehicles import VehicleScreensMixin
from app.screens.maintenance import MaintenanceScreensMixin


class VehicleMaintenanceApp(ClientScreensMixin, DashboardScreensMixin, VehicleScreensMixin, MaintenanceScreensMixin):
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

        configure_style()
        self.build_layout()
        self.show_dashboard()

    def build_layout(self):
        """Modern dashboard layout for administrator accounts."""
        self.sidebar = tk.Frame(self.root, bg="#1F4D3A", width=235)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        brand = tk.Frame(self.sidebar, bg="#1F4D3A")
        brand.pack(fill="x", padx=18, pady=(24, 28))
        logo = tk.Label(
            brand,
            text="VM",
            font=("Segoe UI", 20, "bold"),
            bg="#2E6B50",
            fg="white",
            width=3,
            pady=5,
        )
        logo.pack(side="left")
        text = tk.Frame(brand, bg="#1F4D3A")
        text.pack(side="left", padx=10)
        tk.Label(text, text="Vehicle Maintenance", font=("Segoe UI", 10, "bold"), bg="#1F4D3A", fg="white").pack(anchor="w")
        tk.Label(text, text="Service Tracking", font=("Segoe UI", 9), bg="#1F4D3A", fg="#DDD8CB").pack(anchor="w")

        tk.Label(self.sidebar, text="MAIN MENU", font=("Segoe UI", 8, "bold"), bg="#1F4D3A", fg="#78847D").pack(anchor="w", padx=22, pady=(0, 8))
        nav_button(self.sidebar, "Dashboard", self.show_dashboard)
        nav_button(self.sidebar, "Vehicles", self.show_vehicles)
        nav_button(self.sidebar, "Maintenance", self.show_maintenance)
        nav_button(self.sidebar, "Service History", self.show_history)

        tk.Frame(self.sidebar, bg="#D8D2C3", height=1).pack(fill="x", padx=20, pady=18)
        tk.Label(self.sidebar, text="ACCOUNT", font=("Segoe UI", 8, "bold"), bg="#1F4D3A", fg="#78847D").pack(anchor="w", padx=22, pady=(0, 8))
        tk.Button(
            self.sidebar,
            text="  Logout",
            anchor="w",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            relief="flat",
            bg="#1F4D3A",
            fg="#B8D4C5",
            activebackground="#17402F",
            activeforeground="white",
            padx=20,
            pady=11,
            command=self.logout,
        ).pack(fill="x", padx=10)

        self.main = tk.Frame(self.root, bg="#F7F3E8")
        self.main.pack(side="left", fill="both", expand=True)

        header = tk.Frame(self.main, bg="white", height=72, highlightthickness=1, highlightbackground="#E6E6E6")
        header.pack(fill="x")
        header.pack_propagate(False)
        self.header_title = tk.Label(header, text="Dashboard", font=("Segoe UI", 18, "bold"), bg="white", fg="#1F4D3A")
        self.header_title.pack(side="left", padx=28)
        userbox = tk.Frame(header, bg="white")
        userbox.pack(side="right", padx=24)
        tk.Label(userbox, text="Administrator", font=("Segoe UI", 9), bg="white", fg="#78847D").pack(anchor="e")
        tk.Label(userbox, text=self.user.get("full_name", "User"), font=("Segoe UI", 10, "bold"), bg="white", fg="#1F4D3A").pack(anchor="e")

        self.content = tk.Frame(self.main, bg="#F7F3E8")
        self.content.pack(fill="both", expand=True)

    def build_client_layout(self):
        """Modern simplified navigation for client accounts."""
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        self.sidebar.configure(bg="#1F4D3A")
        brand = tk.Frame(self.sidebar, bg="#1F4D3A")
        brand.pack(fill="x", padx=18, pady=(24, 28))
        tk.Label(brand, text="VM", font=("Segoe UI", 20, "bold"), bg="#2E6B50", fg="white", width=3, pady=5).pack(side="left")
        t = tk.Frame(brand, bg="#1F4D3A")
        t.pack(side="left", padx=10)
        tk.Label(t, text="Client Portal", font=("Segoe UI", 11, "bold"), bg="#1F4D3A", fg="white").pack(anchor="w")
        tk.Label(t, text="Service Tracking", font=("Segoe UI", 9), bg="#1F4D3A", fg="#DDD8CB").pack(anchor="w")
        tk.Label(self.sidebar, text="MY ACCOUNT", font=("Segoe UI", 8, "bold"), bg="#1F4D3A", fg="#78847D").pack(anchor="w", padx=22, pady=(0, 8))
        nav_button(self.sidebar, "My Dashboard", self.show_client_dashboard)
        nav_button(self.sidebar, "My Service History", self.show_client_history)
        tk.Button(
            self.sidebar,
            text="  Logout",
            anchor="w",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            relief="flat",
            bg="#1F4D3A",
            fg="#B8D4C5",
            activebackground="#17402F",
            activeforeground="white",
            padx=20,
            pady=11,
            command=self.logout,
        ).pack(side="bottom", fill="x", padx=10, pady=18)

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
        frame = tk.Frame(parent, bg="white", height=112, highlightthickness=1, highlightbackground="#E6E6E6")
        frame.pack_propagate(False)
        tk.Frame(frame, bg=accent, width=5).pack(side="left", fill="y")
        inner = tk.Frame(frame, bg="white")
        inner.pack(side="left", fill="both", expand=True, padx=16, pady=14)
        tk.Label(inner, text=title, font=("Segoe UI", 8, "bold"), bg="white", fg="#78847D").pack(anchor="w")
        tk.Label(inner, text=value, font=("Segoe UI", 21, "bold"), bg="white", fg="#1F4D3A").pack(anchor="w", pady=(7, 0))
        return frame

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

    tk.Label(left, text="VM", font=("Segoe UI", 42, "bold"), fg="white", bg="#2E6B50", width=4, pady=5).pack(anchor="w", padx=50, pady=(105, 25))
    tk.Label(left, text="Vehicle Maintenance\n& Service Tracking\nSystem", font=("Segoe UI", 21, "bold"), fg="white", bg="#23352D", justify="left", wraplength=340).pack(anchor="w", padx=35)
    tk.Label(left, text="Manage vehicles and services, or let clients\ntrack their own maintenance history.", font=("Segoe UI", 11), fg="#E2DED2", bg="#23352D", justify="left").pack(anchor="w", padx=50, pady=(20, 0))

    right = tk.Frame(login, bg="#F7F3E8")
    right.pack(side="right", fill="both", expand=True)

    box = tk.Frame(right, bg="white")
    box.pack(fill="both", expand=True, padx=45, pady=65)

    tk.Label(box, text="Welcome Back", font=("Segoe UI", 24, "bold"), bg="white", fg="#23352D").pack(anchor="w", padx=35, pady=(42, 5))
    tk.Label(box, text="Sign in to continue", font=("Segoe UI", 10), bg="white", fg="#5F6B64").pack(anchor="w", padx=35, pady=(0, 28))
    tk.Label(box, text="Username", font=("Segoe UI", 10, "bold"), bg="white", fg="#D8D2C3").pack(anchor="w", padx=35)

    username = tk.Entry(box, font=("Segoe UI", 11), bd=1, relief="solid")
    username.pack(fill="x", padx=35, pady=(7, 18), ipady=9)

    tk.Label(box, text="Password", font=("Segoe UI", 10, "bold"), bg="white", fg="#D8D2C3").pack(anchor="w", padx=35)

    password_frame = tk.Frame(box, bg="white")
    password_frame.pack(fill="x", padx=35, pady=(7, 20))

    password = tk.Entry(password_frame, font=("Segoe UI", 11), bd=1, relief="solid", show="*")
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

    show = tk.Button(password_frame, text="Show", command=toggle, bg="white", fg="#2E6B50", bd=0, font=("Segoe UI", 9, "bold"))
    show.pack(side="right", padx=5)

    def do_login():
        u = username.get().strip()
        p = password.get()
        if not u or not p:
            messagebox.showwarning("Login Required", "Please enter your username and password.", parent=login)
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
                messagebox.showerror("Login Failed", "Invalid username or password.", parent=login)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e), parent=login)

    tk.Button(box, text="SIGN IN", command=do_login, font=("Segoe UI", 11, "bold"), bg="#2E6B50", fg="white", activebackground="#C65D0E", activeforeground="white", bd=0, pady=11).pack(fill="x", padx=35)

    login.bind("<Return>", lambda e: do_login())
    username.focus()
    login.mainloop()
