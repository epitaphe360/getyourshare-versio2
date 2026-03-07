
import os
import sys
from backend.supabase_client import supabase

def fix_placeholders():
    print("🔧 Starting placeholder image fix...")
    
    tables_columns = [
        ("products", "image_url"),
        ("users", "avatar_url"),
        ("users", "profile_picture_url"),
        ("badges", "icon_url"),
        # services has 'images' which might be an array/json
        # campaigns seems to lack an image column based on inspection
    ]
    
    total_fixed = 0
    
    for table, column in tables_columns:
        try:
            print(f"Checking table '{table}' column '{column}'...")
            
            # Fetch rows with via.placeholder.com
            # Note: Supabase/PostgREST ilike filter
            response = supabase.table(table).select("id", column).ilike(column, "%via.placeholder.com%").execute()
            
            rows = response.data
            if not rows:
                print(f"  No rows found in {table}")
                continue
                
            print(f"  Found {len(rows)} rows to fix in {table}")
            
            for row in rows:
                old_url = row.get(column)
                if not old_url:
                    continue
                    
                new_url = old_url.replace("via.placeholder.com", "placehold.co")
                
                # Update the row
                supabase.table(table).update({column: new_url}).eq("id", row["id"]).execute()
                total_fixed += 1
                
        except Exception as e:
            print(f"  Error processing {table}: {e}")

    # Special handling for services (images array)
    try:
        print("Checking table 'services' column 'images'...")
        response = supabase.table("services").select("id, images").execute()
        rows = response.data
        
        services_fixed = 0
        for row in rows:
            images = row.get("images")
            if not images:
                continue
                
            # Handle if images is a list
            if isinstance(images, list):
                new_images = []
                changed = False
                for img in images:
                    if isinstance(img, str) and "via.placeholder.com" in img:
                        new_images.append(img.replace("via.placeholder.com", "placehold.co"))
                        changed = True
                    else:
                        new_images.append(img)
                
                if changed:
                    supabase.table("services").update({"images": new_images}).eq("id", row["id"]).execute()
                    services_fixed += 1
            
            # Handle if images is a string (sometimes happens with bad json)
            elif isinstance(images, str) and "via.placeholder.com" in images:
                 new_images = images.replace("via.placeholder.com", "placehold.co")
                 supabase.table("services").update({"images": new_images}).eq("id", row["id"]).execute()
                 services_fixed += 1

        print(f"  Fixed {services_fixed} rows in services")
        total_fixed += services_fixed

    except Exception as e:
        print(f"  Error processing services: {e}")

    print(f"\n✅ Finished! Fixed {total_fixed} image URLs.")

if __name__ == "__main__":
    fix_placeholders()
