import customtkinter as ctk
from gui.themes import get_color, FONTS

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Settings")
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Center dialog
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - 200
        y = master.winfo_y() + (master.winfo_height() // 2) - 250
        self.geometry(f"+{x}+{y}")
        
        self.transient(master)
        self.grab_set()
        
        # Layout
        self.grid_columnconfigure(0, weight=1)
        
        lbl = ctk.CTkLabel(self, text="Settings", font=FONTS["title"], text_color=get_color("text"))
        lbl.grid(row=0, column=0, pady=(20, 20), padx=20, sticky="w")
        
        # Theme
        theme_frame = ctk.CTkFrame(self, fg_color="transparent")
        theme_frame.grid(row=1, column=0, pady=(0, 15), padx=20, sticky="ew")
        ctk.CTkLabel(theme_frame, text="Theme:", font=FONTS["label"]).pack(side="left")
        self.theme_var = ctk.StringVar(value=ctk.get_appearance_mode())
        ctk.CTkOptionMenu(theme_frame, variable=self.theme_var, values=["Dark", "Light"]).pack(side="right")
        
        # Auto Copy
        self.auto_copy_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(self, text="Auto Copy to Clipboard", font=FONTS["label"], variable=self.auto_copy_var).grid(row=2, column=0, pady=(0, 15), padx=20, sticky="w")
        
        # Auto Save
        self.auto_save_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(self, text="Auto Save to History", font=FONTS["label"], variable=self.auto_save_var).grid(row=3, column=0, pady=(0, 15), padx=20, sticky="w")
        
        # Default Version
        ver_frame = ctk.CTkFrame(self, fg_color="transparent")
        ver_frame.grid(row=4, column=0, pady=(0, 15), padx=20, sticky="ew")
        ctk.CTkLabel(ver_frame, text="Default UUID Version:", font=FONTS["label"]).pack(side="left")
        self.version_var = ctk.StringVar(value="4")
        ctk.CTkOptionMenu(ver_frame, variable=self.version_var, values=["1", "3", "4", "5"]).pack(side="right")
        
        # Save Button
        save_btn = ctk.CTkButton(self, text="Save Preferences", font=FONTS["label"], command=self.save, corner_radius=10, height=42)
        save_btn.grid(row=5, column=0, pady=(30, 20), padx=20, sticky="ew")
        
    def save(self):
        new_theme = self.theme_var.get()
        ctk.set_appearance_mode(new_theme)
        # We would ideally save to settings.json here
        self.destroy()
