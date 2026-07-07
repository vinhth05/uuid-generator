import customtkinter as ctk
import tkinter as tk
from typing import List
from core.clipboard import ClipboardManager
from utils.logger import logger

class VirtualizedTextbox(ctk.CTkTextbox):
    """
    A textbox that doesn't hold all items in memory.
    It takes a list of strings and only renders a subset if the list is huge.
    """
    def __init__(self, master, max_display=10000, **kwargs):
        kwargs.setdefault("spacing1", 5)
        kwargs.setdefault("spacing3", 5)
        super().__init__(master, **kwargs)
        self.max_display = max_display
        self._full_data = []
        
        # Bindings for easy copying
        self.bind("<Double-Button-1>", self._on_double_click)
        self.bind("<Button-3>", self._on_right_click)
        
        # Context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copy Selected", command=self._copy_selected)
        self.context_menu.add_command(label="Copy Line", command=self._copy_line_at_cursor)

    def set_data(self, data: List[str]):
        self._full_data = data
        self.configure(state="normal")
        self.delete("1.0", "end")
        
        display_count = min(len(data), self.max_display)
        text_to_insert = "\n".join(data[:display_count])
        
        if len(data) > self.max_display:
            text_to_insert += f"\n\n... and {len(data) - self.max_display} more UUIDs (Export to view all)."
            
        self.insert("1.0", text_to_insert)
        self.configure(state="disabled")

    def get_all_data(self) -> List[str]:
        return self._full_data

    def clear(self):
        self._full_data = []
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")

    def _get_line_at_event(self, event):
        index = self.index(f"@{event.x},{event.y}")
        line_start = f"{index} linestart"
        line_end = f"{index} lineend"
        return self.get(line_start, line_end).strip()

    def _on_double_click(self, event):
        text = self._get_line_at_event(event)
        if text and "..." not in text:
            ClipboardManager.copy_to_clipboard(text)
            self._flash_selection(event)

    def _on_right_click(self, event):
        # Move cursor to click position
        self.mark_set("insert", f"@{event.x},{event.y}")
        self.context_menu.tk_popup(event.x_root, event.y_root)
        
    def _copy_selected(self):
        try:
            text = self.selection_get()
            if text:
                ClipboardManager.copy_to_clipboard(text)
        except tk.TclError:
            pass # Nothing selected

    def _copy_line_at_cursor(self):
        index = self.index("insert")
        line_start = f"{index} linestart"
        line_end = f"{index} lineend"
        text = self.get(line_start, line_end).strip()
        if text and "..." not in text:
            ClipboardManager.copy_to_clipboard(text)

    def _flash_selection(self, event):
        """Temporarily highlight the line to indicate it was copied."""
        index = self.index(f"@{event.x},{event.y}")
        line_start = f"{index} linestart"
        line_end = f"{index} lineend"
        
        self.tag_add("copied", line_start, line_end)
        self.tag_config("copied", background="green", foreground="white")
        
        # Remove the tag after 300ms
        self.after(300, lambda: self.tag_delete("copied"))

class StatusBar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, height=30, **kwargs)
        self.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(self, text="Ready", anchor="w")
        self.status_label.pack(side="left", padx=10)
        
        self.stats_label = ctk.CTkLabel(self, text="", anchor="e")
        self.stats_label.pack(side="right", padx=10)

    def set_status(self, text: str):
        self.status_label.configure(text=text)

    def set_stats(self, text: str):
        self.stats_label.configure(text=text)
