
from backend.supabase_client import supabase

def verify_fix():
    print("Verifying fix for 'Accessoires' product...")
    try:
        # Search for product with 'Accessoires' in name or image_url
        res = supabase.table("products").select("id, name, image_url").ilike("name", "%Accessoires%").execute()
        
        for product in res.data:
            print(f"Product: {product['name']}")
            print(f"Image URL: {product['image_url']}")
            
            if "via.placeholder.com" in product['image_url']:
                print("❌ Still has placeholder!")
            elif "placehold.co" in product['image_url']:
                print("✅ Fixed!")
            else:
                print("ℹ️ Other URL")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_fix()
