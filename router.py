"""
Gemini LLM-based department routing (no RAG required).
"""

import os
import google.generativeai as genai

# Try loading from .env if available (local dev only)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def load_departments(file_path: str = "data/departments.txt") -> str:
    """Load departments knowledge base as plain text."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def route_to_department(issue_description: str) -> dict:
    """
    Uses Gemini LLM to route the issue to the correct department.
    The full department knowledge is passed directly in the prompt.

    Args:
        issue_description: Description of the issue (from vision.py).

    Returns:
        dict with keys: department, sla, contact, reason, answer, raw
    """
    departments_text = load_departments()

    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""You are a civic issue router. Here is the complete list of city departments and what they handle:

{departments_text}

A citizen reported this issue:
"{issue_description}"

Based ONLY on the department info above, respond in EXACTLY this format (no extra text):

DEPARTMENT: <exact department name>
SLA_DAYS: <number of days>
CONTACT: <email address>
REASON: <one sentence explaining why this department>"""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    return parse_routing_response(raw)


def parse_routing_response(raw: str) -> dict:
    """Parse the structured routing response from Gemini."""
    result = {
        "department": "General Complaints",
        "sla": "N/A",
        "contact": "info@city.gov.pk",
        "reason": raw,
        "answer": raw,
        "raw": raw,
    }

    for line in raw.split("\n"):
        line = line.strip()
        if line.startswith("DEPARTMENT:"):
            result["department"] = line.replace("DEPARTMENT:", "").strip()
        elif line.startswith("SLA_DAYS:"):
            sla_val = line.replace("SLA_DAYS:", "").strip()
            result["sla"] = f"{sla_val} days"
        elif line.startswith("CONTACT:"):
            result["contact"] = line.replace("CONTACT:", "").strip()
        elif line.startswith("REASON:"):
            result["reason"] = line.replace("REASON:", "").strip()

    result["answer"] = (
        f"Department: {result['department']}\n"
        f"SLA: {result['sla']}\n"
        f"Contact: {result['contact']}\n"
        f"Reason: {result['reason']}"
    )

    return result
