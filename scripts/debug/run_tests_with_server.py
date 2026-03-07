#!/usr/bin/env python3
"""Run comprehensive tests with server"""

import subprocess
import time
import sys
import os

# Set working directory
os.chdir(r"C:\Users\samye\OneDrive\Desktop\getyoursharelivrable\getyourshare-versio2")

# Start server in background
print("[SERVER] Starting...")
server_process = subprocess.Popen(
    [r"C:\Users\samye\OneDrive\Desktop\getyoursharelivrable\getyourshare-versio2\.venv\Scripts\python.exe", 
     "-m", "uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "5000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# Wait for server to start
print("[SERVER] Waiting for initialization (20 seconds)...")
time.sleep(20)

# Run tests
print("\n[TESTS] Running comprehensive tests...\n")
test_process = subprocess.run(
    [r"C:\Users\samye\OneDrive\Desktop\getyoursharelivrable\getyourshare-versio2\.venv\Scripts\python.exe",
     "test_comprehensive.py"],
    capture_output=False
)

# Kill server
print("\n[SERVER] Stopping...")
server_process.terminate()
server_process.wait(timeout=5)

sys.exit(test_process.returncode)
