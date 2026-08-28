"""Loop principal do Jarvis Caseiro (Fase 1 — MVP conversacional, sem ferramentas).

Ciclo: espera "Ok Nyx" -> grava comando -> transcreve -> pergunta ao cérebro
-> fala a resposta -> escuta uma janela de acompanhamento (sem exigir o
wake word) -> se vier outro comando, repete; se ficar em silêncio, volta a
esperar "Ok Nyx". Se nada for capturado logo após o wake word, pergunta
"continua, estou ouvindo?" antes de desistir.

`run(stop_event=...)` aceita um threading.Event opcional para ser
interrompido de fora (usado pelo app de barra de menu, jarvis/app.py, no
botão Desligar) — checado a cada pedaço de áudio lido, sem travar o loop
até o próximo wake word.
"""

from jarvis import config
from jarvis.brain.chat import Brain
from jarvis.stt.transcribe import record_command, transcribe
from jarvis.tts.speak import speak
from jarvis.wakeword.listener import WakeWordListener


def _listen_after_wakeword(stop_event=None) -> str:
    """Tenta capturar um comando logo após o wake word, perguntando
    "continua, estou ouvindo?" se nada for capturado, até
    MAX_FOLLOWUP_ATTEMPTS vezes."""
    text = ""
    for attempt in range(config.MAX_FOLLOWUP_ATTEMPTS + 1):
        if stop_event is not None and stop_event.is_set():
            return ""

        audio = record_command(stop_event=stop_event)
        text = transcribe(audio)
        print(f"[usuário disse] {text}")

        if text:
            return text
        if attempt < config.MAX_FOLLOWUP_ATTEMPTS:
            speak(config.FOLLOWUP_PROMPT[config.DEFAULT_TTS_LANGUAGE])

    return text


def run(stop_event=None):
    if not config.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY não configurada. Copie .env.example para .env.")

    listener = WakeWordListener()
    brain = Brain()

    print("Jarvis Caseiro rodando. Diga 'Ok Nyx' para começar.")

    while stop_event is None or not stop_event.is_set():
        detected = listener.wait_for_wakeword(stop_event=stop_event)
        if not detected:
            break
        print("[wake word detectada]")

        text = _listen_after_wakeword(stop_event=stop_event)

        while text:
            reply = brain.ask(text)
            print(f"[Nyx responde] {reply}")
            speak(reply)

            if stop_event is not None and stop_event.is_set():
                break

            # Janela de acompanhamento: escuta mais um pouco sem exigir o
            # wake word de novo. Silêncio total aqui é normal (usuário
            # terminou de usar) — não pergunta "continua ouvindo".
            followup_audio = record_command(
                pre_speech_timeout=config.FOLLOWUP_LISTEN_SECONDS, stop_event=stop_event
            )
            text = transcribe(followup_audio)
            if text:
                print(f"[usuário disse] {text}")

    print("Jarvis Caseiro parado.")


if __name__ == "__main__":
    run()
