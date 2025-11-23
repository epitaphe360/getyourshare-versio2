import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    url = os.getenv("DATABASE_URL")
    if not url:
        print("DATABASE_URL not found")
        return None
    try:
        conn = psycopg2.connect(url)
        return conn
    except Exception as e:
        print(f"Error connecting to DB: {e}")
        return None

def check_influencers():
    conn = get_db_connection()
    if not conn:
        return

    try:
        cur = conn.cursor()
        cur.execute("SELECT id, first_name, last_name, email FROM users WHERE role = 'influencer'")
        influencers = cur.fetchall()
        
        print(f"Total Influencers found: {len(influencers)}")
        for inf in influencers:
            print(f"- {inf[1]} {inf[2]} ({inf[3]})")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_influencers()
