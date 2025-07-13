import platform
import psutil
import cpuinfo
import wmi
import customtkinter as ctk
import datetime

# Importación opcional de GPUtil
try:
    import GPUtil
    GPUTIL_AVAILABLE = True
except ImportError:
    GPUTIL_AVAILABLE = False
    print("GPUtil no está disponible - continuando sin información de GPU detallada")

class SystemInfoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Información Detallada del Sistema")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.configure(bg="#18181b")
        self.setup_ui()
        self.load_system_info()

    # ...existing code...

    def setup_ui(self):
        main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#18181b")
        main_frame.pack(fill="both", expand=True, padx=24, pady=24)

        title = ctk.CTkLabel(main_frame, text="Información Detallada del Sistema", font=("Segoe UI", 22, "bold"), text_color="#fafafa")
        title.pack(pady=10)

        btn_frame = ctk.CTkFrame(main_frame, fg_color="#232326")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Actualizar", command=self.load_system_info, fg_color="#3b82f6", hover_color="#6366f1", text_color="#fafafa").pack(side="left", padx=8)

        self.tabview = ctk.CTkTabview(main_frame, width=700, height=400, fg_color="#18181b")
        self.tabview.pack(fill="both", expand=True, padx=8, pady=8)

        self.cpu_tab = self.tabview.add("Procesador")
        self.ram_tab = self.tabview.add("Memoria RAM")
        self.disk_tab = self.tabview.add("Discos")
        self.motherboard_tab = self.tabview.add("Placa Madre")

        self.cpu_text = ctk.CTkTextbox(self.cpu_tab, font=("Consolas", 12), fg_color="#232326", text_color="#fafafa", wrap="word")
        self.cpu_text.pack(fill="both", expand=True, padx=8, pady=8)
        self.ram_text = ctk.CTkTextbox(self.ram_tab, font=("Consolas", 12), fg_color="#232326", text_color="#fafafa", wrap="word")
        self.ram_text.pack(fill="both", expand=True, padx=8, pady=8)
        self.disk_text = ctk.CTkTextbox(self.disk_tab, font=("Consolas", 12), fg_color="#232326", text_color="#fafafa", wrap="word")
        self.disk_text.pack(fill="both", expand=True, padx=8, pady=8)
        self.motherboard_text = ctk.CTkTextbox(self.motherboard_tab, font=("Consolas", 12), fg_color="#232326", text_color="#fafafa", wrap="word")
        self.motherboard_text.pack(fill="both", expand=True, padx=8, pady=8)

        self.status_var = ctk.StringVar(value=f"Última actualización: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        status_bar = ctk.CTkLabel(main_frame, textvariable=self.status_var, font=("Segoe UI", 13), text_color="#f59e42", anchor="w")
        status_bar.pack(fill="x", pady=(5, 0))


    def load_system_info(self):
        """Carga toda la información del sistema"""
        try:
            # Limpiar pestañas (CTkTextbox)
            for text in [self.cpu_text, self.ram_text, self.disk_text, self.motherboard_text]:
                text.delete('0.0', 'end')
            # Obtener información del sistema
            self.get_cpu_info()
            self.get_ram_info()
            self.get_disk_info()
            self.get_motherboard_info()
            self.status_var.set(f"Última actualización: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            self.status_var.set(f"Error al cargar información: {str(e)}")

    def get_cpu_info(self):
        """Obtiene información esencial de la CPU"""
        info = "=== PROCESADOR ===\n\n"
        try:
            cpu_info = cpuinfo.get_cpu_info()
            info += f"Modelo: {cpu_info.get('brand_raw', 'Desconocido')}\n"
            info += f"Núcleos físicos: {psutil.cpu_count(logical=False)}\n"
            info += f"Núcleos lógicos: {psutil.cpu_count(logical=True)}\n"
            info += f"Frecuencia actual: {psutil.cpu_freq().current:.0f} MHz\n"
        except Exception as e:
            info += f"Error: {str(e)}\n"
        self.cpu_text.insert('end', info)

    def get_ram_info(self):
        """Obtiene información esencial de la memoria RAM"""
        info = "=== MEMORIA RAM ===\n\n"
        try:
            mem = psutil.virtual_memory()
            info += f"Total: {self.format_bytes(mem.total)}\n"
            info += f"En uso: {self.format_bytes(mem.used)} ({mem.percent:.1f}%)\n"
            info += f"Disponible: {self.format_bytes(mem.available)}\n"
        except Exception as e:
            info += f"Error: {str(e)}\n"
        self.ram_text.insert('end', info)

    def get_disk_info(self):
        """Obtiene información esencial de los discos"""
        info = "=== DISCOS ===\n\n"
        try:
            for part in psutil.disk_partitions():
                if 'cdrom' not in part.opts and part.fstype:
                    try:
                        usage = psutil.disk_usage(part.mountpoint)
                        info += f"{part.device}: {self.format_bytes(usage.total)} total, {self.format_bytes(usage.used)} usados ({usage.percent:.1f}%)\n"
                    except Exception:
                        continue
        except Exception as e:
            info += f"Error: {str(e)}\n"
        self.disk_text.insert('end', info)

    def get_motherboard_info(self):
        """Obtiene información esencial de la placa madre"""
        info = "=== PLACA MADRE ===\n\n"
        try:
            c = wmi.WMI()
            for board in c.Win32_BaseBoard():
                info += f"Fabricante: {board.Manufacturer or 'Desconocido'}\n"
                info += f"Modelo: {board.Product or 'Desconocido'}\n"
                break
        except Exception as e:
            info += f"Error: {str(e)}\n"
        self.motherboard_text.insert('end', info)

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
    app = SystemInfoApp()
    app.mainloop()