import requests
import time
import urllib3
import ssl
from utils.logger import setup_logger

urllib3.disable_warnings()

logger = setup_logger()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"


class GroqClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

        # Force TLS 1.2
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        self.session.mount("https://", adapter)

    def chat(self, prompt: str, system: str = None, max_tokens: int = 2000) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.3,
        }

        for attempt in range(4):
            try:
                response = self.session.post(
                    GROQ_API_URL,
                    json=payload,
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()
                time.sleep(2)
                return data["choices"][0]["message"]["content"]

            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    wait = 10 * (attempt + 1)
                    logger.warning(f"⏳ Rate limited. Waiting {wait}s... retry {attempt+1}/4")
                    time.sleep(wait)
                else:
                    logger.error(f"❌ Groq API error: {e}")
                    raise

            except Exception as e:
                wait = 5 * (attempt + 1)
                logger.warning(f"⏳ Connection error. Waiting {wait}s... retry {attempt+1}/4")
                time.sleep(wait)

        raise Exception("❌ Groq API failed after 4 retries")