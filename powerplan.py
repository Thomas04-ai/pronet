import os
import subprocess
import customtkinter as ctk
from tkinter import messagebox, filedialog
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
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.root.geometry("1000x700")
        self.root.configure(bg="#18181b")
        # Configuración
        self.github_repo = "IDIVASM/POWERPLAN-WINDOWS-10-"
        self.temp_dir = os.path.join(os.environ['TEMP'], "PowerPlans")
        self.downloaded_plans = []
        # Interfaz
        self.setup_ui()
        # Cargar datos iniciales
        self.update_power_plans_list()
    
    # Elimino setup_styles, no es necesario con customtkinter
    
    def setup_ui(self):
        frame = ctk.CTkFrame(self.root, corner_radius=15, fg_color="#232326")
        frame.pack(fill="both", expand=True, padx=24, pady=24)

        ctk.CTkLabel(frame, text="Gestor Avanzado de Planes de Energía", font=("Segoe UI", 18, "bold"), text_color="#fafafa").pack(anchor="w", pady=(6, 2))

        # Botones principales
        btn_frame = ctk.CTkFrame(frame, fg_color="#232326")
        btn_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkButton(btn_frame, text="Actualizar Lista", command=self.update_power_plans_list, fg_color="#64748b", hover_color="#0ea5e9", text_color="#fafafa").pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Eliminar", command=self.delete_selected_plan, fg_color="#ef4444", hover_color="#dc2626", text_color="#fafafa").pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Restaurar Planes por Defecto", command=self.restore_default_plans, fg_color="#f59e42", hover_color="#fbbf24", text_color="#18181b").pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Importar desde Archivo", command=self.import_from_file, fg_color="#22c55e", hover_color="#16a34a", text_color="#fafafa").pack(side="right", padx=8)
        ctk.CTkButton(btn_frame, text="Descargar e Importar GitHub", command=self.download_and_import_github, fg_color="#3b82f6", hover_color="#6366f1", text_color="#fafafa").pack(side="right", padx=8)

        # Panel principal - Planes instalados (moderno)
        plans_frame = ctk.CTkFrame(frame, corner_radius=10, fg_color="#232326")
        plans_frame.pack(fill="both", expand=True, pady=10)
        ctk.CTkLabel(plans_frame, text="Planes Instalados", font=("Segoe UI", 15, "bold"), text_color="#fafafa").pack(anchor="w", pady=(0, 6))

        self.selected_plan_idx = None
        self.plans_scroll = ctk.CTkScrollableFrame(plans_frame, width=900, height=400, fg_color="#18181b")
        self.plans_scroll.pack(fill="both", expand=True, pady=4)
        self.plan_rows = []

        # Botón para activar el plan seleccionado
        def activate_selected_plan():
            if self.selected_plan_idx is None or self.selected_plan_idx >= len(self.plan_rows):
                messagebox.showwarning("Selección inválida", "Selecciona un plan para activar")
                return
            plan = self.plan_rows[self.selected_plan_idx]['data']
            guid = plan['guid']
            name = plan['name']
            try:
                subprocess.run(['powercfg', '/setactive', guid], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                messagebox.showinfo("Activado", f"El plan '{name}' ha sido activado.")
                self.update_power_plans_list()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo activar el plan: {str(e)}")
        ctk.CTkButton(plans_frame, text="Activar seleccionado", command=activate_selected_plan, fg_color="#22d3ee", hover_color="#0ea5e9", text_color="#18181b").pack(anchor='e', pady=8)


        # Barra de estado
        self.status_var = ctk.StringVar(value="Listo")
        ctk.CTkLabel(frame, textvariable=self.status_var, font=("Segoe UI", 13), text_color="#f59e42", anchor="w").pack(fill="x", pady=5)
    
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
        """Actualiza la lista de planes de energía instalados (moderno)"""
        # Limpiar scrollable frame
        for row in getattr(self, 'plan_rows', []):
            for widget in row['widgets']:
                widget.destroy()
        self.plan_rows = []
        self.selected_plan_idx = None
        self.status_var.set("Actualizando lista de planes instalados...")
        try:
            result = subprocess.run(['powercfg', '/list'], capture_output=True, text=True, check=True)
            lines = result.stdout.split('\n')
            plans = []
            for line in lines:
                if 'GUID' in line:
                    parts = line.split()
                    guid = parts[3]
                    name = ' '.join(parts[4:]) if len(parts) > 4 else 'Desconocido'
                    status = 'Activo' if '*' in line else 'Inactivo'
                    plans.append({'guid': guid, 'name': name, 'status': status})
            # Render filas
            for idx, plan in enumerate(plans):
                row_widgets = []
                bg = "#232326" if idx % 2 == 0 else "#18181b"
                row_frame = ctk.CTkFrame(self.plans_scroll, fg_color=bg, corner_radius=8)
                row_frame.pack(fill="x", pady=2, padx=2)
                # Selección visual
                def select_row(i=idx):
                    for j, r in enumerate(self.plan_rows):
                        r['frame'].configure(fg_color="#2563eb" if j == i else ("#232326" if j % 2 == 0 else "#18181b"))
                    self.selected_plan_idx = i
                row_frame.bind("<Button-1>", lambda e, i=idx: select_row(i))
                # GUID
                guid_lbl = ctk.CTkLabel(row_frame, text=plan['guid'], font=("Segoe UI", 11), text_color="#a3e635", width=320, anchor="w")
                guid_lbl.pack(side="left", padx=8)
                guid_lbl.bind("<Button-1>", lambda e, i=idx: select_row(i))
                # Nombre
                name_lbl = ctk.CTkLabel(row_frame, text=plan['name'], font=("Segoe UI", 11, "bold"), text_color="#fafafa", width=340, anchor="w")
                name_lbl.pack(side="left", padx=8)
                name_lbl.bind("<Button-1>", lambda e, i=idx: select_row(i))
                # Estado
                status_lbl = ctk.CTkLabel(row_frame, text=plan['status'], font=("Segoe UI", 11), text_color="#f59e42" if plan['status']=="Activo" else "#fafafa", width=120, anchor="w")
                status_lbl.pack(side="left", padx=8)
                status_lbl.bind("<Button-1>", lambda e, i=idx: select_row(i))
                row_widgets.extend([row_frame, guid_lbl, name_lbl, status_lbl])
                self.plan_rows.append({'frame': row_frame, 'widgets': row_widgets, 'data': plan})
            self.status_var.set(f"Listo - {len(plans)} planes instalados")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo obtener la lista de planes: {str(e)}")
            self.status_var.set("Error al actualizar lista")
    
    def delete_selected_plan(self):
        """Elimina el plan seleccionado en la UI moderna"""
        idx = self.selected_plan_idx
        if idx is None or idx >= len(self.plan_rows):
            messagebox.showwarning("Advertencia", "Selecciona un plan para eliminar")
            return
        plan = self.plan_rows[idx]['data']
        guid = plan['guid']
        name = plan['name']
        if not messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de eliminar el plan '{name}'?\n\nGUID: {guid}"):
            return
        success = 0
        failed = 0
        try:
            subprocess.run(['powercfg', '/delete', guid], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            success += 1
        except subprocess.CalledProcessError as e:
            failed += 1
            print(f"Error eliminando {guid}: {e.stderr}")
        except Exception as e:
            failed += 1
            print(f"Error inesperado eliminando {guid}: {str(e)}")
        result_msg = f"Resultado de eliminación:\n\nCorrectos: {success}\nFallidos: {failed}"
        if failed > 0:
            result_msg += f"\n\nNo se pudo eliminar: {name}"
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
        """Muestra los planes disponibles en GitHub y permite seleccionar cuáles importar"""
        Thread(target=self._show_github_plans_selection, daemon=True).start()

    def _show_github_plans_selection(self):
        try:
            self.status_var.set("Conectando con GitHub...")
            os.makedirs(self.temp_dir, exist_ok=True)
            self.status_var.set("Descargando repositorio...")
            response = requests.get(f"https://github.com/{self.github_repo}/archive/refs/heads/main.zip", stream=True)
            response.raise_for_status()
            self.status_var.set("Extrayendo archivos...")
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                zip_ref.extractall(self.temp_dir)
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
            # Mostrar ventana de selección
            self.root.after(0, lambda: self._show_plan_selection_window(plans_found))
        except requests.RequestException as e:
            messagebox.showerror("Error de Descarga", f"No se pudo descargar del GitHub: {str(e)}")
            self.status_var.set("Error en descarga")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
            self.status_var.set("Error")
        finally:
            self.status_var.set("Listo")

    def _show_plan_selection_window(self, plans_found):
        """Ventana para seleccionar qué planes importar y activar (customtkinter)"""
        win = ctk.CTkToplevel(self.root)
        win.title("Seleccionar planes de energía para importar y activar")
        win.geometry("500x500")
        ctk.CTkLabel(win, text="Selecciona los planes que deseas importar:", font=("Segoe UI", 15, "bold"), text_color="#fafafa").pack(pady=10)
        scroll_frame = ctk.CTkScrollableFrame(win, width=460, height=340, fg_color="#18181b")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.plan_vars = []
        for file, path in plans_found:
            var = ctk.BooleanVar()
            chk = ctk.CTkCheckBox(scroll_frame, text=file, variable=var, fg_color="#27272a", text_color="#fafafa")
            chk.pack(anchor='w', pady=2)
            self.plan_vars.append((var, file, path))
        # Botón de importar
        def import_selected():
            selected = [(file, path) for var, file, path in self.plan_vars if var.get()]
            if not selected:
                messagebox.showwarning("Sin selección", "Selecciona al menos un plan para importar")
                return
            win.destroy()
            Thread(target=self._import_selected_github_plans, args=(selected,), daemon=True).start()
        ctk.CTkButton(win, text="Importar seleccionados", command=import_selected, fg_color="#3b82f6", hover_color="#6366f1", text_color="#fafafa").pack(pady=10)

        # Botón para activar un plan seleccionado (solo uno)
        def activate_selected():
            selected = [(file, path) for var, file, path in self.plan_vars if var.get()]
            if len(selected) != 1:
                messagebox.showwarning("Selección inválida", "Selecciona solo un plan para activar")
                return
            file, path = selected[0]
            # Importar el plan si no está importado
            try:
                subprocess.run(['powercfg', '/import', path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except Exception:
                pass  # Si ya está importado, ignorar error
            # Obtener GUID del plan importado
            guid = self._get_guid_from_pow(path)
            if not guid:
                messagebox.showerror("Error", f"No se pudo obtener el GUID del plan: {file}")
                return
            try:
                subprocess.run(['powercfg', '/setactive', guid], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                messagebox.showinfo("Activado", f"El plan '{file}' ha sido activado.")
                self.update_power_plans_list()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo activar el plan: {str(e)}")
        ctk.CTkButton(win, text="Activar seleccionado", command=activate_selected, fg_color="#22c55e", hover_color="#16a34a", text_color="#fafafa").pack(pady=5)

    def _get_guid_from_pow(self, pow_path):
        """Obtiene el GUID de un archivo .pow importado"""
        try:
            # Ejecutar powercfg /import y capturar el GUID del resultado
            # El GUID se puede obtener de la lista de planes tras importar
            result = subprocess.run(['powercfg', '/list'], capture_output=True, text=True, check=True)
            lines = result.stdout.split('\n')
            pow_name = os.path.splitext(os.path.basename(pow_path))[0].lower()
            for line in lines:
                if 'GUID' in line:
                    parts = line.split()
                    guid = parts[3]
                    name = ' '.join(parts[4:]).lower()
                    if pow_name in name:
                        return guid
            return None
        except Exception:
            return None

    def _import_selected_github_plans(self, selected_plans):
        """Importa los planes seleccionados desde GitHub"""
        try:
            self.status_var.set(f"Importando {len(selected_plans)} planes...")
            success = 0
            failed = 0
            failed_list = []
            for i, (file, path) in enumerate(selected_plans):
                self.status_var.set(f"Importando {i+1}/{len(selected_plans)}: {file}...")
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
            result_msg = f"Importación completada:\n\nSeleccionados: {len(selected_plans)}\nImportados: {success}\nFallidos: {failed}"
            if failed > 0:
                result_msg += f"\n\nNo se pudieron importar:\n" + "\n".join(failed_list)
            messagebox.showinfo("Resultado", result_msg)
            self.update_power_plans_list()
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la importación: {str(e)}")
        finally:
            self.status_var.set("Listo")
    
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
    root = ctk.CTk()

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