import customtkinter as ctk
from tkinter import messagebox
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
        self.frame = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="#18181b")
        self.frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Variables para almacenar las selecciones
        self.selected_software = {
            "Google Chrome": ctk.BooleanVar(),
            "Brave": ctk.BooleanVar(),
            "Opera GX": ctk.BooleanVar(),
            "Opera": ctk.BooleanVar(),
            "Zen": ctk.BooleanVar(),
            "CPU-Z": ctk.BooleanVar(),
            "HWMonitor": ctk.BooleanVar(),
            "OpenShell": ctk.BooleanVar(),
            "DiskInfo": ctk.BooleanVar(),
            "Discord": ctk.BooleanVar(),
            "Notepad++": ctk.BooleanVar(),
            "CRU (Custom Resolution Utility)": ctk.BooleanVar(),
            "DDU": ctk.BooleanVar(),
            "Lightshot": ctk.BooleanVar(),
            "Geek Uninstaller": ctk.BooleanVar(),
            "7-Zip": ctk.BooleanVar(),
            "WinRAR": ctk.BooleanVar()
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
        """Crear la interfaz moderna del instalador"""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Título
        title = ctk.CTkLabel(self.frame, text="Instalador de Software", font=("Segoe UI", 22, "bold"), text_color="#fafafa")
        title.pack(pady=10)

        # ScrollableFrame para la lista de categorías
        self.scrollable_frame = ctk.CTkScrollableFrame(self.frame, width=600, height=400, fg_color="#18181b")
        self.scrollable_frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Paneles expandibles (acordeón)
        self.category_panels = []
        self.create_category_panel("Navegadores Web", ["Google Chrome", "Brave", "Opera GX", "Opera", "Zen"])
        self.create_category_panel("Utilidades del Sistema", ["CPU-Z", "HWMonitor", "OpenShell", "DiskInfo", "Geek Uninstaller", "7-Zip", "WinRAR"])
        self.create_category_panel("Herramientas Avanzadas", ["Notepad++", "CRU (Custom Resolution Utility)", "DDU"])
        self.create_category_panel("Otras Aplicaciones", ["Discord", "Lightshot"])

        # Frame para botones
        btn_frame = ctk.CTkFrame(self.frame, fg_color="#232326")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Instalar Seleccionados", command=self.install_selected, fg_color="#3b82f6", hover_color="#6366f1", text_color="#fafafa").pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Seleccionar Todo", command=self.select_all, fg_color="#64748b", hover_color="#0ea5e9", text_color="#fafafa").pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Deseleccionar Todo", command=self.deselect_all, fg_color="#ef4444", hover_color="#dc2626", text_color="#fafafa").pack(side="left", padx=8)

        # Barra de progreso
        self.progress = ctk.CTkProgressBar(self.frame, width=400)
        self.progress.pack(pady=5)
        self.progress.set(0)

        # Etiqueta de estado
        self.status_label = ctk.CTkLabel(self.frame, text="Seleccione los programas a instalar", font=("Segoe UI", 13), text_color="#f59e42", wraplength=400)
        self.status_label.pack(pady=5)

    def create_category_panel(self, title, items):
        panel = ctk.CTkFrame(self.scrollable_frame, corner_radius=10, fg_color="#232326")
        panel.pack(fill="x", pady=6, padx=8)
        # Botón para expandir/colapsar
        expanded = ctk.BooleanVar(value=False)
        def toggle():
            if expanded.get():
                content_frame.pack_forget()
                expand_btn.configure(text=f"+ {title}")
                expanded.set(False)
            else:
                content_frame.pack(fill="x", padx=8, pady=4)
                expand_btn.configure(text=f"- {title}")
                expanded.set(True)
        expand_btn = ctk.CTkButton(panel, text=f"+ {title}", command=toggle, fg_color="#3b82f6", hover_color="#6366f1", text_color="#fafafa")
        expand_btn.pack(fill="x", pady=2)
        # Frame para los checkboxes
        content_frame = ctk.CTkFrame(panel, fg_color="#232326")
        for item in items:
            cb = ctk.CTkCheckBox(content_frame, text=item, variable=self.selected_software[item], fg_color="#27272a", text_color="#fafafa")
            cb.pack(anchor="w", padx=8, pady=2)
        self.category_panels.append(panel)
    
    def select_all(self):
        for var in self.selected_software.values():
            var.set(True)
    
    def deselect_all(self):
        for var in self.selected_software.values():
            var.set(False)
    
    def install_selected(self):
        selected = [name for name, var in self.selected_software.items() if var.get()]
        if not selected:
            messagebox.showwarning("Advertencia", "No ha seleccionado ningún programa para instalar")
            return
        if not self.is_admin():
            if not messagebox.askyesno(
                "Permisos requeridos", 
                "Esta operación requiere privilegios de administrador. ¿Desea reiniciar la aplicación como administrador?"):
                return
            self.run_as_admin()
            return
        total = len(selected)
        self.progress.configure(mode="determinate")
        self.progress.set(0)
        installed = 0
        failed = []
        for i, software in enumerate(selected, 1):
            self.status_label.configure(text=f"Instalando {software}... ({i}/{total})")
            self.frame.update()
            try:
                if self.install_software(software):
                    installed += 1
                else:
                    failed.append(software)
            except Exception as e:
                failed.append(software)
                print(f"Error instalando {software}: {str(e)}")
            self.progress.set(i/total)
            self.frame.update()
        message = f"Instalación completada:\n\nInstalados correctamente: {installed}"
        if failed:
            message += f"\n\nFallaron: {', '.join(failed)}"
        self.status_label.configure(text="Instalación completada")
        messagebox.showinfo("Resultado", message)
    
    def install_software(self, software_name):
        """Instalar un software específico con manejo de errores y certificados"""
        url = self.download_urls.get(software_name)
        if not url:
            messagebox.showerror("Error", f"No hay URL de descarga configurada para {software_name}")
            return False

        # Enlaces alternativos para DiskInfo
        alt_urls = {
            "DiskInfo": [
                "https://crystalmark.info/download/zip/CrystalDiskInfo8_17_14.zip",
                "https://crystalmark.info/download/zip/CrystalDiskInfoPortable.zip"
            ]
        }

        try:
            self.status_label.configure(text=f"Descargando {software_name}...")
            self.frame.update()
            temp_dir = tempfile.gettempdir()
            download_file = f"{software_name.replace(' ', '_')}_installer"
            # Determinar extensión del archivo
            if software_name in ["CRU (Custom Resolution Utility)", "Geek Uninstaller"]:
                download_file += ".zip"
            elif software_name == "DiskInfo" and url.endswith(".zip"):
                download_file += ".zip"
            else:
                download_file += ".exe"
            installer_path = os.path.join(temp_dir, download_file)

            # Descarga con manejo de certificados
            def try_download(url_to_try):
                try:
                    import certifi
                    urllib.request.urlretrieve(url_to_try, installer_path)
                    return True
                except Exception as e:
                    # Si es error de certificado, usar contexto SSL
                    try:
                        import ssl, certifi
                        ssl_context = ssl.create_default_context(cafile=certifi.where())
                        with urllib.request.urlopen(url_to_try, context=ssl_context) as response, open(installer_path, 'wb') as out_file:
                            out_file.write(response.read())
                        return True
                    except Exception as e2:
                        print(f"Error de descarga: {e2}")
                        return False

            downloaded = try_download(url)
            # Si DiskInfo falla, probar alternativos
            if not downloaded and software_name == "DiskInfo":
                for alt_url in alt_urls["DiskInfo"]:
                    if try_download(alt_url):
                        downloaded = True
                        break
            if not downloaded:
                messagebox.showerror("Error", f"No se pudo descargar {software_name}. Revisa tu conexión o intenta más tarde.")
                return False

            self.status_label.configure(text=f"Instalando {software_name}...")
            self.frame.update()

            # Manejo especial para CRU y DiskInfo ZIP
            if software_name == "CRU (Custom Resolution Utility)":
                target_dir = os.path.join(os.environ['ProgramFiles'], 'CRU')
                os.makedirs(target_dir, exist_ok=True)
                with zipfile.ZipFile(installer_path, 'r') as zip_ref:
                    zip_ref.extractall(target_dir)
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
            if software_name == "Geek Uninstaller":
                import zipfile
                with zipfile.ZipFile(installer_path, 'r') as zip_ref:
                    zip_ref.extractall(os.path.join(temp_dir, "GeekUninstaller"))
                os.remove(installer_path)
                return True
            if software_name == "DiskInfo" and installer_path.endswith(".zip"):
                # Extraer el ZIP a Program Files\CrystalDiskInfo
                target_dir = os.path.join(os.environ['ProgramFiles'], 'CrystalDiskInfo')
                os.makedirs(target_dir, exist_ok=True)
                with zipfile.ZipFile(installer_path, 'r') as zip_ref:
                    zip_ref.extractall(target_dir)
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
            cmd = f'"{installer_path}" {silent_switches.get(software_name, "")}'
            if software_name == "WinRAR":
                cmd += ' /D=C:\\Program Files\\WinRAR'
            try:
                result = subprocess.run(cmd, shell=True, check=True)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo instalar {software_name}. Error: {str(e)}")
                return False
            if os.path.exists(installer_path):
                os.remove(installer_path)
            return result.returncode == 0
        except Exception as e:
            print(f"Error instalando {software_name}: {str(e)}")
            messagebox.showerror("Error", f"No se pudo instalar {software_name}. Error: {str(e)}")
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
    app = ctk.CTk()
    app.title("Instalador de Software")
    app.geometry("700x700")
    installer = SoftwareInstaller(app)
    app.mainloop()