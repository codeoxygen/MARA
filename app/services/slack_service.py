import httpx
from app.core.config import settings
from app.core.logging import logger
from typing import Optional

class SlackService:
    """Slack service for approval requests and notifications"""

    def __init__(self):
        self.slack_webhook_url = settings.slack_webhook_url
        self.slack_bot_token = settings.slack_bot_token
        self.base_url = settings.base_url

        logger.info(f"SlackService initialized")
        logger.debug(f"  Webhook URL: {self.slack_webhook_url[:50]}..." if self.slack_webhook_url else "  Webhook URL: Not configured")
        logger.debug(f"  Base URL: {self.base_url}")

    async def send_approval_request(
        self,
        campaign_id: str,
        campaign_name: str,
        proposal_content: str,
        approval_token: str,
    ) -> bool:
        """Send approval request to Slack channel with token for validation"""
        if not self.slack_webhook_url:
            logger.error("❌ Slack webhook URL not configured - cannot send approval request")
            logger.error("   Please set SLACK_WEBHOOK_URL in environment variables")
            return False

        approval_link = f"{self.base_url}/api/campaigns/{campaign_id}/approve?token={approval_token}"
        view_proposal_link = f"{self.base_url}/api/campaigns/{campaign_id}/proposal"

        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"📋 {campaign_name}",
                        "emoji": True,
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": proposal_content,
                    },
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📄 View Full Proposal",
                            },
                            "url": view_proposal_link,
                            "style": "primary",
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "✅ Approve",
                            },
                            "url": f"{approval_link}&action=approve",
                            "style": "primary",
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "🔄 Request Revisions",
                            },
                            "url": f"{approval_link}&action=request_revisions",
                            "style": "danger",
                        },
                    ],
                },
            ]
        }

        try:
            async with httpx.AsyncClient() as client:
                logger.info(f"📤 Sending Slack approval request for campaign: {campaign_name} ({campaign_id})")
                logger.debug(f"   Webhook URL: {self.slack_webhook_url[:60]}...")
                logger.debug(f"   Approval token: {approval_token[:8]}...")
                
                response = await client.post(
                    self.slack_webhook_url,
                    json=message,
                    timeout=10,
                )
                
                success = response.status_code == 200
                
                if success:
                    logger.info(f"✅ Approval request successfully sent to Slack for campaign {campaign_id}")
                    logger.info(f"   Awaiting human approval via Slack...")
                else:
                    logger.error(f"❌ Failed to send Slack message: HTTP {response.status_code}")
                    logger.error(f"   Response: {response.text}")
                    logger.error(f"   URL: {self.slack_webhook_url[:60]}...")
                    
                return success
        except Exception as e:
            logger.error(f"❌ Error sending Slack approval request: {e}", exc_info=True)
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            logger.error(f"   Campaign: {campaign_id}")
            logger.error(f"   Webhook configured: {bool(self.slack_webhook_url)}")
            return False

    async def send_notification(
        self, message: str, channel: Optional[str] = None
    ) -> bool:
        """Send general notification to Slack"""
        if not self.slack_webhook_url:
            logger.warning("Slack webhook URL not configured")
            return False

        payload = {
            "text": message,
            **({"channel": channel} if channel else {}),
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.slack_webhook_url,
                    json=payload,
                    timeout=10,
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
            return False

slack_service = SlackService()
