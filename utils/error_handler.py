import logging

logger = logging.getLogger(__name__)


def classify_api_error(exc):
    message = str(exc).lower()

    if "api key" in message or "authentication" in message or "permission" in message or "forbidden" in message:
        return {
            "user_message": "Gemini API configuration error.\n\nPlease verify your GEMINI_API_KEY in the .env file.",
            "category": "INVALID_API_KEY",
        }

    if "quota" in message or "rate limit" in message or "429" in message or "too many requests" in message:
        return {
            "user_message": "AI request limit reached.\n\nPlease try again later or check your Gemini API quota.",
            "category": "QUOTA_EXCEEDED",
        }

    if "network" in message or "timeout" in message or "connection" in message or "unavailable" in message:
        return {
            "user_message": "AI service is temporarily unavailable.\n\nPlease check your Gemini API configuration or try again later.",
            "category": "NETWORK_ERROR",
        }

    if "model" in message or "not found" in message or "unsupported" in message:
        return {
            "user_message": "AI service is temporarily unavailable.\n\nPlease check your Gemini API configuration or try again later.",
            "category": "MODEL_UNAVAILABLE",
        }

    if "invalid request" in message or "malformed" in message or "bad request" in message:
        return {
            "user_message": "AI service is temporarily unavailable.\n\nPlease check your Gemini API configuration or try again later.",
            "category": "INVALID_REQUEST",
        }

    return {
        "user_message": "AI service is temporarily unavailable.\n\nPlease check your Gemini API configuration or try again later.",
        "category": "AI_ERROR",
    }


def log_error(exc, context: str = "Application error"):
    logger.exception("%s: %s", context, exc)
