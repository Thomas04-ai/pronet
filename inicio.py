import ctypes
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class StartupManager:
    def __init__(self, parent_frame):
        self.frame = ttk.Frame(parent_frame, padding="10")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Interfaz
        title_label = ttk.Label(self.frame, text="Gestor de Inicio de Windows", font=('Helvetica', 12, 'bold'))
        title_label.pack(pady=5)
        
        # Frame para el treeview y scrollbars
        tree_frame = ttk.Frame(self.frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview
        self.tree = ttk.Treeview(tree_frame, columns=('Name', 'Status'), show='headings')
        self.tree.heading('Name', text='Nombre del Programa')
        self.tree.heading('Status', text='Estado')
        
        # Configurar ancho de columnas
        self.tree.column('Name', width=400)
        self.tree.column('Status', width=150)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Layout con grid dentro del tree_frame
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # Configurar pesos para que el treeview se expanda
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Botones
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Deshabilitar Seleccionado", command=self.disable_startup).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Habilitar Seleccionado", command=self.enable_startup).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Actualizar Lista", command=self.load_startup).pack(side=tk.RIGHT, padx=5)
        
        # Cargar datos
        self.load_startup()
    
    def load_startup(self):
        self.tree.delete(*self.tree.get_children())
        
        # Cargar programas de inicio desde ambos registros
        startup_locations = [
            ("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "Usuario"),
            ("HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "Sistema")
        ]
        
        for registry_path, location_type in startup_locations:
            try:
                # Obtener entradas del registro
                result = subprocess.run(['reg', 'query', registry_path], 
                                      capture_output=True, text=True, shell=True)
                
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and 'REG_SZ' in line:
                            # Extraer nombre del programa
                            parts = line.split('REG_SZ')
                            if len(parts) >= 2:
                                name = parts[0].strip()
                                path = parts[1].strip()
                                
                                # Filtrar entradas válidas
                                if name and name not in ['(Default)', '(Predeterminado)']:
                                    status = f"Habilitado ({location_type})"
                                    self.tree.insert('', tk.END, values=(name, status), 
                                                   tags=(registry_path, name, path))
                                    
            except Exception as e:
                continue
                
        # También agregar programas deshabilitados conocidos (opcional)
        self.add_disabled_programs()
    
    def add_disabled_programs(self):
        """Agregar algunos programas comunes que pueden estar deshabilitados"""
        # Esta es una función opcional para mostrar programas que podrían estar deshabilitados
        common_programs = [
            "Discord", "Spotify", "Steam", "Skype", "Teams", "Zoom", 
            "Adobe Updater", "Java Update", "Chrome", "Firefox"
        ]
        
        for program in common_programs:
            # Verificar si ya está en la lista
            found = False
            for child in self.tree.get_children():
                if program.lower() in self.tree.item(child)['values'][0].lower():
                    found = True
                    break
            
            if not found:
                # Buscar en archivos de inicio comunes
                common_paths = [
                    f"C:\\Program Files\\{program}\\{program}.exe",
                    f"C:\\Program Files (x86)\\{program}\\{program}.exe",
                    f"C:\\Users\\{subprocess.getoutput('echo %USERNAME%')}\\AppData\\Local\\{program}\\{program}.exe"
                ]
                
                for path in common_paths:
                    try:
                        if subprocess.run(['where', program], capture_output=True, shell=True).returncode == 0:
                            self.tree.insert('', tk.END, values=(program, "Deshabilitado"), 
                                           tags=("DISABLED", program, path))
                            break
                    except:
                        continue
    
    def disable_startup(self):
        """Deshabilitar un elemento del inicio"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un elemento para deshabilitar")
            return
        
        item = self.tree.item(selected[0])
        name = item['values'][0]
        status = item['values'][1]
        tags = item['tags']
        
        if "Deshabilitado" in status:
            messagebox.showinfo("Información", f"{name} ya está deshabilitado")
            return
        
        if not name:
            messagebox.showwarning("Advertencia", "No se puede determinar el nombre del programa")
            return
        
        try:
            # Obtener la ruta del registro desde los tags
            registry_path = tags[0] if tags else "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            
            # Eliminar del registro para deshabilitarlo
            subprocess.run(['reg', 'delete', registry_path, '/v', name, '/f'], 
                         shell=True, check=True)
            messagebox.showinfo("Éxito", f"{name} deshabilitado del inicio")
            self.load_startup()
            
        except subprocess.CalledProcessError:
            # Si no funciona, intentar en ambos registros
            success = False
            for reg_path in ["HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", 
                           "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"]:
                try:
                    subprocess.run(['reg', 'delete', reg_path, '/v', name, '/f'], 
                                 shell=True, check=True)
                    success = True
                    break
                except:
                    continue
            
            if success:
                messagebox.showinfo("Éxito", f"{name} deshabilitado del inicio")
                self.load_startup()
            else:
                messagebox.showerror("Error", 
                    f"No se pudo deshabilitar {name}. Puede requerir permisos de administrador.")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
    
    def enable_startup(self):
        """Habilitar un elemento del inicio"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un elemento para habilitar")
            return
        
        item = self.tree.item(selected[0])
        name = item['values'][0]
        status = item['values'][1]
        tags = item['tags']
        
        if "Habilitado" in status:
            messagebox.showinfo("Información", f"{name} ya está habilitado")
            return
        
        if not name:
            messagebox.showwarning("Advertencia", "No se puede determinar el nombre del programa")
            return
        
        # Si es un programa deshabilitado, necesitamos obtener su ruta
        if tags and len(tags) > 2:
            location = tags[2]
        else:
            # Solicitar al usuario la ruta del programa
            location = tk.simpledialog.askstring(
                "Ruta del programa", 
                f"Ingrese la ruta completa del ejecutable para {name}:",
                initialvalue=f"C:\\Program Files\\{name}\\{name}.exe"
            )
            
        if not location:
            messagebox.showwarning("Advertencia", "Se necesita la ruta del programa para habilitarlo")
            return
        
        try:
            # Agregar al registro de usuario para habilitarlo
            subprocess.run(['reg', 'add', 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run', 
                          '/v', name, '/t', 'REG_SZ', '/d', f'"{location}"', '/f'], 
                         shell=True, check=True)
            messagebox.showinfo("Éxito", f"{name} habilitado en el inicio")
            self.load_startup()
            
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"No se pudo habilitar: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")

# Agregar interfaz principal para ejecutar directamente
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Gestor de Inicio de Windows")
    root.geometry("900x600")
    root.minsize(600, 400)
    
    # Crear la aplicación
    app = StartupManager(root)
    
    # Ejecutar la aplicación
    root.mainloop()