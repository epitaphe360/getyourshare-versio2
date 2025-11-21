#!/usr/bin/env python
"""Launch server in background without expecting input"""

import subprocess
import time
import os

os.chdir(r"c:\Users\samye\OneDrive\Desktop\getyoursharelivrable\getyourshare-versio2\backend")

# Launch server in background with output to file
print("Starting server...")
proc = subprocess.Popen(
    [r"c:\Users\samye\AppData\Local\Python\pythoncore-3.14-64\python.exe", "server.py"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    stdin=subprocess.DEVNULL,
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
)

print(f"Server process ID: {proc.pid}")
time.sleep(10)
print("Server should now be running on http://localhost:5000")
