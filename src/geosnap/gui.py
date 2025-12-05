import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import sys
import threading
from pathlib import Path
from typing import Optional, List, Callable, Any, Tuple

# Drag-and-drop support (optional)
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False

# --- IMPORTACIONES ---
try:
    from .main import process_photos_backend, process_excel_to_kmz_backend
    from .exceptions import (
        GeoSnapError,
        InputFolderMissingError,
        NoImagesFoundError,
        NoGPSDataError,
        ProcessCancelledError
    )
    from .config import ConfigManager
    from .constants import APP_TITLE, APP_SIZE, APP_MIN_SIZE, UIMessages
    from .settings import SettingsDialog
    from .batch_processor import BatchProcessor
except ImportError as e:
    if not tk._default_root:
        root_temp = tk.Tk()
        root_temp.withdraw()
    messagebox.showerror("Error de Importación",
                         f"Falta módulo necesario.\nDetalle: {e}\n"
                         "Ejecuta desde la carpeta 'src'.")
    sys.exit(1)


class GeoPhotoApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(APP_SIZE)
        
        # Ventana ajustable
        self.root.resizable(True, True) 
        self.root.minsize(*APP_MIN_SIZE)     

        self.stop_event = threading.Event()

        # --- CARGAR CONFIGURACIÓN ---
        self.config = ConfigManager.load_config()

        self.input_dir_var = tk.StringVar(value=self.config.get("input_dir", ""))
        self.output_dir_var = tk.StringVar(value=self.config.get("output_dir", ""))
        self.project_name_var = tk.StringVar(value=self.config.get("project_name", "Mi_Reporte"))
        self.progress_var = tk.DoubleVar()
        
        # Batch processing
        self.batch_processor = BatchProcessor()
        self.queue_count_var = tk.StringVar(value="Cola: 0")

        # --- HEADER ---
        header_frame = ttk.Frame(root, bootstyle="primary")
        header_frame.pack(fill=X)
        
        ttk.Label(
            header_frame, 
            text=APP_TITLE,
            font=("Helvetica", 24, "bold"), 
            bootstyle="inverse-primary",
            padding=15
        ).pack()

        # --- CONTENEDOR PRINCIPAL ---
        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(fill=BOTH, expand=True)

        # 0. Switch de Modo
        self.is_reverse_mode = tk.BooleanVar(value=False)
        # Texto inicial actualizado con "+ EXCEL"
        self.mode_text_var = tk.StringVar(value=UIMessages.MODE_PHOTOS) 
        self.mode_switch = ttk.Checkbutton(
            main_frame,
            textvariable=self.mode_text_var,
            bootstyle="success-round-toggle",
            variable=self.is_reverse_mode,
            command=self._toggle_mode_ui
        )
        self.mode_switch.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 15))

        # 0.b Checkbox "Incluir fotos sin GPS"
        self.include_no_gps_var = tk.BooleanVar(value=False)
        self.chk_no_gps = ttk.Checkbutton(
            main_frame,
            text="Incluir fotos sin GPS",
            variable=self.include_no_gps_var,
            bootstyle="secondary"
        )
        self.chk_no_gps.grid(row=0, column=2, sticky="e", pady=(0, 15))

        # 1. Selección de Carpetas
        self.input_label, self.input_entry, self.input_btn = self._crear_selector_carpeta(
            main_frame, row=1, label_text="Fotos Origen", var=self.input_dir_var
        )
        self.output_label, self.output_entry, self.output_btn = self._crear_selector_carpeta(
            main_frame, row=3, label_text="Carpeta Salida", var=self.output_dir_var
        )

        # 1.b Selector de Excel (oculto por defecto)
        self.excel_path_var = tk.StringVar(value="")
        self.excel_label = ttk.Label(main_frame, text="Excel Origen", font=("Helvetica", 10, "bold"))
        self.excel_entry = ttk.Entry(main_frame, textvariable=self.excel_path_var, width=45, state="readonly")
        self.excel_btn = ttk.Button(
            main_frame,
            text="Buscar",
            bootstyle="info-outline",
            command=lambda: self._browse_excel_file()
        )
        
        self.excel_label.grid(row=2, column=0, sticky="w", pady=10)
        self.excel_entry.grid(row=2, column=1, pady=10, padx=10, sticky="ew")
        self.excel_btn.grid(row=2, column=2, pady=10)
        
        # Enable DnD for Excel entry
        self._enable_dnd(self.excel_entry, self.excel_path_var)
        
        self.excel_label.grid_remove()
        self.excel_entry.grid_remove()
        self.excel_btn.grid_remove()

        # 2. Nombre del Proyecto
        ttk.Label(main_frame, text="Nombre Proyecto", font=("Helvetica", 10, "bold")).grid(
            row=4, column=0, sticky="w", pady=(20, 5))
        
        ttk.Entry(main_frame, textvariable=self.project_name_var, width=40).grid(
            row=4, column=1, sticky="ew", pady=(20, 5), padx=10
        )

        main_frame.columnconfigure(1, weight=1)

        # --- BARRA DE PROGRESO ---
        self.progress_frame = ttk.Frame(root, padding=20)
        self.progress_frame.pack(fill=X, side=BOTTOM)

        self.status_label = ttk.Label(self.progress_frame, text=UIMessages.WAITING, anchor="w")
        self.status_label.pack(fill=X, pady=(0, 5))

        self.progress_bar = ttk.Progressbar(
            self.progress_frame, 
            variable=self.progress_var, 
            maximum=100, 
            bootstyle="success-striped"
        )
        self.progress_bar.pack(fill=X)

        # --- BOTONES ---
        btn_frame = ttk.Frame(root, padding=20)
        btn_frame.pack(fill=X, side=BOTTOM)

        # BOTÓN UNIFICADO "GO"
        self.btn_generate = ttk.Button(
            btn_frame, 
            text=UIMessages.BTN_GO, 
            bootstyle="success", 
            cursor="hand2",
            command=self.start_generation_thread,
            width=20
        )
        self.btn_generate.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))

        self.btn_cancel = ttk.Button(
            btn_frame, 
            text="Cancelar", 
            bootstyle="danger-outline", 
            cursor="hand2",
            state=DISABLED, 
            command=self.cancel_process,
            width=10
        )
        self.btn_cancel.pack(side=RIGHT)
        
        # Settings button
        self.btn_settings = ttk.Button(
            btn_frame,
            text="⚙ Ajustes",
            bootstyle="secondary-outline",
            cursor="hand2",
            command=self._open_settings,
            width=10
        )
        self.btn_settings.pack(side=RIGHT, padx=(0, 10))
        
        # Batch queue button
        self.btn_add_queue = ttk.Button(
            btn_frame,
            text="+ Cola",
            bootstyle="info-outline",
            cursor="hand2",
            command=self._add_to_queue,
            width=8
        )
        self.btn_add_queue.pack(side=RIGHT, padx=(0, 5))
        
        # Queue counter label
        self.queue_label = ttk.Label(btn_frame, textvariable=self.queue_count_var, bootstyle="info")
        self.queue_label.pack(side=RIGHT, padx=(0, 5))

        # Ajustar UI inicial
        self._toggle_mode_ui()

    def _crear_selector_carpeta(self, parent: ttk.Frame, row: int, label_text: str, var: tk.StringVar) -> Tuple[ttk.Label, ttk.Entry, ttk.Button]:
        label = ttk.Label(parent, text=label_text, font=("Helvetica", 10, "bold"))
        label.grid(row=row, column=0, sticky="w", pady=10)

        entry = ttk.Entry(parent, textvariable=var, width=45, state="readonly")
        entry.grid(row=row, column=1, pady=10, padx=10, sticky="ew")
        
        # Enable drag-and-drop if available
        self._enable_dnd(entry, var)

        btn = ttk.Button(
            parent,
            text="Buscar",
            bootstyle="info-outline",
            command=lambda: self._browse_folder(var)
        )
        btn.grid(row=row, column=2, pady=10)
        return label, entry, btn
    
    def _enable_dnd(self, widget: ttk.Entry, var: tk.StringVar) -> None:
        """Enable drag-and-drop for folder/file selection."""
        if not HAS_DND:
            return
        try:
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind('<<Drop>>', lambda e: self._handle_drop(e, var))
        except Exception:
            pass  # DnD not available, silently ignore
    
    def _handle_drop(self, event: Any, var: tk.StringVar) -> None:
        """Handle dropped files/folders."""
        # Clean up the path (remove braces on Windows)
        path = event.data.strip()
        if path.startswith('{') and path.endswith('}'):
            path = path[1:-1]
        
        # Validate it's a directory for folder vars
        if Path(path).is_dir():
            var.set(path)
        elif Path(path).is_file():
            # For files, set parent directory or file path depending on context
            if var == self.excel_path_var:
                var.set(path)
            else:
                var.set(str(Path(path).parent))

    def _browse_folder(self, target_var: tk.StringVar) -> None:
        initial_dir = target_var.get() if target_var.get() else str(Path.home())
        folder_selected = filedialog.askdirectory(initialdir=initial_dir)
        if folder_selected:
            target_var.set(folder_selected)

    def _browse_excel_file(self) -> None:
        initial_dir = self.excel_path_var.get() if self.excel_path_var.get() else str(Path.home())
        file_selected = filedialog.askopenfilename(initialdir=initial_dir, filetypes=[("Excel", "*.xlsx")])
        if file_selected:
            self.excel_path_var.set(file_selected)

    def update_progress_safe(self, current: int, total: int, message: str) -> None:
        percentage = (current / total) * 100 if total > 0 else 0
        self.root.after(0, lambda: self._update_ui_elements(percentage, message))

    def _update_ui_elements(self, percentage: float, message: str) -> None:
        self.progress_var.set(percentage)
        # Show percentage with message for better feedback
        progress_text = f"{int(percentage)}% - {message}" if percentage > 0 else message
        self.status_label.config(text=progress_text)

    def start_generation_thread(self) -> None:
        input_path = self.input_dir_var.get()
        output_path = self.output_dir_var.get()
        project_name = self.project_name_var.get()
        reverse_mode = self.is_reverse_mode.get()
        include_no_gps = self.include_no_gps_var.get()
        excel_path = self.excel_path_var.get()

        if reverse_mode:
            if not excel_path or not excel_path.lower().endswith('.xlsx'):
                messagebox.showwarning("Error", "Selecciona un Excel válido (.xlsx).")
                return
            if not Path(excel_path).exists():
                messagebox.showwarning("Error", "El archivo Excel no existe.")
                return
            if not input_path:
                messagebox.showwarning("Error", "Selecciona la carpeta de Fotos Origen.")
                return
        if not input_path or not output_path:
            messagebox.showwarning("Error", "Selecciona carpetas de Entrada y Salida.")
            return

        if not project_name:
            messagebox.showwarning("Error", "Escribe un nombre para el proyecto.")
            return

        ConfigManager.save_config(input_path, output_path, project_name)

        self.stop_event.clear()
        mode_text = UIMessages.PROCESSING 
        self.btn_generate.config(state=DISABLED, text=mode_text)
        self.btn_cancel.config(state=NORMAL)
        status_text = UIMessages.STARTING
        self.status_label.config(text=status_text, bootstyle="warning")
        self.progress_var.set(0)

        thread = threading.Thread(
            target=self._run_backend_process,
            args=(input_path, output_path, project_name, reverse_mode, excel_path, include_no_gps)
        )
        thread.daemon = True
        thread.start()

    def cancel_process(self) -> None:
        if messagebox.askyesno("Cancelar", "¿Detener proceso?"):
            self.stop_event.set()
            self.status_label.config(text=UIMessages.CANCELLING, bootstyle="danger")
            self.btn_cancel.config(state=DISABLED)

    def _run_backend_process(self, input_path: str, output_path: str, project_name: str, reverse_mode: bool = False, excel_path: str = "", include_no_gps: bool = False) -> None:
        try:
            if reverse_mode:
                resultado_msg = process_excel_to_kmz_backend(
                    excel_path, input_path, output_path, project_name,
                    progress_callback=self.update_progress_safe,
                    stop_event=self.stop_event,
                )
            else:
                resultado_msg = process_photos_backend(
                    input_path, output_path, project_name,
                    progress_callback=self.update_progress_safe,
                    stop_event=self.stop_event,
                    include_no_gps=include_no_gps
                )
            self.root.after(0, lambda: self._show_success(resultado_msg))

        except ProcessCancelledError:
            self.root.after(0, self._show_cancelled)
        except (InputFolderMissingError, NoImagesFoundError, NoGPSDataError) as e:
            self.root.after(0, lambda: self._show_warning(str(e)))
        except Exception as e:
            self.root.after(0, lambda: self._show_error(str(e)))

    def _reset_ui_state(self) -> None:
        # SIEMPRE "GO" AL FINALIZAR
        self.btn_generate.config(state=NORMAL, text=UIMessages.BTN_GO)
        self.btn_cancel.config(state=DISABLED)
        self.status_label.config(bootstyle="default")

    def _show_success(self, message: str) -> None:
        self._reset_ui_state()
        self.status_label.config(text=UIMessages.SUCCESS, bootstyle="success")
        self.progress_var.set(100)
        messagebox.showinfo("Éxito", message)

    def _show_cancelled(self) -> None:
        self._reset_ui_state()
        self.status_label.config(text=UIMessages.CANCELLED, bootstyle="danger")
        self.progress_var.set(0)
        messagebox.showinfo("Info", "Proceso cancelado.")

    def _show_warning(self, message: str) -> None:
        self._reset_ui_state()
        self.status_label.config(text=UIMessages.WARNING, bootstyle="warning")
        self.progress_var.set(0)
        messagebox.showwarning("Atención", message)

    def _show_error(self, error_msg: str) -> None:
        self._reset_ui_state()
        self.status_label.config(text=UIMessages.ERROR, bootstyle="danger")
        self.progress_var.set(0)
        messagebox.showerror("Error Crítico", f"{error_msg}")

    def _open_settings(self) -> None:
        """Open settings dialog."""
        current_settings = {
            "thumbnail_size": self.config.get("thumbnail_size", 800),
            "jpeg_quality": self.config.get("jpeg_quality", 75),
            "arrow_length": self.config.get("arrow_length", 30),
            "arrow_width": self.config.get("arrow_width", 4),
        }
        
        def on_save(new_settings):
            ConfigManager.update_settings(new_settings)
            self.config.update(new_settings)
            self.status_label.config(text="✅ Ajustes guardados", bootstyle="success")
        
        SettingsDialog(self.root, current_settings, on_save)

    def _add_to_queue(self) -> None:
        """Add current config to batch queue."""
        input_path = self.input_dir_var.get()
        output_path = self.output_dir_var.get()
        project_name = self.project_name_var.get()
        include_no_gps = self.include_no_gps_var.get()
        
        # Validate
        if not input_path or not output_path:
            messagebox.showwarning("Error", "Selecciona carpetas de Entrada y Salida.")
            return
        if not project_name:
            messagebox.showwarning("Error", "Escribe un nombre para el proyecto.")
            return
        
        # Add to queue
        self.batch_processor.add_job(input_path, output_path, project_name, include_no_gps)
        count = self.batch_processor.get_pending_count()
        self.queue_count_var.set(f"Cola: {count}")
        self.status_label.config(text=f"✅ Añadido a cola: {project_name}", bootstyle="success")
        
        # Ask if user wants to process now
        if count >= 2:
            if messagebox.askyesno("Procesar Cola", f"Hay {count} trabajos en cola. ¿Procesar todos ahora?"):
                self._process_batch()

    def _process_batch(self) -> None:
        """Process all jobs in the batch queue."""
        if self.batch_processor.get_pending_count() == 0:
            messagebox.showinfo("Info", "La cola está vacía.")
            return
        
        self.stop_event.clear()
        self.btn_generate.config(state=DISABLED, text="Procesando...")
        self.btn_cancel.config(state=NORMAL)
        self.btn_add_queue.config(state=DISABLED)
        self.status_label.config(text="Procesando cola...", bootstyle="warning")
        
        def run_batch():
            result = self.batch_processor.process_all(
                progress_callback=self.update_progress_safe,
                stop_event=self.stop_event
            )
            self.root.after(0, lambda: self._show_batch_result(result))
        
        thread = threading.Thread(target=run_batch)
        thread.daemon = True
        thread.start()

    def _show_batch_result(self, result) -> None:
        """Show batch processing results."""
        self._reset_ui_state()
        self.btn_add_queue.config(state=NORMAL)
        self.queue_count_var.set(f"Cola: {self.batch_processor.get_pending_count()}")
        
        summary = f"Completados: {result.completed}/{result.total_jobs}"
        if result.failed > 0:
            summary += f" | Fallidos: {result.failed}"
        if result.cancelled > 0:
            summary += f" | Cancelados: {result.cancelled}"
        
        self.progress_var.set(100)
        self.status_label.config(text=f"✅ {summary}", bootstyle="success")
        
        # Show details
        details = "\n".join(result.details)
        messagebox.showinfo("Resultado Lote", f"{summary}\n\n{details}")

    def _toggle_mode_ui(self) -> None:
        reverse = self.is_reverse_mode.get()
        if reverse:
            self.excel_label.grid()
            self.excel_entry.grid()
            self.excel_btn.grid()
            self.input_label.config(text="Fotos Origen")
            self.mode_text_var.set(UIMessages.MODE_EXCEL)
            self.status_label.config(text=UIMessages.STATUS_EXCEL)
        else:
            self.excel_label.grid_remove()
            self.excel_entry.grid_remove()
            self.excel_btn.grid_remove()
            self.input_label.config(text="Fotos Origen")
            # Texto actualizado con EXCEL
            self.mode_text_var.set(UIMessages.MODE_PHOTOS)
            self.status_label.config(text=UIMessages.STATUS_PHOTOS)
        
        # SIEMPRE "GO"
        self.btn_generate.config(text=UIMessages.BTN_GO)


def main():
    try:
        import PIL, simplekml, openpyxl
    except ImportError:
        root_temp = tk.Tk(); root_temp.withdraw()
        messagebox.showerror("Error", "Faltan librerías.")
        sys.exit(1)

    # Use TkinterDnD if available for drag-and-drop support
    if HAS_DND:
        app_window = TkinterDnD.Tk()
        style = ttk.Style("cosmo")
    else:
        app_window = ttk.Window(themename="cosmo")
    app = GeoPhotoApp(app_window)
    app_window.mainloop()

if __name__ == "__main__":
    main()