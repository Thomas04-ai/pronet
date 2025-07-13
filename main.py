import os
import sys
import ctypes
import customtkinter as ctk
from PIL import Image

# Configuración inicial de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ToolCard(ctk.CTkFrame):
    def __init__(self, master=None, title=None, description=None, command=None, **kwargs):
        super().__init__(master=master, **kwargs)
        self.configure(fg_color="#232326", corner_radius=10)
        
        # Contenedor principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Título
        title_label = ctk.CTkLabel(
            content,
            text=title,
            font=("Segoe UI", 16, "bold"),
            text_color="#fafafa"
        )
        title_label.pack(anchor="w", pady=(0, 5))
        
        # Descripción
        desc_label = ctk.CTkLabel(
            content,
            text=description,
            font=("Segoe UI", 12),
            text_color="#a0a0a0",
            wraplength=300
        )
        desc_label.pack(anchor="w", pady=(0, 10))
        
        # Botón
        button = ctk.CTkButton(
            content,
            text="Ejecutar",
            command=command,
            font=("Segoe UI", 12),
            fg_color="#89B4FA",
            hover_color="#74C7EC"
        )
        button.pack(anchor="w")

class CategoryTab(ctk.CTkScrollableFrame):
    def __init__(self, category, tools, **kwargs):
        super().__init__(**kwargs)
        self.configure(fg_color="transparent")
        
        # Título de la categoría
        title = ctk.CTkLabel(
            self,
            text=category,
            font=("Segoe UI", 24, "bold"),
            text_color="#fafafa"
        )
        title.pack(anchor="w", pady=(0, 20))
        
        # Grid para las herramientas
        for tool in tools:
            card = ToolCard(
                master=self,
                title=tool['name'],
                description=tool['description'],
                command=tool['action'],
                height=140
            )
            card.pack(fill="x", pady=(0, 10), padx=5)

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana
        self.title("Windows Ultimate Toolkit")
        self.geometry("1000x700")
        self.minsize(800, 600)
        self.configure(fg_color="#18181b")
        
        if not self.is_admin():
            self.request_admin()
        
        # Frame principal
        main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#232326")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Pestañas
        self.tabs = ctk.CTkTabview(
            main_frame,
            fg_color="#18181b",
            segmented_button_fg_color="#232326",
            segmented_button_selected_color="#89B4FA",
            segmented_button_selected_hover_color="#74C7EC"
        )
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)
        
        categories = [
            {
                'name': 'Limpieza',
                'tools': [
                    {
                        'name': 'Limpiador de Disco',
                        'description': 'Elimina archivos temporales y libera espacio en disco',
                        'action': lambda: self.run_tool('cleanup.py')
                    },
                    {
                        'name': 'Limpiar DNS',
                        'description': 'Limpia la caché DNS del sistema',
                        'action': lambda: self.run_tool('cleanup.py dns')
                    },
                    {
                        'name': 'Archivos Temporales',
                        'description': 'Elimina archivos temporales del sistema',
                        'action': lambda: self.run_tool('cleanup.py temp')
                    }
                ]
            },
            {
                'name': 'Rendimiento',
                'tools': [
                    {
                        'name': 'Optimizar Internet',
                        'description': 'Ajusta parámetros de red para mejor rendimiento',
                        'action': lambda: self.run_tool('internet.py')
                    },
                    {
                        'name': 'Administrar Prioridades',
                        'description': 'Cambia la prioridad de procesos en ejecución',
                        'action': lambda: self.run_tool('prioridad.py')
                    },
                    {
                        'name': 'Afinidad de CPU',
                        'description': 'Controla qué núcleos del CPU usan los procesos',
                        'action': lambda: self.run_tool('cpuaffinity.py')
                    },
                    {
                        'name': 'Tweaks para Gaming',
                        'description': 'Ajustes avanzados para mejorar el rendimiento en juegos',
                        'action': lambda: self.run_tool('gamingTweaks.py')
                    }
                ]
            },
            {
                'name': 'Sistema',
                'tools': [
                    {
                        'name': 'Información del Sistema',
                        'description': 'Muestra detalles detallados del hardware',
                        'action': lambda: self.run_tool('infosystem.py')
                    },
                    {
                        'name': 'Administrar Servicios',
                        'description': 'Controla los servicios de Windows',
                        'action': lambda: self.run_tool('services.py')
                    },
                    {
                        'name': 'Gestor de Inicio',
                        'description': 'Administra programas que se inician con Windows',
                        'action': lambda: self.run_tool('inicio.py')
                    },
                    {
                        'name': 'Planes de Energía',
                        'description': 'Administra y optimiza los planes de energía',
                        'action': lambda: self.run_tool('powerplan.py')
                    }
                ]
            },
            {
                'name': 'Personalización',
                'tools': [
                    {
                        'name': 'Tweaks Visuales',
                        'description': 'Personaliza la apariencia de Windows',
                        'action': lambda: self.run_tool('visuales.py')
                    },
                    {
                        'name': 'Instalar Software',
                        'description': 'Instala programas útiles con un clic',
                        'action': lambda: self.run_tool('instalar_app.py')
                    },
                    {
                        'name': 'Gestor de Drivers',
                        'description': 'Descarga e instala drivers fácilmente',
                        'action': lambda: self.run_tool('drivers.py')
                    }
                ]
            }
        ]
        
        # Crear pestañas
        for category in categories:
            tab = self.tabs.add(category['name'])  # Cambiado de add_tab a add
            tab_content = CategoryTab(
                master=tab,
                category=category['name'],
                tools=category['tools'],
                fg_color="transparent"
            )
            tab_content.pack(fill="both", expand=True)
        
        # Barra de estado
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Bienvenido a Windows Ultimate Toolkit",
            font=("Segoe UI", 12),
            text_color="#a0a0a0"
        )
        self.status_label.pack(pady=(5, 10))
    
    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def request_admin(self):
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit()
        except:
            self.status_text = "Error: Se requieren privilegios de administrador"
    
    def run_tool(self, tool_name):
        """Método mejorado para ejecutar herramientas"""
        try:
            script_path = os.path.join(os.path.dirname(__file__), tool_name.split()[0])
            
            if not os.path.exists(script_path):
                self.status_label.configure(text=f"Error: No se encontró {tool_name}")
                return

            if sys.platform == 'win32':
                params = tool_name.split()[1:] if len(tool_name.split()) > 1 else []
                ctypes.windll.shell32.ShellExecuteW(
                    None,
                    "open",
                    sys.executable,
                    f'"{script_path}" ' + " ".join(params),
                    None,
                    1
                )
            else:
                os.system(f'python3 "{script_path}"')
                
            self.status_label.configure(text=f"Ejecutando {tool_name}...")
            
        except Exception as e:
            self.status_label.configure(text=f"Error al ejecutar {tool_name}: {str(e)}")

if __name__ == '__main__':
    try:
        app = MainApp()
        app.mainloop()
    except Exception as e:
        print(f"Error fatal: {str(e)}")
        input("Presiona Enter para salir...")