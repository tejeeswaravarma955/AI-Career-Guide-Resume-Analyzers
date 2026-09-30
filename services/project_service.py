from typing import Any, Dict

from services.gemini_service import AIServiceError, generate_structured_json


PROJECT_PROMPT_TEMPLATE = """
You are a product and technical reviewer. Evaluate the following project idea and return valid JSON only.

Project Title: {title}
Project Description: {description}
Technology Used: {technology}
Target Users: {users}

Return JSON with this exact structure:
{{
  "technical_feasibility": "High",
  "problem_clarity": "Good",
  "scalability": "Medium",
  "complexity": "Medium",
  "overall_assessment": "string",
  "problem_statement": "string",
  "target_users": "string",
  "proposed_solution": "string",
  "required_resources": ["string"],
  "potential_challenges": ["string"],
  "uniqueness": "string",
  "missing_features": ["string"],
  "development_complexity": "Medium"
}}

Rules:
- Complexity should be Low, Medium, or High.
- The overall assessment should clearly indicate that success depends on implementation, testing, user adoption, and real-world factors.
- Do not say the project will definitely succeed.
- Keep the assessment practical and realistic.
- JSON only.
"""


def analyze_project(data: Dict[str, Any]) -> Dict[str, Any]:
    fallback = {
        "technical_feasibility": "High",
        "problem_clarity": "Good",
        "scalability": "Medium",
        "complexity": "Medium",
        "overall_assessment": "The project appears technically feasible based on the provided description, but actual success depends on implementation, testing, user adoption and other real-world factors.",
        "problem_statement": "The project addresses a real need for career guidance and project self-assessment using AI-driven recommendations.",
        "target_users": "Students, job seekers, and early-career professionals looking for guidance and career support.",
        "proposed_solution": "The solution combines structured guidance, resume review, interview practice, and project evaluation into one user-friendly platform.",
        "required_resources": ["Python and Flask", "Gemini API access", "HTML/CSS/JS frontend", "Resume processing tools", "Testing and deployment setup"],
        "potential_challenges": ["Handling API rate limits and errors", "Ensuring resume parsing works across file variants", "Improving usability for mobile devices"],
        "uniqueness": "The project blends career planning, interview practice, and project evaluation in a single student-friendly platform.",
        "missing_features": ["User authentication", "Progress tracking dashboards", "Saved resume history", "More advanced analytics"],
        "development_complexity": "Medium",
    }

    prompt = PROJECT_PROMPT_TEMPLATE.format(
        title=data.get("title", "Untitled Project"),
        description=data.get("description", "No description provided."),
        technology=data.get("technology", "Not specified"),
        users=data.get("target_users", "General users"),
    )
    try:
        payload = generate_structured_json(prompt, fallback=fallback)
        if not isinstance(payload, dict):
            return fallback
        for key, value in fallback.items():
            payload.setdefault(key, value)
        return payload
    except AIServiceError:
        return fallback
