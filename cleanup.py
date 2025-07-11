import customtkinter as ctk
from tkinter import messagebox
import os
import shutil
import subprocess
import ctypes
import sys
import tempfile

def run_as_admin():
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

# Disk Cleanup (calls Windows built-in tool)
def disk_cleanup():
    print("[LOG] Ejecutando Disk Cleanup...")
    try:
        subprocess.run(["cleanmgr", "/sagerun:1"])
        print("[LOG] Disk Cleanup finalizado.")
        return True
    except Exception as e:
        print(f"[ERROR] Disk Cleanup: {e}")
        return False

# DNS Cache Cleanup
def dns_cache_cleanup():
    print("[LOG] Limpiando DNS Cache...")
    try:
        subprocess.run(["ipconfig", "/flushdns"], shell=True)
        print("[LOG] DNS Cache limpiada.")
        return True
    except Exception as e:
        print(f"[ERROR] DNS Cache: {e}")
        return False

# Internet Cookies Cleanup
def cookies_cleanup():
    user_profile = os.environ.get("USERPROFILE")
    cookies_path = os.path.join(user_profile, r"AppData\Roaming\Microsoft\Windows\Cookies")
    print(f"[LOG] Eliminando cookies en: {cookies_path}")
    try:
        if os.path.exists(cookies_path):
            shutil.rmtree(cookies_path, ignore_errors=True)
            print("[LOG] Cookies eliminadas.")
        else:
            print("[LOG] No se encontraron cookies para eliminar.")
        return True
    except Exception as e:
        print(f"[ERROR] Cookies: {e}")
        return False

# Temporary Internet Files Cleanup
def temp_internet_files_cleanup():
    user_profile = os.environ.get("USERPROFILE")
    temp_inet_path = os.path.join(user_profile, r"AppData\Local\Microsoft\Windows\INetCache")
    print(f"[LOG] Eliminando archivos temporales de Internet en: {temp_inet_path}")
    try:
        if os.path.exists(temp_inet_path):
            shutil.rmtree(temp_inet_path, ignore_errors=True)
            print("[LOG] Archivos temporales de Internet eliminados.")
        else:
            print("[LOG] No se encontraron archivos temporales de Internet para eliminar.")
        return True
    except Exception as e:
        print(f"[ERROR] Temp Internet Files: {e}")
        return False

# Temporary Files Cleanup
def temp_files_cleanup():
    temp_path = tempfile.gettempdir()
    print(f"[LOG] Eliminando archivos temporales en: {temp_path}")
    try:
        for filename in os.listdir(temp_path):
            file_path = os.path.join(temp_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    print(f"[LOG] Archivo eliminado: {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"[LOG] Carpeta eliminada: {file_path}")
            except Exception as e:
                print(f"[ERROR] No se pudo eliminar {file_path}: {e}")
        print("[LOG] Archivos temporales eliminados.")
        return True
    except Exception as e:
        print(f"[ERROR] Temp Files: {e}")
        return False

class CleanupApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Herramientas de Limpieza de Windows")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.geometry("420x400")
        self.configure(bg="#18181b")
        self.setup_ui()

    def setup_ui(self):
        frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#232326")
        frame.pack(fill="both", expand=True, padx=24, pady=24)

        ctk.CTkLabel(frame, text="Seleccione la acción de limpieza:", font=("Segoe UI", 20, "bold"), text_color="#fafafa").pack(pady=(12, 6))

        ctk.CTkButton(frame, text="Disk Cleanup", command=self.disk_cleanup, fg_color="#27272a", hover_color="#3b82f6", text_color="#fafafa").pack(fill="x", pady=7)
        ctk.CTkButton(frame, text="DNS Cache", command=self.dns_cache_cleanup, fg_color="#27272a", hover_color="#6366f1", text_color="#fafafa").pack(fill="x", pady=7)
        ctk.CTkButton(frame, text="Internet Cookies", command=self.cookies_cleanup, fg_color="#27272a", hover_color="#0ea5e9", text_color="#fafafa").pack(fill="x", pady=7)
        ctk.CTkButton(frame, text="Temporary Internet Files", command=self.temp_internet_files_cleanup, fg_color="#27272a", hover_color="#64748b", text_color="#fafafa").pack(fill="x", pady=7)
        ctk.CTkButton(frame, text="Temporary Files", command=self.temp_files_cleanup, fg_color="#27272a", hover_color="#f59e42", text_color="#fafafa").pack(fill="x", pady=7)

    def disk_cleanup(self):
        if messagebox.askyesno("Disk Cleanup", "¿Desea ejecutar la limpieza de disco? Puede tardar unos minutos."):
            ok = disk_cleanup()
            messagebox.showinfo("Disk Cleanup", "Completado." if ok else "Error al ejecutar.")

    def dns_cache_cleanup(self):
        ok = dns_cache_cleanup()
        messagebox.showinfo("DNS Cache", "Caché DNS limpiada." if ok else "Error al limpiar.")

    def cookies_cleanup(self):
        ok = cookies_cleanup()
        messagebox.showinfo("Internet Cookies", "Cookies eliminadas." if ok else "Error al eliminar cookies.")

    def temp_internet_files_cleanup(self):
        ok = temp_internet_files_cleanup()
        messagebox.showinfo("Temporary Internet Files", "Archivos temporales de Internet eliminados." if ok else "Error al eliminar.")

    def temp_files_cleanup(self):
        ok = temp_files_cleanup()
        messagebox.showinfo("Temporary Files", "Archivos temporales eliminados." if ok else "Error al eliminar.")

if __name__ == "__main__":
    run_as_admin()
    app = CleanupApp()
    app.mainloop()
