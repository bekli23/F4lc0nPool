# range_usage.py
import os

def load_range_usage(path):
    data = {}
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                if ":" in line:
                    parts = line.strip().split(":")
                    if len(parts) >= 2:
                        try:
                            bit = int(parts[0])
                            count_part = parts[1].split()[0]
                            data[bit] = int(count_part)
                        except ValueError:
                            continue
    return data

def save_range_usage(path, usage_data, current_bit, gpu_speed_info=""):
    usage_data[current_bit] += 1
    with open(path, "w") as f:
        for bit in sorted(usage_data.keys()):
            line = f"{bit}:{usage_data[bit]}"
            if bit == current_bit and gpu_speed_info:
                line += f" - {gpu_speed_info}"
            f.write(line + "\n")
    return usage_data[current_bit]