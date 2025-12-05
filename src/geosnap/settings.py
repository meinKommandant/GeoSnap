# src/geosnap/settings.py
"""Settings dialog for GeoSnap application."""
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import Dict, Any, Optional, Callable


class SettingsDialog:
    """Modal dialog for application settings."""
    
    def __init__(self, parent: tk.Tk, current_settings: Dict[str, Any], on_save: Callable[[Dict[str, Any]], None]):
        self.result: Optional[Dict[str, Any]] = None
        self.on_save = on_save
        
        # Create modal window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Ajustes")
        self.dialog.geometry("400x350")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center on parent
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        # Variables
        self.thumbnail_size_var = tk.IntVar(value=current_settings.get("thumbnail_size", 800))
        self.jpeg_quality_var = tk.IntVar(value=current_settings.get("jpeg_quality", 75))
        self.arrow_length_var = tk.IntVar(value=current_settings.get("arrow_length", 30))
        self.arrow_width_var = tk.IntVar(value=current_settings.get("arrow_width", 4))
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # --- Thumbnail Settings ---
        ttk.Label(main_frame, text="Miniaturas", font=("Helvetica", 11, "bold")).pack(anchor="w", pady=(0, 10))
        
        thumb_frame = ttk.Frame(main_frame)
        thumb_frame.pack(fill=X, pady=5)
        ttk.Label(thumb_frame, text="Tamaño máximo (px):").pack(side=LEFT)
        ttk.Spinbox(thumb_frame, from_=200, to=1600, increment=100, 
                    textvariable=self.thumbnail_size_var, width=8).pack(side=RIGHT)
        
        quality_frame = ttk.Frame(main_frame)
        quality_frame.pack(fill=X, pady=5)
        ttk.Label(quality_frame, text="Calidad JPEG (%):").pack(side=LEFT)
        ttk.Spinbox(quality_frame, from_=30, to=100, increment=5,
                    textvariable=self.jpeg_quality_var, width=8).pack(side=RIGHT)
        
        # --- Arrow Settings ---
        ttk.Separator(main_frame, orient=HORIZONTAL).pack(fill=X, pady=15)
        ttk.Label(main_frame, text="Flechas de Rumbo", font=("Helvetica", 11, "bold")).pack(anchor="w", pady=(0, 10))
        
        arrow_len_frame = ttk.Frame(main_frame)
        arrow_len_frame.pack(fill=X, pady=5)
        ttk.Label(arrow_len_frame, text="Longitud (m):").pack(side=LEFT)
        ttk.Spinbox(arrow_len_frame, from_=10, to=100, increment=5,
                    textvariable=self.arrow_length_var, width=8).pack(side=RIGHT)
        
        arrow_width_frame = ttk.Frame(main_frame)
        arrow_width_frame.pack(fill=X, pady=5)
        ttk.Label(arrow_width_frame, text="Grosor (px):").pack(side=LEFT)
        ttk.Spinbox(arrow_width_frame, from_=1, to=10, increment=1,
                    textvariable=self.arrow_width_var, width=8).pack(side=RIGHT)
        
        # --- Buttons ---
        ttk.Separator(main_frame, orient=HORIZONTAL).pack(fill=X, pady=15)
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=X)
        
        ttk.Button(btn_frame, text="Guardar", bootstyle="success", 
                   command=self._save).pack(side=RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", bootstyle="secondary",
                   command=self.dialog.destroy).pack(side=RIGHT)
        ttk.Button(btn_frame, text="Restablecer", bootstyle="warning-outline",
                   command=self._reset_defaults).pack(side=LEFT)
    
    def _save(self) -> None:
        self.result = {
            "thumbnail_size": self.thumbnail_size_var.get(),
            "jpeg_quality": self.jpeg_quality_var.get(),
            "arrow_length": self.arrow_length_var.get(),
            "arrow_width": self.arrow_width_var.get(),
        }
        self.on_save(self.result)
        self.dialog.destroy()
    
    def _reset_defaults(self) -> None:
        self.thumbnail_size_var.set(800)
        self.jpeg_quality_var.set(75)
        self.arrow_length_var.set(30)
        self.arrow_width_var.set(4)
