"""Loop principal do Jarvis Caseiro (Fase 1 — MVP conversacional, sem ferramentas).

Ciclo: espera "Ei Arima" -> grava comando (com escuta inteligente de pausa) ->
transcreve -> pergunta ao cérebro -> fala a resposta -> volta a escutar.
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

    print("Jarvis Caseiro rodando. Diga 'Ei Arima' para começar.")

    while True:
        listener.wait_for_wakeword()
        print("[wake word detectada]")

        followups_used = 0

        def on_silence_timeout():
            nonlocal followups_used
            if followups_used >= config.MAX_FOLLOWUP_ATTEMPTS:
                return False
            followups_used += 1
            speak(config.FOLLOWUP_PROMPT[config.DEFAULT_TTS_LANGUAGE])
            return True

        audio = record_command(on_silence_timeout=on_silence_timeout)
        text = transcribe(audio)
        print(f"[usuário disse] {text}")

        if not text:
            continue

        reply = brain.ask(text)
        print(f"[Arima responde] {reply}")
        speak(reply)


if __name__ == "__main__":
    run()
