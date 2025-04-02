import subprocess
import sys
import importlib.util
import platform

# Module list based on your full script
raw_modules = [
    "tkinter", "messagebox", "scrolledtext", "threading", "subprocess", "os", "signal", "json",
    "webbrowser", "time", "matplotlib.pyplot", "matplotlib.backends.backend_tkagg.FigureCanvasTkAgg",
    "re", "psutil", "random", "os.path", "shlex", "colorama", "config", "range_usage", "logger",
    "client", "send", "datetime", "socket", "hashlib"
]

# Map custom/import submodules to pip-installable packages
module_to_pip = {
    "matplotlib.pyplot": "matplotlib",
    "matplotlib.backends.backend_tkagg.FigureCanvasTkAgg": "matplotlib",
    "colorama": "colorama",
    "psutil": "psutil",
}

# Filter and prepare list for installation
installable_modules = set()
for m in raw_modules:
    pip_name = module_to_pip.get(m, None)
    if pip_name:
        installable_modules.add(pip_name)

REQUIRED_MODULES = sorted(list(installable_modules))

def detect_python_pip():
    commands = [["python3", "-m", "pip"], ["python", "-m", "pip"], ["py", "-m", "pip"]]
    for cmd in commands:
        try:
            subprocess.check_output(cmd + ["--version"], stderr=subprocess.DEVNULL)
            return cmd
        except Exception:
            continue
    return None

def is_module_installed(module_name):
    try:
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    except Exception:
        return False

def install_modules():
    pip_cmd = detect_python_pip()
    if pip_cmd is None:
        print("[ERROR] Could not detect a working pip command. Make sure Python and pip are installed.")
        return

    print(f"Using pip command: {' '.join(pip_cmd)}")
    print("Starting module installation...\n")

    for module in REQUIRED_MODULES:
        print(f"[INFO] Checking module '{module}'...")
        if is_module_installed(module):
            print(f"[OK] '{module}' is already installed.")
            continue
        try:
            subprocess.check_call(pip_cmd + ["install", module])
            print(f"[SUCCESS] Installed '{module}'.")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to install '{module}': {e}")
        except Exception as e:
            print(f"[EXCEPTION] Unexpected error installing '{module}': {e}")

    print("\n[INFO] Checking tkinter (built-in)...")
    if is_module_installed("tkinter"):
        print("[OK] tkinter is available.")
    else:
        print("[WARNING] tkinter is missing. Reinstall Python with Tcl/Tk support.")

    print("\n✅ All done.")

if __name__ == "__main__":
    print(f"Python version detected: {platform.python_version()}")
    install_modules()
