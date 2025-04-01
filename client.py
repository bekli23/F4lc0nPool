# client.py — Handles API authentication, status sync and appends scanned ranges

import socket
import os
import hashlib
from config import CONFIG
from colorama import init as colorama_init, Fore, Style

colorama_init()

SERVER_HOST = '84.46.242.149'
SERVER_PORT = 1239
API_FILE = 'api.txt'
SYNC_FILE = 'client_sync_summary.txt'
RANGE_LOG_FILE = 'range_log.txt'
GPU_FILE = 'gpu.txt'

# 🔹 Read API Key
if os.path.exists(API_FILE):
    with open(API_FILE, 'r') as f:
        API_KEY = f.read().strip()
        print(f"{Fore.CYAN}[INFO] Using saved API key from {API_FILE}{Style.RESET_ALL}")
else:
    API_KEY = input("Enter your API key: ").strip()
    with open(API_FILE, 'w') as f:
        f.write(API_KEY)
    print(f"{Fore.CYAN}[INFO] API key saved to {API_FILE}{Style.RESET_ALL}")

def authenticate_with_server():
    try:
        with socket.create_connection((SERVER_HOST, SERVER_PORT)) as sock:
            print(f"{Fore.BLUE}[CLIENT] Connected to {SERVER_HOST}:{SERVER_PORT}{Style.RESET_ALL}")
            sock.sendall(f"authenticate\n{API_KEY}\n".encode())
            response = sock.recv(1024).decode()
            print(f"[SERVER RESPONSE] {response.strip()}")

            if "Authentication successful" in response:
                print(f"\n{Fore.YELLOW}Thank you for contributing to the Puzzle Hunting Pool!")
                print("Every cycle brings us one step closer to finding the missing key.")
                print(f"Good luck, and may your GPU be fast and lucky!{Style.RESET_ALL}")
                save_client_state()
                return True
            else:
                print(f"{Fore.RED}[ERROR] Authentication failed.{Style.RESET_ALL}")
                return False

    except Exception as e:
        print(f"{Fore.RED}[CLIENT ERROR] Could not connect to server: {e}{Style.RESET_ALL}")
        return False

def save_client_state():
    summary = []
    summary.append("--- Client Sync Summary ---")
    summary.append(f"API Key: {API_KEY}")

    # Add Puzzle bits
    try:
        end_int = int(CONFIG["range_end"], 16)
        max_bits = end_int.bit_length()
        summary.append(f"Puzzle: {max_bits} bits")
    except:
        summary.append("Puzzle: unknown bits")

    # Add Scan Counter
    if os.path.exists(CONFIG["scan_file"]):
        with open(CONFIG["scan_file"], 'r', encoding='utf-8') as fscan:
            scan = fscan.read().strip()
            summary.append(f"Scan Counter: {scan}")

    # Add Range Bits Usage
    if os.path.exists(CONFIG["usage_file"]):
        with open(CONFIG["usage_file"], 'r', encoding='utf-8') as fusage:
            usage = fusage.read().strip()
            if usage:
                summary.append("Range Bits Usage:")
                summary.extend(usage.splitlines())

    # Add Found Result Output
    if os.path.exists(CONFIG["output_file"]):
        with open(CONFIG["output_file"], 'r', encoding='utf-8') as fout:
            found = fout.read().strip()
            if found:
                summary.append("Found Result Output:")
                summary.append(found)

    # 🔹 Add Scanned Ranges
    if os.path.exists(RANGE_LOG_FILE):
        with open(RANGE_LOG_FILE, 'r', encoding='utf-8') as rf:
            scanned_ranges = [line.strip() for line in rf if line.strip()]
        if scanned_ranges:
            summary.append("Scanned Ranges:")
            summary.extend(scanned_ranges)
        open(RANGE_LOG_FILE, 'w').close()

    # 🔹 Add GPU Info (Formatted) + GPU Count
    gpu_lines = []
    if os.path.exists(GPU_FILE):
        with open(GPU_FILE, 'r', encoding='utf-8') as gf:
            gpu_lines = [line.strip() for line in gf if line.strip() and line.strip().lower().startswith("gpu")]
        if gpu_lines:
            summary.append("GPU Info:")
            summary.extend(gpu_lines)
            summary.append(f"GPU Count: {len(gpu_lines)}")

    # 🔏 Hash Signature
    hash_input = "\n".join(summary).encode('utf-8')
    signature = hashlib.sha256(hash_input).hexdigest()
    summary.append(f"SIGNATURE: {signature}")

    with open(SYNC_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(summary) + "\n")

    print(f"{Fore.CYAN}[CLIENT] Sync summary saved to {SYNC_FILE}{Style.RESET_ALL}")

# Entry point
if __name__ == "__main__":
    if authenticate_with_server():
        print(f"{Fore.CYAN}[CLIENT] Ready to proceed with main scanning logic (e.g., run main.py){Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}[CLIENT] Connection or authentication failed.{Style.RESET_ALL}")
