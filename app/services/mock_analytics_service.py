"""Mock Google Analytics service with realistic campaign data"""
from app.core.logging import logger
from datetime import datetime, timedelta


class MockAnalyticsService:
    """Mock GA4 data for campaign performance"""

    async def fetch_campaign_metrics(self, campaign_id: str, campaign_name: str) -> dict:
        """Fetch mock campaign metrics from GA4"""
        try:
            logger.info(f"Analytics: Fetching metrics for campaign {campaign_name}")

            # Generate realistic mock data
            metrics = {
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "date_range": {
                    "start_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                    "end_date": datetime.now().strftime("%Y-%m-%d"),
                },
                "channels": {
                    "instagram": {
                        "impressions": 45230,
                        "engagement_rate": 4.2,
                        "reach": 38450,
                        "followers_gained": 287,
                    },
                    "email": {
                        "emails_sent": 850,
                        "open_rate": 28.5,
                        "click_rate": 6.4,
                        "subscribers_gained": 312,
                    },
                    "google_ads": {
                        "impressions": 125000,
                        "clicks": 3420,
                        "ctr": 2.74,
                        "conversions": 89,
                        "conversion_rate": 2.6,
                    },
                    "tiktok": {
                        "views": 320500,
                        "engagement_rate": 7.8,
                        "shares": 1240,
                        "followers_gained": 156,
                    },
                },
                "overall_metrics": {
                    "total_sessions": 14520,
                    "total_users": 9340,
                    "bounce_rate": 35.2,
                    "avg_session_duration": "2m 24s",
                    "conversion_rate": 3.8,
                    "total_conversions": 552,
                },
                "performance_summary": {
                    "status": "exceeding_targets",
                    "performance_vs_goal": "+12%",
                    "best_performing_channel": "instagram",
                    "roi_estimate": "320%",
                },
                "insights": [
                    "Instagram content showed highest engagement rate at 4.2%",
                    "Email open rates exceeded industry benchmark by 15%",
                    "Google Ads CTR of 2.74% is 35% above account average",
                    "TikTok driving highest engagement rate at 7.8%",
                    "Overall conversion rate of 3.8% exceeds Q2 target of 3%",
                ],
                "recommendations": [
                    "Increase budget allocation to TikTok (highest engagement)",
                    "Replicate Instagram content strategy for next campaign",
                    "A/B test longer email sequences (high open rate indicates audience interest)",
                    "Expand Google Ads to competitor keywords (strong CTR performance)",
                    "Leverage top-performing TikTok creators for brand partnerships",
                ],
            }

            logger.info(f"Analytics: Generated metrics with {len(metrics['channels'])} channels")
            return metrics

        except Exception as e:
            logger.error(f"Analytics fetch failed: {e}")
            raise


mock_analytics_service = MockAnalyticsService()
