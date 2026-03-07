import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()
if not os.environ.get("SUPABASE_URL"):
    load_dotenv(".env.railway")

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_KEY not found.")
    exit(1)

supabase: Client = create_client(url, key)

def update_stats():
    print("Updating affiliate stats in users table...")
    
    # 1. Get all influencers
    response = supabase.table("users").select("id").eq("role", "influencer").execute()
    influencers = response.data
    print(f"Found {len(influencers)} influencers.")

    for inf in influencers:
        inf_id = inf['id']
        
        # Calculate clicks from tracking_links
        clicks_res = supabase.table("tracking_links").select("clicks").eq("influencer_id", inf_id).execute()
        total_clicks = sum(item.get("clicks", 0) for item in clicks_res.data) if clicks_res.data else 0
        
        # Calculate conversions/revenue
        # This depends on schema. Assuming 'conversions' table has 'influencer_id' or linked via tracking_link
        # Let's try to get from tracking_links first if it has aggregated data
        # The sample link showed: 'conversions': 10, 'revenue': 0.0, 'commission_earned': 0.0
        
        conversions_res = supabase.table("tracking_links").select("conversions, commission_earned").eq("influencer_id", inf_id).execute()
        total_conversions = sum(item.get("conversions", 0) for item in conversions_res.data) if conversions_res.data else 0
        total_earned = sum(item.get("commission_earned", 0) for item in conversions_res.data) if conversions_res.data else 0

        # Update user
        if total_clicks > 0 or total_conversions > 0 or total_earned > 0:
            print(f"Updating Influencer {inf_id}: Clicks={total_clicks}, Conv={total_conversions}, Earned={total_earned}")
            supabase.table("users").update({
                "clicks": total_clicks,
                "conversions": total_conversions,
                "total_earned": total_earned
            }).eq("id", inf_id).execute()
        
    print("Update complete.")

if __name__ == "__main__":
    update_stats()
