import httpx
from app.core.config import settings
from app.core.logging import logger
from typing import Optional

class SlackService:
    """Slack service for approval requests and notifications"""

    def __init__(self):
        self.slack_webhook_url = getattr(settings, "slack_webhook_url", None)
        self.slack_bot_token = getattr(settings, "slack_bot_token", None)
        self.base_url = getattr(settings, "base_url", "https://example.ngrok.io")

    async def send_approval_request(
        self,
        campaign_id: str,
        campaign_name: str,
        proposal_content: str,
        approval_token: str,
    ) -> bool:
        """Send approval request to Slack channel"""
        if not self.slack_webhook_url:
            logger.warning("Slack webhook URL not configured")
            return False

        approval_link = f"{self.base_url}/api/campaigns/{campaign_id}/approve?token={approval_token}"

        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"📋 Campaign Approval Request: {campaign_name}",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Campaign ID:* {campaign_id}\n\n*Proposal:*\n{proposal_content}",
                    },
                },
                {
                    "type": "actions",
                    "elements": [
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
                            "url": f"{approval_link}&action=revisions",
                            "style": "danger",
                        },
                    ],
                },
            ]
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.slack_webhook_url,
                    json=message,
                    timeout=10,
                )
                success = response.status_code == 200
                if success:
                    logger.info(f"Approval request sent to Slack for campaign {campaign_id}")
                else:
                    logger.error(f"Failed to send Slack message: {response.status_code}")
                return success
        except Exception as e:
            logger.error(f"Error sending Slack approval request: {e}")
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
