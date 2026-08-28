"""Gravação de comando de voz e transcrição via Groq Whisper.

Reaproveita a mesma API key do Groq já usada pelo FreeFlow. A gravação para
assim que detecta silêncio (fim natural da fala) — a lógica de "continua
ouvindo?" fica em jarvis/orchestrator.py, e só entra em ação quando nada foi
capturado, não a cada pausa normal de fim de frase.
"""

import io
import wave

import numpy as np
import sounddevice as sd
from groq import Groq

from jarvis import config

SAMPLE_RATE = 16000
CHUNK_MS = 100
CHUNK_SAMPLES = int(SAMPLE_RATE * CHUNK_MS / 1000)
SILENCE_RMS_THRESHOLD = 300  # ajustar conforme ambiente/microfone real
MAX_RECORDING_SECONDS = 30

_client = Groq(api_key=config.GROQ_API_KEY)


def _rms(chunk: np.ndarray) -> float:
    return float(np.sqrt(np.mean(chunk.astype(np.float64) ** 2)))


def record_command() -> np.ndarray:
    """Grava áudio do microfone até detectar um período de silêncio
    (config.SILENCE_TIMEOUT_SECONDS), indicando que o usuário terminou de
    falar."""
    frames = []
    silence_seconds = 0.0
    total_seconds = 0.0

    with sd.InputStream(
        samplerate=SAMPLE_RATE, channels=1, dtype="int16", blocksize=CHUNK_SAMPLES
    ) as stream:
        while total_seconds < MAX_RECORDING_SECONDS:
            chunk, _ = stream.read(CHUNK_SAMPLES)
            chunk = np.squeeze(chunk)
            frames.append(chunk)
            total_seconds += CHUNK_MS / 1000

            if _rms(chunk) < SILENCE_RMS_THRESHOLD:
                silence_seconds += CHUNK_MS / 1000
            else:
                silence_seconds = 0.0

            if silence_seconds >= config.SILENCE_TIMEOUT_SECONDS:
                break

    return np.concatenate(frames) if frames else np.array([], dtype=np.int16)


def _to_wav_bytes(audio: np.ndarray) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(audio.tobytes())
    return buffer.getvalue()


def transcribe(audio: np.ndarray) -> str:
    if audio.size == 0:
        return ""
    wav_bytes = _to_wav_bytes(audio)
    response = _client.audio.transcriptions.create(
        file=("command.wav", wav_bytes),
        model=config.STT_MODEL,
    )
    return response.text.strip()
