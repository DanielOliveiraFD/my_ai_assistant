"""Loop principal do Jarvis Caseiro (Fase 1 — MVP conversacional, sem ferramentas).

Ciclo: espera "Ok Nyx" -> grava comando -> transcreve -> pergunta ao cérebro
-> fala a resposta -> volta a escutar. Se nada for capturado (silêncio
total), pergunta "continua, estou ouvindo?" antes de desistir.
"""

from jarvis import config
from jarvis.brain.chat import Brain
from jarvis.stt.transcribe import record_command, transcribe
from jarvis.tts.speak import speak
from jarvis.wakeword.listener import WakeWordListener


def run():
    if not config.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY não configurada. Copie .env.example para .env.")

    listener = WakeWordListener()
    brain = Brain()

    print("Jarvis Caseiro rodando. Diga 'Ok Nyx' para começar.")

    while True:
        listener.wait_for_wakeword()
        print("[wake word detectada]")

        text = ""
        for attempt in range(config.MAX_FOLLOWUP_ATTEMPTS + 1):
            audio = record_command()
            text = transcribe(audio)
            print(f"[usuário disse] {text}")

            if text:
                break
            if attempt < config.MAX_FOLLOWUP_ATTEMPTS:
                speak(config.FOLLOWUP_PROMPT[config.DEFAULT_TTS_LANGUAGE])

        if not text:
            continue

        reply = brain.ask(text)
        print(f"[Nyx responde] {reply}")
        speak(reply)


if __name__ == "__main__":
    run()
