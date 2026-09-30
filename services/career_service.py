import json
from typing import Any, Dict, List

from services.gemini_service import AIServiceError, generate_structured_json


def build_career_prompt(data: Dict[str, Any]) -> str:
    return f"""
You are a career counselor for students and job seekers. Generate valid JSON only.

User data:
- Name: {data.get('name', 'Student')}
- Target Career: {data.get('target_career', 'Software Development')}
- Target Role: {data.get('target_role', 'Python Developer')}
- Current Skills: {data.get('current_skills', '')}
- Available Time Per Day: {data.get('available_time', '2 hours/day')}
- Experience Level: {data.get('experience_level', 'Beginner')}

Return a JSON object with this exact structure:
{{
  "name": "string",
  "target_career": "string",
  "target_role": "string",
  "experience_level": "string",
  "available_time": "string",
  "time_plan": {{
    "summary": "string",
    "focus": ["string"]
  }},
  "plan": [
    {{
      "day": 1,
      "topic": "string",
      "learn": ["string"],
      "why_it_matters": "string",
      "task": "string",
      "exercise": "string",
      "estimated_time": "string",
      "resources": [
        {{"name": "string", "description": "string", "platform": "string", "url": "string"}}
      ]
    }}
  ],
  "resources": [
    {{"name": "string", "description": "string", "platform": "string", "url": "string"}}
  ]
}}

Rules:
- Create a 30-day roadmap.
- The daily workload must adapt to available time.
- Keep the output practical and beginner-friendly.
- For every major topic, provide learning resources.
- Use only real and reliable resource names and URLs where available.
- If a URL is not known, return empty string for the URL field.
- Do not invent fake URLs.
- Do not include markdown or extra text outside JSON.
"""


def build_fallback_plan(data: Dict[str, Any]) -> Dict[str, Any]:
    name = data.get("name", "Student")
    target_role = data.get("target_role", "Python Developer")
    experience = data.get("experience_level", "Beginner")
    available_time = data.get("available_time", "2 hours/day")
    time_value = 2
    try:
        digits = ''.join(ch for ch in str(available_time) if ch.isdigit())
        if digits:
            time_value = int(digits[:1]) if digits else 2
    except ValueError:
        time_value = 2

    time_plan = {
        "summary": f"This roadmap fits a {available_time} schedule and emphasizes building skills through focused practice.",
        "focus": [
            "Core learning",
            "Small exercises",
            "Practical implementation",
            "Portfolio improvement",
            "Interview readiness",
        ] if time_value >= 3 else [
            "Core learning",
            "Small exercises",
            "Practical implementation",
        ]
    }

    topics = [
        "Python fundamentals",
        "Data structures",
        "Functions and modules",
        "Web basics",
        "Databases",
        "API development",
        "Version control",
        "Project building",
        "Resume optimization",
        "Interview preparation",
    ]

    plan = []
    for i in range(1, 31):
        topic = topics[(i - 1) % len(topics)]
        exercise = "Create a small script or mini project tied to the topic."
        if i % 5 == 0:
            exercise = "Build a small portfolio project demonstrating the concepts learned this week."
        if i % 10 == 0:
            exercise = "Review your progress and prepare a short self-introduction for interviews."

        plan.append({
            "day": i,
            "topic": topic,
            "learn": [
                "Core concepts",
                "Hands-on practice",
                "Common mistakes",
            ],
            "why_it_matters": "This topic strengthens the foundations needed for real-world work and interview confidence.",
            "task": f"Practice the topic through a short daily exercise that connects directly to the {target_role} role.",
            "exercise": exercise,
            "estimated_time": f"{1.5 if time_value <= 2 else 2.5} hours" if time_value >= 2 else "1 hour",
            "resources": [
                {"name": "Official Documentation", "description": "Core reference material for the topic.", "platform": "Official docs", "url": ""},
                {"name": "YouTube Tutorial", "description": "Video walkthrough for beginners.", "platform": "YouTube", "url": ""},
                {"name": "Practice Platform", "description": "Hands-on exercises to reinforce learning.", "platform": "Coding practice website", "url": ""},
            ],
        })

    resources = [
        {"name": "Python Official Documentation", "description": "Language reference and tutorials.", "platform": "Python.org", "url": "https://docs.python.org/3/"},
        {"name": "W3Schools", "description": "Beginner-friendly website for web and programming basics.", "platform": "W3Schools", "url": "https://www.w3schools.com/"},
        {"name": "freeCodeCamp", "description": "Free structured learning path for coding and web development.", "platform": "freeCodeCamp", "url": "https://www.freecodecamp.org/"},
        {"name": "Coursera", "description": "Free course options for foundational learning.", "platform": "Coursera", "url": "https://www.coursera.org/"},
    ]

    return {
        "name": name,
        "target_career": data.get("target_career", "Software Development"),
        "target_role": target_role,
        "experience_level": experience,
        "available_time": available_time,
        "time_plan": time_plan,
        "plan": plan,
        "resources": resources,
    }


def generate_career_plan(data: Dict[str, Any]) -> Dict[str, Any]:
    fallback = build_fallback_plan(data)
    try:
        payload = generate_structured_json(build_career_prompt(data), fallback=fallback)
        if not isinstance(payload, dict):
            return fallback
        if "plan" not in payload or not isinstance(payload.get("plan", []), list):
            payload["plan"] = fallback["plan"]
        if "resources" not in payload or not isinstance(payload.get("resources", []), list):
            payload["resources"] = fallback["resources"]
        if "time_plan" not in payload:
            payload["time_plan"] = fallback["time_plan"]
        return payload
    except AIServiceError:
        return fallback
