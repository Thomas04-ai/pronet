import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import urllib.request
import tempfile
import ctypes
import sys
import webbrowser
import zipfile

class SoftwareInstaller:
    def __init__(self, parent_frame):
        self.frame = ttk.Frame(parent_frame, padding="10")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Variables para almacenar las selecciones
        self.selected_software = {
            # Navegadores
            "Google Chrome": tk.BooleanVar(),
            "Brave": tk.BooleanVar(),
            "Opera GX": tk.BooleanVar(),
            "Opera": tk.BooleanVar(),
            "Zen": tk.BooleanVar(),
            # Aplicaciones
            "CPU-Z": tk.BooleanVar(),
            "HWMonitor": tk.BooleanVar(),
            "OpenShell": tk.BooleanVar(),
            "DiskInfo": tk.BooleanVar(),
            # Nuevas aplicaciones
            "Discord": tk.BooleanVar(),
            "Notepad++": tk.BooleanVar(),
            "CRU (Custom Resolution Utility)": tk.BooleanVar(),
            "DDU": tk.BooleanVar(),
            "Lightshot": tk.BooleanVar(),
            "Geek Uninstaller": tk.BooleanVar(),
            # Compresores
            "7-Zip": tk.BooleanVar(),
            "WinRAR": tk.BooleanVar()
        }
        
        # URLs de descarga actualizadas
        self.download_urls = {
            "Google Chrome": "https://dl.google.com/chrome/install/standalonesetup.exe",
            "Brave": "https://referrals.brave.com/latest/BraveBrowserSetup.exe",
            "Opera GX": "https://net.geo.opera.com/opera_gx/stable/windows/Opera_GX_Setup.exe",
            "Opera": "https://get.geo.opera.com/pub/opera/desktop/",
            "Zen": "https://github.com/zenbrowser/zenbrowser/releases/download/v1.0.0/ZenBrowserSetup.exe",
            "CPU-Z": "https://download.cpuid.com/cpu-z/cpu-z_2.09-en.exe",
            "HWMonitor": "https://www.cpuid.com/softwares/hwmonitor-pro.html",
            "OpenShell": "https://github.com/Open-Shell/Open-Shell-Menu/releases/download/v4.4.191/OpenShellSetup_4_4_191.exe",
            "DiskInfo": "https://osdn.net/dl/crystaldiskinfo/CrystalDiskInfo8_17_14.exe",
            "Discord": "https://discord.com/api/downloads/distributions/app/installers/latest?channel=stable&platform=win&arch=x86",
            "Notepad++": "https://github.com/notepad-plus-plus/notepad-plus-plus/releases/download/v8.6.4/npp.8.6.4.Installer.exe",
            "CRU (Custom Resolution Utility)": "https://www.monitortests.com/download/CRU/CRU-1.5.2.zip",
            "DDU": "https://www.wagnardsoft.com/forums/viewtopic.php?f=5&t=3586",
            "Lightshot": "https://app.prntscr.com/build/setup-lightshot.exe",
            "Geek Uninstaller": "https://geekuninstaller.com/geek.zip",
            "7-Zip": "https://www.7-zip.org/a/7z2406-x64.exe",
            "WinRAR": "https://www.win-rar.com/fileadmin/winrar-versions/winrar/winrar-x64-624es.exe"
        }
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crear la interfaz del instalador"""
        # Configuración de estilo
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Helvetica', 14, 'bold'))
        style.configure('Section.TLabelframe.Label', font=('Helvetica', 10, 'bold'))
        
        # Título
        title = ttk.Label(self.frame, text="Instalador de Software", style='Title.TLabel')
        title.pack(pady=10)
        
        # Frame contenedor con scrollbar
        container = ttk.Frame(self.frame)
        container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Frame para navegadores
        browsers_frame = ttk.LabelFrame(scrollable_frame, text="Navegadores Web", padding="10", style='Section.TLabelframe')
        browsers_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Checkboxes para navegadores
        browsers = ["Google Chrome", "Brave", "Opera GX", "Opera", "Zen"]
        for browser in browsers:
            cb = ttk.Checkbutton(browsers_frame, text=browser, variable=self.selected_software[browser])
            cb.pack(anchor=tk.W, padx=5, pady=2)
        
        # Frame para utilidades del sistema
        system_frame = ttk.LabelFrame(scrollable_frame, text="Utilidades del Sistema", padding="10", style='Section.TLabelframe')
        system_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Checkboxes para utilidades del sistema
        system_apps = ["CPU-Z", "HWMonitor", "OpenShell", "DiskInfo", "Geek Uninstaller", "7-Zip", "WinRAR"]
        for app in system_apps:
            cb = ttk.Checkbutton(system_frame, text=app, variable=self.selected_software[app])
            cb.pack(anchor=tk.W, padx=5, pady=2)
        
        # Frame para herramientas avanzadas
        advanced_frame = ttk.LabelFrame(scrollable_frame, text="Herramientas Avanzadas", padding="10", style='Section.TLabelframe')
        advanced_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Checkboxes para herramientas avanzadas
        advanced_apps = ["Notepad++", "CRU (Custom Resolution Utility)", "DDU"]
        for app in advanced_apps:
            cb = ttk.Checkbutton(advanced_frame, text=app, variable=self.selected_software[app])
            cb.pack(anchor=tk.W, padx=5, pady=2)
        
        # Frame para otras aplicaciones
        other_frame = ttk.LabelFrame(scrollable_frame, text="Otras Aplicaciones", padding="10", style='Section.TLabelframe')
        other_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Checkboxes para otras aplicaciones
        other_apps = ["Discord", "Lightshot"]
        for app in other_apps:
            cb = ttk.Checkbutton(other_frame, text=app, variable=self.selected_software[app])
            cb.pack(anchor=tk.W, padx=5, pady=2)
        
        # Frame para botones
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(pady=10)
        
        # Botón de instalación
        install_btn = ttk.Button(btn_frame, text="Instalar Seleccionados", command=self.install_selected)
        install_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón para seleccionar todo
        select_all_btn = ttk.Button(btn_frame, text="Seleccionar Todo", command=self.select_all)
        select_all_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón para deseleccionar todo
        deselect_all_btn = ttk.Button(btn_frame, text="Deseleccionar Todo", command=self.deselect_all)
        deselect_all_btn.pack(side=tk.LEFT, padx=5)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(self.frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress.pack(pady=5)
        
        # Etiqueta de estado
        self.status_label = ttk.Label(self.frame, text="Seleccione los programas a instalar", wraplength=400)
        self.status_label.pack(pady=5)
    
    def select_all(self):
        """Seleccionar todos los programas"""
        for var in self.selected_software.values():
            var.set(True)
    
    def deselect_all(self):
        """Deseleccionar todos los programas"""
        for var in self.selected_software.values():
            var.set(False)
    
    def install_selected(self):
        """Instalar los programas seleccionados"""
        selected = [name for name, var in self.selected_software.items() if var.get()]
        
        if not selected:
            messagebox.showwarning("Advertencia", "No ha seleccionado ningún programa para instalar")
            return
        
        if not self.is_admin():
            if not messagebox.askyesno(
                "Permisos requeridos", 
                "Esta operación requiere privilegios de administrador. ¿Desea reiniciar la aplicación como administrador?"
            ):
                return
            
            self.run_as_admin()
            return
        
        total = len(selected)
        self.progress['maximum'] = total
        self.progress['value'] = 0
        
        installed = 0
        failed = []
        
        for i, software in enumerate(selected, 1):
            self.status_label.config(text=f"Instalando {software}... ({i}/{total})")
            self.frame.update()
            
            try:
                if self.install_software(software):
                    installed += 1
                else:
                    failed.append(software)
            except Exception as e:
                failed.append(software)
                print(f"Error instalando {software}: {str(e)}")
            
            self.progress['value'] = i
            self.frame.update()
        
        # Mostrar resumen
        message = f"Instalación completada:\n\nInstalados correctamente: {installed}"
        if failed:
            message += f"\n\nFallaron: {', '.join(failed)}"
        
        self.status_label.config(text="Instalación completada")
        messagebox.showinfo("Resultado", message)
    
    def install_software(self, software_name):
        """Instalar un software específico"""
        url = self.download_urls.get(software_name)
        if not url:
            messagebox.showerror("Error", f"No hay URL de descarga configurada para {software_name}")
            return False
        
        try:
            # Descargar el instalador
            self.status_label.config(text=f"Descargando {software_name}...")
            self.frame.update()
            
            temp_dir = tempfile.gettempdir()
            download_file = f"{software_name.replace(' ', '_')}_installer"
            
            # Determinar extensión del archivo
            if software_name in ["CRU (Custom Resolution Utility)", "Geek Uninstaller"]:
                download_file += ".zip"
            else:
                download_file += ".exe"
            
            installer_path = os.path.join(temp_dir, download_file)
            
            # Descargar el archivo
            urllib.request.urlretrieve(url, installer_path)
            
            # Ejecutar el instalador o extraer archivos
            self.status_label.config(text=f"Instalando {software_name}...")
            self.frame.update()
            
            # Manejo especial para CRU
            if software_name == "CRU (Custom Resolution Utility)":
                # Extraer el ZIP a una carpeta CRU en Program Files
                target_dir = os.path.join(os.environ['ProgramFiles'], 'CRU')
                os.makedirs(target_dir, exist_ok=True)
                
                with zipfile.ZipFile(installer_path, 'r') as zip_ref:
                    zip_ref.extractall(target_dir)
                
                # Crear un acceso directo en el escritorio si es posible
                try:
                    from win32com.client import Dispatch
                    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
                    shortcut_path = os.path.join(desktop, 'CRU.lnk')
                    
                    target = os.path.join(target_dir, 'CRU.exe')
                    shell = Dispatch('WScript.Shell')
                    shortcut = shell.CreateShortCut(shortcut_path)
                    shortcut.Targetpath = target
                    shortcut.WorkingDirectory = target_dir
                    shortcut.save()
                except:
                    pass
                
                os.remove(installer_path)
                return True
            
            # Manejar Geek Uninstaller (extraer ZIP)
            if software_name == "Geek Uninstaller":
                import zipfile
                with zipfile.ZipFile(installer_path, 'r') as zip_ref:
                    zip_ref.extractall(os.path.join(temp_dir, "GeekUninstaller"))
                os.remove(installer_path)
                return True
            
            # Comandos de instalación silenciosa para diferentes programas
            silent_switches = {
                "Google Chrome": "/silent /install",
                "Brave": "--silent --install",
                "Opera GX": "/silent /install",
                "Opera": "/silent /install",
                "Zen": "/S",
                "CPU-Z": "/VERYSILENT",
                "HWMonitor": "/VERYSILENT",
                "OpenShell": "/VERYSILENT",
                "DiskInfo": "/VERYSILENT",
                "Discord": "--silent",
                "Notepad++": "/S",
                "Lightshot": "/VERYSILENT",
                "7-Zip": "/S",
                "WinRAR": "/S"
            }
            
            # Comando de instalación
            cmd = f'"{installer_path}" {silent_switches.get(software_name, "")}'
            
            # Para WinRAR, añadir parámetro adicional para aceptar la licencia
            if software_name == "WinRAR":
                cmd += ' /D=C:\\Program Files\\WinRAR'
            
            result = subprocess.run(cmd, shell=True, check=True)
            
            # Limpiar instalador temporal
            if os.path.exists(installer_path):
                os.remove(installer_path)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error instalando {software_name}: {str(e)}")
            return False
    
    def is_admin(self):
        """Verificar si el programa se ejecuta como administrador"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def run_as_admin(self):
        """Reiniciar la aplicación como administrador"""
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()
        except:
            messagebox.showerror("Error", "No se pudo ejecutar como administrador")

# Ejemplo de cómo integrar en tu aplicación principal
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Instalador de Software")
    root.geometry("650x650")
    
    # Crear pestañas
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)
    
    # Pestaña de instalador
    installer_tab = ttk.Frame(notebook)
    notebook.add(installer_tab, text="Instalar Software")
    
    # Agregar el instalador
    installer = SoftwareInstaller(installer_tab)
    
    root.mainloop()