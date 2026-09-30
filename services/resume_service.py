import os
from typing import Any, Dict, List

from pypdf import PdfReader
from docx import Document

from services.gemini_service import AIServiceError, generate_structured_json


def extract_resume_text(file_path: str) -> str:
    extension = os.path.splitext(file_path)[1].lower()
    if extension == '.pdf':
        reader = PdfReader(file_path)
        pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)
        return "\n".join(pages)
    if extension == '.docx':
        doc = Document(file_path)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(paragraphs)
    return ""


def build_resume_prompt(target_role: str, resume_text: str) -> str:
    return f"""
You are an expert hiring counselor and ATS reviewer. Analyze the resume text below against the target role: {target_role}.

Return valid JSON only using this structure:
{{
  "score": 78,
  "category_scores": {{
    "Keyword Match": 20,
    "Skills Match": 18,
    "Experience": 15,
    "Projects": 12,
    "Formatting": 8,
    "Education": 5
  }},
  "strengths": ["string"],
  "weaknesses": ["string"],
  "recommended_skills": ["string"],
  "certifications_to_consider": ["string"],
  "keywords_to_add": ["string"],
  "resume_changes": ["string"],
  "job_portals": [
    {{"name": "string", "why": "string", "relevance": "string", "url": "string"}}
  ],
  "summary": "string"
}}

Rules:
- Keep total score between 0 and 100.
- The score is an estimate based on resume quality and role fit, not a guaranteed ATS result.
- Do not invent fake URLs.
- If a real official URL is uncertain, use an empty string for the URL.
- Do not tell the user they will definitely get the job.
- Resume text:
{resume_text[:8000]}
"""


def fallback_resume_result(target_role: str, resume_text: str) -> Dict[str, Any]:
    text = (resume_text or "").lower()
    role_keywords = {
        "Python Developer": ["python", "flask", "django", "sql", "api", "rest", "git", "oop"],
        "Java Developer": ["java", "spring", "sql", "oop", "rest", "maven", "git"],
        "Web Developer": ["html", "css", "javascript", "responsive", "api", "git", "frontend"],
        "Data Analyst": ["sql", "python", "excel", "power bi", "statistics", "dashboard"],
        "Data Scientist": ["python", "machine learning", "statistics", "sql", "pandas", "numpy"],
        "AI/ML Engineer": ["python", "machine learning", "deep learning", "tensorflow", "pytorch", "nlp"],
        "Frontend Developer": ["html", "css", "javascript", "react", "ui", "ux"],
        "Backend Developer": ["api", "python", "sql", "node", "spring", "database"],
        "Full Stack Developer": ["javascript", "html", "css", "api", "sql", "frontend", "backend"],
    }
    matched = [kw for kw in role_keywords.get(target_role, []) if kw in text]
    missing = [kw for kw in role_keywords.get(target_role, []) if kw not in text][:5]

    score = max(55, min(92, 70 + len(matched) * 3))
    category_scores = {
        "Keyword Match": min(25, max(10, 12 + len(matched))),
        "Skills Match": min(20, max(8, 10 + len(matched) // 2)),
        "Experience": 15,
        "Projects": 12,
        "Formatting": 8,
        "Education": 5,
    }
    total = sum(category_scores.values())

    result = {
        "score": int(round(min(100, total))),
        "category_scores": category_scores,
        "strengths": [
            "Resume includes relevant career experience and educational background.",
            "The document is structured enough to be reviewed with clear sections.",
        ],
        "weaknesses": [
            "Add more targeted keywords matching the target role.",
            "Show measurable achievements in projects and experience sections.",
            "Include a stronger summary aligned with the role.",
        ],
        "recommended_skills": role_keywords.get(target_role, [])[:5],
        "certifications_to_consider": [
            "Python",
            "SQL",
            "Cloud",
            "Data Structures",
            "Git",
        ][:5],
        "keywords_to_add": missing if missing else role_keywords.get(target_role, [])[:5],
        "resume_changes": [
            "Improve professional summary and align it to the target role.",
            "Add measurable project achievements with tools, impact, and outcomes.",
            "Add technical keywords relevant to the role in the skills and experience sections.",
            "Remove unnecessary or outdated information that reduces clarity.",
            "Improve project descriptions by documenting the problem, solution, and result.",
        ],
        "job_portals": [
            {"name": "LinkedIn", "why": "Strong for professional networking and role-based job boards.", "relevance": "High", "url": "https://www.linkedin.com/jobs/"},
            {"name": "Indeed", "why": "Useful for broad job listings across companies and roles.", "relevance": "High", "url": "https://www.indeed.com/"},
            {"name": "Naukri", "why": "Popular for Indian job opportunities and recruiter matching.", "relevance": "High", "url": "https://www.naukri.com/"},
            {"name": "Glassdoor", "why": "Helps review company hiring trends and job posts.", "relevance": "Medium", "url": "https://www.glassdoor.com/"},
        ],
        "summary": "Your ATS score is an estimate based on the target role and resume content. Different companies use different ATS systems and scoring methods.",
    }
    return result


def analyze_resume(file_path: str, target_role: str) -> Dict[str, Any]:
    resume_text = extract_resume_text(file_path)
    fallback = fallback_resume_result(target_role, resume_text)
    prompt = build_resume_prompt(target_role, resume_text)
    try:
        payload = generate_structured_json(prompt, fallback=fallback)
        if not isinstance(payload, dict):
            return fallback
        payload.setdefault("summary", fallback["summary"])
        payload.setdefault("score", fallback["score"])
        payload.setdefault("category_scores", fallback["category_scores"])
        return payload
    except AIServiceError:
        return fallback
