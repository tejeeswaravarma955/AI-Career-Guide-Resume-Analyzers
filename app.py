import os
from typing import Any, Dict, List

from flask import Flask, redirect, render_template, request, session, url_for

from services.career_service import generate_career_plan
from services.gemini_service import AIServiceError
from services.interview_service import generate_interview_report, generate_mock_report, get_questions_for_role
from services.project_service import analyze_project
from services.resume_service import analyze_resume
from utils.error_handler import classify_api_error, log_error
from utils.validators import validate_resume_file

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "career-guide-demo-secret")
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

ROLE_OPTIONS = [
    "Python Developer",
    "Java Developer",
    "Web Developer",
    "Data Analyst",
    "Data Scientist",
    "AI/ML Engineer",
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
]


@app.get("/")
def index():
    return render_template("index.html", roles=ROLE_OPTIONS)


@app.get("/career-guide")
def career_guide():
    return render_template("career_guide.html", roles=ROLE_OPTIONS)


@app.post("/career-guide/generate")
def career_generate():
    payload = {
        "name": request.form.get("name", "Student").strip(),
        "target_career": request.form.get("target_career", "Software Development").strip(),
        "target_role": request.form.get("target_role", "Python Developer").strip(),
        "current_skills": request.form.get("current_skills", "").strip(),
        "available_time": request.form.get("available_time", "2 hours/day").strip(),
        "experience_level": request.form.get("experience_level", "Beginner").strip(),
    }

    if not payload["name"] or not payload["target_role"]:
        return render_template("error.html", message="Please complete the required career details."), 400

    try:
        result = generate_career_plan(payload)
        return render_template("career_result.html", result=result)
    except AIServiceError as exc:
        return render_template("error.html", message=exc.message), 400
    except Exception as exc:
        log_error(exc, "Career generation failed")
        return render_template("error.html", message="AI service is temporarily unavailable. Please check your Gemini API configuration or try again later."), 500


@app.get("/resume-analyzer")
def resume_analyzer():
    return render_template("resume_analyzer.html", roles=ROLE_OPTIONS)


@app.post("/resume-analyzer/analyze")
def resume_analyze():
    target_role = request.form.get("target_role", "Python Developer").strip()
    uploaded_file = request.files.get("resume")
    try:
        filename = validate_resume_file(uploaded_file)
    except ValueError as exc:
        return render_template("error.html", message=str(exc)), 400

    upload_dir = app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"resume_{abs(hash(filename))}_{filename}")
    uploaded_file.save(file_path)

    try:
        result = analyze_resume(file_path, target_role)
        return render_template("resume_result.html", result=result, role=target_role)
    except AIServiceError as exc:
        return render_template("error.html", message=exc.message), 400
    except Exception as exc:
        log_error(exc, "Resume analysis failed")
        return render_template("error.html", message="AI service is temporarily unavailable. Please check your Gemini API configuration or try again later."), 500


@app.get("/interview")
def interview_page():
    return render_template("interview.html", roles=ROLE_OPTIONS)


@app.post("/interview/start")
def interview_start():
    role = request.form.get("job_type", "Python Developer").strip()
    questions = get_questions_for_role(role, count=5)
    session["interview_role"] = role
    session["interview_questions"] = questions
    session["interview_answers"] = []
    session["interview_index"] = 0
    return render_template(
        "interview.html",
        roles=ROLE_OPTIONS,
        role=role,
        question=questions[0],
        question_index=1,
        total_questions=len(questions),
    )


@app.post("/interview/answer")
def interview_answer():
    role = session.get("interview_role", "Python Developer")
    questions = session.get("interview_questions", [])
    answers = session.get("interview_answers", [])
    answer_text = request.form.get("answer", "").strip()
    if answer_text:
        answers.append(answer_text)
        session["interview_answers"] = answers

    current_index = len(answers) - 1 if answer_text else len(answers)
    if current_index < len(questions) - 1:
        next_index = current_index + 1
        session["interview_index"] = next_index
        return render_template(
            "interview.html",
            roles=ROLE_OPTIONS,
            role=role,
            question=questions[next_index],
            question_index=next_index + 1,
            total_questions=len(questions),
        )

    report = generate_interview_report(role, answers)
    session.pop("interview_questions", None)
    session.pop("interview_answers", None)
    return render_template("interview_result.html", result=report, role=role)


@app.get("/mock-interview")
def mock_page():
    return render_template("mock_interview.html", roles=ROLE_OPTIONS)


@app.post("/mock-interview/start")
def mock_start():
    role = request.form.get("job_role", "Python Developer").strip()
    questions = get_questions_for_role(role, count=5)
    session["mock_role"] = role
    session["mock_questions"] = questions
    session["mock_history"] = []
    session["mock_index"] = 0
    return render_template(
        "mock_interview.html",
        roles=ROLE_OPTIONS,
        role=role,
        question=questions[0],
        question_index=1,
        total_questions=len(questions),
    )


@app.post("/mock-interview/answer")
def mock_answer():
    role = session.get("mock_role", "Python Developer")
    questions = session.get("mock_questions", [])
    history = session.get("mock_history", [])
    answer_text = request.form.get("answer", "").strip()
    if answer_text and len(history) < len(questions):
        history.append(f"Q: {questions[len(history)]}\nA: {answer_text}")
        session["mock_history"] = history

    if len(history) < len(questions):
        next_index = len(history)
        return render_template(
            "mock_interview.html",
            roles=ROLE_OPTIONS,
            role=role,
            question=questions[next_index],
            question_index=next_index + 1,
            total_questions=len(questions),
        )

    report = generate_mock_report(role, history)
    session.pop("mock_questions", None)
    session.pop("mock_history", None)
    return render_template("mock_result.html", result=report, role=role)


@app.get("/project-analyzer")
def project_analyzer():
    return render_template("project_analyzer.html")


@app.post("/project-analyzer/analyze")
def project_analyze():
    payload = {
        "title": request.form.get("project_title", "").strip(),
        "description": request.form.get("project_description", "").strip(),
        "technology": request.form.get("technology", "").strip(),
        "target_users": request.form.get("target_users", "Students").strip(),
    }

    if not payload["title"] or not payload["description"]:
        return render_template("error.html", message="Please enter a project title and description."), 400

    try:
        result = analyze_project(payload)
        return render_template("project_analyzer.html", result=result)
    except AIServiceError as exc:
        return render_template("error.html", message=exc.message), 400
    except Exception as exc:
        log_error(exc, "Project analysis failed")
        return render_template("error.html", message="AI service is temporarily unavailable. Please check your Gemini API configuration or try again later."), 500


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/error")
def render_error_page():
    return render_template("error.html", message=request.args.get("message", "Something went wrong."))


@app.errorhandler(404)
def not_found_error(_):
    return render_template("error.html", message="Page not found."), 404


@app.errorhandler(Exception)
def handle_unexpected_error(exc):
    log_error(exc, "Unhandled application error")
    if isinstance(exc, AIServiceError):
        return render_template("error.html", message=exc.message), 400
    friendly = classify_api_error(exc)
    return render_template("error.html", message=friendly["user_message"]), 500


if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)
