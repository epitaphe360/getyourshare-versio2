import stripe
import os
from fastapi import Request, HTTPException

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_mock")
BASE_URL = os.getenv("BASE_URL", os.getenv("API_URL", "http://localhost:5000"))

async def create_stripe_checkout(amount: float, subscription_plan: str, user_email: str):
    """Créer session Stripe Checkout"""
    
    if stripe.api_key == "sk_test_mock":
         return {
            "session_id": "mock_session_123",
            "checkout_url": f"{BASE_URL}/mock-payment/stripe?plan={subscription_plan}"
        }

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'mad',
                    'unit_amount': int(amount * 100),  # Centimes
                    'product_data': {
                        'name': f'Abonnement {subscription_plan}',
                        'description': 'ShareYourSales - Plateforme d\'affiliation'
                    }
                },
                'quantity': 1
            }],
            mode='subscription',
            success_url=f'{BASE_URL}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{BASE_URL}/subscription',
            customer_email=user_email,
            metadata={
                'plan': subscription_plan,
                'platform': 'shareyoursales'
            }
        )
        
        return {
            "session_id": session.id,
            "checkout_url": session.url
        }
    except Exception as e:
        print(f"Stripe error: {e}")
        return None

async def handle_stripe_webhook(request: Request):
    """Gérer événements Stripe (paiements réussis, échecs, etc.)"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_mock")
    
    try:
        if webhook_secret == "whsec_mock":
            # Mock verification
            event = {"type": "checkout.session.completed", "data": {"object": {"customer_email": "test@test.com", "metadata": {"plan": "pro"}}}}
        else:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Gérer l'événement
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # await activate_subscription(session['customer_email'], session['metadata']['plan'])
        print(f"Subscription activated for {session.get('customer_email')}")
    
    elif event['type'] == 'invoice.payment_failed':
        # Gérer échec paiement
        # await handle_payment_failure(event['data']['object'])
        print("Payment failed")
    
    return {"status": "success"}
