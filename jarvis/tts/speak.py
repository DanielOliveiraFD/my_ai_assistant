"""Fala de volta via Piper, com troca automática de voz PT/EN conforme o texto."""

import io
import wave

import sounddevice as sd
from langdetect import DetectorFactory, detect
from piper import PiperVoice

from jarvis import config

DetectorFactory.seed = 0  # torna a detecção de idioma determinística

_voice_cache = {}


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
