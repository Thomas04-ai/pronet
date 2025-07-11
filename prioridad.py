import win32api
import win32process
import win32con
import psutil
import sys
import tkinter as tk
from tkinter import ttk, messagebox

class UniversalPriorityOptimizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Optimizador Universal de Prioridad")
        
        # Prioridades válidas
        self.valid_priorities = {
            '0x40': 'Idle (0x40)',
            '0x4000': 'Below Normal (0x4000)',
            '0x20': 'Normal (0x20)',
            '0x8000': 'Above Normal (0x8000)',
            '0x80': 'High (0x80)',
            '0x100': 'Realtime (0x100)'
        }
        
        # Configuración de la interfaz
        self.setup_ui()
        
        # Diccionario para mapear nombres de procesos
        self.process_map = {}
        
        # Actualizar lista al iniciar
        self.update_process_list()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista de procesos (mostrando solo un proceso por nombre)
        self.tree = ttk.Treeview(main_frame, columns=('Nombre', 'Cantidad', 'Prioridad'), show='headings')
        self.tree.heading('Nombre', text='Nombre del Proceso')
        self.tree.heading('Cantidad', text='Procesos')
        self.tree.heading('Prioridad', text='Prioridad Actual')
        self.tree.column('Nombre', width=200)
        self.tree.column('Cantidad', width=80)
        self.tree.column('Prioridad', width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Controles
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X)
        
        # Selector de prioridad
        ttk.Label(control_frame, text="Nueva Prioridad:").pack(side=tk.LEFT)
        
        self.priority_var = tk.StringVar(value='0x80')  # High por defecto
        
        priority_menu = ttk.OptionMenu(
            control_frame,
            self.priority_var,
            '0x80',
            *sorted(self.valid_priorities.keys()),
            command=self.update_priority_description
        )
        priority_menu.pack(side=tk.LEFT, padx=5)
        
        self.priority_desc = ttk.Label(control_frame, text=self.valid_priorities['0x80'])
        self.priority_desc.pack(side=tk.LEFT)
        
        # Botones
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="Actualizar Lista", command=self.update_process_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Aplicar a Todos", command=self.apply_to_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Ver Detalles", command=self.show_details).pack(side=tk.LEFT, padx=2)
    
    def update_priority_description(self, *args):
        """Actualiza la descripción de la prioridad seleccionada"""
        selected = self.priority_var.get()
        self.priority_desc.config(text=self.valid_priorities.get(selected, selected))
    
    def update_process_list(self):
        """Actualiza la lista de procesos mostrados (agrupados por nombre)"""
        self.tree.delete(*self.tree.get_children())
        self.process_map.clear()
        
        # Agrupar procesos por nombre
        process_count = {}
        process_priority = {}
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                name = proc.name().lower()
                if name not in process_count:
                    process_count[name] = 0
                    process_priority[name] = self.get_process_priority(proc.pid)
                
                process_count[name] += 1
                self.process_map.setdefault(name, []).append(proc.pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Mostrar en el Treeview
        for name, count in process_count.items():
            self.tree.insert('', 'end', values=(name, count, process_priority[name]))
    
    def get_process_priority(self, pid):
        """Obtiene la prioridad actual de un proceso"""
        try:
            handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)
            priority = win32process.GetPriorityClass(handle)
            win32api.CloseHandle(handle)
            
            for hex_val, desc in self.valid_priorities.items():
                if priority == int(hex_val, 16):
                    return desc
            
            return f"Desconocido ({hex(priority)})"
        except Exception:
            return "No accesible"
    
    def apply_to_all(self):
        """Cambia la prioridad de TODOS los procesos con el mismo nombre"""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Selecciona un proceso primero")
            return
        
        process_name = self.tree.item(selected_item)['values'][0]
        priority_hex = self.priority_var.get()
        priority_value = int(priority_hex, 16)
        
        if process_name not in self.process_map:
            messagebox.showwarning("Error", "No se encontraron procesos para este nombre")
            return
        
        pids = self.process_map[process_name]
        process_count = len(pids)
        
        if priority_hex == '0x100':  # Realtime
            if not messagebox.askyesno(
                "¡Precaución!",
                f"Prioridad Realtime puede inestabilizar el sistema.\n"
                f"Se aplicará a {process_count} procesos de {process_name}.\n"
                "¿Estás seguro de continuar?"
            ):
                return
        
        # Cambiar prioridad para todos los procesos
        success_count = 0
        failed_pids = []
        
        for pid in pids:
            try:
                handle = win32api.OpenProcess(
                    win32con.PROCESS_SET_INFORMATION,
                    False,
                    pid
                )
                
                if handle:
                    win32process.SetPriorityClass(handle, priority_value)
                    win32api.CloseHandle(handle)
                    success_count += 1
                else:
                    failed_pids.append(pid)
            except Exception:
                failed_pids.append(pid)
        
        # Mostrar resultados
        result_message = (
            f"Resultado para {process_name}:\n"
            f"Prioridad cambiada a {self.valid_priorities[priority_hex]}\n"
            f"Procesos modificados: {success_count}/{process_count}"
        )
        
        if failed_pids:
            result_message += f"\n\nNo se pudo cambiar estos PIDs: {', '.join(map(str, failed_pids))}"
        
        messagebox.showinfo("Resultado", result_message)
        
        # Actualizar lista
        self.update_process_list()
    
    def show_details(self):
        """Muestra los detalles de los procesos seleccionados"""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Selecciona un proceso primero")
            return
        
        process_name = self.tree.item(selected_item)['values'][0]
        
        if process_name not in self.process_map:
            messagebox.showwarning("Error", "No se encontraron procesos para este nombre")
            return
        
        pids = self.process_map[process_name]
        details = f"Detalles para {process_name}:\n\n"
        details += f"Total de procesos: {len(pids)}\n\n"
        
        for pid in pids:
            try:
                priority = self.get_process_priority(pid)
                details += f"PID: {pid} - Prioridad: {priority}\n"
            except:
                details += f"PID: {pid} - No se pudo obtener información\n"
        
        messagebox.showinfo("Detalles del Proceso", details)

if __name__ == "__main__":
    root = tk.Tk()
    
    # Intentar ejecutar como administrador
    try:
        import ctypes
        if ctypes.windll.shell32.IsUserAnAdmin() == 0:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()
    except:
        pass
    
    app = UniversalPriorityOptimizer(root)
    root.mainloop()