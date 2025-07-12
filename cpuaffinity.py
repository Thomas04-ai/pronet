import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import os

class ProcessAffinityManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Administrador de Afinidad de Procesos")
        self.root.geometry("600x500")
        
        # Variables
        self.core_vars = []
        self.selected_process = None
        
        # Crear interfaz
        self.create_widgets()
        
        # Actualizar lista de procesos
        self.update_process_list()
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista de procesos
        ttk.Label(main_frame, text="Procesos en ejecución:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        self.process_tree = ttk.Treeview(main_frame, columns=('PID', 'Nombre', 'Afinidad'), show='headings')
        self.process_tree.heading('PID', text='PID')
        self.process_tree.heading('Nombre', text='Nombre')
        self.process_tree.heading('Afinidad', text='Afinidad')
        self.process_tree.pack(fill=tk.BOTH, expand=True)
        
        self.process_tree.bind('<<TreeviewSelect>>', self.on_process_select)
        
        # Frame de afinidad
        affinity_frame = ttk.LabelFrame(main_frame, text="Seleccionar Afinidad", padding="10")
        affinity_frame.pack(fill=tk.X, pady=10)
        
        # Crear checkboxes para cada núcleo
        num_cores = os.cpu_count()
        for i in range(num_cores):
            var = tk.IntVar(value=1)  # Por defecto todos seleccionados
            self.core_vars.append(var)
            cb = ttk.Checkbutton(affinity_frame, text=f"Núcleo {i}", variable=var)
            cb.grid(row=0, column=i, padx=5)
        
        # Botón para aplicar afinidad
        ttk.Button(main_frame, text="Aplicar Afinidad", command=self.apply_affinity).pack(pady=5)
        
        # Botón para actualizar lista
        ttk.Button(main_frame, text="Actualizar Lista", command=self.update_process_list).pack(pady=5)
        
        # Barra de estado
        self.status_var = tk.StringVar(value="Selecciona un proceso para modificar su afinidad")
        ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN).pack(fill=tk.X, pady=5)
    
    def update_process_list(self):
        # Limpiar lista actual
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        # Obtener y mostrar procesos
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                affinity = proc.cpu_affinity()
                affinity_str = ", ".join(map(str, affinity)) if affinity else "Todos"
                self.process_tree.insert('', 'end', values=(proc.pid, proc.name(), affinity_str))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    
    def on_process_select(self, event):
        selected = self.process_tree.focus()
        if not selected:
            return
        
        self.selected_process = self.process_tree.item(selected)['values'][0]
        
        try:
            proc = psutil.Process(self.selected_process)
            current_affinity = proc.cpu_affinity()
            
            # Actualizar checkboxes según la afinidad actual
            for i, var in enumerate(self.core_vars):
                var.set(1 if i in current_affinity else 0)
            
            self.status_var.set(f"Proceso seleccionado: {proc.name()} (PID: {proc.pid})")
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            messagebox.showerror("Error", f"No se pudo obtener afinidad: {str(e)}")
            self.selected_process = None
    
    def apply_affinity(self):
        if not self.selected_process:
            messagebox.showwarning("Advertencia", "Selecciona un proceso primero")
            return
        
        try:
            proc = psutil.Process(self.selected_process)
            
            # Obtener núcleos seleccionados
            selected_cores = [i for i, var in enumerate(self.core_vars) if var.get() == 1]
            
            if not selected_cores:
                messagebox.showwarning("Advertencia", "Debes seleccionar al menos un núcleo")
                return
            
            # Aplicar afinidad
            proc.cpu_affinity(selected_cores)
            
            # Actualizar lista
            self.update_process_list()
            
            # Mostrar mensaje de éxito
            self.status_var.set(f"Afinidad aplicada al proceso {proc.name()} (PID: {proc.pid})")
            messagebox.showinfo("Éxito", f"Afinidad actualizada para {proc.name()}\nNúcleos seleccionados: {', '.join(map(str, selected_cores))}")
        
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            messagebox.showerror("Error", f"No se pudo aplicar afinidad: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessAffinityManager(root)
    root.mainloop()