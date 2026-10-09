import tkinter as tk
from tkinter import ttk


def enable_entry_shortcuts(entry):
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


def nav_button(parent, text, command):
    btn = tk.Button(
        parent,
        text=f"  {text}",
        anchor="w",
        font=("Segoe UI", 10, "bold"),
        bd=0,
        relief="flat",
        bg="#1F4D3A",
        fg="#E5E5E5",
        activebackground="#383838",
        activeforeground="white",
        padx=18,
        pady=11,
        command=command,
    )
    btn.pack(fill="x", padx=10, pady=2)
    return btn


def clear_content(content, header_title, root, client_refresh_job=None):
    if client_refresh_job is not None:
        try:
            root.after_cancel(client_refresh_job)
        except tk.TclError:
            pass
    for widget in content.winfo_children():
        widget.destroy()
    header_title.config(text="Dashboard")


def card(parent, title, value, accent):
    frame = tk.Frame(parent, bg="white", height=112, highlightthickness=1, highlightbackground="#E6E6E6")
    frame.pack_propagate(False)
    tk.Frame(frame, bg=accent, width=5).pack(side="left", fill="y")
    inner = tk.Frame(frame, bg="white")
    inner.pack(side="left", fill="both", expand=True, padx=16, pady=14)
    tk.Label(inner, text=title, font=("Segoe UI", 8, "bold"), bg="white", fg="#78847D").pack(anchor="w")
    tk.Label(inner, text=value, font=("Segoe UI", 21, "bold"), bg="white", fg="#1F4D3A").pack(anchor="w", pady=(7, 0))
    return frame


def configure_style():
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
        font=("Segoe UI", 10),
    )
    style.configure(
        "Treeview.Heading",
        background="#E2DED2",
        foreground="#23352D",
        font=("Segoe UI", 10, "bold"),
    )
    style.map("Treeview", background=[("selected", "#ECE8DD")])
    style.configure("TCombobox", padding=7, font=("Segoe UI", 10))
