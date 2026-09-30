import json
import logging
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from google import genai

from utils.error_handler import classify_api_error

load_dotenv()
logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    def __init__(self, message: str, category: str = "AI_ERROR"):
        super().__init__(message)
        self.message = message
        self.category = category


def get_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "YOUR_GEMINI_API_KEY":
        raise AIServiceError(
            "Gemini API configuration error. Please verify your GEMINI_API_KEY in the .env file.",
            category="INVALID_API_KEY",
        )
    return api_key


def get_client() -> genai.Client:
    api_key = get_api_key()
    return genai.Client(api_key=api_key)


def extract_text_from_response(response: Any) -> str:
    if hasattr(response, "text") and response.text:
        return response.text

    if hasattr(response, "candidates"):
        for candidate in response.candidates:
            if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                segments = []
                for part in candidate.content.parts:
                    if hasattr(part, "text") and part.text:
                        segments.append(part.text)
                if segments:
                    return "\n".join(segments)

    return ""


def parse_json_payload(raw_text: str, fallback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        if fallback is not None:
            return fallback
        raise AIServiceError("AI response could not be parsed. Please try again later.")


def generate_structured_json(prompt: str, fallback: Optional[Dict[str, Any]] = None, model: str = "gemini-2.0-flash") -> Dict[str, Any]:
    try:
        client = get_client()
        response = client.models.generate_content(model=model, contents=prompt)
        text = extract_text_from_response(response)
        if not text:
            if fallback is not None:
                return fallback
            raise AIServiceError("AI service returned no usable response.")
        return parse_json_payload(text, fallback=fallback)
    except AIServiceError:
        raise
    except Exception as exc:
        logger.exception("Gemini JSON generation failed")
        friendly = classify_api_error(exc)
        raise AIServiceError(friendly["user_message"], category=friendly["category"]) from exc


def generate_text(prompt: str, fallback: str = "", model: str = "gemini-2.0-flash") -> str:
    try:
        client = get_client()
        response = client.models.generate_content(model=model, contents=prompt)
        text = extract_text_from_response(response)
        if text:
            return text
        return fallback
    except AIServiceError:
        raise
    except Exception as exc:
        logger.exception("Gemini text generation failed")
        friendly = classify_api_error(exc)
        raise AIServiceError(friendly["user_message"], category=friendly["category"]) from exc
