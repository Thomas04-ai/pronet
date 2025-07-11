import customtkinter as ctk
from tkinter import messagebox
import subprocess
import winreg
import ctypes
import sys
import time

def run_as_admin():
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def restore_classic_menu():
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32")
        winreg.SetValueEx(key, None, 0, winreg.REG_SZ, "")
        winreg.CloseKey(key)
        print("[LOG] Menú clásico restaurado.")
        return True
    except Exception as e:
        print(f"[ERROR] Menú clásico: {e}")
        return False

def disable_animations():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "UserPreferencesMask", 0, winreg.REG_BINARY, b'\x90\x1E\x27\x80\x78\x12\x00\x00')
        winreg.SetValueEx(key, "MenuShowDelay", 0, winreg.REG_SZ, "10")
        winreg.CloseKey(key)
        key2 = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key2, "TaskbarAnimations", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key2)
        print("[LOG] Animaciones deshabilitadas.")
        return True
    except Exception as e:
        print(f"[ERROR] Animaciones: {e}")
        return False

def enable_dark_mode():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, 0)
        winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        print("[LOG] Dark Mode activado.")
        return True
    except Exception as e:
        print(f"[ERROR] Dark Mode: {e}")
        return False

def disable_transparency():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "EnableTransparency", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        key2 = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\DWM", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key2, "EnableTransparency", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key2)
        print("[LOG] Transparencias eliminadas.")
        return True
    except Exception as e:
        print(f"[ERROR] Transparencias: {e}")
        return False

def restart_explorer():
    try:
        subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], shell=True)
        time.sleep(2)
        # Reiniciar explorer usando powershell para asegurar que la barra de tareas vuelva
        subprocess.run(["powershell", "-Command", "Start-Process explorer.exe"], shell=True)
        print("[LOG] Explorer reiniciado.")
        return True
    except Exception as e:
        print(f"[ERROR] Explorer: {e}")
        return False

class VisualTweaksApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Visual Tweaks - Windows 11 Ultimate")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.geometry("420x420")
        self.configure(bg="#18181b")  # Fondo oscuro tipo Vercel
        self.setup_ui()

    def setup_ui(self):
        frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#232326")
        frame.pack(fill="both", expand=True, padx=24, pady=24)

        ctk.CTkLabel(frame, text="Visual Tweaks", font=("Segoe UI", 22, "bold"), text_color="#fafafa").pack(pady=(12, 6))
        ctk.CTkLabel(frame, text="Optimiza la apariencia y animaciones de Windows.", font=("Segoe UI", 14), text_color="#a1a1aa").pack(pady=(0, 18))

        ctk.CTkButton(frame, text="Restaurar Menú Clásico W10", command=self.restore_menu, fg_color="#27272a", hover_color="#3b82f6", text_color="#fafafa").pack(fill="x", pady=7)
        ctk.CTkButton(frame, text="Deshabilitar Animaciones", command=self.disable_animations, fg_color="#27272a", hover_color="#6366f1", text_color="#fafafa").pack(fill="x", pady=7)
        ctk.CTkButton(frame, text="Activar Dark Mode", command=self.enable_dark_mode, fg_color="#27272a", hover_color="#0ea5e9", text_color="#fafafa").pack(fill="x", pady=7)
        ctk.CTkButton(frame, text="Eliminar Transparencias", command=self.disable_transparency, fg_color="#27272a", hover_color="#64748b", text_color="#fafafa").pack(fill="x", pady=7)
        ctk.CTkButton(frame, text="Reiniciar Explorer", command=self.restart_explorer, fg_color="#27272a", hover_color="#f59e42", text_color="#fafafa").pack(fill="x", pady=7)

    def restore_menu(self):
        ok = restore_classic_menu()
        messagebox.showinfo("Menú Clásico", "Restaurado correctamente." if ok else "Error al restaurar.")

    def disable_animations(self):
        ok = disable_animations()
        messagebox.showinfo("Animaciones", "Animaciones deshabilitadas." if ok else "Error al deshabilitar.")

    def enable_dark_mode(self):
        ok = enable_dark_mode()
        messagebox.showinfo("Dark Mode", "Dark Mode activado." if ok else "Error al activar.")

    def disable_transparency(self):
        ok = disable_transparency()
        messagebox.showinfo("Transparencias", "Transparencias eliminadas." if ok else "Error al eliminar.")

    def restart_explorer(self):
        ok = restart_explorer()
        messagebox.showinfo("Explorer", "Explorer reiniciado." if ok else "Error al reiniciar.")

if __name__ == "__main__":
    run_as_admin()
    app = VisualTweaksApp()
    app.mainloop()
