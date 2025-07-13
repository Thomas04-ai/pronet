import customtkinter as ctk
from tkinter import messagebox
import winreg
import subprocess
import json
import os
import ctypes
import sys

class InternetOptimizerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Optimizador de Internet")
        self.geometry("540x360")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.configure(bg="#18181b")
        self.backup_file = "internet_settings_backup.json"
        # Verificar permisos de administrador
        if not self.is_admin():
            self.run_as_admin()
            sys.exit()
        self.create_widgets()
    
    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def run_as_admin(self):
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    
    def create_widgets(self):
        main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#18181b")
        main_frame.pack(fill="both", expand=True, padx=24, pady=24)

        title_label = ctk.CTkLabel(main_frame, text="Optimizador de Conexión a Internet", font=("Segoe UI", 22, "bold"), text_color="#fafafa")
        title_label.pack(pady=10)

        desc_label = ctk.CTkLabel(main_frame, text="Esta herramienta optimiza la configuración de red para mejorar el rendimiento", font=("Segoe UI", 13), text_color="#f59e42", wraplength=420)
        desc_label.pack(pady=10)

        btn_frame = ctk.CTkFrame(main_frame, fg_color="#232326")
        btn_frame.pack(pady=16)
        self.optimize_btn = ctk.CTkButton(btn_frame, text="Optimizar Internet", command=self.optimize_internet, fg_color="#3b82f6", hover_color="#6366f1", text_color="#fafafa")
        self.optimize_btn.pack(side="left", padx=10)
        self.revert_btn = ctk.CTkButton(btn_frame, text="Revertir Cambios", command=self.revert_changes, fg_color="#64748b", hover_color="#0ea5e9", text_color="#fafafa")
        self.revert_btn.pack(side="left", padx=10)

        self.status_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#232326")
        self.status_frame.pack(fill="both", expand=True, pady=10)
        self.status_label = ctk.CTkLabel(self.status_frame, text="Preparado para optimizar", font=("Consolas", 12), text_color="#fafafa", anchor="w")
        self.status_label.pack(fill="x", padx=8, pady=8)

        self.check_backup()
    
    def check_backup(self):
        """Verificar si existe configuración previa"""
        if os.path.exists(self.backup_file):
            self.status_label.configure(text="ADVERTENCIA: Hay cambios previos. Revierta antes de optimizar nuevamente.")
            self.optimize_btn.configure(state="disabled")
        else:
            self.status_label.configure(text="Listo para optimizar la conexión")
            self.optimize_btn.configure(state="normal")
    
    def optimize_internet(self):
        """Aplicar optimizaciones"""
        try:
            self.create_backup()
            optimizations = [
                ("Configurando MTU", lambda: self.set_mtu(1500)),
                ("Optimizando parámetros TCP", lambda: self.set_tcp_global_parameters(
                    EnableCongestionAvoidance=1,
                    EnableECN=0,
                    EnableRSS=1,
                    EnableWindowAutoTuning=1,
                    Tcp1323Opts=1
                )),
                ("Limpiando DNS", self.flush_dns),
                ("Optimizando parámetros avanzados", lambda: self.set_tcp_parameters(
                    TcpAckFrequency=1,
                    TcpDelAckTicks=0,
                    SackOpts=1
                )),
                ("Desactivando algoritmo de Nagle", self.disable_nagle_algorithm)
            ]
            for desc, func in optimizations:
                self.status_label.configure(text=desc + "...")
                self.update()  # Actualizar la interfaz
                func()
                self.after(500)  # Pequeña pausa para que se vea el progreso
            self.status_label.configure(text="¡Optimización completada con éxito!")
            messagebox.showinfo("Éxito", "Optimizaciones aplicadas correctamente.\nAlgunos cambios requieren reinicio.")
            self.check_backup()
        except Exception as e:
            self.status_label.configure(text="Error durante la optimización")
            messagebox.showerror("Error", f"No se pudo completar la optimización:\n{str(e)}")
    
    def revert_changes(self):
        """Revertir a la configuración anterior"""
        try:
            if not os.path.exists(self.backup_file):
                messagebox.showwarning("Advertencia", "No hay configuración previa guardada")
                return
            with open(self.backup_file, 'r') as f:
                backup_data = json.load(f)
            reversions = [
                ("Restaurando MTU", lambda: self.set_mtu(backup_data.get('MTU', 1500))),
                ("Restaurando parámetros TCP", lambda: self.set_tcp_global_parameters(
                    **backup_data.get('TCPGlobalParams', {}))),
                ("Restaurando parámetros avanzados", lambda: self.set_tcp_parameters(
                    **backup_data.get('TCPParams', {})))
            ]
            for desc, func in reversions:
                self.status_label.configure(text=desc + "...")
                self.update()  # Actualizar la interfaz
                func()
                self.after(500)  # Pequeña pausa
            os.remove(self.backup_file)
            self.status_label.configure(text="Configuración revertida correctamente")
            messagebox.showinfo("Éxito", "Todos los cambios han sido revertidos")
            self.check_backup()
        except Exception as e:
            self.status_label.configure(text="Error al revertir cambios")
            messagebox.showerror("Error", f"No se pudieron revertir los cambios:\n{str(e)}")
    
    # ===== Métodos técnicos (iguales a la versión anterior) =====
    
    def create_backup(self):
        backup_data = {
            'MTU': self.get_current_mtu(),
            'TCPGlobalParams': self.get_tcp_global_parameters(),
            'TCPParams': self.get_tcp_parameters()
        }
        with open(self.backup_file, 'w') as f:
            json.dump(backup_data, f, indent=4)
    
    def set_mtu(self, mtu_value):
        try:
            result = subprocess.run(['netsh', 'interface', 'ipv4', 'show', 'interfaces'], 
                                  capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            for line in result.stdout.split('\n'):
                if "connected" in line.lower():
                    parts = line.split()
                    if len(parts) > 0 and parts[0].isdigit():
                        interface_idx = parts[0]
                        subprocess.run(['netsh', 'interface', 'ipv4', 'set', 'interface', 
                                      interface_idx, f'mtu={mtu_value}'], 
                                     check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            raise Exception(f"Error al configurar MTU: {str(e)}")
    
    def get_current_mtu(self):
        try:
            result = subprocess.run(['netsh', 'interface', 'ipv4', 'show', 'interfaces'], 
                                  capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            for line in result.stdout.split('\n'):
                if "mtu" in line.lower():
                    return int(line.split('MTU:')[1].split()[0])
            return 1500
        except:
            return 1500
    
    def set_tcp_global_parameters(self, **params):
        try:
            key_path = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE) as key:
                for name, value in params.items():
                    if value is not None:  # Solo escribir valores no nulos
                        winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
        except Exception as e:
            raise Exception(f"Error al configurar parámetros TCP globales: {str(e)}")
    
    def get_tcp_global_parameters(self):
        params = {}
        key_path = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
        
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                for name in ['EnableCongestionAvoidance', 'EnableECN', 'EnableRSS', 
                           'EnableWindowAutoTuning', 'Tcp1323Opts']:
                    try:
                        value, _ = winreg.QueryValueEx(key, name)
                        params[name] = value
                    except:
                        params[name] = None
        except:
            pass
        
        return params
    
    # ...existing code...
    
    def flush_dns(self):
        try:
            subprocess.run(['ipconfig', '/flushdns'], 
                         check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            raise Exception(f"Error al limpiar caché DNS: {str(e)}")
    
    def set_tcp_parameters(self, **params):
        try:
            key_path = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as interfaces_key:
                for i in range(winreg.QueryInfoKey(interfaces_key)[0]):
                    interface_name = winreg.EnumKey(interfaces_key, i)
                    with winreg.OpenKey(interfaces_key, interface_name, 0, winreg.KEY_WRITE) as interface_key:
                        for name, value in params.items():
                            if value is not None:  # Solo escribir valores no nulos
                                winreg.SetValueEx(interface_key, name, 0, winreg.REG_DWORD, value)
        except Exception as e:
            raise Exception(f"Error al configurar parámetros TCP: {str(e)}")
    
    def get_tcp_parameters(self):
        params = {}
        key_path = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
        
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as interfaces_key:
                first_interface = winreg.EnumKey(interfaces_key, 0)
                with winreg.OpenKey(interfaces_key, first_interface) as interface_key:
                    for name in ['TcpAckFrequency', 'TcpDelAckTicks', 'SackOpts']:
                        try:
                            value, _ = winreg.QueryValueEx(interface_key, name)
                            params[name] = value
                        except:
                            params[name] = None
        except:
            pass
        
        return params
    
    def disable_nagle_algorithm(self):
        try:
            key_path = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as interfaces_key:
                for i in range(winreg.QueryInfoKey(interfaces_key)[0]):
                    interface_name = winreg.EnumKey(interfaces_key, i)
                    with winreg.OpenKey(interfaces_key, interface_name, 0, winreg.KEY_WRITE) as interface_key:
                        winreg.SetValueEx(interface_key, 'TcpNoDelay', 0, winreg.REG_DWORD, 1)
        except Exception as e:
            raise Exception(f"Error al desactivar Nagle's Algorithm: {str(e)}")

if __name__ == "__main__":
    try:
        app = InternetOptimizerGUI()
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Error fatal", f"La aplicación falló:\n{str(e)}")