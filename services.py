import win32serviceutil
import win32service
import tkinter as tk
from tkinter import ttk, messagebox

class ServiceManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Optimizador de Servicios Windows")
        
        # Frame principal
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview para mostrar servicios
        self.tree = ttk.Treeview(self.main_frame, columns=('Name', 'Status', 'Startup'), show='headings')
        self.tree.heading('Name', text='Nombre del Servicio')
        self.tree.heading('Status', text='Estado')
        self.tree.heading('Startup', text='Inicio')
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Frame de botones
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=10)
        
        # Botones
        self.start_btn = ttk.Button(self.button_frame, text="Iniciar", command=self.start_service)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(self.button_frame, text="Detener", command=self.stop_service)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.disable_btn = ttk.Button(self.button_frame, text="Desactivar", command=self.disable_service)
        self.disable_btn.pack(side=tk.LEFT, padx=5)
        
        self.enable_btn = ttk.Button(self.button_frame, text="Habilitar", command=self.enable_service)
        self.enable_btn.pack(side=tk.LEFT, padx=5)
        
        self.optimize_btn = ttk.Button(self.button_frame, text="Optimizar Servicios", command=self.optimize_services)
        self.optimize_btn.pack(side=tk.RIGHT, padx=5)
        
        # Cargar servicios
        self.load_services()
    
    def load_services(self):
        """Cargar la lista de servicios en el Treeview"""
        self.tree.delete(*self.tree.get_children())
        
        # Obtener todos los servicios
        hscm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ENUMERATE_SERVICE)
        try:
            services = win32service.EnumServicesStatus(hscm)
        finally:
            win32service.CloseServiceHandle(hscm)
        
        for service in services:
            name, display_name, status = service
            status_text = "Running" if status[1] == win32service.SERVICE_RUNNING else "Stopped"
            
            try:
                startup_type = win32service.QueryServiceConfig(name)[0]
            except:
                startup_type = win32service.SERVICE_DEMAND_START  # Default fallback
            
            # Traducir tipo de inicio
            if startup_type == win32service.SERVICE_AUTO_START:
                startup_text = "Automático"
            elif startup_type == win32service.SERVICE_DEMAND_START:
                startup_text = "Manual"
            else:
                startup_text = "Deshabilitado"
            
            self.tree.insert('', tk.END, values=(display_name, status_text, startup_text), tags=(name,))
    
    def get_selected_service(self):
        """Obtener el servicio seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un servicio")
            return None
        return self.tree.item(selected[0], "tags")[0]
    
    def start_service(self):
        """Iniciar el servicio seleccionado"""
        service = self.get_selected_service()
        if service:
            try:
                win32serviceutil.StartService(service)
                messagebox.showinfo("Éxito", f"Servicio {service} iniciado correctamente")
                self.load_services()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo iniciar el servicio: {str(e)}")
    
    def stop_service(self):
        """Detener el servicio seleccionado"""
        service = self.get_selected_service()
        if service:
            try:
                win32serviceutil.StopService(service)
                messagebox.showinfo("Éxito", f"Servicio {service} detenido correctamente")
                self.load_services()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo detener el servicio: {str(e)}")
    
    def disable_service(self):
        """Deshabilitar el servicio seleccionado"""
        service = self.get_selected_service()
        if service:
            try:
                win32serviceutil.ChangeServiceConfig(service, startType=win32service.SERVICE_DISABLED)
                messagebox.showinfo("Éxito", f"Servicio {service} deshabilitado correctamente")
                self.load_services()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo deshabilitar el servicio: {str(e)}")
    
    def enable_service(self):
        """Habilitar el servicio seleccionado (modo manual)"""
        service = self.get_selected_service()
        if service:
            try:
                win32serviceutil.ChangeServiceConfig(service, startType=win32service.SERVICE_DEMAND_START)
                messagebox.showinfo("Éxito", f"Servicio {service} habilitado (modo manual)")
                self.load_services()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo habilitar el servicio: {str(e)}")
    
    def optimize_services(self):
        """Optimizar servicios según recomendaciones"""
        # Lista de servicios que generalmente se pueden deshabilitar sin problemas
        safe_to_disable = [
            "Fax", "XboxNetApiSvc", "XblAuthManager", "XblGameSave",
            "MapsBroker", "lfsvc", "TrkWks", "WMPNetworkSvc",
            "RemoteRegistry", "SSDPSRV", "upnphost", "WerSvc"
        ]
        
        # Lista de servicios que deberían estar habilitados para funcionalidad básica
        should_be_enabled = [
            "Dnscache", "Dhcp", "EventLog", "PlugPlay",
            "RpcSs", "Winmgmt", "LanmanWorkstation"
        ]
        
        disabled_count = 0
        enabled_count = 0
        
        try:
            # Deshabilitar servicios innecesarios
            for service in safe_to_disable:
                try:
                    current_status = win32service.QueryServiceConfig(service)[0]
                    if current_status != win32service.SERVICE_DISABLED:
                        win32serviceutil.ChangeServiceConfig(service, startType=win32service.SERVICE_DISABLED)
                        disabled_count += 1
                except:
                    continue
            
            # Asegurar que servicios esenciales estén habilitados
            for service in should_be_enabled:
                try:
                    current_status = win32service.QueryServiceConfig(service)[0]
                    if current_status == win32service.SERVICE_DISABLED:
                        win32serviceutil.ChangeServiceConfig(service, startType=win32service.SERVICE_AUTO_START)
                        enabled_count += 1
                except:
                    continue
            
            messagebox.showinfo("Optimización completada", 
                               f"Se deshabilitaron {disabled_count} servicios innecesarios\n"
                               f"Se habilitaron {enabled_count} servicios esenciales")
            self.load_services()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error durante la optimización: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ServiceManagerApp(root)
    root.geometry("800x600")
    root.mainloop()