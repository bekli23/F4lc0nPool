# logger.py
from datetime import datetime

def write_log(log_file, scan_number, start_hex, end_hex, gpu_speed_info=""):
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Scan #{scan_number} | Range {start_hex}:{end_hex} {gpu_speed_info}\n")

def backup_file(source_file, backup_suffix=".backup"):
    import shutil
    backup_path = source_file + backup_suffix
    shutil.copyfile(source_file, backup_path)
    return backup_path
