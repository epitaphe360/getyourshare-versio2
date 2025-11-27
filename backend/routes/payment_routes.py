from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any
import logging

# Adjust imports based on project structure
try:
    from payment_integrations.cmi_maroc import CMIPaymentGateway
    from payment_integrations.stripe_morocco import create_stripe_checkout, handle_stripe_webhook
    from auth import get_current_user_from_cookie
except ImportError:
    # Fallback for different running contexts
    from backend.payment_integrations.cmi_maroc import CMIPaymentGateway
    from backend.payment_integrations.stripe_morocco import create_stripe_checkout, handle_stripe_webhook
    from backend.auth import get_current_user_from_cookie

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payments", tags=["Payments"])

cmi_gateway = CMIPaymentGateway()

@router.post("/cmi/initiate")
async def initiate_cmi_payment(
    payment_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Initiate a CMI payment for Moroccan cards."""
    amount = payment_data.get("amount")
    order_id = payment_data.get("order_id")
    email = current_user.get("email")
    
    if not amount or not order_id:
        raise HTTPException(status_code=400, detail="Missing amount or order_id")
        
    try:
        result = cmi_gateway.create_payment(float(amount), str(order_id), email)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to initiate CMI payment")
        return result
    except Exception as e:
        logger.error(f"CMI Payment Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cmi/callback")
async def cmi_callback(request: Request):
    """Handle CMI callback."""
    try:
        form_data = await request.form()
        # Log the callback for debugging
        logger.info(f"CMI Callback received: {form_data}")
        
        # Here you would verify the hash and update the order status
        # For now, we just acknowledge receipt
        return {"status": "OK"}
    except Exception as e:
        logger.error(f"CMI Callback Error: {e}")
        return {"status": "ERROR", "message": str(e)}

@router.post("/stripe/create-checkout-session")
async def create_stripe_session(
    session_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Create a Stripe Checkout session."""
    price_id = session_data.get("price_id")
    success_url = session_data.get("success_url")
    cancel_url = session_data.get("cancel_url")
    
    if not price_id:
        raise HTTPException(status_code=400, detail="Missing price_id")
        
    try:
        session = create_stripe_checkout(
            price_id=price_id,
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=current_user.get("email"),
            metadata={"user_id": current_user.get("id")}
        )
        
        if not session:
            raise HTTPException(status_code=500, detail="Failed to create Stripe session")
            
        return {"url": session.url}
    except Exception as e:
        logger.error(f"Stripe Session Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stripe/webhook")
async def stripe_webhook_endpoint(request: Request):
    """Handle Stripe webhooks."""
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        return handle_stripe_webhook(payload, sig_header)
    except Exception as e:
        logger.error(f"Stripe Webhook Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
