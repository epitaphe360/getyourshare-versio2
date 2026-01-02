import hmac
import hashlib
import requests
import os

class CMIPaymentGateway:
    """Intégration CMI (Centre Monétique Interbancaire) - Maroc"""
    
    def __init__(self):
        self.merchant_id = os.getenv("CMI_MERCHANT_ID", "DEFAULT_MERCHANT_ID")
        self.api_key = os.getenv("CMI_API_KEY", "DEFAULT_API_KEY")
        self.endpoint = "https://payment.cmi.co.ma/fim/api"
        self.base_url = os.getenv("BASE_URL", os.getenv("API_URL", "http://localhost:5000"))
    
    def create_payment(self, amount: float, order_id: str, customer_email: str):
        """Créer une transaction CMI"""
        
        data = {
            "clientid": self.merchant_id,
            "amount": amount,
            "currency": "504",  # MAD
            "oid": order_id,
            "okUrl": f"{self.base_url}/api/payments/cmi/success",
            "failUrl": f"{self.base_url}/api/payments/cmi/fail",
            "callbackUrl": f"{self.base_url}/webhooks/cmi",
            "email": customer_email,
            "BillToName": customer_email.split('@')[0]
        }
        
        # Calculer hash de sécurité
        hash_string = f"{self.merchant_id}|{order_id}|{amount}|{self.api_key}"
        data["hash"] = hmac.new(
            self.api_key.encode(),
            hash_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Simulation pour le développement si pas de clés réelles
        if self.merchant_id == "DEFAULT_MERCHANT_ID":
            return {
                "payment_url": f"{self.base_url}/mock-payment/cmi?oid={order_id}",
                "transaction_id": f"mock_cmi_{order_id}"
            }

        try:
            response = requests.post(f"{self.endpoint}/pay", data=data)
            response.raise_for_status()
            return {
                "payment_url": response.json().get("redirectUrl"),
                "transaction_id": response.json().get("tranid")
            }
        except Exception as e:
            print(f"Error creating CMI payment: {e}")
            return None
    
    def verify_payment(self, transaction_id: str):
        """Vérifier statut paiement"""
        if transaction_id.startswith("mock_"):
            return {"status": "APPROVED", "amount": 100.00}

        try:
            response = requests.get(
                f"{self.endpoint}/transaction/{transaction_id}",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return response.json()
        except Exception as e:
            print(f"Error verifying CMI payment: {e}")
            return None
