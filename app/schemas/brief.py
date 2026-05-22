from pydantic import BaseModel
from typing import Optional, List

class CampaignBriefInput(BaseModel):
    """Raw campaign brief from user"""
    campaign_name: str
    objective: str
    target_audience: str
    channels: List[str]
    duration_days: int
    budget: Optional[float] = None
    key_messages: Optional[List[str]] = None
    success_metrics: Optional[List[str]] = None
    additional_context: Optional[str] = None

class EnrichedBrief(CampaignBriefInput):
    """Brief enriched with LLM analysis"""
    inferred_goals: List[str]
    channel_fit_analysis: dict
    identified_gaps: List[str]
    recommended_adjustments: Optional[List[str]] = None
