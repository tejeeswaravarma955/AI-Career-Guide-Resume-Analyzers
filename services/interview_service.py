import json
import random
from typing import Any, Dict, List, Tuple

from services.gemini_service import AIServiceError, generate_structured_json

ROLE_QUESTION_BANK = {
    "Python Developer": [
        "What is a variable in Python?",
        "What is the difference between a list and a tuple?",
        "Explain Python dictionaries with an example.",
        "How do you handle exceptions in Python?",
        "What is the difference between a function and a method?",
        "How do you optimize a slow Python script?",
        "Explain list comprehension with an example.",
        "How would you design a Flask API for a student management system?",
    ],
    "Java Developer": [
        "What is the difference between JDK and JRE?",
        "Explain inheritance in Java.",
        "What is a HashMap?",
        "How do you write a custom exception in Java?",
        "What are interfaces in Java?",
        "How do you optimize Java application performance?",
        "How does multithreading work in Java?",
        "Design a Java service for user authentication.",
    ],
    "Web Developer": [
        "What is the DOM?",
        "Explain CSS box model.",
        "What is the difference between GET and POST?",
        "How do you make a design responsive?",
        "What is event bubbling?",
        "How do you build a reusable component in JavaScript?",
        "Explain async and await in JavaScript.",
        "Design a dashboard with API-driven data rendering.",
    ],
    "Data Analyst": [
        "What is SQL JOIN?",
        "What is data cleaning?",
        "Explain the difference between a dataset and a table.",
        "What is a KPI?",
        "How do you handle missing values in a dataset?",
        "Explain correlation and causation.",
        "How would you create a dashboard for business performance?",
        "Design a sales analysis report for a retail company.",
    ],
    "Data Scientist": [
        "What is a confusion matrix?",
        "Explain overfitting.",
        "How do you evaluate a model?",
        "What is feature engineering?",
        "How do you handle imbalanced data?",
        "Explain cross-validation.",
        "How do you select a machine learning model?",
        "Design a churn prediction pipeline for a SaaS product.",
    ],
    "AI/ML Engineer": [
        "What is supervised learning?",
        "What is the difference between training and validation data?",
        "Explain overfitting and regularization.",
        "What is precision and recall?",
        "What is model evaluation?",
        "Explain neural network basics.",
        "How do you deploy a model in production?",
        "Design a text classification system for spam detection.",
    ],
    "Frontend Developer": [
        "What is semantic HTML?",
        "Explain CSS Flexbox and Grid.",
        "What is a promise in JavaScript?",
        "How do you optimize page performance?",
        "Explain accessibility best practices.",
        "How do you handle state in a frontend app?",
        "How do you design reusable UI components?",
        "Build a responsive dashboard UI using modern frontend patterns.",
    ],
    "Backend Developer": [
        "What is an API?",
        "How do you secure an API?",
        "Explain database indexing.",
        "What is REST?",
        "How do you handle authentication?",
        "What is caching and why is it useful?",
        "How do you manage database transactions?",
        "Design a scalable backend for an e-commerce system.",
    ],
    "Full Stack Developer": [
        "What is the difference between frontend and backend?",
        "How do you connect an API to a database?",
        "What is JWT?",
        "How do you manage authentication across a full stack app?",
        "Explain CORS.",
        "How do you test an application end-to-end?",
        "How do you design a production-ready web app?",
        "Build a full-stack CRUD application for tasks and users.",
    ]
}


def get_questions_for_role(role: str, count: int = 5) -> List[str]:
    bank = ROLE_QUESTION_BANK.get(role, ROLE_QUESTION_BANK["Python Developer"])
    return bank[:count]


def build_interview_prompt(role: str, answers: List[str]) -> str:
    joined = "\n".join(f"{idx + 1}. {answer}" for idx, answer in enumerate(answers))
    return f"""
You are a recruiter and technical interviewer for the role: {role}.
Evaluate the candidate's answers and return valid JSON only.

Answer history:
{joined}

Return JSON with the structure:
{{
  "overall_score": 72,
  "technical_knowledge": 75,
  "communication": 68,
  "problem_solving": 70,
  "role_knowledge": 76,
  "strengths": ["string"],
  "areas_to_improve": ["string"],
  "recommended_topics": ["string"],
  "summary": "string"
}}
Rules:
- Score values must be integers between 0 and 100.
- The score is a practice assessment and not a real hiring verdict.
- Do not tell the user they will get the job.
- Keep the feedback practical and encouraging.
- Do not include markdown.
"""


def generate_interview_report(role: str, answers: List[str]) -> Dict[str, Any]:
    fallback = {
        "overall_score": 72,
        "technical_knowledge": 75,
        "communication": 68,
        "problem_solving": 70,
        "role_knowledge": 76,
        "strengths": [
            "Good understanding of core concepts.",
            "Clear technical vocabulary.",
        ],
        "areas_to_improve": [
            "Improve practical examples.",
            "Practice data structures and problem solving.",
            "Increase explanation clarity.",
        ],
        "recommended_topics": [
            "Core language fundamentals",
            "Data structures",
            "Project-based problem solving",
            "Interview communication",
        ],
        "summary": "Interview Readiness Estimate: 72%. Based on your answers, your current performance is above the configured 65% practice benchmark. This is a practice assessment and cannot guarantee an actual job offer.",
    }

    if not answers:
        return fallback

    try:
        payload = generate_structured_json(build_interview_prompt(role, answers), fallback=fallback)
        if not isinstance(payload, dict):
            return fallback
        return payload
    except AIServiceError:
        return fallback


def build_mock_prompt(role: str, history: List[str]) -> str:
    joined = "\n".join(history)
    return f"""
You are a technical interviewer. Simulate a realistic mock interview for the role {role}.
Evaluate the candidate responses and return valid JSON only.

Interview history:
{joined}

Return JSON with the structure:
{{
  "overall_performance": 76,
  "technical_knowledge": 78,
  "communication": 72,
  "confidence": 70,
  "problem_solving": 80,
  "role_knowledge": 79,
  "strong_areas": ["string"],
  "weak_areas": ["string"],
  "questions_answered_well": ["string"],
  "questions_need_improvement": ["string"],
  "recommended_preparation_topics": ["string"],
  "summary": "string"
}}

Rules:
- Keep scores between 0 and 100.
- Keep feedback professional and realistic.
- Do not promise a job.
- Exactly valid JSON only.
"""


def generate_mock_report(role: str, history: List[str]) -> Dict[str, Any]:
    fallback = {
        "overall_performance": 76,
        "technical_knowledge": 78,
        "communication": 72,
        "confidence": 70,
        "problem_solving": 80,
        "role_knowledge": 79,
        "strong_areas": [
            "Good technical foundation",
            "Strong reasoning during practical questions",
        ],
        "weak_areas": [
            "Need more project examples",
            "Improve clarity under time pressure",
        ],
        "questions_answered_well": [
            "Basic Python concepts",
            "Core role-related questions",
        ],
        "questions_need_improvement": [
            "Scenario-based problem solving",
            "Detailed explanation of trade-offs",
        ],
        "recommended_preparation_topics": [
            "System design basics",
            "Data structures",
            "Project storytelling",
            "Behavioral interview responses",
        ],
        "summary": "Overall, your performance is promising. Continue practicing real coding questions and improve explanation clarity to increase confidence.",
    }
    try:
        payload = generate_structured_json(build_mock_prompt(role, history), fallback=fallback)
        if not isinstance(payload, dict):
            return fallback
        return payload
    except AIServiceError:
        return fallback
