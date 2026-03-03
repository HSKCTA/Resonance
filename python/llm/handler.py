import requests
import logging
import time
import threading
import os
import tempfile
from abc import ABC, abstractmethod

logger = logging.getLogger("LLM")

# Language rotation: cycles through en → hi → mr
LANGUAGES = ["en", "hi", "mr"]
LANG_NAMES = {"en": "English", "hi": "Hindi", "mr": "Marathi"}

# Healthy baseline (from calibration)
HEALTHY_RMS = 0.303
HEALTHY_MSE = 0.0009


# ─────────────────────────────────────────────
#  Abstract provider — swap in any backend
# ─────────────────────────────────────────────

class LLMProvider(ABC):
    """Base class for all LLM backends."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Send a prompt and return the model's text response."""
        pass

    @abstractmethod
    def check_connection(self) -> bool:
        """Return True if the backend is reachable."""
        pass


# ─────────────────────────────────────────────
#  Local LLM — OpenAI-compatible endpoint
#  Works with: Ollama, llama.cpp, vLLM, LM Studio
# ─────────────────────────────────────────────

class LocalLLM(LLMProvider):
    """Talks to any local server that exposes /v1/chat/completions."""

    DEFAULT_URL = "http://localhost:11434/v1/chat/completions"
    # Groq testing used llama-3.1-8b-instant → Ollama equivalent is llama3.1:8b
    DEFAULT_MODEL = "llama3.1:8b"

    def __init__(self, url: str | None = None, model: str | None = None):
        self.url = url or os.environ.get("LLM_URL", self.DEFAULT_URL)
        self.model = model or os.environ.get("LLM_MODEL", self.DEFAULT_MODEL)
        self.api_key = os.environ.get("LLM_API_KEY", "")

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def generate(self, prompt: str) -> str:
        """Send a chat-completion request and return the assistant message."""
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 80,
            "temperature": 0.3,
        }
        resp = requests.post(
            self.url, headers=self._headers(), json=payload, timeout=30
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()

    def generate_chat(self, messages: list[dict], **kwargs) -> str:
        """Send a full messages list (system + user) and return the response."""
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 80),
            "temperature": kwargs.get("temperature", 0.3),
        }
        resp = requests.post(
            self.url, headers=self._headers(), json=payload, timeout=30
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()

    def check_connection(self) -> bool:
        try:
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 5,
            }
            resp = requests.post(
                self.url, headers=self._headers(), json=payload, timeout=15
            )
            if resp.status_code == 200:
                logger.info(f"Connected to LLM ({self.url}, model: {self.model})")
                return True
            logger.warning(f"LLM returned {resp.status_code}: {resp.text[:200]}")
            return False
        except requests.exceptions.ConnectionError:
            logger.warning(
                f"LLM unreachable at {self.url} — "
                f"start your local server (e.g. 'ollama serve')"
            )
            return False
        except Exception as e:
            logger.warning(f"LLM connection check failed: {e}")
            return False


# ─────────────────────────────────────────────
#  LLMHandler — alert logic, diagnosis, TTS
#  Uses any LLMProvider under the hood
# ─────────────────────────────────────────────

class LLMHandler:
    """High-level fault alert generator with diagnosis + TTS."""

    def __init__(self, provider: LLMProvider | None = None):
        self.provider = provider or LocalLLM()
        self._last_alert_time = 0
        self._cooldown = 10
        self._lang_index = 0
        self._audio_ready = False

    # ── public API (used by main.py) ─────────

    def check_connection(self) -> bool:
        return self.provider.check_connection()

    def warmup(self):
        p = self.provider
        if isinstance(p, LocalLLM):
            logger.info(f"LLM endpoint: {p.url} (model: {p.model})")
        else:
            logger.info("LLM provider ready.")

    def generate_alert(self, anomaly_score, detection_details):
        """Generate a worker-friendly alert with motor-specific diagnosis."""
        if not self._should_alert():
            return None

        severity = detection_details.get("severity", "Unknown")
        rms = detection_details.get("rms", 0.0)
        lang = self._get_next_lang()
        lang_name = LANG_NAMES.get(lang, "English")
        diagnosis = self._diagnose(anomaly_score, rms)

        if lang == "en":
            lang_instruction = "Reply in English."
        elif lang == "hi":
            lang_instruction = (
                "Reply in Hindi (Devanagari script). "
                "Example: 'मोटर बेयरिंग की तुरंत जांच करें, शाफ्ट असंतुलन हो सकता है।'"
            )
        else:
            lang_instruction = (
                "Reply in Marathi (Devanagari script). "
                "Example: 'मोटर बेअरिंग ताबडतोब तपासा, शाफ्ट असंतुलन असू शकतो।'"
            )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an industrial AI assistant monitoring a 12V DC motor "
                    "via a vibration sensor (Logitech G430 headset used as accelerometer). "
                    "The autoencoder compares current vibration to baseline healthy vibration. "
                    "Based on the diagnosis below, write ONE short sentence (under 25 words) "
                    "telling the factory worker what specific physical check to do on the MOTOR. "
                    "Mention specific parts: bearings, shaft, coupling, load, belt, mounting bolts. "
                    "Do NOT mention conveyor belts, hydraulic lines, or unrelated machines. "
                    + lang_instruction
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Severity: {severity} | "
                    f"MSE: {anomaly_score:.4f} (healthy: {HEALTHY_MSE}) | "
                    f"RMS: {rms:.4f} (healthy: {HEALTHY_RMS}) | "
                    f"Diagnosis: {diagnosis}"
                ),
            },
        ]

        try:
            text = self.provider.generate_chat(messages)
            text = text.split("\n")[0].strip().strip('"')
            if text:
                logger.info(f"LLM alert [{lang_name}]: {text}")
                self.speak_alert(text, lang=lang)
                return text
        except Exception as e:
            logger.error(f"LLM query failed: {e}")

        fallback = f"FAULT DETECTED — {severity}. Check motor bearings and shaft immediately."
        self.speak_alert(fallback, lang="en")
        return fallback

    def speak_alert(self, text, lang="en"):
        """Speak alert using Google TTS. Falls back to console print if audio fails."""
        def _speak():
            try:
                if not self._ensure_audio():
                    logger.info(f"[ALERT] {text}")
                    return
                from gtts import gTTS
                import pygame

                tts = gTTS(text=text, lang=lang, slow=False)
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    tmp_path = f.name
                    tts.save(tmp_path)

                pygame.mixer.music.load(tmp_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

                os.unlink(tmp_path)
            except Exception as e:
                logger.warning(f"TTS failed ({e}) — alert text: {text}")

        t = threading.Thread(target=_speak, daemon=False)
        t.start()

    # ── internal helpers ─────────────────────

    def _ensure_audio(self):
        if self._audio_ready:
            return True
        try:
            import pygame
            pygame.mixer.init()
            self._audio_ready = True
            logger.info("Audio playback initialized (pygame + gTTS)")
            return True
        except Exception as e:
            logger.warning(f"Audio init failed: {e}")
            return False

    def _should_alert(self):
        now = time.time()
        if now - self._last_alert_time >= self._cooldown:
            self._last_alert_time = now
            return True
        return False

    def _get_next_lang(self):
        lang = LANGUAGES[self._lang_index % len(LANGUAGES)]
        self._lang_index += 1
        return lang

    def _diagnose(self, mse, rms):
        hints = []
        rms_ratio = rms / HEALTHY_RMS if HEALTHY_RMS > 0 else 0
        if rms < 0.02:
            hints.append("RMS is near zero — motor may be stopped or sensor detached")
        elif rms_ratio < 0.5:
            hints.append(f"RMS dropped to {rms:.3f} (healthy: {HEALTHY_RMS:.3f}) — possible physical load/obstruction")
        elif rms_ratio > 1.5:
            hints.append(f"RMS spiked to {rms:.3f} (healthy: {HEALTHY_RMS:.3f}) — possible shaft imbalance or bearing wear")
        else:
            hints.append(f"RMS is {rms:.3f} (near healthy {HEALTHY_RMS:.3f}) — possible bearing misalignment")

        mse_ratio = mse / HEALTHY_MSE if HEALTHY_MSE > 0 else 0
        if mse_ratio > 10:
            hints.append(f"MSE is {mse_ratio:.0f}× above healthy — severe anomaly")
        elif mse_ratio > 3:
            hints.append(f"MSE is {mse_ratio:.1f}× above healthy — moderate anomaly")

        return "; ".join(hints)


# ─── CLI self-test ───────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    handler = LLMHandler()
    if handler.check_connection():
        for _ in range(3):
            alert = handler.generate_alert(0.019, {"severity": "HIGH", "rms": 0.007})
            if alert:
                print(f"Alert: {alert}")
            time.sleep(12)
    else:
        llm = handler.provider
        print(f"LLM not reachable at {llm.url}")
        print("Start your local server, e.g.:")
        print("  ollama serve          # then: ollama pull llama3.1:8b")
        print("  # or set LLM_URL / LLM_MODEL env vars")
