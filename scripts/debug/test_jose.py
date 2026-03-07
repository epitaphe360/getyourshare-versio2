
from jose import jwt
print("python-jose imported successfully")
encoded = jwt.encode({"some": "payload"}, "secret", algorithm="HS256")
print(f"Encoded: {encoded}")
decoded = jwt.decode(encoded, "secret", algorithms=["HS256"])
print(f"Decoded: {decoded}")
