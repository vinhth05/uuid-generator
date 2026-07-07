import customtkinter as ctk
import queue
import time
from pathlib import Path
from tkinter import messagebox, filedialog
from config import DEFAULT_WINDOW_SIZE, DEFAULT_THEME, APP_NAME, EXPORTS_DIR
from gui.themes import apply_theme
from gui.widgets import VirtualizedTextbox, StatusBar
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
        self.minsize(800, 600)
        
        apply_theme(DEFAULT_THEME)
        
        self.generator = UUIDGenerator()
        self.output_queue = queue.Queue()
        self.is_generating = False
        self.start_time = 0
        self.generated_data = []
        
        self._build_ui()
        
        # Periodic check for the queue
        self.after(100, self._process_queue)

    def _build_ui(self):
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)
        
        logo_label = ctk.CTkLabel(self.sidebar, text="UUID Generator Pro", font=ctk.CTkFont(size=20, weight="bold"))
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Version Selection
        ctk.CTkLabel(self.sidebar, text="UUID Version:").grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.version_var = ctk.StringVar(value="4")
        self.version_menu = ctk.CTkOptionMenu(
            self.sidebar, values=["1", "3", "4", "5"], variable=self.version_var, command=self._on_version_change
        )
        self.version_menu.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Namespace / Name (Hidden by default, shown for v3/v5)
        self.namespace_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        
        ctk.CTkLabel(self.namespace_frame, text="Namespace:").pack(anchor="w")
        self.namespace_var = ctk.StringVar(value="DNS")
        self.namespace_menu = ctk.CTkOptionMenu(self.namespace_frame, values=["DNS", "URL", "OID", "X500"], variable=self.namespace_var)
        self.namespace_menu.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(self.namespace_frame, text="Name:").pack(anchor="w")
        self.name_entry = ctk.CTkEntry(self.namespace_frame, placeholder_text="example.com")
        self.name_entry.pack(fill="x")
        
        # Quantity
        ctk.CTkLabel(self.sidebar, text="Quantity:").grid(row=4, column=0, padx=20, pady=(20, 0), sticky="w")
        self.quantity_entry = ctk.CTkEntry(self.sidebar, placeholder_text="10")
        self.quantity_entry.insert(0, "10")
        self.quantity_entry.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        # Actions
        self.generate_btn = ctk.CTkButton(self.sidebar, text="Generate", command=self._start_generation)
        self.generate_btn.grid(row=6, column=0, padx=20, pady=10, sticky="ew")
        
        self.cancel_btn = ctk.CTkButton(self.sidebar, text="Cancel", command=self._cancel_generation, state="disabled", fg_color="red")
        self.cancel_btn.grid(row=7, column=0, padx=20, pady=10, sticky="ew")
        
        # Theme toggle
        self.theme_btn = ctk.CTkButton(self.sidebar, text="Toggle Theme", command=self._toggle_theme, fg_color="transparent", border_width=1)
        self.theme_btn.grid(row=9, column=0, padx=20, pady=20, sticky="ew")
        
        # Main content area
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Toolbar
        self.toolbar = ctk.CTkFrame(self.main_frame, height=50, fg_color="transparent")
        self.toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkButton(self.toolbar, text="Copy All", width=100, command=self._copy_all).pack(side="left", padx=5)
        ctk.CTkButton(self.toolbar, text="Export CSV", width=100, command=lambda: self._export("csv")).pack(side="left", padx=5)
        ctk.CTkButton(self.toolbar, text="Export TXT", width=100, command=lambda: self._export("txt")).pack(side="left", padx=5)
        ctk.CTkButton(self.toolbar, text="Clear", width=100, command=self._clear, fg_color="gray").pack(side="right", padx=5)
        
        # Textbox
        self.textbox = VirtualizedTextbox(self.main_frame)
        self.textbox.grid(row=1, column=0, sticky="nsew")
        
        # Progress Bar
        self.progress = ctk.CTkProgressBar(self.main_frame)
        self.progress.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.progress.set(0)
        
        # Status Bar
        self.statusbar = StatusBar(self)
        self.statusbar.grid(row=1, column=0, columnspan=2, sticky="ew")

    def _on_version_change(self, value):
        if value in ["3", "5"]:
            self.namespace_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        else:
            self.namespace_frame.grid_forget()

    def _toggle_theme(self):
        current_mode = ctk.get_appearance_mode()
        new_mode = "Light" if current_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)

    def _start_generation(self):
        try:
            quantity_str = self.quantity_entry.get().replace(",", "")
            quantity = int(quantity_str)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive integer for quantity.")
            return

        version = self.version_var.get()
        namespace = self.namespace_var.get()
        name = self.name_entry.get()
        
        if version in ["3", "5"] and not name:
            messagebox.showerror("Error", "Name cannot be empty for UUID v3/v5.")
            return

        self._clear()
        self.is_generating = True
        self.generate_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.start_time = time.perf_counter()
        self.progress.set(0)
        self.statusbar.set_status(f"Generating {format_number(quantity)} UUIDs...")
        
        # Start worker thread
        self.generator.start_generation(
            version, quantity, namespace, name,
            self.output_queue, self._update_progress_callback, self._generation_complete_callback
        )

    def _cancel_generation(self):
        if self.is_generating:
            self.generator.cancel()
            self.statusbar.set_status("Cancelling...")

    def _update_progress_callback(self, current, total):
        # We don't update UI directly from thread, we could use events, but
        # for progress, queue or simple variables are fine. CustomTkinter is mostly thread-safe for basic sets, 
        # but to be totally safe, we use after(). However, scheduling thousands of after() calls freezes the UI.
        # So we handle progress in _process_queue.
        pass

    def _process_queue(self):
        if self.is_generating:
            chunks_received = 0
            while not self.output_queue.empty() and chunks_received < 10: # process up to 10 chunks per tick
                try:
                    chunk = self.output_queue.get_nowait()
                    self.generated_data.extend(chunk)
                    chunks_received += 1
                except queue.Empty:
                    break
            
            # Update progress UI safely
            if self.is_generating:
                target = int(self.quantity_entry.get().replace(",", ""))
                current = len(self.generated_data)
                
                if target > 0:
                    self.progress.set(current / target)
                
                elapsed = time.perf_counter() - self.start_time
                speed = current / elapsed if elapsed > 0 else 0
                self.statusbar.set_stats(f"{format_number(current)} / {format_number(target)} | {format_number(int(speed))} UUIDs/s")
                
        self.after(100, self._process_queue)

    def _generation_complete_callback(self, cancelled):
        # Safely execute UI updates in main thread
        self.after(0, lambda: self._finalize_generation(cancelled))

    def _finalize_generation(self, cancelled):
        self.is_generating = False
        self.generate_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        
        # Flush remaining queue
        while not self.output_queue.empty():
            try:
                self.generated_data.extend(self.output_queue.get_nowait())
            except queue.Empty:
                break
                
        self.textbox.set_data(self.generated_data)
        
        duration = time.perf_counter() - self.start_time
        target = int(self.quantity_entry.get().replace(",", ""))
        actual = len(self.generated_data)
        
        if cancelled:
            self.statusbar.set_status(f"Cancelled. Generated {format_number(actual)} in {duration:.2f}s.")
        else:
            self.progress.set(1.0)
            self.statusbar.set_status(f"Completed in {duration:.2f}s.")
            HistoryManager.add_entry(self.version_var.get(), actual, duration)
            
        logger.info(f"Generation finished. Cancelled: {cancelled}. Count: {actual}. Time: {duration:.2f}s")

    def _copy_all(self):
        if not self.generated_data:
            return
        self.statusbar.set_status("Copying...")
        self.update()
        success = ClipboardManager.copy_list_to_clipboard(self.generated_data)
        if success:
            self.statusbar.set_status(f"Copied {format_number(len(self.generated_data))} UUIDs to clipboard.")
        else:
            self.statusbar.set_status("Failed to copy to clipboard.")

    def _export(self, fmt: str):
        if not self.generated_data:
            return
            
        filename = generate_export_filename() + f".{fmt}"
        filepath = filedialog.asksaveasfilename(
            initialdir=EXPORTS_DIR,
            initialfile=filename,
            defaultextension=f".{fmt}",
            filetypes=[(f"{fmt.upper()} files", f"*.{fmt}")]
        )
        
        if filepath:
            self.statusbar.set_status(f"Exporting to {fmt.upper()}...")
            self.update()
            
            success = False
            path_obj = Path(filepath)
            if fmt == "csv":
                success = Exporter.export_to_csv(path_obj, self.generated_data)
            elif fmt == "txt":
                success = Exporter.export_to_txt(path_obj, self.generated_data)
                
            if success:
                self.statusbar.set_status(f"Successfully exported to {path_obj.name}.")
            else:
                self.statusbar.set_status("Export failed. Check logs.")

    def _clear(self):
        self.generated_data = []
        self.textbox.clear()
        self.progress.set(0)
        self.statusbar.set_status("Cleared.")
        self.statusbar.set_stats("")
