import requests
import json

BASE_URL = "http://localhost:5000"

def test_endpoint(path, expected_keys):
    url = f"{BASE_URL}{path}"
    print(f"Testing {url}...")
    try:
        # We might need authentication. 
        # But let's try without first, or assume we have a token.
        # Since I can't easily get a valid token without logging in, 
        # I'll try to login first if needed.
        
        response = requests.get(url)
        
        if response.status_code == 401:
            print("  Auth required. Skipping for now (or implement login).")
            return
            
        if response.status_code != 200:
            print(f"  Failed with status {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return

        data = response.json()
        print("  Success!")
        
        missing_keys = [key for key in expected_keys if key not in data]
        
        if missing_keys:
            print(f"  MISSING KEYS: {missing_keys}")
            print(f"  Available keys: {list(data.keys())}")
        else:
            print("  All expected keys present.")
            
    except Exception as e:
        print(f"  Error: {e}")

def main():
    # Test /api/analytics/overview
    # Expected keys from analytics_endpoints.py: users, catalog, financial, tracking, leads
    test_endpoint("/api/analytics/overview", ["users", "catalog", "financial", "tracking", "leads"])
    
    # Test /api/analytics/merchant/performance
    # Expected keys: total_sales, total_revenue, products_count, affiliates_count, total_clicks
    test_endpoint("/api/analytics/merchant/performance", ["total_sales", "total_revenue", "products_count", "affiliates_count", "total_clicks"])

    # Test /api/analytics/merchant/sales-chart
    # Expected keys: data, total_sales, total_orders
    test_endpoint("/api/analytics/merchant/sales-chart", ["data", "total_sales", "total_orders"])

if __name__ == "__main__":
    main()
