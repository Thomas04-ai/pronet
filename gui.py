import tkinter as tk
from tkinter import ttk, messagebox
import psutil  # pip install psutil
import prioridad # Importa el módulo que contiene set_priority y get_priority

class PriorityOptimizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Optimizador de Prioridad Win32")
        
        # Lista de procesos
        self.tree = ttk.Treeview(root, columns=('PID', 'Nombre', 'Prioridad'), show='headings')
        self.tree.heading('PID', text='PID')
        self.tree.heading('Nombre', text='Nombre')
        self.tree.heading('Prioridad', text='Prioridad')
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Controles
        frame = tk.Frame(root)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.priority_var = tk.StringVar(value='normal')
        priorities = ['idle', 'below_normal', 'normal', 'above_normal', 'high', 'realtime']
        tk.OptionMenu(frame, self.priority_var, *priorities).pack(side=tk.LEFT)
        
        tk.Button(frame, text="Actualizar lista", command=self.update_list).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Cambiar prioridad", command=self.change_priority).pack(side=tk.LEFT)
        
        # Actualizar lista al iniciar
        self.update_list()
    
    def update_list(self):
        """Actualiza la lista de procesos"""
        self.tree.delete(*self.tree.get_children())
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                priority = get_priority(proc.pid)
                if priority:
                    self.tree.insert('', 'end', values=(proc.pid, proc.name(), priority))
            except:
                continue
    
    def change_priority(self):
        """Cambia la prioridad del proceso seleccionado"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona un proceso primero")
            return
        
        pid = int(self.tree.item(selected)['values'][0])
        priority = self.priority_var.get()
        
        if priority == 'realtime':
            if not messagebox.askyesno("Advertencia", "Prioridad Realtime puede hacer inestable el sistema. ¿Continuar?"):
                return
        
        if set_priority(pid, priority):
            messagebox.showinfo("Éxito", f"Prioridad cambiada a {priority}")
            self.update_list()
        else:
            messagebox.showerror("Error", "No se pudo cambiar la prioridad")

if __name__ == "__main__":
    root = tk.Tk()
    app = PriorityOptimizer(root)
    root.mainloop()