
import sys
import os
from datetime import datetime, timezone, timedelta

# Mock objects
class MockRequest:
    def __init__(self, json_data):
        self._json = json_data
    
    async def json(self):
        return self._json

async def test_payout_error():
    print("Testing Payout Error Handling...")
    # We can't easily mock the DB call inside request_payout without mocking supabase
    # But we can simulate the exception handling logic.
    
    # Let's copy the exception handling logic from server.py and test it
    error_msg = "{'message': 'Payout refusé : Le total des retraits (2145.00.2f€) dépasserait les commissions gagnées (2119.34.2f€). Solde disponible: 74.34.2f€', 'code': 'P0001', 'hint': None, 'details': None}"
    
    try:
        # Simulate the logic
        import re
        import ast
        
        error_data = {}
        try:
            match = re.search(r"\{.*\}", error_msg)
            if match:
                error_data = ast.literal_eval(match.group(0))
        except:
            pass
            
        print(f"Parsed error data: {error_data}")
        
        if "Payout refusé" in error_msg or "P0001" in error_msg or error_data.get('code') == 'P0001':
             detail = error_data.get('message') if error_data.get('message') else "Payout refusé par la banque (Solde insuffisant)"
             print(f"Caught! Raising 400 with detail: {detail}")
        else:
             print("Not caught! Raising 500")
             
    except Exception as e:
        print(f"Exception during test: {e}")

def test_datetime_logic():
    print("\nTesting Datetime Logic...")
    
    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)
    
    # Test cases
    dates = [
        "2023-10-27T10:00:00Z",
        "2023-10-27T10:00:00+00:00",
        "2023-10-27T10:00:00", # Naive
        datetime.now(), # Naive datetime
        datetime.now(timezone.utc) # Aware datetime
    ]
    
    for d in dates:
        print(f"Testing: {d} (Type: {type(d)})")
        try:
            created_at_str = d
            created_at = None
            
            if isinstance(created_at_str, str):
                created_at_str = created_at_str.replace("Z", "+00:00")
                created_at = datetime.fromisoformat(created_at_str)
            elif isinstance(created_at_str, datetime):
                created_at = created_at_str
            
            if created_at.tzinfo is None:
                print("  -> Was naive, making aware")
                created_at = created_at.replace(tzinfo=timezone.utc)
            else:
                print(f"  -> Is aware: {created_at.tzinfo}")
                
            # Compare
            if created_at >= thirty_days_ago:
                print("  -> Comparison OK")
            else:
                print("  -> Comparison OK")
                
        except Exception as e:
            print(f"  -> ERROR: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_payout_error())
    test_datetime_logic()
