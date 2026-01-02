
import sys
import os
from fastapi import FastAPI
from fastapi.routing import APIRoute

# Add backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

# Import app from server
try:
    from backend.server import app
except ImportError:
    try:
        from server import app
    except ImportError:
        print("Could not import app from server.py")
        sys.exit(1)

print("Listing all registered routes:")
for route in app.routes:
    if isinstance(route, APIRoute):
        print(f"{route.methods} {route.path}")
