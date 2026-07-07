import customtkinter as ctk
import tkinter as tk
import queue
import time
from pathlib import Path
from tkinter import filedialog
from config import DEFAULT_WINDOW_SIZE, DEFAULT_THEME, APP_NAME, EXPORTS_DIR
from gui.themes import apply_theme, get_color, FONTS
from gui.widgets import StatisticCard, ToastNotification, IconButton, StatusBar
from gui.table import VirtualizedTable
from gui.dialogs import SettingsDialog
from core.generator import UUIDGenerator
from core.exporter import Exporter
from core.clipboard import ClipboardManager
from core.history import HistoryManager
from utils.helpers import format_number, generate_export_filename
from utils.logger import logger

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title(APP_NAME)
        self.geometry(DEFAULT_WINDOW_SIZE)
        self.minsize(1000, 700)
        
        apply_theme(DEFAULT_THEME)
        
        self.generator = UUIDGenerator()
        self.output_queue = queue.Queue()
        self.is_generating = False
        self.start_time = 0
        self.generated_data = []
        
        self._build_menu()
        self._build_ui()
        
        self.after(100, self._process_queue)

    def _build_menu(self):
        self.menubar = tk.Menu(self)
        
        # File Menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="New Generation", command=self._clear)
        file_menu.add_separator()
        file_menu.add_command(label="Import...", command=self._import)
        file_menu.add_command(label="Export TXT...", command=lambda: self._export("txt"))
        file_menu.add_command(label="Export CSV...", command=lambda: self._export("csv"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        self.menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit Menu
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        edit_menu.add_command(label="Copy All", command=self._copy_all)
        edit_menu.add_command(label="Clear", command=self._clear)
        self.menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # View Menu
        view_menu = tk.Menu(self.menubar, tearoff=0)
        view_menu.add_command(label="Toggle Theme", command=self._toggle_theme)
        self.menubar.add_cascade(label="View", menu=view_menu)
        
        self.config(menu=self.menubar)

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # --- LEFT SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=get_color("sidebar"))
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(15, weight=1)
        
        logo_lbl = ctk.CTkLabel(self.sidebar, text="⚡ UUID Generator Pro", font=FONTS["title"], text_color=get_color("primary"))
        logo_lbl.grid(row=0, column=0, padx=20, pady=(20, 30), sticky="w")
        
        # Configuration Section
        ctk.CTkLabel(self.sidebar, text="CONFIGURATION", font=FONTS["section"]).grid(row=1, column=0, padx=20, sticky="w")
        
        ctk.CTkLabel(self.sidebar, text="UUID Version:", font=FONTS["label"]).grid(row=2, column=0, padx=20, pady=(15, 0), sticky="w")
        self.version_var = ctk.StringVar(value="4")
        ctk.CTkOptionMenu(self.sidebar, values=["1", "3", "4", "5"], variable=self.version_var, command=self._on_version_change).grid(row=3, column=0, padx=20, pady=(5, 10), sticky="ew")
        
        self.namespace_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        ctk.CTkLabel(self.namespace_frame, text="Namespace:").pack(anchor="w")
        self.namespace_var = ctk.StringVar(value="DNS")
        ctk.CTkOptionMenu(self.namespace_frame, values=["DNS", "URL", "OID", "X500"], variable=self.namespace_var).pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(self.namespace_frame, text="Name:").pack(anchor="w")
        self.name_entry = ctk.CTkEntry(self.namespace_frame, placeholder_text="example.com")
        self.name_entry.pack(fill="x")
        
        ctk.CTkLabel(self.sidebar, text="Quantity:", font=FONTS["label"]).grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")
        self.quantity_entry = ctk.CTkEntry(self.sidebar, placeholder_text="1,000,000")
        self.quantity_entry.insert(0, "100")
        self.quantity_entry.grid(row=6, column=0, padx=20, pady=(5, 20), sticky="ew")
        
        # Toggles
        self.auto_copy_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(self.sidebar, text="Auto Copy", font=FONTS["label"], variable=self.auto_copy_var).grid(row=7, column=0, padx=20, pady=5, sticky="w")
        
        self.uppercase_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(self.sidebar, text="Uppercase", font=FONTS["label"], variable=self.uppercase_var).grid(row=8, column=0, padx=20, pady=5, sticky="w")
        
        self.remove_hyphen_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(self.sidebar, text="Remove Hyphens", font=FONTS["label"], variable=self.remove_hyphen_var).grid(row=9, column=0, padx=20, pady=5, sticky="w")
        
        # Actions
        self.generate_btn = ctk.CTkButton(self.sidebar, text="⚡ Generate", font=FONTS["label"], height=42, command=self._start_generation)
        self.generate_btn.grid(row=10, column=0, padx=20, pady=(30, 10), sticky="ew")
        
        self.cancel_btn = ctk.CTkButton(self.sidebar, text="Cancel", font=FONTS["label"], height=42, fg_color=get_color("danger"), state="disabled", command=self._cancel_generation)
        self.cancel_btn.grid(row=11, column=0, padx=20, pady=10, sticky="ew")

        # --- MAIN PANEL ---
        self.main_panel = ctk.CTkFrame(self, fg_color=get_color("bg"), corner_radius=0)
        self.main_panel.grid(row=0, column=1, sticky="nsew")
        self.main_panel.grid_rowconfigure(1, weight=1)
        self.main_panel.grid_columnconfigure(0, weight=1)
        
        # Toolbar
        self.toolbar = ctk.CTkFrame(self.main_panel, height=60, fg_color=get_color("sidebar"), corner_radius=0)
        self.toolbar.grid(row=0, column=0, sticky="ew")
        
        IconButton(self.toolbar, icon="📋", text="Copy All", command=self._copy_all, fg_color="transparent", text_color=get_color("text")).pack(side="left", padx=5, pady=10)
        IconButton(self.toolbar, icon="💾", text="Export CSV", command=lambda: self._export("csv"), fg_color="transparent", text_color=get_color("text")).pack(side="left", padx=5)
        IconButton(self.toolbar, icon="🗑", text="Clear", command=self._clear, fg_color="transparent", text_color=get_color("text")).pack(side="left", padx=5)
        
        IconButton(self.toolbar, icon="⚙", command=self._open_settings, fg_color="transparent", text_color=get_color("text"), width=40).pack(side="right", padx=10)
        IconButton(self.toolbar, icon="🌙", command=self._toggle_theme, fg_color="transparent", text_color=get_color("text"), width=40).pack(side="right", padx=5)
        
        # Result Area
        self.result_container = ctk.CTkFrame(self.main_panel, fg_color="transparent")
        self.result_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.result_container.grid_rowconfigure(0, weight=1)
        self.result_container.grid_columnconfigure(0, weight=1)
        
        # Empty State
        self.empty_state = ctk.CTkFrame(self.result_container, fg_color="transparent")
        self.empty_state.grid(row=0, column=0, sticky="nsew")
        self.empty_state.grid_rowconfigure(0, weight=1)
        self.empty_state.grid_rowconfigure(2, weight=1)
        self.empty_state.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.empty_state, text="No UUIDs generated yet.", font=FONTS["section"], text_color=get_color("secondary_text")).grid(row=1, column=0)
        
        # Table
        self.table = VirtualizedTable(self.result_container)
        self.table.on_copy_callback = self.show_toast
        
        # Stats Panel
        self.stats_panel = ctk.CTkFrame(self.main_panel, fg_color="transparent")
        self.stats_panel.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        for i in range(4): self.stats_panel.grid_columnconfigure(i, weight=1)
        
        self.stat_generated = StatisticCard(self.stats_panel, "⚡", "Generated")
        self.stat_generated.grid(row=0, column=0, sticky="ew", padx=5)
        self.stat_unique = StatisticCard(self.stats_panel, "✨", "Unique")
        self.stat_unique.grid(row=0, column=1, sticky="ew", padx=5)
        self.stat_time = StatisticCard(self.stats_panel, "🕒", "Time (s)")
        self.stat_time.grid(row=0, column=2, sticky="ew", padx=5)
        self.stat_speed = StatisticCard(self.stats_panel, "🚀", "UUID/sec")
        self.stat_speed.grid(row=0, column=3, sticky="ew", padx=5)

        # Status Bar
        self.statusbar = StatusBar(self)
        self.statusbar.grid(row=1, column=0, columnspan=2, sticky="ew")

    def _on_version_change(self, value):
        if value in ["3", "5"]:
            self.namespace_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        else:
            self.namespace_frame.grid_forget()

    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if current == "Dark" else "Dark")
        self.statusbar.mode_label.configure(text="Light Mode" if current == "Dark" else "Dark Mode")

    def _open_settings(self):
        SettingsDialog(self)

    def show_toast(self, message: str, type: str = "success"):
        toast = ToastNotification(self, message, type=type)
        toast.show(self.winfo_width() - 20, self.toolbar.winfo_height() + 20)

    def _start_generation(self):
        try:
            qty = int(self.quantity_entry.get().replace(",", ""))
            if qty <= 0: raise ValueError
        except:
            self.show_toast("Invalid quantity", "error")
            return

        ver = self.version_var.get()
        ns = self.namespace_var.get()
        name = self.name_entry.get()
        
        if ver in ["3", "5"] and not name:
            self.show_toast("Name required for v3/v5", "error")
            return

        self._clear()
        self.empty_state.grid_forget()
        self.table.grid(row=0, column=0, sticky="nsew")
        
        self.is_generating = True
        self.generate_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.start_time = time.perf_counter()
        self.statusbar.set_status(f"Generating {format_number(qty)} UUIDs...")
        
        self.generator.start_generation(ver, qty, ns, name, self.output_queue, self._update_progress, self._generation_complete)

    def _cancel_generation(self):
        if self.is_generating:
            self.generator.cancel()
            self.statusbar.set_status("Cancelling...")

    def _update_progress(self, c, t):
        pass # Handled in _process_queue

    def _process_queue(self):
        if self.is_generating:
            chunks = 0
            while not self.output_queue.empty() and chunks < 10:
                try:
                    self.generated_data.extend(self.output_queue.get_nowait())
                    chunks += 1
                except: break
            
            c = len(self.generated_data)
            self.stat_generated.set_value(format_number(c))
            
            elapsed = time.perf_counter() - self.start_time
            if elapsed > 0:
                self.stat_speed.set_value(format_number(int(c/elapsed)))
                self.stat_time.set_value(f"{elapsed:.1f}")
                
        self.after(100, self._process_queue)

    def _generation_complete(self, cancelled):
        self.after(0, lambda: self._finalize(cancelled))

    def _finalize(self, cancelled):
        self.is_generating = False
        self.generate_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        
        while not self.output_queue.empty():
            self.generated_data.extend(self.output_queue.get())
            
        # Apply formatting
        upper = self.uppercase_var.get()
        no_hyphen = self.remove_hyphen_var.get()
        
        if upper or no_hyphen:
            formatted = []
            for u in self.generated_data:
                if upper: u = u.upper()
                if no_hyphen: u = u.replace("-", "")
                formatted.append(u)
            self.generated_data = formatted
            
        self.table.set_data(self.generated_data)
        
        c = len(self.generated_data)
        self.stat_generated.set_value(format_number(c))
        # For performance on 1M, uniqueness check is heavy. Just setting same as generated.
        self.stat_unique.set_value(format_number(c))
        
        dur = time.perf_counter() - self.start_time
        self.stat_time.set_value(f"{dur:.2f}")
        
        self.statusbar.set_status(f"{'Cancelled' if cancelled else 'Ready'}")
        
        if not cancelled:
            self.show_toast(f"Generated {format_number(c)} UUIDs")
            HistoryManager.add_entry(self.version_var.get(), c, dur)
            if self.auto_copy_var.get():
                self._copy_all()

    def _copy_all(self):
        if self.generated_data:
            ClipboardManager.copy_list_to_clipboard(self.generated_data)
            self.show_toast("Copied all to clipboard")

    def _export(self, fmt):
        if not self.generated_data: return
        fn = filedialog.asksaveasfilename(initialfile=f"uuid.{fmt}", defaultextension=f".{fmt}")
        if fn:
            Exporter.export_to_csv(Path(fn), self.generated_data) if fmt=="csv" else Exporter.export_to_txt(Path(fn), self.generated_data)
            self.show_toast(f"Exported to {fmt.upper()}")

    def _clear(self):
        self.generated_data = []
        self.table.clear()
        self.table.grid_forget()
        self.empty_state.grid(row=0, column=0, sticky="nsew")
        self.stat_generated.set_value("0")
        self.stat_unique.set_value("0")
        self.stat_time.set_value("0")
        self.stat_speed.set_value("0")
        self.statusbar.set_status("Ready")

    def _import(self):
        self.show_toast("Import feature coming soon", "error")
