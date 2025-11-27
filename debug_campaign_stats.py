
import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load env
env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
load_dotenv(env_path)

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_KEY not found")
    sys.exit(1)

supabase: Client = create_client(url, key)

# Campaign ID for "Tech Innovation 2024"
campaign_id = 'c2222222-2222-2222-2222-222222222222'

print(f"--- Debugging Campaign {campaign_id} ---")

# 1. Fetch Campaign
response = supabase.table('campaigns').select('*').eq('id', campaign_id).execute()
if not response.data:
    print("Campaign not found!")
    sys.exit(1)

campaign = response.data[0]
print(f"Campaign Name: {campaign.get('name')}")
performance_metrics = campaign.get('performance_metrics')
print(f"Performance Metrics (Raw): {performance_metrics}")
print(f"Type of performance_metrics: {type(performance_metrics)}")

# 2. Fetch Tracking Links
tracking_response = supabase.table('tracking_links').select('id, clicks, conversions, revenue').eq('campaign_id', campaign_id).execute()
tracking_links = tracking_response.data or []
print(f"Tracking Links Count: {len(tracking_links)}")
print(f"Tracking Links Data: {tracking_links}")

# 3. Simulate Logic
total_clicks = sum(link.get('clicks', 0) for link in tracking_links)
total_conversions = sum(link.get('conversions', 0) for link in tracking_links)

print(f"Initial Total Clicks: {total_clicks}")
print(f"Initial Total Conversions: {total_conversions}")

views = 0
if isinstance(performance_metrics, dict):
    print("performance_metrics is a dict")
    
    # Logic from server.py
    views = int(performance_metrics.get('impressions', performance_metrics.get('clicks', total_clicks)))
    print(f"Calculated Views: {views}")
    
    pm_clicks = performance_metrics.get('clicks', 0)
    print(f"PM Clicks: {pm_clicks} (Type: {type(pm_clicks)})")
    
    if total_clicks == 0 and int(pm_clicks) > 0:
        print("TRIGGERED: Updating total_clicks from PM")
        total_clicks = int(pm_clicks)
    else:
        print(f"NOT TRIGGERED: total_clicks={total_clicks}, pm_clicks={pm_clicks}")

    pm_conversions = performance_metrics.get('conversions', 0)
    if total_conversions == 0 and int(pm_conversions) > 0:
        print("TRIGGERED: Updating total_conversions from PM")
        total_conversions = int(pm_conversions)
else:
    print("performance_metrics is NOT a dict")
    views = total_clicks

print(f"Final Total Clicks: {total_clicks}")
print(f"Final Total Conversions: {total_conversions}")

ctr = (total_clicks / views * 100) if views > 0 else 0
conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0

print(f"CTR: {ctr}%")
print(f"Conversion Rate: {conversion_rate}%")
