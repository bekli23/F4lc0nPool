# 🧠 F4lc0nPool - GPU Bitcoin Puzzle Hunting

Welcome to **F4lc0nPool**, a decentralized GPU-powered platform that unites users to collectively search for missing Bitcoin private keys, leveraging the speed of CUDA-based GPU computation.
http://84.46.242.149/APP.PNG
---
![alt text]([https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png](http://84.46.242.149/APP.PNG) "Logo Title Text 1")
 
## 🔧 Getting Started

This software uses **KeyHunt-Cuda** to scan Bitcoin puzzle ranges using your GPU and reports statistics back to the pool server. You retain control over your machine and private key access.

### ✅ Requirements

- Python 3.6+
- `libgmp-dev` (`sudo apt install -y libgmp-dev`)
- NVIDIA GPU + CUDA Toolkit installed
- Optional: `nvcc` compiler for CUDA support

---

## 🚀 Setup Instructions

### 1. Clone this repo
```bash
git clone https://github.com/bekli23/F4lc0nPool.git
cd F4lc0nPool
```

### 2. Register & Get API Key

- Login to your account.
- Generate your API key using `generate_api_key.php`.

### 3. Edit `config.py` if needed

Set range start/end and other parameters.

### 4. First Time Setup

```bash
python client.py
```

This will ask for your API key and save it in `api.txt`.

### 5. Start Scanning

```bash
python main.py
```

This will scan ranges using `KeyHunt-Cuda`, log progress, and sync to the server demo user api 0cb2a47c424b1a22b5cea037a746282df6bd9e56e1071ad1e417a8387733ddea.

---

## ⚙️ Building KeyHunt-Cuda (Linux Only)

> For CUDA support

### Prerequisites:

- CUDA installed (recommend >= 10.2)
- libgmp-dev:
```bash
sudo apt install -y libgmp-dev
```

### Edit Makefile:

```Makefile
CUDA     = /usr/local/cuda-11.0
CXXCUDA  = /usr/bin/g++
```

Refer to [CUDA Compute Capability chart](https://arnon.dk/matching-sm-architectures-arch-and-gencode-for-various-nvidia-cards/) for your GPU's CCAP.

### Compile with CUDA support:
```bash
cd KeyHunt-Cuda
make gpu=1 CCAP=75 all
```

To compile CPU-only:
```bash
make all
```

---

## 🔁 Automatic Sync

- Every 10–35 seconds, `send.py` syncs:
  - scanned ranges
  - GPU model and count
  - hash rate performance
  - puzzle bit usage
- Synced via cryptographically signed file `client_sync_summary.txt`.

---

## 💼 Wallet Integration

- Only the user who finds the private key has access to the puzzle.
- Admin does **not** have access to the private key.
- Found keys are optionally downloadable and decrypted securely.
- All user data is encrypted.

---

## 📊 Track Progress

- `leaderboard.php` — see user points and speed.
- `scanned_ranges.php` — view covered ranges.
- `user_list.php` — view online users.

---

## 🛠 Files Overview

- `client.py`: manages API key & syncs summary.
- `main.py`: runs the actual scanner (KeyHunt).
- `send.py`: syncs scanned ranges & statsL.
- `gpu.txt`: logs GPU info.
- `range_log.txt`: tracks scanned hex ranges.

---

## 🤝 Contributing

Pull requests and forks are welcome! Help us grow this ethical puzzle-solving community.

---

## 💬 Contact

Visit the community or admin dashboard for support and updates.

Good luck puzzle hunters! 💸
