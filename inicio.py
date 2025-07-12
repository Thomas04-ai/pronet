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
        self.geometry("700x520")
        self.configure(bg="#18181b")

        # Frame principal moderno
        main_frame = ctk.CTkFrame(self, corner_radius=18, fg_color="#232326")
        main_frame.pack(fill="both", expand=True, padx=28, pady=28)

        # Título
        ctk.CTkLabel(main_frame, text="Gestor de Inicio de Windows", font=("Segoe UI", 22, "bold"), text_color="#fafafa").pack(pady=(10, 18))

        # Frame para Treeview y barra de búsqueda
        tree_outer_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#18181b")
        tree_outer_frame.pack(fill="both", expand=True, pady=(0, 12))

        # Barra de búsqueda
        search_frame = ctk.CTkFrame(tree_outer_frame, fg_color="#18181b")
        search_frame.pack(fill="x", pady=(8, 2), padx=8)
        ctk.CTkLabel(search_frame, text="Buscar programa:", font=("Segoe UI", 13), text_color="#fafafa").pack(side="left", padx=(4, 6))
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, width=220, fg_color="#232326", text_color="#fafafa")
        search_entry.pack(side="left", padx=(0, 8))
        self.search_var.trace_add("write", lambda *args: self.filter_treeview())

        # Treeview con estilo profesional
        tree_frame = ctk.CTkFrame(tree_outer_frame, corner_radius=10, fg_color="#232326")
        tree_frame.pack(fill="both", expand=True, pady=(0, 8), padx=8)

        style = tk.ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#232326", foreground="#fafafa", fieldbackground="#232326", font=("Segoe UI", 12), borderwidth=0)
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

        # Botones con diseño moderno
        btn_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#232326")
        btn_frame.pack(fill="x", pady=5, padx=8)
        ctk.CTkButton(btn_frame, text="Deshabilitar Seleccionado", command=self.disable_startup, fg_color="#ef4444", hover_color="#dc2626", text_color="#fafafa").pack(side="left", padx=7, pady=8, fill="x", expand=True)
        ctk.CTkButton(btn_frame, text="Actualizar Lista", command=self.load_startup, fg_color="#3b82f6", hover_color="#2563eb", text_color="#fafafa").pack(side="right", padx=7, pady=8, fill="x", expand=True)

        # Barra de estado inferior
        self.status_var = ctk.StringVar(value="Selecciona un programa para habilitar o deshabilitar del inicio")
        ctk.CTkLabel(main_frame, textvariable=self.status_var, font=("Segoe UI", 13), text_color="#f59e42", anchor="w").pack(fill="x", pady=(8, 2), padx=8)

        self.load_startup()
    def filter_treeview(self):
        """Filtra los elementos del Treeview según el texto de búsqueda"""
        search_text = self.search_var.get().lower() if hasattr(self, 'search_var') else ""
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            name = str(values[0]).lower() if values else ""
            if search_text in name:
                self.tree.reattach(item, '', tk.END)
            else:
                self.tree.detach(item)
        # Actualiza barra de estado
        if search_text:
            self.status_var.set(f"Filtrando por: '{self.search_var.get()}'")
        else:
            self.status_var.set("Selecciona un programa para habilitar o deshabilitar del inicio")
    
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
    

# Agregar interfaz principal para ejecutar directamente
if __name__ == "__main__":
    app = StartupManager(None)
    app.mainloop()