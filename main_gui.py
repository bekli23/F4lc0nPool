import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import subprocess
import os
import signal
import json
import webbrowser
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
import psutil

CONFIG_FILE = "config.py"
API_FILE = "api.txt"
SUMMARY_FILE = "client_sync_summary.txt"
POOL_URL = "http://84.46.242.149/"
TELEGRAM_URL = "https://t.me/f4lc0npool"
APP_VERSION = "F4lc0nPool 2.0"

class GPUScannerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("F4lc0nPool - GPU Bitcoin Puzzle Hunting")
        self.master.geometry("1200x800")
        self.process = None
        self.speed_log = []
        self.max_points = 50

        self.build_gui()
        self.load_config()
        self.load_api_key()
        self.update_gpu_info_loop()

    def build_gui(self):
        title_frame = tk.Frame(self.master)
        title_frame.pack(pady=5, fill="x")
        tk.Label(title_frame, text="F4lc0nPool - GPU Bitcoin Puzzle Hunting", font=("Arial", 18, "bold"), fg="darkblue").pack()

        top_frame = tk.Frame(self.master)
        top_frame.pack(fill="x", padx=10)

        self.frame_config = tk.LabelFrame(top_frame, text="Configuration", padx=10, pady=10)
        self.frame_config.pack(side=tk.LEFT, fill="both", expand=True)
        self.entries = {}
        self.create_config_fields()

        tk.Label(self.frame_config, text="API Key:").grid(row=7, column=0, sticky='e', padx=5, pady=2)
        self.api_entry = tk.Entry(self.frame_config, width=50)
        self.api_entry.grid(row=7, column=1, padx=5, pady=2)
        tk.Button(self.frame_config, text="💾 Save Config", command=self.save_config).grid(row=8, column=1, pady=10)

        tk.Label(self.frame_config, text="🔗 Register API", fg="blue", cursor="hand2", font=("Arial", 10, "underline")).grid(row=9, column=1)
        self.frame_config.grid_slaves(row=9, column=1)[0].bind("<Button-1>", lambda e: webbrowser.open(POOL_URL))

        self.stats_frame = tk.LabelFrame(top_frame, text="Live GPU Info & Speed", padx=10, pady=10)
        self.stats_frame.pack(side=tk.RIGHT, fill="both", expand=True, padx=10)
        self.gpu_info_label = tk.Label(self.stats_frame, text="GPU Info: Loading...", justify="left", anchor="w")
        self.gpu_info_label.pack(anchor="w")
        self.speed_label = tk.Label(self.stats_frame, text="Speed: -- Mk/s", font=("Arial", 12, "bold"))
        self.speed_label.pack(anchor="w", pady=5)

        self.figure, self.ax = plt.subplots(figsize=(5, 2.5))
        self.line, = self.ax.plot([], [], marker='o')
        self.ax.set_title("Speed (Mk/s) over Time")
        self.ax.set_ylabel("Mk/s")
        self.ax.set_xlabel("Checkpoints")
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.stats_frame)
        self.canvas.get_tk_widget().pack()

        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=5)

        self.start_btn = tk.Button(button_frame, text="▶ Start Scan", font=("Arial", 12), width=15, command=self.start_scan)
        self.start_btn.pack(side=tk.LEFT, padx=10)

        self.stop_btn = tk.Button(button_frame, text="⏹ Stop Scan", font=("Arial", 12), width=15, state=tk.DISABLED, command=self.stop_scan)
        self.stop_btn.pack(side=tk.LEFT, padx=10)

        self.quit_btn = tk.Button(button_frame, text="❌ Quit App", font=("Arial", 12), width=15, command=self.quit_app)
        self.quit_btn.pack(side=tk.LEFT, padx=10)

        self.output_area = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, font=("Courier", 10), height=18)
        self.output_area.pack(expand=True, fill='both', padx=10, pady=10)

        bottom = tk.Label(
            self.master,
            text=f"{APP_VERSION}   |   Telegram: {TELEGRAM_URL}   |   Website: {POOL_URL}",
            font=("Arial", 10),
            fg="gray"
        )
        bottom.pack(pady=3)

    def create_config_fields(self):
        labels = [
            ("Address", "address"),
            ("Range Start", "range_start"),
            ("Range End", "range_end"),
            ("Range Bits", "range_bits"),
            ("GPU IDs (comma-separated)", "gpu_ids"),
            ("GPU Threads", "gpu_threads"),
            ("CPU Threads", "cpu_threads"),
            ("Mode", "mode"),
            ("Coin", "coin"),
            ("Backup Every", "backup_every"),
            ("Log File", "log_file"),
            ("Output File", "output_file"),
            ("Usage File", "usage_file"),
            ("Scan File", "scan_file")
        ]
        for idx, (label, key) in enumerate(labels):
            row = idx % 7
            col = 0 if idx < 7 else 2
            tk.Label(self.frame_config, text=label).grid(row=row, column=col, sticky='e', padx=5, pady=2)
            entry = tk.Entry(self.frame_config, width=40)
            entry.grid(row=row, column=col+1, padx=5, pady=2)
            self.entries[key] = entry

    def load_config(self):
        try:
            namespace = {}
            if not os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "w") as f:
                    f.write("CONFIG = {}\n")
            with open(CONFIG_FILE) as f:
                exec(f.read(), namespace)
            config = namespace.get("CONFIG", {})
            for key, entry in self.entries.items():
                value = config.get(key, "")
                if isinstance(value, list):
                    value = ",".join(str(v) for v in value)
                entry.delete(0, tk.END)
                entry.insert(0, str(value))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config: {e}")

    def load_api_key(self):
        if not os.path.exists(API_FILE) or os.stat(API_FILE).st_size == 0:
            with open(API_FILE, "w", encoding="utf-8") as f:
                f.write("Enter your API key generated from the pool website.\n")
        with open(API_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            self.api_entry.delete(0, tk.END)
            self.api_entry.insert(0, content)

    def save_api_key(self):
        with open(API_FILE, "w", encoding="utf-8") as f:
            f.write(self.api_entry.get().strip() + "\n")

    def save_config(self):
        try:
            config = {}
            for key, entry in self.entries.items():
                value = entry.get().strip()
                if key == "gpu_ids":
                    value = [int(v) for v in value.split(",") if v.strip().isdigit()]
                elif key in ["range_bits", "cpu_threads", "backup_every"]:
                    value = int(value)
                config[key] = value
            with open(CONFIG_FILE, "w") as f:
                f.write(f"CONFIG = {json.dumps(config, indent=4)}\n")
            self.save_api_key()
            messagebox.showinfo("Saved", "Configuration and API key saved.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")

    def start_scan(self):
        self.output_area.delete('1.0', tk.END)
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        threading.Thread(target=self.run_main_script, daemon=True).start()

    def stop_scan(self):
        if self.process and self.process.poll() is None:
            try:
                proc = psutil.Process(self.process.pid)
                for child in proc.children(recursive=True):
                    child.terminate()
                proc.terminate()
                self.append_output("\n[STOPPED] Scan process terminated.\n")
            except Exception as e:
                messagebox.showerror("Error", f"Could not stop process: {e}")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def run_main_script(self):
        try:
            self.process = subprocess.Popen(
                ["python", "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            for line in self.process.stdout:
                self.append_output(line)
                self.extract_speed(line)
            self.process.wait()
        except Exception as e:
            self.append_output(f"\n[ERROR] {e}\n")
        finally:
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

    def extract_speed(self, line):
        if "Mk/s" in line:
            try:
                value = float(line.split("Mk/s")[0].split()[-1])
                self.speed_log.append(value)
                self.speed_label.config(text=f"Speed: {value} Mk/s")
                if len(self.speed_log) > self.max_points:
                    self.speed_log = self.speed_log[-self.max_points:]
                self.update_chart()
            except:
                pass

    def update_chart(self):
        self.line.set_data(range(len(self.speed_log)), self.speed_log)
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, max(self.speed_log + [10]))
        self.canvas.draw()

    def update_gpu_info_loop(self):
        if os.path.exists(SUMMARY_FILE):
            try:
                with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                    speed_match = re.search(r"\[GPU:\s*([\d.]+)\s*Mk/s\]", content)
                    if speed_match:
                        speed = float(speed_match.group(1))
                        self.speed_label.config(text=f"Speed: {speed} Mk/s")
                        self.speed_log.append(speed)
                        if len(self.speed_log) > self.max_points:
                            self.speed_log = self.speed_log[-self.max_points:]
                        self.update_chart()

                    gpu_info_match = re.search(r"GPU Info:\s*(.*?)\nGPU Count", content, re.DOTALL)
                    if gpu_info_match:
                        info = gpu_info_match.group(1).strip()
                        self.gpu_info_label.config(text=f"GPU Info:\n{info}")
            except Exception as e:
                print("Error reading summary:", e)

        if self.master.winfo_exists():
            self.master.after(3000, self.update_gpu_info_loop)

    def quit_app(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit the application?"):
            self.stop_scan()
            self.master.destroy()

    def append_output(self, text):
        self.output_area.insert(tk.END, text)
        self.output_area.see(tk.END)

if __name__ == '__main__':
    root = tk.Tk()
    gui = GPUScannerGUI(root)
    root.mainloop()
