
import os
from dotenv import load_dotenv
load_dotenv()

print("Importing openai...")
from openai import OpenAI
try:
    client = OpenAI(api_key="test")
    print("OpenAI client created.")
except Exception as e:
    print(f"OpenAI error: {e}")

print("Importing supabase...")
from supabase import create_client, Client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
if url and key:
    try:
        supabase: Client = create_client(url, key)
        print("Supabase client created.")
    except Exception as e:
        print(f"Supabase error: {e}")
else:
    print("Supabase credentials not found.")
