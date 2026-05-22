"""Channel-specific task templates for content production"""

CHANNEL_TASK_TEMPLATES = {
    "linkedin": {
        "name": "LinkedIn Content Production",
        "task_sequence": [
            {
                "step": 1,
                "task_name": "Copy",
                "description": "Write LinkedIn post copy",
                "owner_role": "copywriter",
                "estimated_hours": 2,
            },
            {
                "step": 2,
                "task_name": "Visual",
                "description": "Create or source visual assets",
                "owner_role": "designer",
                "estimated_hours": 3,
            },
            {
                "step": 3,
                "task_name": "Approval",
                "description": "Review and approve post",
                "owner_role": "manager",
                "estimated_hours": 1,
            },
            {
                "step": 4,
                "task_name": "Publish",
                "description": "Schedule and publish post",
                "owner_role": "social_manager",
                "estimated_hours": 1,
            },
        ],
    },
    "email": {
        "name": "Email Campaign Production",
        "task_sequence": [
            {
                "step": 1,
                "task_name": "Copy",
                "description": "Write email copy",
                "owner_role": "copywriter",
                "estimated_hours": 2,
            },
            {
                "step": 2,
                "task_name": "HTML Build",
                "description": "Build HTML email template",
                "owner_role": "developer",
                "estimated_hours": 4,
            },
            {
                "step": 3,
                "task_name": "QA/Test",
                "description": "Test email rendering across clients",
                "owner_role": "qa",
                "estimated_hours": 2,
            },
            {
                "step": 4,
                "task_name": "Approval",
                "description": "Final approval before send",
                "owner_role": "manager",
                "estimated_hours": 1,
            },
            {
                "step": 5,
                "task_name": "Send",
                "description": "Deploy email campaign",
                "owner_role": "marketer",
                "estimated_hours": 1,
            },
        ],
    },
    "instagram": {
        "name": "Instagram Content Production",
        "task_sequence": [
            {
                "step": 1,
                "task_name": "Visual",
                "description": "Create Instagram post visuals",
                "owner_role": "designer",
                "estimated_hours": 3,
            },
            {
                "step": 2,
                "task_name": "Copy",
                "description": "Write caption and hashtags",
                "owner_role": "copywriter",
                "estimated_hours": 1,
            },
            {
                "step": 3,
                "task_name": "Approval",
                "description": "Review post before publishing",
                "owner_role": "manager",
                "estimated_hours": 1,
            },
            {
                "step": 4,
                "task_name": "Publish",
                "description": "Schedule and publish to Instagram",
                "owner_role": "social_manager",
                "estimated_hours": 1,
            },
        ],
    },
    "paid_search": {
        "name": "Paid Search Campaign Setup",
        "task_sequence": [
            {
                "step": 1,
                "task_name": "Ad Copy",
                "description": "Write ad headlines and descriptions",
                "owner_role": "copywriter",
                "estimated_hours": 2,
            },
            {
                "step": 2,
                "task_name": "Audience Setup",
                "description": "Configure targeting and audiences",
                "owner_role": "ppc_specialist",
                "estimated_hours": 3,
            },
            {
                "step": 3,
                "task_name": "Bid Strategy",
                "description": "Set bids and budget allocation",
                "owner_role": "ppc_specialist",
                "estimated_hours": 2,
            },
            {
                "step": 4,
                "task_name": "Approval",
                "description": "Final approval before launch",
                "owner_role": "manager",
                "estimated_hours": 1,
            },
            {
                "step": 5,
                "task_name": "Launch",
                "description": "Launch paid search campaigns",
                "owner_role": "ppc_specialist",
                "estimated_hours": 1,
            },
        ],
    },
}

def get_template_for_channel(channel: str) -> dict:
    """Get task template for a specific channel"""
    normalized_channel = channel.lower().replace(" ", "_")
    return CHANNEL_TASK_TEMPLATES.get(normalized_channel, CHANNEL_TASK_TEMPLATES.get("linkedin"))
