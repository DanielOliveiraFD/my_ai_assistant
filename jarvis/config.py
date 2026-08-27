"""Configuração central do Jarvis Caseiro: chaves, caminhos e parâmetros ajustáveis."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

load_dotenv(BASE_DIR.parent / ".env")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# --- Wake word ---
WAKEWORD_MODEL_PATH = MODELS_DIR / "hey_arima.onnx"
WAKEWORD_THRESHOLD = 0.5

# --- STT (Groq Whisper) ---
STT_MODEL = "whisper-large-v3-turbo"

# --- Cérebro (Groq chat) ---
BRAIN_MODEL = "llama-3.3-70b-versatile"
SYSTEM_PROMPT = (
    "Você é o Arima, um assistente pessoal de voz que roda localmente no "
    "computador do usuário. Responda em português ou inglês, no mesmo idioma "
    "em que o usuário falou. Seja direto e breve, como convém a uma resposta "
    "falada em voz alta — evite listas longas ou formatação, prefira frases "
    "curtas e naturais."
)

# --- TTS (Piper) ---
PIPER_VOICES = {
    "pt": MODELS_DIR / "pt_BR-faber-medium.onnx",
    "en": MODELS_DIR / "en_US-lessac-medium.onnx",
}
DEFAULT_TTS_LANGUAGE = "pt"

# --- Escuta inteligente com pausa ---
SILENCE_TIMEOUT_SECONDS = 2.0  # silêncio até perguntar "continua ouvindo?"
FOLLOWUP_PROMPT = {
    "pt": "Continua, estou ouvindo.",
    "en": "Go on, I'm listening.",
}
MAX_FOLLOWUP_ATTEMPTS = 2  # quantas vezes pergunta antes de desistir
