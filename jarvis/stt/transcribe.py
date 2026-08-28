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


def record_command(pre_speech_timeout: float | None = None, stop_event=None) -> np.ndarray:
    """Grava áudio do microfone até detectar silêncio depois do usuário falar.

    `pre_speech_timeout` é quanto tempo esperar em silêncio ANTES do usuário
    começar a falar, antes de desistir (retorna áudio vazio) — usado na
    janela de acompanhamento pós-resposta, que é mais longa que o padrão.
    Se None, usa config.SILENCE_TIMEOUT_SECONDS (comportamento padrão logo
    após o wake word). Depois que a fala começa, sempre usa
    config.SILENCE_TIMEOUT_SECONDS como corte de silêncio de fim de frase.

    `stop_event`, se marcado no meio da gravação, interrompe e retorna o que
    já foi capturado até então (usado pelo app de barra de menu).
    """
    if pre_speech_timeout is None:
        pre_speech_timeout = config.SILENCE_TIMEOUT_SECONDS

    frames = []
    silence_seconds = 0.0
    total_seconds = 0.0
    has_spoken = False

    with sd.InputStream(
        samplerate=SAMPLE_RATE, channels=1, dtype="int16", blocksize=CHUNK_SAMPLES
    ) as stream:
        while total_seconds < MAX_RECORDING_SECONDS:
            if stop_event is not None and stop_event.is_set():
                break
            chunk, _ = stream.read(CHUNK_SAMPLES)
            chunk = np.squeeze(chunk)
            frames.append(chunk)
            total_seconds += CHUNK_MS / 1000

            if _rms(chunk) < SILENCE_RMS_THRESHOLD:
                silence_seconds += CHUNK_MS / 1000
            else:
                has_spoken = True
                silence_seconds = 0.0

            timeout = config.SILENCE_TIMEOUT_SECONDS if has_spoken else pre_speech_timeout
            if silence_seconds >= timeout:
                break

    if not has_spoken:
        return np.array([], dtype=np.int16)
    return np.concatenate(frames)


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
