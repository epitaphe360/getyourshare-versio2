from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid
from supabase_client import supabase
from middleware.security import get_current_user

router = APIRouter(prefix="/api/support", tags=["Support"])

class TicketCreate(BaseModel):
    subject: str
    category: str
    priority: str = "medium"
    message: str

class TicketResponse(BaseModel):
    id: str
    ticket_number: str
    subject: str
    category: str
    priority: str
    status: str
    created_at: str
    updated_at: Optional[str] = None

@router.post("/tickets", response_model=TicketResponse)
async def create_ticket(ticket: TicketCreate, current_user: dict = Depends(get_current_user)):
    try:
        # Generate a ticket number (e.g., T-20251023-1234)
        timestamp = datetime.now().strftime("%Y%m%d")
        short_uuid = str(uuid.uuid4())[:4].upper()
        ticket_number = f"T-{timestamp}-{short_uuid}"

        ticket_data = {
            "user_id": current_user["id"],
            "ticket_number": ticket_number,
            "subject": ticket.subject,
            "description": ticket.message, # Mapping message to description
            "category": ticket.category,
            "priority": ticket.priority,
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        response = supabase.table("support_tickets").insert(ticket_data).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create ticket")
            
        return response.data[0]
    except Exception as e:
        print(f"Error creating ticket: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tickets", response_model=List[TicketResponse])
async def get_my_tickets(current_user: dict = Depends(get_current_user)):
    try:
        response = supabase.table("support_tickets")\
            .select("*")\
            .eq("user_id", current_user["id"])\
            .order("created_at", desc=True)\
            .execute()
            
        return response.data
    except Exception as e:
        print(f"Error fetching tickets: {e}")
        raise HTTPException(status_code=500, detail=str(e))
