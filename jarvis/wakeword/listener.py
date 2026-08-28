"""Escuta contínua do microfone até detectar a palavra de ativação ("Ok Nyx")."""

import numpy as np
import openwakeword.utils
import sounddevice as sd
from openwakeword.model import Model

from jarvis import config

SAMPLE_RATE = 16000
CHUNK_SIZE = 1280  # 80ms, tamanho esperado pelo openWakeWord


class WakeWordListener:
    def __init__(self):
        if not config.WAKEWORD_MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Modelo de wake word não encontrado em {config.WAKEWORD_MODEL_PATH}. "
                "Treine o modelo customizado (ver README) e coloque o .onnx nesse caminho."
            )
        # O pip install do openwakeword não inclui os modelos compartilhados de
        # pré-processamento (melspectrogram + embedding) — precisam ser
        # baixados uma vez. A própria função pula o download se já existirem.
        openwakeword.utils.download_models()
        self.model = Model(
            wakeword_models=[str(config.WAKEWORD_MODEL_PATH)],
            inference_framework="onnx",
        )
        self.model_name = config.WAKEWORD_MODEL_PATH.stem

    def wait_for_wakeword(self, stop_event=None) -> bool:
        """Bloqueia até detectar a palavra de ativação ou até `stop_event` ser
        sinalizado. Retorna True se detectou, False se foi interrompido
        (usado pelo app de barra de menu para desligar a escuta)."""
        with sd.InputStream(
            samplerate=SAMPLE_RATE, channels=1, dtype="int16", blocksize=CHUNK_SIZE
        ) as stream:
            while True:
                if stop_event is not None and stop_event.is_set():
                    return False
                audio_chunk, _ = stream.read(CHUNK_SIZE)
                audio = np.squeeze(audio_chunk)
                predictions = self.model.predict(audio)
                score = predictions.get(self.model_name, 0.0)
                if score >= config.WAKEWORD_THRESHOLD:
                    self.model.reset()
                    return True
