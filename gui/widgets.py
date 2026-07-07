import customtkinter as ctk
import tkinter as tk
from typing import Callable, Optional
from gui.themes import get_color, FONTS

class IconButton(ctk.CTkButton):
    def __init__(self, master, icon: str, text: str = "", **kwargs):
        super().__init__(
            master, 
            text=f"{icon} {text}" if text else icon,
            font=FONTS["label"],
            height=42,
            corner_radius=10,
            **kwargs
        )

class StatisticCard(ctk.CTkFrame):
    def __init__(self, master, icon: str, title: str, value: str = "0", **kwargs):
        super().__init__(master, corner_radius=10, fg_color=get_color("card"), **kwargs)
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Icon
        self.icon_label = ctk.CTkLabel(
            self, text=icon, font=("Segoe UI", 32), 
            text_color=get_color("primary")
        )
        self.icon_label.grid(row=0, column=0, rowspan=2, padx=(16, 10), pady=16, sticky="nsew")
        
        # Value
        self.value_label = ctk.CTkLabel(
            self, text=value, font=FONTS["title"], 
            text_color=get_color("text"), anchor="w"
        )
        self.value_label.grid(row=0, column=1, padx=(0, 16), pady=(16, 0), sticky="sw")
        
        # Title (Description)
        self.title_label = ctk.CTkLabel(
            self, text=title, font=FONTS["label"], 
            text_color=get_color("secondary_text"), anchor="w"
        )
        self.title_label.grid(row=1, column=1, padx=(0, 16), pady=(0, 16), sticky="nw")

    def set_value(self, value: str):
        self.value_label.configure(text=value)


class ToastNotification(ctk.CTkFrame):
    """A floating toast notification."""
    def __init__(self, master, message: str, duration: int = 2000, type: str = "success", **kwargs):
        color = get_color("success") if type == "success" else get_color("danger")
        super().__init__(master, corner_radius=8, fg_color=color, border_width=0, **kwargs)
        
        icon = "✓" if type == "success" else "⚠"
        
        self.label = ctk.CTkLabel(
            self, text=f"{icon}  {message}", 
            font=FONTS["label"], text_color="#FFFFFF"
        )
        self.label.pack(padx=20, pady=10)
        
        # Automatically hide
        self.after(duration, self.destroy)

    def show(self, x: int, y: int):
        self.place(x=x, y=y, anchor="ne")


class StatusBar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, height=30, fg_color=get_color("sidebar"), corner_radius=0, **kwargs)
        self.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(self, text="Ready", font=FONTS["label"], text_color=get_color("secondary_text"), anchor="w")
        self.status_label.pack(side="left", padx=10)
        
        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.pack(side="right", padx=10)
        
        self.mode_label = ctk.CTkLabel(self.right_frame, text="Dark Mode", font=FONTS["label"], text_color=get_color("secondary_text"))
        self.mode_label.pack(side="left", padx=10)
        
        self.encoding_label = ctk.CTkLabel(self.right_frame, text="UTF-8", font=FONTS["label"], text_color=get_color("secondary_text"))
        self.encoding_label.pack(side="left", padx=10)
        
        self.version_label = ctk.CTkLabel(self.right_frame, text="v1.0.0", font=FONTS["label"], text_color=get_color("secondary_text"))
        self.version_label.pack(side="left", padx=10)

    def set_status(self, text: str):
        self.status_label.configure(text=text)
