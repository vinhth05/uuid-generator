import customtkinter as ctk

def apply_theme(mode: str):
    """Applies the application theme."""
    ctk.set_appearance_mode(mode)
    # Using CustomTkinter's default dark blue theme as a base
    ctk.set_default_color_theme("blue")

# Modern Professional Color Palette
COLORS = {
    "dark": {
        "bg": "#1E1E1E",
        "sidebar": "#252526",
        "card": "#2D2D30",
        "primary": "#0E639C",
        "success": "#4CAF50",
        "danger": "#F44336",
        "text": "#FFFFFF",
        "secondary_text": "#BDBDBD",
        "border": "#3E3E42",
        "hover": "#2A2D2E"
    },
    "light": {
        "bg": "#FFFFFF",
        "sidebar": "#F3F3F3",
        "card": "#F5F5F5",
        "primary": "#007ACC",
        "success": "#388E3C",
        "danger": "#D32F2F",
        "text": "#000000",
        "secondary_text": "#616161",
        "border": "#E5E5E5",
        "hover": "#E8E8E8"
    }
}

FONTS = {
    "title": ("Segoe UI", 24, "bold"),
    "section": ("Segoe UI", 16, "bold"),
    "label": ("Segoe UI", 14),
    "uuid": ("Consolas", 14) # Fallback to standard monospaced font
}

def get_color(color_name: str, mode: str = None) -> str:
    if mode is None:
        mode = ctk.get_appearance_mode().lower()
    return COLORS.get(mode, COLORS["dark"]).get(color_name, "#000000")
