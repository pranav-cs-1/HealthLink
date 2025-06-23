# dashboard/singletons.py
import threading
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SingletonMeta(type):
    _instances = {}
    _lock = threading.Lock()
    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class GeminiClient(metaclass=SingletonMeta):
    """
    Thread‑safe singleton wrapper around requests to the Gemini API.
    """
    def __init__(self):
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    def describe_medication(self, medication_name: str) -> str:
        url = f"{self.base_url}?key={settings.GEMINI_API_KEY}"

        payload = {
            "contents": [{
                "parts": [{"text": f"Write a short, one-sentence description of what {medication_name} is."}]
            }]
        }

        headers = {
            "Content-Type": "application/json",
        }

        logger.debug(f"Making request to Gemini API: {url}")
        resp = requests.post(url, json=payload, headers=headers)
        resp.raise_for_status()

        data = resp.json()
        logger.debug(f"Received response from Gemini API: {data}")

        # Extract the generated text from the Gemini API response
        generated_text = ""
        if "candidates" in data and len(data["candidates"]) > 0:
            candidate = data["candidates"][0]
            content = candidate.get("content", {})
            parts = content.get("parts", [])
            if parts:
                # Join all parts' text (if more than one part) or just use the first
                generated_text = "".join(part.get("text", "") for part in parts).strip()

        if not generated_text:
            logger.warning("No generated text found in the response.")
            return f"{medication_name} is a medication used to treat specific conditions."

        return generated_text