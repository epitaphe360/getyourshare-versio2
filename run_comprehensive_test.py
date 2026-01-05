import subprocess
import time
import sys
import os
import requests
import signal

# Configuration
PYTHON_EXE = r"C:\Users\samye\OneDrive\Desktop\getyoursharelivrable\getyourshare-versio2\.venv\Scripts\python.exe"
SERVER_SCRIPT = r"backend/run.py"
TEST_SCRIPT = r"backend/test_full_system.py"
BASE_URL = "http://localhost:5000"
WORKING_DIR = r"C:\Users\samye\OneDrive\Desktop\getyoursharelivrable\getyourshare-versio2"

def start_server():
    print(f"🚀 Starting server using {PYTHON_EXE}...")
    
    # Set environment variables if needed
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.join(WORKING_DIR, "backend")
    env["PORT"] = "5000"
    
    # Start process
    process = subprocess.Popen(
        [PYTHON_EXE, SERVER_SCRIPT],
        cwd=WORKING_DIR,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return process

def wait_for_server(process, timeout=30):
    print("⏳ Waiting for server to be ready...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        if process.poll() is not None:
            print("❌ Server process terminated unexpectedly!")
            stdout, stderr = process.communicate()
            print("STDOUT:", stdout)
            print("STDERR:", stderr)
            return False
            
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=1)
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        
        time.sleep(1)
    
    print("❌ Timeout waiting for server")
    return False

def run_tests():
    print(f"\n🧪 Running tests: {TEST_SCRIPT}...")
    result = subprocess.run(
        [PYTHON_EXE, TEST_SCRIPT],
        cwd=WORKING_DIR,
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    return result.returncode == 0

def main():
    # 1. Kill existing python processes to free port 5000
    # print("🧹 Cleaning up existing processes...")
    # subprocess.run(["taskkill", "/F", "/IM", "python.exe"], capture_output=True)
    # time.sleep(2)

    # 2. Start Server
    server_process = start_server()
    
    try:
        # 3. Wait for readiness
        if wait_for_server(server_process):
            # 4. Run Tests
            success = run_tests()
            if success:
                print("\n🎉 ALL TESTS PASSED! SYSTEM IS 100% OPERATIONAL")
            else:
                print("\n⚠️ SOME TESTS FAILED")
        else:
            print("\n❌ COULD NOT START SERVER FOR TESTING")
            
    finally:
        # 5. Cleanup
        print("\n🛑 Stopping server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        print("✅ Server stopped")

if __name__ == "__main__":
    main()
