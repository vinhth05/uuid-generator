import customtkinter as ctk

def apply_theme(mode: str):
    """Applies the application theme."""
    ctk.set_appearance_mode(mode)
    ctk.set_default_color_theme("blue")  # Using default blue theme

# We can define specific color codes here if we build custom widgets
COLORS = {
    "dark": {
        "bg": "#1e1e1e",
        "fg": "#ffffff",
        "accent": "#1f538d",
        "error": "#d32f2f",
        "success": "#388e3c"
    },
    "light": {
        "bg": "#f5f5f5",
        "fg": "#000000",
        "accent": "#3a7ebf",
        "error": "#f44336",
        "success": "#4caf50"
    }
}
