import customtkinter as ctk
from tkinter import messagebox
import winreg

SPLIT_KEY = r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"
SPLIT_VALUE = "SvcHostSplitThresholdInKB"

RAM_OPTIONS = [
    (4, 4 * 1024 * 1024),
    (6, 6 * 1024 * 1024),
    (8, 8 * 1024 * 1024),
    (12, 12 * 1024 * 1024),
    (16, 16 * 1024 * 1024),
    (32, 32 * 1024 * 1024)
]

class GamingTweaksApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gaming Tweaks - SvcHostSplitThreshold")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.geometry("420x320")
        self.configure(bg="#18181b")
        self.current_value = self.get_current_value()
        self.setup_ui()

    def setup_ui(self):
        frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#232326")
        frame.pack(fill="both", expand=True, padx=24, pady=24)

        ctk.CTkLabel(frame, text="Miscellaneous", font=("Segoe UI", 20, "bold"), text_color="#fafafa").pack(pady=(12, 6))
        ctk.CTkLabel(frame, text="SvcHostSplitThreshold", font=("Segoe UI", 14), text_color="#a1a1aa").pack(pady=(0, 18))

        self.selected_label = ctk.CTkLabel(frame, text="Actual: ...", font=("Segoe UI", 14), text_color="#fafafa")
        self.selected_label.pack(pady=(0, 12))
        self.update_selected_label()

        btn_frame = ctk.CTkFrame(frame, fg_color="#232326")
        btn_frame.pack(pady=6)

        # Distribuir los botones en dos filas de 3
        ram_buttons = []
        for i, (ram, kb) in enumerate(RAM_OPTIONS):
            btn = ctk.CTkButton(btn_frame, text=f"{ram}GB RAM", command=lambda kb=kb: self.set_split_value(kb), fg_color="#27272a", hover_color="#3b82f6", text_color="#fafafa", width=80)
            ram_buttons.append(btn)

        for i, btn in enumerate(ram_buttons):
            row = i // 3
            col = i % 3
            btn.grid(row=row, column=col, padx=4, pady=4, sticky="ew")
        btn_frame.grid_columnconfigure((0,1,2), weight=1)

        ctk.CTkButton(frame, text="Revert", command=self.revert_value, fg_color="#27272a", hover_color="#64748b", text_color="#fafafa").pack(pady=14)

    def get_current_value(self):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, SPLIT_KEY) as key:
                value, _ = winreg.QueryValueEx(key, SPLIT_VALUE)
                return value
        except Exception:
            return None

    def set_split_value(self, kb):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, SPLIT_KEY, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, SPLIT_VALUE, 0, winreg.REG_DWORD, kb)
            messagebox.showinfo("SvcHostSplitThreshold", f"Valor cambiado a {kb // 1024 // 1024}GB RAM.")
            print(f"[LOG] SvcHostSplitThreshold cambiado a {kb} KB.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cambiar el valor: {e}")
            print(f"[ERROR] {e}")
        self.current_value = self.get_current_value()
        self.update_selected_label()

    def revert_value(self):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, SPLIT_KEY, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, SPLIT_VALUE)
            messagebox.showinfo("SvcHostSplitThreshold", "Valor revertido a predeterminado.")
            print("[LOG] SvcHostSplitThreshold revertido.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo revertir: {e}")
            print(f"[ERROR] {e}")
        self.current_value = self.get_current_value()
        self.update_selected_label()

    def update_selected_label(self):
        if self.current_value:
            gb = self.current_value // 1024 // 1024
            self.selected_label.configure(text=f"Actual: {gb}GB RAM")
        else:
            self.selected_label.configure(text="Actual: predeterminado/no configurado")

if __name__ == "__main__":
    import ctypes
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    app = GamingTweaksApp()
    app.mainloop()
