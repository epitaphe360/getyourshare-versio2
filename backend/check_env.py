
import os
from dotenv import load_dotenv

load_dotenv()

if os.environ.get("DATABASE_URL"):
    print("DATABASE_URL exists")
else:
    print("DATABASE_URL missing")
