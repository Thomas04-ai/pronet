import customtkinter as ctk
from tkinter import messagebox
import psutil
import os

class ProcessAffinityManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Administrador de Afinidad de Procesos")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.geometry("650x520")
        self.configure(bg="#18181b")
        # Variables
        self.core_vars = []
        self.selected_process = None
        self.setup_ui()
        self.update_process_list()
    
    def setup_ui(self):
        frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#232326")
        frame.pack(fill="both", expand=True, padx=24, pady=24)

        ctk.CTkLabel(frame, text="Procesos en ejecución:", font=("Segoe UI", 18, "bold"), text_color="#fafafa").pack(anchor="w", pady=(6, 2))

        # Search bar for processes
        search_frame = ctk.CTkFrame(frame, fg_color="#232326")
        search_frame.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(search_frame, text="Buscar proceso:", font=("Segoe UI", 13), text_color="#fafafa").pack(side="left", padx=(4, 6))
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, width=220, fg_color="#18181b", text_color="#fafafa")
        search_entry.pack(side="left", padx=(0, 8))
        self.search_var.trace_add("write", lambda *args: self.update_process_list())

        # Scrollable frame for process checkboxes
        self.process_scroll = ctk.CTkScrollableFrame(frame, width=580, height=220, fg_color="#18181b")
        self.process_scroll.pack(fill="x", pady=4)
        self.process_check_vars = []
        self.process_checkboxes = []

        affinity_frame = ctk.CTkFrame(frame, corner_radius=10, fg_color="#232326")
        affinity_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(affinity_frame, text="Seleccionar Afinidad:", font=("Segoe UI", 15, "bold"), text_color="#fafafa").pack(anchor="w", pady=(0, 6))


        # Crear checkboxes para cada núcleo en un scroll horizontal
        num_cores = os.cpu_count()
        cb_scroll = ctk.CTkScrollableFrame(affinity_frame, orientation="horizontal", height=50, fg_color="#232326")
        cb_scroll.pack(fill="x")
        self.core_vars = []
        for i in range(num_cores):
            var = ctk.IntVar(value=1)
            self.core_vars.append(var)
            cb = ctk.CTkCheckBox(cb_scroll, text=f"Núcleo {i}", variable=var, fg_color="#27272a", text_color="#fafafa")
            cb.pack(side="left", padx=5, pady=5)

        # Botones y status bar
        btn_frame = ctk.CTkFrame(frame, fg_color="#232326")
        btn_frame.pack(fill="x", pady=8)
        ctk.CTkButton(btn_frame, text="Aplicar Afinidad", command=self.apply_affinity, fg_color="#3b82f6", hover_color="#6366f1", text_color="#fafafa").pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Actualizar Lista", command=self.update_process_list, fg_color="#64748b", hover_color="#0ea5e9", text_color="#fafafa").pack(side="left", padx=8)

        self.status_var = ctk.StringVar(value="Selecciona un proceso para modificar su afinidad")
        ctk.CTkLabel(frame, textvariable=self.status_var, font=("Segoe UI", 13), text_color="#f59e42", anchor="w").pack(fill="x", pady=5)

    def _draw_core_checkboxes(self, event=None):
        cb_frame = self.cb_frame
        num_cores = self.num_cores
        # Elimina los checkboxes previos si existen
        for cb in getattr(self, 'core_checkboxes', []):
            cb.destroy()
        self.core_checkboxes = []
        # Calcula el ancho disponible y el tamaño de cada checkbox
        frame_width = cb_frame.winfo_width() or 600
        min_cb_width = 90  # Aproximado, ajusta si quieres más pequeño/grande
        cores_per_row = max(1, frame_width // min_cb_width)
        for i in range(num_cores):
            var = self.core_vars[i] if i < len(self.core_vars) else ctk.IntVar(value=1)
            if i >= len(self.core_vars):
                self.core_vars.append(var)
            cb = ctk.CTkCheckBox(cb_frame, text=f"Núcleo {i}", variable=var, fg_color="#27272a", text_color="#fafafa")
            row = i // cores_per_row
            col = i % cores_per_row
            cb.grid(row=row, column=col, padx=5, pady=5, sticky="w")
            self.core_checkboxes.append(cb)
        # Redibuja al cambiar tamaño de ventana
        cb_frame.bind("<Configure>", self._draw_core_checkboxes)

        btn_frame = ctk.CTkFrame(frame, fg_color="#232326")
        btn_frame.pack(fill="x", pady=8)
        ctk.CTkButton(btn_frame, text="Aplicar Afinidad", command=self.apply_affinity, fg_color="#3b82f6", hover_color="#6366f1", text_color="#fafafa").pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Actualizar Lista", command=self.update_process_list, fg_color="#64748b", hover_color="#0ea5e9", text_color="#fafafa").pack(side="left", padx=8)

        self.status_var = ctk.StringVar(value="Selecciona un proceso para modificar su afinidad")
        ctk.CTkLabel(frame, textvariable=self.status_var, font=("Segoe UI", 13), text_color="#f59e42", anchor="w").pack(fill="x", pady=5)
    
    def update_process_list(self):
        # Remove old checkboxes
        for cb in self.process_checkboxes:
            cb.destroy()
        self.process_check_vars.clear()
        self.process_checkboxes.clear()
        self.processes = []
        self.process_name_map = {}
        # Get search filter
        search_text = self.search_var.get().lower() if hasattr(self, 'search_var') else ""
        # Group processes by name
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                name = proc.name()
                if search_text and search_text not in name.lower():
                    continue
                if name not in self.process_name_map:
                    self.process_name_map[name] = []
                self.process_name_map[name].append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        # Show one checkbox per process name
        for idx, (name, procs) in enumerate(self.process_name_map.items()):
            try:
                affinity = procs[0].cpu_affinity()
                affinity_str = ", ".join(map(str, affinity)) if affinity else "Todos"
                var = ctk.IntVar(value=1 if self.selected_process == name else 0)
                cb = ctk.CTkCheckBox(self.process_scroll, text=f"{name} | {len(procs)} procesos | Afinidad: {affinity_str}", variable=var, fg_color="#27272a", text_color="#fafafa", command=lambda n=name: self.on_process_select(n))
                cb.pack(anchor="w", pady=2)
                self.process_check_vars.append(var)
                self.process_checkboxes.append(cb)
                self.processes.append((name, procs))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    
    def on_process_select(self, name):
        # Uncheck all except the selected one
        for i, cb_var in enumerate(self.process_check_vars):
            proc_name = self.processes[i][0]
            cb_var.set(1 if proc_name == name else 0)
        self.selected_process = name
        procs = self.process_name_map.get(name, [])
        if not procs:
            return
        try:
            affinity = procs[0].cpu_affinity()
            for i, var in enumerate(self.core_vars):
                var.set(1 if i in affinity else 0)
            self.status_var.set(f"Seleccionado: {name} ({len(procs)} procesos)")
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            messagebox.showerror("Error", f"No se pudo obtener afinidad: {str(e)}")
            self.selected_process = None
    
    def apply_affinity(self):
        if not self.selected_process:
            messagebox.showwarning("Advertencia", "Selecciona un proceso primero")
            return
        procs = self.process_name_map.get(self.selected_process, [])
        if not procs:
            messagebox.showerror("Error", "No se encontraron procesos para aplicar afinidad.")
            return
        selected_cores = [i for i, var in enumerate(self.core_vars) if var.get() == 1]
        if not selected_cores:
            messagebox.showwarning("Advertencia", "Debes seleccionar al menos un núcleo")
            return
        success = 0
        errors = []
        for proc in procs:
            try:
                proc.cpu_affinity(selected_cores)
                success += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                errors.append(str(e))
        self.update_process_list()
        if success:
            self.status_var.set(f"Afinidad aplicada a {self.selected_process} ({success} procesos)")
            messagebox.showinfo("Éxito", f"Afinidad actualizada para {self.selected_process}\nNúcleos seleccionados: {', '.join(map(str, selected_cores))}\nProcesos afectados: {success}")
        if errors:
            messagebox.showerror("Error", f"Algunos procesos no se pudieron modificar:\n{chr(10).join(errors)}")

if __name__ == "__main__":
    app = ProcessAffinityManager()
    app.mainloop()