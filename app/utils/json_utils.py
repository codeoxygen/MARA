import json
import re


def extract_json(text: str) -> dict:
    """Extract and parse JSON from text, handling markdown code blocks."""
    # Extract JSON from markdown code block if present
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if json_match:
        json_str = json_match.group(1).strip()
    else:
        json_str = text.strip()

    return json.loads(json_str)
