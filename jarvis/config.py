"""Configuração central do Jarvis Caseiro: chaves, caminhos e parâmetros ajustáveis."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

load_dotenv(BASE_DIR.parent / ".env")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# --- Wake word ---
WAKEWORD_MODEL_PATH = MODELS_DIR / "ok_nyx.onnx"
WAKEWORD_THRESHOLD = 0.5

# --- STT (Groq Whisper) ---
STT_MODEL = "whisper-large-v3-turbo"

# --- Cérebro (provedor de IA) ---
# Módulo isolado em jarvis/brain/ — trocar de provedor no futuro não exige
# mexer em wake word, STT, TTS ou automações. Ver jarvis/brain/factory.py.
AI_PROVIDER = "groq"
SYSTEM_PROMPT = (
    "Você é o Nyx, um assistente pessoal de voz que roda localmente no "
    "computador do usuário. Responda em português ou inglês, no mesmo idioma "
    "em que o usuário falou. Seja direto e breve, como convém a uma resposta "
    "falada em voz alta — evite listas longas ou formatação, prefira frases "
    "curtas e naturais. Quando fizer sentido, ofereça proativamente um "
    "próximo passo útil relacionado ao pedido (ex: perguntar a fonte ao "
    "resumir algo, sugerir revisar antes de enviar uma mensagem) — sem "
    "exagerar, só quando a sugestão realmente agregar."
)

# --- Memória de longo prazo (SQLite local) ---
MEMORY_DB_PATH = BASE_DIR / "memory.sqlite3"

# --- TTS (Piper) ---
PIPER_VOICES = {
    "pt": MODELS_DIR / "pt_BR-cadu-medium.onnx",
    "en": MODELS_DIR / "en_US-lessac-medium.onnx",
}
DEFAULT_TTS_LANGUAGE = "pt"

# --- Detecção de fim de fala ---
SILENCE_TIMEOUT_SECONDS = 1.2  # silêncio até considerar que terminou de falar
# "Continua, estou ouvindo?" só é usado quando NADA foi capturado (silêncio
# total após o wake word) — não a cada pausa normal de fim de frase.
FOLLOWUP_PROMPT = {
    "pt": "Continua, estou ouvindo.",
    "en": "Go on, I'm listening.",
}
MAX_FOLLOWUP_ATTEMPTS = 2  # quantas vezes pergunta antes de desistir

# --- Janela de acompanhamento (pós-resposta) ---
# Depois de falar a resposta, escuta por esse tempo sem exigir o wake word
# de novo. Se o usuário começar a falar dentro da janela, processa normal
# (com o corte de fim de frase de sempre); se passar em silêncio total,
# volta a exigir "Ok Nyx".
FOLLOWUP_LISTEN_SECONDS = 5.0
