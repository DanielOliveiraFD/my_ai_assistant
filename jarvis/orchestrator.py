"""Loop principal do Jarvis Caseiro (Fase 1 — MVP conversacional, sem ferramentas).

Ciclo: espera "Ok Nyx" -> grava comando -> transcreve -> pergunta ao cérebro
-> fala a resposta -> escuta uma janela de acompanhamento (sem exigir o
wake word) -> se vier outro comando, repete; se ficar em silêncio, volta a
esperar "Ok Nyx". Se nada for capturado logo após o wake word, pergunta
"continua, estou ouvindo?" antes de desistir.
"""

from jarvis import config
from jarvis.brain.chat import Brain
from jarvis.stt.transcribe import record_command, transcribe
from jarvis.tts.speak import speak
from jarvis.wakeword.listener import WakeWordListener


def _listen_after_wakeword() -> str:
    """Tenta capturar um comando logo após o wake word, perguntando
    "continua, estou ouvindo?" se nada for capturado, até
    MAX_FOLLOWUP_ATTEMPTS vezes."""
    text = ""
    for attempt in range(config.MAX_FOLLOWUP_ATTEMPTS + 1):
        audio = record_command()
        text = transcribe(audio)
        print(f"[usuário disse] {text}")

        if text:
            return text
        if attempt < config.MAX_FOLLOWUP_ATTEMPTS:
            speak(config.FOLLOWUP_PROMPT[config.DEFAULT_TTS_LANGUAGE])

    return text


def run():
    if not config.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY não configurada. Copie .env.example para .env.")

    listener = WakeWordListener()
    brain = Brain()

    print("Jarvis Caseiro rodando. Diga 'Ok Nyx' para começar.")

    while True:
        listener.wait_for_wakeword()
        print("[wake word detectada]")

        text = _listen_after_wakeword()

        while text:
            reply = brain.ask(text)
            print(f"[Nyx responde] {reply}")
            speak(reply)

            # Janela de acompanhamento: escuta mais um pouco sem exigir o
            # wake word de novo. Silêncio total aqui é normal (usuário
            # terminou de usar) — não pergunta "continua ouvindo".
            followup_audio = record_command(pre_speech_timeout=config.FOLLOWUP_LISTEN_SECONDS)
            text = transcribe(followup_audio)
            if text:
                print(f"[usuário disse] {text}")


if __name__ == "__main__":
    run()
