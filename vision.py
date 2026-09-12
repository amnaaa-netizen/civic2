"""
Gemini Vision-based image classification for civic issues.
"""

import os
import google.generativeai as genai
from PIL import Image

# Try loading from .env if available (local dev only)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def classify_issue(image_path: str) -> dict:
    """
    Uses Gemini Vision to classify a civic issue from an image.

    Args:
        image_path: Path to the uploaded image file.

    Returns:
        dict with keys: category, severity, description, confidence, raw
    """
    model = genai.GenerativeModel("gemini-1.5-flash")

    image = Image.open(image_path)

    prompt = """You are a civic issue classifier. Analyze this image and respond ONLY in this exact format:

CATEGORY: <one of: Pothole, Broken Streetlight, Garbage Pile, Water Leak, Fallen Tree, Traffic Signal Issue, Blocked Drain, Other>
SEVERITY: <Low / Medium / High / Critical>
DESCRIPTION: <one sentence describing what you see>
CONFIDENCE: <0-100>

Be precise. If you see a pothole, say Pothole. If you see garbage, say Garbage Pile. Do not add any extra text."""

    response = model.generate_content([prompt, image])
    raw = response.text.strip()

    return parse_vision_response(raw)


def parse_vision_response(raw: str) -> dict:
    """Parse the structured response from Gemini into a dict."""
    result = {
        "category": "Other",
        "severity": "Medium",
        "description": raw,
        "confidence": 0,
        "raw": raw,
    }

    for line in raw.split("\n"):
        line = line.strip()
        if line.startswith("CATEGORY:"):
            result["category"] = line.replace("CATEGORY:", "").strip()
        elif line.startswith("SEVERITY:"):
            result["severity"] = line.replace("SEVERITY:", "").strip()
        elif line.startswith("DESCRIPTION:"):
            result["description"] = line.replace("DESCRIPTION:", "").strip()
        elif line.startswith("CONFIDENCE:"):
            try:
                result["confidence"] = int(
                    line.replace("CONFIDENCE:", "").strip().replace("%", "")
                )
            except ValueError:
                result["confidence"] = 0

    return result
