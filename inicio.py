import ctypes
import subprocess
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog

class StartupManager(ctk.CTk):
    def __init__(self, parent_frame):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.title("Gestor de Inicio de Windows")
        self.geometry("700x500")
        self.configure(bg="#18181b")

        self.frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#232326")
        self.frame.pack(fill="both", expand=True, padx=24, pady=24)

        title_label = ctk.CTkLabel(self.frame, text="Gestor de Inicio de Windows", font=("Segoe UI", 20, "bold"), text_color="#fafafa")
        title_label.pack(pady=12)

        # Treeview (usamos ttk pero lo integramos en el frame de ctk)
        tree_frame = ctk.CTkFrame(self.frame, corner_radius=10, fg_color="#232326")
        tree_frame.pack(fill="both", expand=True, pady=(0, 10))

        style = tk.ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#232326", foreground="#fafafa", fieldbackground="#232326", font=("Segoe UI", 12))
        style.configure("Treeview.Heading", background="#27272a", foreground="#fafafa", font=("Segoe UI", 13, "bold"))
        style.map('Treeview', background=[('selected', '#3b82f6')])

        self.tree = tk.ttk.Treeview(tree_frame, columns=('Name', 'Status'), show='headings', selectmode='browse')
        self.tree.heading('Name', text='Nombre del Programa')
        self.tree.heading('Status', text='Estado')
        self.tree.column('Name', width=400)
        self.tree.column('Status', width=180)

        vsb = tk.ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = tk.ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Botones
        btn_frame = ctk.CTkFrame(self.frame, corner_radius=10, fg_color="#232326")
        btn_frame.pack(fill="x", pady=5)

        ctk.CTkButton(btn_frame, text="Deshabilitar Seleccionado", command=self.disable_startup, fg_color="#27272a", hover_color="#ef4444", text_color="#fafafa").pack(side="left", padx=5, pady=7, fill="x", expand=True)
        ctk.CTkButton(btn_frame, text="Habilitar Seleccionado", command=self.enable_startup, fg_color="#27272a", hover_color="#22c55e", text_color="#fafafa").pack(side="left", padx=5, pady=7, fill="x", expand=True)
        ctk.CTkButton(btn_frame, text="Actualizar Lista", command=self.load_startup, fg_color="#27272a", hover_color="#3b82f6", text_color="#fafafa").pack(side="right", padx=5, pady=7, fill="x", expand=True)

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
    app = StartupManager(None)
    app.mainloop()