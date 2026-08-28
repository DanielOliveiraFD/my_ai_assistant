"""Fala de volta via Piper, com troca automática de voz PT/EN conforme o texto."""

import io
import re
import wave

import sounddevice as sd
from langdetect import DetectorFactory, detect
from piper import PiperVoice

from jarvis import config

DetectorFactory.seed = 0  # torna a detecção de idioma determinística

_voice_cache = {}


def _strip_markdown(text: str) -> str:
    """Remove formatação Markdown (negrito, itálico, marcadores de lista,
    títulos, código) antes de falar — sem isso, o Piper lê os símbolos em
    voz alta (ex: "asterisco, asterisco, Hoje, asterisco, asterisco").
    O cérebro é instruído a evitar formatação, mas isso serve de garantia
    mesmo quando ele esquece, como em respostas mais longas."""
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"(?<!\w)_(.*?)_(?!\w)", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[*\-]\s+", "", text, flags=re.MULTILINE)
    return text


def _load_voice(lang: str) -> PiperVoice:
    if lang not in _voice_cache:
        model_path = config.PIPER_VOICES[lang]
        if not model_path.exists():
            raise FileNotFoundError(
                f"Voz Piper não encontrada em {model_path}. Baixe o modelo (ver README)."
            )
        _voice_cache[lang] = PiperVoice.load(str(model_path))
    return _voice_cache[lang]


def _detect_language(text: str) -> str:
    try:
        detected = detect(text)
    except Exception:
        return config.DEFAULT_TTS_LANGUAGE
    return "en" if detected == "en" else "pt"


def speak(text: str):
    if not text:
        return
    text = _strip_markdown(text)
    lang = _detect_language(text)
    voice = _load_voice(lang)

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)
    buffer.seek(0)

    with wave.open(buffer, "rb") as wav_file:
        audio_data = wav_file.readframes(wav_file.getnframes())
        sample_rate = wav_file.getframerate()

    import numpy as np

    samples = np.frombuffer(audio_data, dtype=np.int16)
    sd.play(samples, samplerate=sample_rate)
    sd.wait()
