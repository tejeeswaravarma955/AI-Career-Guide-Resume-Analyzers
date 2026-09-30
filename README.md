# AI Career Guide & Resume Analyzer

A responsive Flask app for career planning, resume analysis, mock interviews, and project evaluation.

## Features

- AI-powered 30-day career roadmap generator
- Resume analysis with ATS-style scoring and recommendations
- Interview question flow with role-based evaluation
- AI mock interview simulation
- Project analyzer with feasibility assessment
- Clean responsive UI and modular Flask architecture

## Tech Stack

- Python 3.12+
- Flask
- Gemini API
- PDF/DOCX processing
- JSON data storage

## Installation

```bash
git clone <repository-url>
cd AI-Career-Guide-Resume-Analyzer
pip install -r requirements.txt
```

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

Run the application:

```bash
python app.py
```

Open http://127.0.0.1:5000

## Project Structure

- `app.py` – Flask entry point
- `services/` – AI and business logic
- `utils/` – validators and error handling
- `templates/` – HTML pages
- `static/` – CSS and JavaScript assets
- `data/` – JSON-backed app data
- `uploads/` – uploaded resumes

## Notes

- API keys are never stored in source code
- Gemini failures are handled with user-friendly messages
- Resume uploads are validated for PDF and DOCX only
