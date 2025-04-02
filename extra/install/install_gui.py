import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading
import sys
import importlib.util
import platform

# Raw imports from your script
raw_modules = [
    "tkinter", "messagebox", "scrolledtext", "threading", "subprocess", "os", "signal", "json",
    "webbrowser", "time", "matplotlib.pyplot", "matplotlib.backends.backend_tkagg.FigureCanvasTkAgg",
    "re", "psutil", "random", "os.path", "shlex", "colorama", "config", "range_usage", "logger",
    "client", "send", "datetime", "socket", "hashlib"
]

# Mapping to actual pip-installable package names
module_to_pip = {
    "matplotlib.pyplot": "matplotlib",
    "matplotlib.backends.backend_tkagg.FigureCanvasTkAgg": "matplotlib",
    "colorama": "colorama",
    "psutil": "psutil",
}

# Filter modules that are actually installable via pip
installable_modules = set()
for m in raw_modules:
    pip_name = module_to_pip.get(m, None)
    if pip_name:
        installable_modules.add(pip_name)

# De-duplicate and sort for display
REQUIRED_MODULES = sorted(list(installable_modules))

class InstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python 3 Module Installer")
        self.root.geometry("720x500")

        python_version = platform.python_version()
        self.label = tk.Label(root, text=f"Detected Python version: v{python_version}", font=("Arial", 12))
        self.label.pack(pady=5)

        self.module_label = tk.Label(root, text="Modules to be installed:", font=("Arial", 10, "bold"))
        self.module_label.pack()

        self.module_list = tk.Label(root, text=", ".join(REQUIRED_MODULES), fg="blue", wraplength=700, justify="left")
        self.module_list.pack(pady=2)

        self.install_button = tk.Button(root, text="Install All Modules", command=self.install_modules)
        self.install_button.pack(pady=5)

        self.output_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=20)
        self.output_area.pack(padx=10, pady=10)

    def detect_python_command(self):
        """Tries to detect which Python command works with pip."""
        commands = [["python3", "-m", "pip"], ["python", "-m", "pip"], ["py", "-m", "pip"]]
        for cmd in commands:
            try:
                subprocess.check_output(cmd + ["--version"])
                return cmd
            except Exception:
                continue
        return None

    def install_modules(self):
        threading.Thread(target=self._install_modules_thread, daemon=True).start()

    def _install_modules_thread(self):
        pip_cmd = self.detect_python_command()

        if pip_cmd is None:
            self.log("[ERROR] Could not detect a working pip command. Make sure Python and pip are properly installed.")
            return

        for module in REQUIRED_MODULES:
            self.log(f"[INFO] Checking module '{module}'...")
            if self.is_module_installed(module):
                self.log(f"[OK] Module '{module}' is already installed.")
                continue

            try:
                subprocess.check_call(pip_cmd + ["install", module])
                self.log(f"[SUCCESS] Module '{module}' has been installed.")
            except subprocess.CalledProcessError as e:
                self.log(f"[ERROR] Failed to install '{module}': {e}")
            except Exception as e:
                self.log(f"[EXCEPTION] Unexpected error with '{module}': {e}")

        # Special note about tkinter
        self.log(f"\n[INFO] Checking for tkinter support...")
        if self.is_module_installed("tkinter"):
            self.log("[OK] tkinter is available (usually built-in).")
        else:
            self.log("[WARNING] tkinter is not available. You may need to reinstall Python with Tcl/Tk support enabled.")

        self.log("\n✔️ Installation process completed.")

    def is_module_installed(self, module_name):
        try:
            spec = importlib.util.find_spec(module_name)
            return spec is not None
        except Exception:
            return False

    def log(self, message):
        self.output_area.insert(tk.END, message + "\n")
        self.output_area.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = InstallerGUI(root)
    root.mainloop()
