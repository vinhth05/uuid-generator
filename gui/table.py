import customtkinter as ctk
import tkinter as tk
from typing import List
from gui.themes import get_color, FONTS
from core.clipboard import ClipboardManager

class VirtualizedTable(ctk.CTkFrame):
    """
    A highly optimized Virtual Table for CustomTkinter.
    Only instantiates and renders rows that are currently visible on screen.
    Supports millions of rows without lag.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.data = []
        self.row_height = 40
        self.visible_rows = []
        
        # Header
        self.header_frame = ctk.CTkFrame(self, height=40, fg_color=get_color("sidebar"), corner_radius=0)
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)
        
        # Define Columns (Weights: #=0.1, UUID=0.6, Version=0.1, Length=0.1, Copy=0.1)
        self._build_header()
        
        # Canvas for scrolling
        self.canvas = tk.Canvas(
            self, 
            bg=get_color("bg"), 
            highlightthickness=0,
            borderwidth=0
        )
        
        # Scrollbar
        self.scrollbar = ctk.CTkScrollbar(self, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Inner frame to hold rows (actually we will place them directly on canvas for max performance)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel) # Linux scroll up
        self.canvas.bind("<Button-5>", self._on_mousewheel) # Linux scroll down
        
        # Bind scrollbar to update visible rows
        self.scrollbar.configure(command=self._on_scroll)
        
        # Context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copy UUID", command=self._copy_context)
        
        self.last_width = 0
        self.selected_index = -1
        self.context_index = -1
        
        # Callback for toast notifications
        self.on_copy_callback = None

    def _build_header(self):
        cols = [("#", 0.1), ("UUID", 0.6), ("Version", 0.1), ("Length", 0.1), ("Copy", 0.1)]
        
        for i, (text, weight) in enumerate(cols):
            self.header_frame.grid_columnconfigure(i, weight=int(weight*100))
            lbl = ctk.CTkLabel(self.header_frame, text=text, font=FONTS["section"], text_color=get_color("secondary_text"), anchor="w")
            lbl.grid(row=0, column=i, sticky="ew", padx=10, pady=5)

    def set_data(self, data: List[str]):
        self.data = data
        self.selected_index = -1
        self.update_view()

    def get_all_data(self) -> List[str]:
        return self.data
        
    def clear(self):
        self.set_data([])

    def _on_canvas_resize(self, event):
        if event.width != self.last_width:
            self.last_width = event.width
            self.update_view()

    def _on_mousewheel(self, event):
        if not self.data: return
        
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
            
        self.update_view()

    def _on_scroll(self, *args):
        self.canvas.yview(*args)
        self.update_view()

    def update_view(self):
        """Calculates visible area and draws only the rows needed."""
        if not self.winfo_exists():
            return
            
        # 1. Update scroll region
        total_height = len(self.data) * self.row_height
        self.canvas.configure(scrollregion=(0, 0, self.winfo_width(), total_height))
        
        if not self.data:
            self.canvas.delete("all")
            return
            
        # 2. Determine visible range
        yview = self.canvas.yview()
        start_y = yview[0] * total_height
        end_y = yview[1] * total_height
        
        start_idx = max(0, int(start_y // self.row_height))
        end_idx = min(len(self.data) - 1, int(end_y // self.row_height) + 1)
        
        # 3. Clear existing drawn rows
        self.canvas.delete("all")
        
        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = self.winfo_width()
            
        # 4. Draw rows
        for i in range(start_idx, end_idx + 1):
            y_pos = i * self.row_height
            uuid_str = self.data[i]
            
            # Row Background
            bg_color = get_color("card") if i % 2 == 0 else get_color("bg")
            if i == self.selected_index:
                bg_color = get_color("hover")
                
            rect_id = self.canvas.create_rectangle(
                0, y_pos, canvas_width, y_pos + self.row_height,
                fill=bg_color, outline="", tags=("row", f"row_{i}")
            )
            
            # Columns (simplified drawing directly on canvas for performance)
            text_color = get_color("text")
            sec_color = get_color("secondary_text")
            font = FONTS["label"]
            uuid_font = FONTS["uuid"]
            
            w0, w1, w2, w3 = canvas_width*0.1, canvas_width*0.6, canvas_width*0.1, canvas_width*0.1
            
            # Index
            self.canvas.create_text(20, y_pos + 20, text=str(i+1), fill=sec_color, font=font, anchor="w", tags=(f"row_{i}",))
            
            # UUID
            self.canvas.create_text(20 + w0, y_pos + 20, text=uuid_str, fill=text_color, font=uuid_font, anchor="w", tags=(f"row_{i}",))
            
            # Version (Extracted or default)
            version_str = uuid_str[14] if len(uuid_str) >= 15 and uuid_str[14].isdigit() else "?"
            self.canvas.create_text(20 + w0 + w1, y_pos + 20, text=f"v{version_str}", fill=sec_color, font=font, anchor="w", tags=(f"row_{i}",))
            
            # Length
            self.canvas.create_text(20 + w0 + w1 + w2, y_pos + 20, text=str(len(uuid_str)), fill=sec_color, font=font, anchor="w", tags=(f"row_{i}",))
            
            # Copy Button (Text representation)
            self.canvas.create_text(20 + w0 + w1 + w2 + w3, y_pos + 20, text="📋 Copy", fill=get_color("primary"), font=font, anchor="w", tags=("copy_btn", f"row_{i}"))
            
        # 5. Bind events
        self.canvas.tag_bind("row", "<Button-1>", self._on_row_click)
        self.canvas.tag_bind("row", "<Double-Button-1>", self._on_row_double_click)
        self.canvas.tag_bind("row", "<Button-3>", self._on_row_right_click)
        self.canvas.tag_bind("copy_btn", "<Button-1>", self._on_copy_click)

    def _get_row_index_from_event(self, event):
        canvas_y = self.canvas.canvasy(event.y)
        idx = int(canvas_y // self.row_height)
        if 0 <= idx < len(self.data):
            return idx
        return -1

    def _on_row_click(self, event):
        idx = self._get_row_index_from_event(event)
        if idx != -1:
            self.selected_index = idx
            self.update_view()

    def _on_row_double_click(self, event):
        idx = self._get_row_index_from_event(event)
        if idx != -1:
            self._copy_uuid(idx)

    def _on_row_right_click(self, event):
        idx = self._get_row_index_from_event(event)
        if idx != -1:
            self.selected_index = idx
            self.context_index = idx
            self.update_view()
            self.context_menu.tk_popup(event.x_root, event.y_root)

    def _on_copy_click(self, event):
        idx = self._get_row_index_from_event(event)
        if idx != -1:
            self._copy_uuid(idx)

    def _copy_context(self):
        if self.context_index != -1:
            self._copy_uuid(self.context_index)

    def _copy_uuid(self, idx: int):
        uuid_str = self.data[idx]
        ClipboardManager.copy_to_clipboard(uuid_str)
        if self.on_copy_callback:
            self.on_copy_callback("Copied to clipboard")
