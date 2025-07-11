import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import zipfile
import io
import ctypes
import sys
from threading import Thread

class AdvancedPowerPlanManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor Avanzado de Planes de Energía")
        self.root.geometry("1000x700")
        
        # Configuración
        self.github_repo = "IDIVASM/POWERPLAN-WINDOWS-10-"
        self.temp_dir = os.path.join(os.environ['TEMP'], "PowerPlans")
        self.downloaded_plans = []
        
        # Estilos
        self.setup_styles()
        
        # Interfaz
        self.setup_ui()
        
        # Cargar datos iniciales
        self.update_power_plans_list()
    
    def setup_styles(self):
        """Configura los estilos visuales"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', background='#f0f0f0')
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Segoe UI', 9))
        self.style.configure('Title.TLabel', font=('Segoe UI', 12, 'bold'))
        self.style.configure('TButton', font=('Segoe UI', 9), padding=5)
        self.style.configure('Treeview', font=('Segoe UI', 9), rowheight=25, fieldbackground='white')
        self.style.configure('Treeview.Heading', font=('Segoe UI', 9, 'bold'), background='#e0e0e0')
        self.style.map('Treeview', background=[('selected', '#0078d7')])
        self.style.configure('Red.TButton', foreground='red')
        self.style.configure('Green.TButton', foreground='green')
        self.style.configure('Blue.TButton', foreground='blue')
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="Gestor Avanzado de Planes de Energía", style='Title.TLabel').pack(side=tk.LEFT)
        
        # Frame de botones principales
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Actualizar Lista", command=self.update_power_plans_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Eliminar Seleccionados", command=self.delete_selected_plans, style='Red.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Restaurar Planes por Defecto", command=self.restore_default_plans).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Importar desde Archivo", command=self.import_from_file, style='Green.TButton').pack(side=tk.RIGHT, padx=2)
        ttk.Button(button_frame, text="Descargar e Importar GitHub", command=self.download_and_import_github, style='Blue.TButton').pack(side=tk.RIGHT, padx=2)
        
        # Panel principal - Planes instalados
        installed_frame = ttk.Frame(main_frame, padding="5")
        installed_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(installed_frame, text="Planes Instalados", style='Title.TLabel').pack(anchor='w')
        self.installed_tree = ttk.Treeview(installed_frame, columns=('GUID', 'Name', 'Status'), show='headings', selectmode='extended')
        self.installed_tree.heading('GUID', text='GUID')
        self.installed_tree.heading('Name', text='Nombre del Plan')
        self.installed_tree.heading('Status', text='Estado')
        self.installed_tree.column('GUID', width=280, anchor='w')
        self.installed_tree.column('Name', width=250, anchor='w')
        self.installed_tree.column('Status', width=100, anchor='w')
        
        installed_scroll = ttk.Scrollbar(installed_frame, orient="vertical", command=self.installed_tree.yview)
        self.installed_tree.configure(yscrollcommand=installed_scroll.set)
        
        self.installed_tree.pack(side="left", fill="both", expand=True)
        installed_scroll.pack(side="right", fill="y")
        
        # Barra de estado
        self.status_var = tk.StringVar()
        self.status_var.set("Listo")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def run_as_admin(self):
        """Verifica y solicita elevación de privilegios si es necesario"""
        try:
            if ctypes.windll.shell32.IsUserAnAdmin() == 0:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                sys.exit()
            return True
        except:
            return False
    
    def update_power_plans_list(self):
        """Actualiza la lista de planes de energía instalados"""
        self.installed_tree.delete(*self.installed_tree.get_children())
        self.status_var.set("Actualizando lista de planes instalados...")
        
        try:
            result = subprocess.run(['powercfg', '/list'], capture_output=True, text=True, check=True)
            lines = result.stdout.split('\n')
            
            for line in lines:
                if 'GUID' in line:
                    parts = line.split()
                    guid = parts[3]
                    name = ' '.join(parts[4:]) if len(parts) > 4 else 'Desconocido'
                    status = 'Activo' if '*' in line else 'Inactivo'
                    self.installed_tree.insert('', 'end', values=(guid, name, status))
            
            self.status_var.set(f"Listo - {self.installed_tree.get_children().__len__()} planes instalados")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo obtener la lista de planes: {str(e)}")
            self.status_var.set("Error al actualizar lista")
    
    def delete_selected_plans(self):
        """Elimina los planes seleccionados"""
        selected_items = self.installed_tree.selection()
        if not selected_items:
            messagebox.showwarning("Advertencia", "Selecciona al menos un plan para eliminar")
            return
        
        # Obtener detalles de los planes seleccionados
        plans_to_delete = []
        for item in selected_items:
            guid = self.installed_tree.item(item)['values'][0]
            name = self.installed_tree.item(item)['values'][1]
            plans_to_delete.append((guid, name))
        
        # Mostrar confirmación
        confirmation_msg = f"¿Estás seguro de eliminar los siguientes {len(plans_to_delete)} planes?\n\n"
        confirmation_msg += "\n".join([f"- {name} ({guid})" for guid, name in plans_to_delete])
        
        if not messagebox.askyesno("Confirmar Eliminación", confirmation_msg):
            return
        
        # Procesar eliminación
        success = 0
        failed = 0
        failed_list = []
        
        for guid, name in plans_to_delete:
            try:
                subprocess.run(['powercfg', '/delete', guid], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                success += 1
            except subprocess.CalledProcessError as e:
                failed += 1
                failed_list.append(name)
                print(f"Error eliminando {guid}: {e.stderr}")
            except Exception as e:
                failed += 1
                failed_list.append(name)
                print(f"Error inesperado eliminando {guid}: {str(e)}")
        
        # Mostrar resultados
        result_msg = f"Resultado de eliminación:\n\nCorrectos: {success}\nFallidos: {failed}"
        if failed > 0:
            result_msg += f"\n\nNo se pudieron eliminar:\n" + "\n".join(failed_list)
        
        messagebox.showinfo("Resultado", result_msg)
        self.update_power_plans_list()
    
    def restore_default_plans(self):
        """Restaura los planes de energía por defecto de Windows"""
        if not messagebox.askyesno(
            "Confirmar Restauración",
            "¿Estás seguro de restaurar los planes de energía por defecto de Windows?\n\n"
            "Esto eliminará cualquier plan personalizado."):
            return
        
        try:
            self.status_var.set("Restaurando planes por defecto...")
            subprocess.run(['powercfg', '/restoredefaultschemes'], check=True)
            messagebox.showinfo("Éxito", "Planes por defecto restaurados correctamente")
            self.update_power_plans_list()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron restaurar los planes: {str(e)}")
        finally:
            self.status_var.set("Listo")
    
    def download_and_import_github(self):
        """Descarga e importa planes de energía desde el repositorio GitHub"""
        if not messagebox.askyesno(
            "Confirmar Descarga e Importación",
            f"¿Descargar e importar automáticamente todos los planes de energía desde:\n\n{self.github_repo}?"):
            return
        
        # Ejecutar en un hilo para no bloquear la interfaz
        Thread(target=self._download_and_import_github_thread, daemon=True).start()
    
    def _download_and_import_github_thread(self):
        """Hilo para la descarga e importación desde GitHub"""
        try:
            self.status_var.set("Conectando con GitHub...")
            
            # Crear directorio temporal si no existe
            os.makedirs(self.temp_dir, exist_ok=True)
            
            # Descargar el repositorio como zip
            self.status_var.set("Descargando repositorio...")
            response = requests.get(f"https://github.com/{self.github_repo}/archive/refs/heads/main.zip", stream=True)
            response.raise_for_status()
            
            # Extraer el zip
            self.status_var.set("Extrayendo archivos...")
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                zip_ref.extractall(self.temp_dir)
            
            # Buscar archivos .pow en la estructura extraída
            self.status_var.set("Buscando planes de energía...")
            plans_found = []
            repo_dir = os.path.join(self.temp_dir, os.listdir(self.temp_dir)[0])
            
            for root, _, files in os.walk(repo_dir):
                for file in files:
                    if file.lower().endswith('.pow'):
                        full_path = os.path.join(root, file)
                        plans_found.append((file, full_path))
            
            if not plans_found:
                messagebox.showwarning("Sin Planes", "No se encontraron archivos .pow en el repositorio")
                self.status_var.set("Sin planes encontrados")
                return
            
            # Importar automáticamente todos los planes encontrados
            self.status_var.set(f"Importando {len(plans_found)} planes...")
            success = 0
            failed = 0
            failed_list = []
            
            for i, (file, path) in enumerate(plans_found):
                self.status_var.set(f"Importando {i+1}/{len(plans_found)}: {file}...")
                
                try:
                    subprocess.run(['powercfg', '/import', path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    success += 1
                except subprocess.CalledProcessError as e:
                    failed += 1
                    failed_list.append(file)
                    print(f"Error importando {file}: {e.stderr}")
                except Exception as e:
                    failed += 1
                    failed_list.append(file)
                    print(f"Error inesperado importando {file}: {str(e)}")
            
            # Mostrar resultados
            result_msg = f"Descarga e importación completada:\n\nEncontrados: {len(plans_found)}\nImportados: {success}\nFallidos: {failed}"
            if failed > 0:
                result_msg += f"\n\nNo se pudieron importar:\n" + "\n".join(failed_list)
            
            messagebox.showinfo("Resultado", result_msg)
            self.update_power_plans_list()
            
        except requests.RequestException as e:
            messagebox.showerror("Error de Descarga", f"No se pudo descargar del GitHub: {str(e)}")
            self.status_var.set("Error en descarga")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
            self.status_var.set("Error")
        finally:
            self.status_var.set("Listo")
    
    def import_from_file(self):
        """Importa planes de energía desde archivos locales"""
        file_paths = filedialog.askopenfilenames(
            title="Seleccionar archivos de planes de energía",
            filetypes=[("Archivos de plan de energía", "*.pow"), ("Todos los archivos", "*.*")]
        )
        
        if not file_paths:
            return
        
        # Confirmar importación
        if not messagebox.askyesno(
            "Confirmar Importación",
            f"¿Importar {len(file_paths)} archivo(s) de plan de energía?"):
            return
        
        # Procesar importación en un hilo
        Thread(target=self._import_files_thread, args=(file_paths,), daemon=True).start()
    
    def _import_files_thread(self, file_paths):
        """Hilo para importar archivos"""
        try:
            success = 0
            failed = 0
            failed_list = []
            
            for i, file_path in enumerate(file_paths):
                file_name = os.path.basename(file_path)
                self.status_var.set(f"Importando {i+1}/{len(file_paths)}: {file_name}...")
                
                try:
                    subprocess.run(['powercfg', '/import', file_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    success += 1
                except subprocess.CalledProcessError as e:
                    failed += 1
                    failed_list.append(file_name)
                    print(f"Error importando {file_name}: {e.stderr}")
                except Exception as e:
                    failed += 1
                    failed_list.append(file_name)
                    print(f"Error inesperado importando {file_name}: {str(e)}")
            
            # Mostrar resultados
            result_msg = f"Resultado de importación:\n\nSeleccionados: {len(file_paths)}\nImportados: {success}\nFallidos: {failed}"
            if failed > 0:
                result_msg += f"\n\nNo se pudieron importar:\n" + "\n".join(failed_list)
            
            messagebox.showinfo("Resultado", result_msg)
            self.update_power_plans_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la importación: {str(e)}")
        finally:
            self.status_var.set("Listo")

if __name__ == "__main__":
    root = tk.Tk()
    
    # Verificar permisos de administrador al inicio
    def check_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    if not check_admin():
        if messagebox.askyesno(
            "Permisos Requeridos",
            "Algunas funciones requieren permisos de administrador.\n\n"
            "¿Deseas ejecutar el programa como administrador?"):
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()
    
    app = AdvancedPowerPlanManager(root)
    root.mainloop()