import platform
import psutil
import cpuinfo
import socket
import uuid
import re
import tkinter as tk
from tkinter import ttk, scrolledtext
import wmi
import screeninfo
import datetime

# Importación opcional de GPUtil
try:
    import GPUtil
    GPUTIL_AVAILABLE = True
except ImportError:
    GPUTIL_AVAILABLE = False
    print("GPUtil no está disponible - continuando sin información de GPU detallada")

class SystemInfoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Información Detallada del Sistema")
        self.root.geometry("1000x700")
        
        # Configurar estilo
        self.setup_styles()
        
        # Crear interfaz
        self.setup_ui()
        
        # Cargar datos del sistema
        self.load_system_info()

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
        self.style.configure('TNotebook', background='#f0f0f0')
        self.style.configure('TNotebook.Tab', font=('Segoe UI', 9, 'bold'), padding=[10, 5])

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="Información del Sistema", style='Title.TLabel').pack(side=tk.LEFT)
        
        # Botón de actualización
        ttk.Button(title_frame, text="Actualizar", command=self.load_system_info).pack(side=tk.RIGHT)
        
        # Notebook (pestañas)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Crear pestañas simplificadas
        self.create_cpu_tab()
        self.create_ram_tab()
        self.create_disk_tab()
        self.create_motherboard_tab()
        
        # Barra de estado
        self.status_var = tk.StringVar()
        self.status_var.set(f"Última actualización: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(5, 0))

    def create_cpu_tab(self):
        """Crea la pestaña de información de la CPU"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Procesador")
        
        text = scrolledtext.ScrolledText(tab, wrap=tk.WORD, font=('Consolas', 10))
        text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.cpu_text = text

    def create_ram_tab(self):
        """Crea la pestaña de información de la RAM"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Memoria RAM")
        
        text = scrolledtext.ScrolledText(tab, wrap=tk.WORD, font=('Consolas', 10))
        text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.ram_text = text

    def create_disk_tab(self):
        """Crea la pestaña de información de discos"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Discos")
        
        text = scrolledtext.ScrolledText(tab, wrap=tk.WORD, font=('Consolas', 10))
        text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.disk_text = text

    def create_motherboard_tab(self):
        """Crea la pestaña de información de la placa madre"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Placa Madre")
        
        text = scrolledtext.ScrolledText(tab, wrap=tk.WORD, font=('Consolas', 10))
        text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.motherboard_text = text

    def load_system_info(self):
        """Carga toda la información del sistema"""
        try:
            # Limpiar pestañas
            for text in [self.cpu_text, self.ram_text, self.disk_text, self.motherboard_text]:
                text.delete(1.0, tk.END)
            
            # Obtener información del sistema
            self.get_cpu_info()
            self.get_ram_info()
            self.get_disk_info()
            self.get_motherboard_info()
            
            self.status_var.set(f"Última actualización: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            self.status_var.set(f"Error al cargar información: {str(e)}")

    def get_cpu_info(self):
        """Obtiene información resumida de la CPU"""
        info = "=== PROCESADOR ===\n\n"
        
        try:
            # Información básica con cpuinfo
            cpu_info = cpuinfo.get_cpu_info()
            info += f"Modelo: {cpu_info.get('brand_raw', 'Desconocido')}\n"
            info += f"Núcleos: {psutil.cpu_count(logical=False)} físicos / {psutil.cpu_count(logical=True)} lógicos\n"
            info += f"Frecuencia: {psutil.cpu_freq().current:.0f} MHz (Max: {psutil.cpu_freq().max:.0f} MHz)\n"
            info += f"Uso actual: {psutil.cpu_percent(interval=1)}%\n"
            
            # Caché principal
            if 'l3_cache_size' in cpu_info:
                info += f"L3 Cache: {cpu_info['l3_cache_size']}\n"
            elif 'l2_cache_size' in cpu_info:
                info += f"L2 Cache: {cpu_info['l2_cache_size']}\n"
                
        except Exception as e:
            info += f"Error al obtener información del procesador: {str(e)}\n"
        
        self.cpu_text.insert(tk.END, info)

    def get_ram_info(self):
        """Obtiene información resumida de la memoria RAM"""
        info = "=== MEMORIA RAM ===\n\n"
        
        try:
            # Memoria física
            mem = psutil.virtual_memory()
            info += f"Total: {self.format_bytes(mem.total)}\n"
            info += f"En uso: {self.format_bytes(mem.used)} ({mem.percent:.1f}%)\n"
            info += f"Disponible: {self.format_bytes(mem.available)}\n\n"
            
            # Módulos de memoria (resumido)
            try:
                c = wmi.WMI()
                info += "=== MÓDULOS INSTALADOS ===\n"
                total_modules = 0
                for mem_module in c.Win32_PhysicalMemory():
                    total_modules += 1
                    info += f"Slot {total_modules}: {self.format_bytes(int(mem_module.Capacity))} "
                    if mem_module.Speed:
                        info += f"@ {mem_module.Speed} MHz\n"
                    else:
                        info += "\n"
            except Exception:
                info += "No se pudo obtener información de módulos\n"
                
        except Exception as e:
            info += f"Error al obtener información de memoria: {str(e)}\n"
        
        self.ram_text.insert(tk.END, info)

    def get_disk_info(self):
        """Obtiene información resumida de los discos"""
        info = "=== DISCOS ===\n\n"
        
        try:
            # Particiones principales
            info += "=== PARTICIONES ===\n"
            for part in psutil.disk_partitions():
                if 'cdrom' not in part.opts and part.fstype:
                    try:
                        usage = psutil.disk_usage(part.mountpoint)
                        info += f"{part.device} ({part.fstype})\n"
                        info += f"  Total: {self.format_bytes(usage.total)}\n"
                        info += f"  Usado: {self.format_bytes(usage.used)} ({usage.percent:.1f}%)\n"
                        info += f"  Libre: {self.format_bytes(usage.free)}\n\n"
                    except Exception:
                        continue
            
            # Discos físicos (resumido)
            try:
                c = wmi.WMI()
                info += "=== DISCOS FÍSICOS ===\n"
                for disk in c.Win32_DiskDrive():
                    if disk.Size:
                        info += f"{disk.Model}\n"
                        info += f"  Tamaño: {self.format_bytes(int(disk.Size))}\n"
                        info += f"  Interface: {disk.InterfaceType or 'Desconocida'}\n\n"
            except Exception:
                info += "No se pudo obtener información de discos físicos\n"
                
        except Exception as e:
            info += f"Error al obtener información de discos: {str(e)}\n"
        
        self.disk_text.insert(tk.END, info)

    def get_motherboard_info(self):
        """Obtiene información resumida de la placa madre"""
        info = "=== PLACA MADRE ===\n\n"
        
        try:
            c = wmi.WMI()
            
            # Información de la placa base
            for board in c.Win32_BaseBoard():
                info += f"Fabricante: {board.Manufacturer or 'Desconocido'}\n"
                info += f"Modelo: {board.Product or 'Desconocido'}\n"
                if board.SerialNumber:
                    info += f"Serial: {board.SerialNumber}\n"
                break
            
            info += "\n=== BIOS ===\n"
            for bios in c.Win32_BIOS():
                info += f"Fabricante: {bios.Manufacturer or 'Desconocido'}\n"
                info += f"Versión: {bios.Version or 'Desconocida'}\n"
                if bios.ReleaseDate:
                    try:
                        date_str = bios.ReleaseDate[:8]
                        formatted_date = f"{date_str[6:8]}/{date_str[4:6]}/{date_str[:4]}"
                        info += f"Fecha: {formatted_date}\n"
                    except:
                        info += f"Fecha: {bios.ReleaseDate}\n"
                break
            
            info += "\n=== SISTEMA OPERATIVO ===\n"
            for os in c.Win32_OperatingSystem():
                info += f"SO: {os.Caption or 'Desconocido'}\n"
                info += f"Arquitectura: {platform.architecture()[0]}\n"
                if os.LastBootUpTime:
                    try:
                        boot_time = os.LastBootUpTime[:14]
                        formatted_boot = f"{boot_time[6:8]}/{boot_time[4:6]}/{boot_time[:4]} {boot_time[8:10]}:{boot_time[10:12]}"
                        info += f"Último arranque: {formatted_boot}\n"
                    except:
                        info += f"Último arranque: {os.LastBootUpTime}\n"
                break
                
        except Exception as e:
            info += f"Error al obtener información de la placa madre: {str(e)}\n"
        
        self.motherboard_text.insert(tk.END, info)

    def format_bytes(self, size):
        """Formatea bytes a una representación legible"""
        power = 2**10
        n = 0
        power_labels = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
        while size > power and n < len(power_labels)-1:
            size /= power
            n += 1
        return f"{size:.2f} {power_labels[n]}"

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemInfoApp(root)
    root.mainloop()