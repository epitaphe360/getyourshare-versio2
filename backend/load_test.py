import threading
import time
import requests
import random
import statistics
from concurrent.futures import ThreadPoolExecutor

# Configuration
BASE_URL = "http://localhost:5000"
NUM_USERS = 50  # Reduced from 100 to be safe with threads vs greenlets
DURATION_SECONDS = 30
RAMP_UP_SECONDS = 10

# Test Data
TEST_ACCOUNTS = [
    ("admin@getyourshare.com", "Admin123!"),
    ("merchant3@beautyparis.com", "Test123!"),
    ("influencer3@lifestyle.com", "Test123!")
]

class LoadTester:
    def __init__(self):
        self.results = []
        self.lock = threading.Lock()
        self.running = True
        self.start_time = 0

    def log_request(self, endpoint, method, status_code, duration_ms, error=None):
        with self.lock:
            self.results.append({
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "error": error,
                "timestamp": time.time()
            })

    def user_scenario(self, user_id):
        # Randomly select a persona
        email, password = random.choice(TEST_ACCOUNTS)
        session = requests.Session()
        
        # 1. Login
        try:
            start = time.time()
            resp = session.post(f"{BASE_URL}/api/auth/login", json={
                "email": email,
                "password": password
            })
            duration = (time.time() - start) * 1000
            self.log_request("/api/auth/login", "POST", resp.status_code, duration)
            
            if resp.status_code == 200:
                token = resp.json().get("access_token")
                if token:
                    session.headers.update({"Authorization": f"Bearer {token}"})
            else:
                # If login fails, we can't do much else
                return
        except Exception as e:
            self.log_request("/api/auth/login", "POST", 0, 0, str(e))
            return

        # 2. Loop actions until test ends
        while self.running:
            action = random.choice(["dashboard", "merchants", "influencers", "campaigns"])
            
            try:
                if action == "dashboard":
                    start = time.time()
                    resp = session.get(f"{BASE_URL}/api/dashboard/stats")
                    duration = (time.time() - start) * 1000
                    self.log_request("/api/dashboard/stats", "GET", resp.status_code, duration)
                
                elif action == "merchants":
                    start = time.time()
                    resp = session.get(f"{BASE_URL}/api/merchants")
                    duration = (time.time() - start) * 1000
                    self.log_request("/api/merchants", "GET", resp.status_code, duration)

                elif action == "influencers":
                    start = time.time()
                    resp = session.get(f"{BASE_URL}/api/influencers")
                    duration = (time.time() - start) * 1000
                    self.log_request("/api/influencers", "GET", resp.status_code, duration)
                    
                elif action == "campaigns":
                    start = time.time()
                    resp = session.get(f"{BASE_URL}/api/campaigns")
                    duration = (time.time() - start) * 1000
                    self.log_request("/api/campaigns", "GET", resp.status_code, duration)

                # Think time
                time.sleep(random.uniform(0.5, 2.0))
                
            except Exception as e:
                self.log_request(f"action_{action}", "GET", 0, 0, str(e))

    def run(self):
        print(f"Starting Load Test: {NUM_USERS} users, {DURATION_SECONDS}s duration")
        print(f"Target: {BASE_URL}")
        
        self.start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=NUM_USERS) as executor:
            # Launch users
            futures = []
            for i in range(NUM_USERS):
                futures.append(executor.submit(self.user_scenario, i))
                # Ramp up
                time.sleep(RAMP_UP_SECONDS / NUM_USERS)
            
            # Wait for duration
            remaining_time = DURATION_SECONDS - RAMP_UP_SECONDS
            if remaining_time > 0:
                time.sleep(remaining_time)
            
            self.running = False
            print("\nStopping test, waiting for threads...")
            
        self.print_report()

    def print_report(self):
        total_requests = len(self.results)
        if total_requests == 0:
            print("No requests recorded.")
            return

        errors = [r for r in self.results if r["status_code"] >= 400 or r["error"]]
        success = [r for r in self.results if r["status_code"] < 400 and not r["error"]]
        
        print("\n" + "="*50)
        print("LOAD TEST REPORT")
        print("="*50)
        print(f"Total Requests: {total_requests}")
        print(f"Successful:     {len(success)} ({len(success)/total_requests*100:.1f}%)")
        print(f"Failed:         {len(errors)} ({len(errors)/total_requests*100:.1f}%)")
        print(f"Duration:       {time.time() - self.start_time:.1f}s")
        print(f"RPS:            {total_requests / (time.time() - self.start_time):.1f}")
        
        print("\nResponse Times (ms):")
        endpoints = set(r["endpoint"] for r in self.results)
        
        print(f"{'Endpoint':<30} | {'Avg':<8} | {'Min':<8} | {'Max':<8} | {'Count':<8}")
        print("-" * 70)
        
        for endpoint in sorted(endpoints):
            reqs = [r for r in self.results if r["endpoint"] == endpoint]
            if not reqs: continue
            
            times = [r["duration_ms"] for r in reqs]
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"{endpoint:<30} | {avg_time:<8.1f} | {min_time:<8.1f} | {max_time:<8.1f} | {len(reqs):<8}")

        if errors:
            print("\nErrors Sample:")
            for e in errors[:5]:
                print(f"- {e['endpoint']}: {e['status_code']} - {e.get('error', 'Http Error')}")

if __name__ == "__main__":
    tester = LoadTester()
    tester.run()
