import subprocess
import random
import os
import re
import threading
import time
from colorama import init as colorama_init, Fore, Style
from config import CONFIG
from range_usage import load_range_usage, save_range_usage
from logger import write_log, backup_file
from client import authenticate_with_server, save_client_state
from send import send_stats_to_mysql

colorama_init()

if not authenticate_with_server():
    print("[EXITING] Authentication failed or server unreachable.")
    exit(1)

print("[OK] Authenticated. Starting scan...")

main_path = os.path.dirname(os.path.abspath(__file__))
keyhunt_exe = os.path.join(main_path, "./KeyHunt")
log_file = os.path.join(main_path, CONFIG["log_file"])
usage_file = os.path.join(main_path, CONFIG["usage_file"])
scan_file = os.path.join(main_path, CONFIG["scan_file"])
found_file1 = os.path.join(main_path, CONFIG["output_file"])
found_file2 = os.path.join(main_path, "Found.txt")
checked_file = os.path.join(main_path, f"checked_random_range_{CONFIG['range_bits']}bit.txt")
range_log_file = os.path.join(main_path, "range_log.txt")
gpu_info_file = os.path.join(main_path, "gpu.txt")

address = CONFIG["address"]
a_int = int(CONFIG["range_start"], 16)
b_int = int(CONFIG["range_end"], 16)
step = 2 ** CONFIG["range_bits"]

range_usage_data = load_range_usage(usage_file)
range_usage_data[CONFIG["range_bits"]] = range_usage_data.get(CONFIG["range_bits"], 0)

quantity = 0
if os.path.exists(scan_file):
    with open(scan_file, "r") as f:
        try:
            quantity = int(f.read().strip())
        except:
            quantity = 0

if not os.path.exists(checked_file):
    open(checked_file, 'w').close()

with open(checked_file, 'r', encoding='utf-8') as f:
    db_ranges = {line.strip(): True for line in f if line.strip()}

API_KEY = ""
if os.path.exists("api.txt"):
    with open("api.txt", "r") as f:
        API_KEY = f.read().strip()

def sync_loop():
    while True:
        save_client_state()
        send_stats_to_mysql()
        time.sleep(60)

threading.Thread(target=sync_loop, daemon=True).start()

while True:
    quantity += 1
    with open(scan_file, "w") as f:
        f.write(str(quantity))

    if os.path.exists(found_file1) or os.path.exists(found_file2):
        print(f'{Fore.GREEN}\n[OK] FOUND! Exiting script.{Style.RESET_ALL}')
        print("[SYNC] Saving final state and syncing to server...")
        save_client_state()
        send_stats_to_mysql()
        break

    while True:
        start = random.randint(a_int, b_int - step)
        end = start + step
        range_key = f"{start}:{end}"
        if range_key not in db_ranges:
            break

    start_hex = hex(start)[2:].zfill(17)
    end_hex = hex(end)[2:].zfill(17)
    print(f"\n[SCAN] #{quantity} | Range {start_hex} : {end_hex}")

    try:
        with open(range_log_file, "a", encoding="utf-8") as rf:
            rf.write(f"{start_hex} : {end_hex}\n")
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Failed to write range to range_log.txt: {e}{Style.RESET_ALL}")

    gpu_speed_info = ""
    gpu_info_collected = []

    gpu_id_str = ",".join(str(gid) for gid in CONFIG["gpu_ids"])
    gpu_grid_str = ",".join(CONFIG["gpu_grids"])

    command = [
        keyhunt_exe,
        "-t", str(CONFIG["cpu_threads"]),
        "-g", "--gpui", gpu_id_str,
        "--gpux", gpu_grid_str,
        "-m", CONFIG["mode"],
        "--coin", CONFIG["coin"],
        "-o", found_file1,
        "--range", f"{start_hex}:{end_hex}",
        address
    ]

    print(f"[CMD] Running on GPUs {gpu_id_str}:\n{Fore.CYAN}{' '.join(command)}{Style.RESET_ALL}\n")

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line.strip())

            match_speed = re.search(r"([\d\.]+)\s+Mk/s", line)
            if match_speed:
                gpu_speed_info = f"[GPU: {match_speed.group(1)} Mk/s]"

            match_gpu = re.search(r"GPU\s*:\s*GPU\s*#(\d+)\s+(.*)", line)
            if match_gpu:
                gpu_id = match_gpu.group(1)
                gpu_name = match_gpu.group(2).strip()
                gpu_info_collected.append(f"#{gpu_id} {gpu_name}")

        process.wait()
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Exception while running KeyHunt: {e}{Style.RESET_ALL}")

    if gpu_info_collected:
        with open(gpu_info_file, "w", encoding="utf-8") as gf:
            gf.write("\n".join(gpu_info_collected) + "\n")

    with open(checked_file, "a", encoding="utf-8") as f:
        f.write(f"{range_key}\n")
    db_ranges[range_key] = True

    current_count = save_range_usage(usage_file, range_usage_data, CONFIG["range_bits"], gpu_speed_info)
    print(f"[INFO] range_bits {CONFIG['range_bits']} used: {current_count} times {gpu_speed_info}")

    write_log(log_file, quantity, start_hex, end_hex, gpu_speed_info)

    if quantity % CONFIG["backup_every"] == 0:
        backup_file(checked_file)
        print(f"{Fore.YELLOW}[BACKUP] File backup created.{Style.RESET_ALL}")
