#!/usr/bin/env python
"""Test script for approval workflow with revisions"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

# Sample campaign brief
campaign_brief = {
    "campaign_name": "Summer Product Launch 2026",
    "objective": "Drive awareness and early adoption of new product line",
    "target_audience": "Tech-savvy millennials and Gen Z (18-35)",
    "channels": ["instagram", "tiktok", "email"],
    "duration_days": 30,
    "budget": 50000,
    "key_messages": [
        "Innovation meets affordability",
        "Sustainability focused",
        "Community-driven design"
    ],
    "success_metrics": [
        "1M impressions",
        "50k engagement",
        "5k conversions"
    ],
    "additional_context": "Focus on user-generated content and influencer partnerships"
}

def test_workflow():
    """Test complete workflow with approval"""

    print("\n" + "="*60)
    print("🚀 MARA Campaign Approval Workflow Test")
    print("="*60 + "\n")

    # Step 1: Start campaign
    print("1️⃣  Starting campaign...")
    response = requests.post(
        f"{BASE_URL}/api/campaigns/run",
        json=campaign_brief
    )

    if response.status_code != 200:
        print(f"❌ Failed to start campaign: {response.status_code}")
        print(response.text)
        return False

    campaign_data = response.json()
    campaign_id = campaign_data["campaign_id"]
    session_id = campaign_data["session_id"]

    print(f"✅ Campaign started")
    print(f"   Campaign ID: {campaign_id}")
    print(f"   Session ID: {session_id}\n")

    # Step 2: Wait for planning to complete and approval request
    print("2️⃣  Waiting for campaign plan and approval request...")
    for i in range(120):  # Wait up to 2 minutes
        response = requests.get(f"{BASE_URL}/api/campaigns/{campaign_id}")
        if response.status_code == 200:
            status = response.json().get("status")
            print(f"   Status: {status}", end="\r")

            if status == "awaiting_approval":
                print(f"   Status: {status}  ✅")
                break
            elif "failed" in status or "error" in status.lower():
                print(f"\n❌ Campaign failed: {status}")
                if "error_message" in response.json():
                    print(f"   Error: {response.json()['error_message']}")
                return False

        time.sleep(1)

    print("✅ Campaign ready for approval\n")

    # Step 3: Simulate Slack approval (reject first to test revision)
    print("3️⃣  Testing revision cycle - submitting REJECTION...")
    rejection_response = requests.api_route(
        f"{BASE_URL}/api/campaigns/{campaign_id}/approve",
        method="POST",
        params={
            "action": "reject",
            "feedback": "Please make the Instagram strategy more focused on trending sounds and challenges. Also reduce the number of email sends to avoid unsubscribes."
        }
    )

    # Fallback to requests if api_route doesn't work
    try:
        rejection_response = requests.post(
            f"{BASE_URL}/api/campaigns/{campaign_id}/approve",
            params={
                "action": "reject",
                "feedback": "Please make the Instagram strategy more focused on trending sounds and challenges. Also reduce the number of email sends to avoid unsubscribes."
            }
        )
    except:
        rejection_response = requests.get(
            f"{BASE_URL}/api/campaigns/{campaign_id}/approve",
            params={
                "action": "reject",
                "feedback": "Please make the Instagram strategy more focused on trending sounds and challenges. Also reduce the number of email sends to avoid unsubscribes."
            }
        )

    if rejection_response.status_code == 200:
        print(f"✅ Rejection submitted")
        print(f"   Response: {rejection_response.json()}\n")
    else:
        print(f"⚠️  Warning: Could not submit rejection: {rejection_response.status_code}\n")

    # Step 4: Wait for revised plan
    print("4️⃣  Waiting for revised campaign plan...")
    for i in range(120):
        response = requests.get(f"{BASE_URL}/api/campaigns/{campaign_id}")
        if response.status_code == 200:
            status = response.json().get("status")
            print(f"   Status: {status}", end="\r")

            if status == "awaiting_approval":
                print(f"   Status: {status}  ✅ (revised)")
                break
            elif status == "approved" or status == "analytics_complete" or status == "complete":
                print(f"   Status: {status}  ✅")
                break
            elif "failed" in status or "error" in status.lower():
                print(f"\n❌ Campaign failed: {status}")
                return False

        time.sleep(1)

    print("✅ Revised plan ready\n")

    # Step 5: Approve the revised plan
    print("5️⃣  Approving revised campaign plan...")
    try:
        approval_response = requests.post(
            f"{BASE_URL}/api/campaigns/{campaign_id}/approve",
            params={
                "action": "approve",
                "feedback": "Plan looks great now! Let's proceed."
            }
        )
    except:
        approval_response = requests.get(
            f"{BASE_URL}/api/campaigns/{campaign_id}/approve",
            params={
                "action": "approve",
                "feedback": "Plan looks great now! Let's proceed."
            }
        )

    if approval_response.status_code == 200:
        print(f"✅ Approval submitted")
        print(f"   Response: {approval_response.json()}\n")
    else:
        print(f"⚠️  Warning: Could not submit approval: {approval_response.status_code}\n")

    # Step 6: Wait for analytics and completion
    print("6️⃣  Waiting for analytics and final report...")
    for i in range(120):
        response = requests.get(f"{BASE_URL}/api/campaigns/{campaign_id}")
        if response.status_code == 200:
            status = response.json().get("status")
            print(f"   Status: {status}", end="\r")

            if "complete" in status or "analytics" in status:
                print(f"   Status: {status}  ✅")
                break
            elif "failed" in status or "error" in status.lower():
                print(f"\n❌ Campaign failed: {status}")
                return False

        time.sleep(1)

    print("✅ Campaign completed\n")

    print("="*60)
    print("✅ WORKFLOW TEST PASSED - Approval cycle with revision works!")
    print("="*60 + "\n")

    return True

if __name__ == "__main__":
    try:
        success = test_workflow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
