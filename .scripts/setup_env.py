#!/usr/bin/env python3
import os, sys, subprocess, platform

venv_dir = ".venv"
is_windows = platform.system() == "Windows"

# 1. Create venv if needed --------------------------------------
if not os.path.exists(venv_dir):
    subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)

# 2. Pick correct pip binary -------------------------------------
if is_windows:
    pip = os.path.join(venv_dir, "Scripts", "pip.exe")
else:
    pip = os.path.join(venv_dir, "bin", "pip")

# 3. Install/upgrade requirements -------------------------------
subprocess.run([pip, "install", "--upgrade", "pip"], check=True)

req_file = "requirements.txt"
if os.path.exists(req_file):
    subprocess.run([pip, "install", "-r", req_file], check=True)

print("\n=== Environment setup completed successfully ===")
print("Using interpreter:", os.path.join(venv_dir, "Scripts" if is_windows else "bin", "python"))
