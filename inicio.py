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


        # Frame para barra de búsqueda y lista moderna
        list_outer_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#18181b")
        list_outer_frame.pack(fill="both", expand=True, pady=(0, 12))

        # Barra de búsqueda
        search_frame = ctk.CTkFrame(list_outer_frame, fg_color="#18181b")
        search_frame.pack(fill="x", pady=(8, 2), padx=8)
        ctk.CTkLabel(search_frame, text="Buscar programa:", font=("Segoe UI", 13), text_color="#fafafa").pack(side="left", padx=(4, 6))
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, width=220, fg_color="#232326", text_color="#fafafa")
        search_entry.pack(side="left", padx=(0, 8))
        self.search_var.trace_add("write", lambda *args: self.filter_program_list())

        # Encabezados de la tabla
        header_frame = ctk.CTkFrame(list_outer_frame, fg_color="#232326")
        header_frame.pack(fill="x", padx=8)
        ctk.CTkLabel(header_frame, text="Nombre del Programa", font=("Segoe UI", 13, "bold"), text_color="#fafafa", width=400, anchor="w").pack(side="left", padx=(0,0))
        ctk.CTkLabel(header_frame, text="Estado", font=("Segoe UI", 13, "bold"), text_color="#fafafa", width=180, anchor="w").pack(side="left", padx=(0,0))

        # ScrollableFrame para la lista de programas
        self.program_scroll = ctk.CTkScrollableFrame(list_outer_frame, width=600, height=260, fg_color="#18181b")
        self.program_scroll.pack(fill="both", expand=True, padx=8, pady=(0,8))
        self.program_rows = []
        self.selected_program = None


        # Botones con diseño moderno
        btn_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#232326")
        btn_frame.pack(fill="x", pady=5, padx=8)
        ctk.CTkButton(btn_frame, text="Deshabilitar Seleccionado", command=self.disable_startup, fg_color="#ef4444", hover_color="#dc2626", text_color="#fafafa").pack(side="left", padx=7, pady=8, fill="x", expand=True)
        ctk.CTkButton(btn_frame, text="Actualizar Lista", command=self.load_startup, fg_color="#3b82f6", hover_color="#2563eb", text_color="#fafafa").pack(side="right", padx=7, pady=8, fill="x", expand=True)

        # Barra de estado inferior
        self.status_var = ctk.StringVar(value="Selecciona un programa para habilitar o deshabilitar del inicio")
        ctk.CTkLabel(main_frame, textvariable=self.status_var, font=("Segoe UI", 13), text_color="#f59e42", anchor="w").pack(fill="x", pady=(8, 2), padx=8)

        self.programs = []
        self.load_startup()
    def filter_program_list(self):
        """Filtra los elementos de la lista moderna según el texto de búsqueda"""
        search_text = self.search_var.get().lower() if hasattr(self, 'search_var') else ""
        for row in self.program_rows:
            name = row['name'].lower()
            if search_text in name:
                row['frame'].pack(fill="x", pady=2, padx=2)
            else:
                row['frame'].pack_forget()
        # Actualiza barra de estado
        if search_text:
            self.status_var.set(f"Filtrando por: '{self.search_var.get()}'")
        else:
            self.status_var.set("Selecciona un programa para habilitar o deshabilitar del inicio")
    
    def load_startup(self):
        # Limpiar lista moderna
        for row in getattr(self, 'program_rows', []):
            row['frame'].destroy()
        self.program_rows = []
        self.programs = []

        # Cargar programas de inicio desde ambos registros
        startup_locations = [
            ("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "Usuario"),
            ("HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "Sistema")
        ]

        for registry_path, location_type in startup_locations:
            try:
                result = subprocess.run(['reg', 'query', registry_path], capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and 'REG_SZ' in line:
                            parts = line.split('REG_SZ')
                            if len(parts) >= 2:
                                name = parts[0].strip()
                                path = parts[1].strip()
                                if name and name not in ['(Default)', '(Predeterminado)']:
                                    status = f"Habilitado ({location_type})"
                                    self.add_program_row(name, status, registry_path, path)
            except Exception:
                continue

        # También agregar programas deshabilitados conocidos (opcional)
        self.add_disabled_programs()
    
    def add_disabled_programs(self):
        """Agregar algunos programas comunes que pueden estar deshabilitados"""
        common_programs = [
            "Discord", "Spotify", "Steam", "Skype", "Teams", "Zoom", 
            "Adobe Updater", "Java Update", "Chrome", "Firefox"
        ]
        for program in common_programs:
            found = False
            for row in self.program_rows:
                if program.lower() in row['name'].lower():
                    found = True
                    break
            if not found:
                common_paths = [
                    f"C:\\Program Files\\{program}\\{program}.exe",
                    f"C:\\Program Files (x86)\\{program}\\{program}.exe",
                    f"C:\\Users\\{subprocess.getoutput('echo %USERNAME%')}\\AppData\\Local\\{program}\\{program}.exe"
                ]
                for path in common_paths:
                    try:
                        if subprocess.run(['where', program], capture_output=True, shell=True).returncode == 0:
                            self.add_program_row(program, "Deshabilitado", "DISABLED", path)
                            break
                    except:
                        continue
    def add_program_row(self, name, status, registry_path, path):
        """Agrega una fila moderna a la lista de programas"""
        frame = ctk.CTkFrame(self.program_scroll, fg_color="#232326", corner_radius=8)
        frame.pack(fill="x", pady=2, padx=2)
        # Selección visual
        def select_row(event=None):
            for r in self.program_rows:
                r['frame'].configure(fg_color="#232326")
            frame.configure(fg_color="#3b82f6")
            self.selected_program = {
                'name': name,
                'status': status,
                'registry_path': registry_path,
                'path': path
            }
            self.status_var.set(f"Seleccionado: {name}")
        frame.bind("<Button-1>", select_row)
        # Nombre y estado
        lbl_name = ctk.CTkLabel(frame, text=name, font=("Segoe UI", 12), text_color="#fafafa", width=400, anchor="w")
        lbl_name.pack(side="left", padx=(8,0))
        lbl_status = ctk.CTkLabel(frame, text=status, font=("Segoe UI", 12), text_color="#fafafa", width=180, anchor="w")
        lbl_status.pack(side="left", padx=(8,0))
        lbl_name.bind("<Button-1>", select_row)
        lbl_status.bind("<Button-1>", select_row)
        self.program_rows.append({
            'frame': frame,
            'name': name,
            'status': status,
            'registry_path': registry_path,
            'path': path
        })
    
    def disable_startup(self):
        """Deshabilitar un elemento del inicio moderno"""
        selected = self.selected_program
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un elemento para deshabilitar")
            return
        name = selected['name']
        status = selected['status']
        registry_path = selected['registry_path']
        if "Deshabilitado" in status:
            messagebox.showinfo("Información", f"{name} ya está deshabilitado")
            return
        if not name:
            messagebox.showwarning("Advertencia", "No se puede determinar el nombre del programa")
            return
        try:
            subprocess.run(['reg', 'delete', registry_path, '/v', name, '/f'], shell=True, check=True)
            messagebox.showinfo("Éxito", f"{name} deshabilitado del inicio")
            self.load_startup()
        except subprocess.CalledProcessError:
            success = False
            for reg_path in ["HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"]:
                try:
                    subprocess.run(['reg', 'delete', reg_path, '/v', name, '/f'], shell=True, check=True)
                    success = True
                    break
                except:
                    continue
            if success:
                messagebox.showinfo("Éxito", f"{name} deshabilitado del inicio")
                self.load_startup()
            else:
                messagebox.showerror("Error", f"No se pudo deshabilitar {name}. Puede requerir permisos de administrador.")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
    

# Agregar interfaz principal para ejecutar directamente
if __name__ == "__main__":
    app = StartupManager(None)
    app.mainloop()