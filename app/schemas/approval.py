from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISIONS_REQUESTED = "revisions_requested"

class ApprovalRequest(BaseModel):
    """Request sent to human for approval"""
    campaign_id: str
    proposal: str
    sections: List[dict]
    deadline: Optional[str] = None
    recipient_email: str
    approval_token: str

class ApprovalResponse(BaseModel):
    """Human's response to approval request"""
    campaign_id: str
    approval_token: str
    status: ApprovalStatus
    feedback: Optional[str] = None
    revisions: Optional[List[dict]] = None
    notes: Optional[str] = None
