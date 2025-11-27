from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from websocket_manager import manager
import json
import asyncio
from datetime import datetime
import logging
from supabase_client import supabase

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter()

class EventTypes:
    COMMISSION_CREATED = "commission_created"
    COMMISSION_UPDATED = "commission_updated"
    PAYMENT_CREATED = "payment_created"
    PAYMENT_STATUS_CHANGED = "payment_status_changed"
    SALE_CREATED = "sale_created"
    DASHBOARD_UPDATE = "dashboard_update"

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    user_id = None
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                msg_type = message.get("type")
                
                if msg_type == "auth":
                    user_id = message.get("user_id")
                    if user_id:
                        # Register connection with user_id
                        await manager.connect(websocket, user_id)
                        
                        # Send confirmation
                        await websocket.send_json({
                            "type": "auth_success",
                            "message": "Authenticated successfully",
                            "timestamp": datetime.now().isoformat()
                        })
                
                elif msg_type == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
                
    except WebSocketDisconnect:
        if user_id:
            manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if user_id:
            manager.disconnect(websocket, user_id)

async def listen_to_database_changes():
    """Background task to poll Supabase for changes"""
    logger.info("Starting database listener for WebSockets...")
    last_check = datetime.utcnow()
    
    while True:
        try:
            # Check for new commissions
            # Note: Using created_at > last_check
            # We need to be careful with timezone, assuming UTC
            
            # Commissions
            try:
                response = supabase.table("commissions")\
                    .select("*")\
                    .gt("created_at", last_check.isoformat())\
                    .execute()
                
                if response.data:
                    for commission in response.data:
                        affiliate_id = commission.get("influencer_id") # Changed from affiliate_id to influencer_id based on schema
                        if affiliate_id:
                            await manager.send_personal_message(
                                {
                                    "type": EventTypes.COMMISSION_CREATED,
                                    "data": {
                                        "commission_id": commission["id"],
                                        "amount": commission["amount"],
                                        "sale_id": commission.get("sale_id")
                                    }
                                },
                                str(affiliate_id)
                            )
            except Exception as e:
                logger.error(f"Error checking commissions: {e}")

            # Payments
            try:
                response = supabase.table("payouts")\
                    .select("*")\
                    .gt("updated_at", last_check.isoformat())\
                    .execute()
                
                if response.data:
                    for payout in response.data:
                        influencer_id = payout.get("influencer_id")
                        if influencer_id:
                            await manager.send_personal_message(
                                {
                                    "type": EventTypes.PAYMENT_STATUS_CHANGED,
                                    "data": {
                                        "payment_id": payout["id"],
                                        "status": payout["status"],
                                        "amount": payout["amount"]
                                    }
                                },
                                str(influencer_id)
                            )
            except Exception as e:
                logger.error(f"Error checking payouts: {e}")

            last_check = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error in database listener: {e}")
            
        # Poll every 5 seconds
        await asyncio.sleep(5)
