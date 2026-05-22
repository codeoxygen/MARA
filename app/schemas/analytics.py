from pydantic import BaseModel
from typing import Dict, List, Optional

class MetricsPayload(BaseModel):
    """Metrics from GA4 or channel APIs"""
    channel: str
    metric_name: str
    value: float
    unit: str
    timestamp: str
    additional_data: Optional[Dict] = None

class ChannelMetrics(BaseModel):
    """Aggregated metrics for a single channel"""
    channel: str
    metrics: List[MetricsPayload]
    summary: Dict[str, float]

class PerformanceReport(BaseModel):
    """Final performance analysis and recommendations"""
    campaign_id: str
    campaign_name: str
    goal_vs_actual: Dict[str, Dict]
    channel_performance: List[ChannelMetrics]
    key_insights: List[str]
    recommended_actions: List[str]
    next_steps: List[str]
    report_timestamp: str
