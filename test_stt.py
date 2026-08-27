"""Teste isolado: grava alguns segundos do microfone e transcreve via Groq
Whisper. Não depende do wake word — só do microfone e da GROQ_API_KEY. Não
faz parte do projeto final, é só validação manual.

Rodar da raiz do projeto (com o venv ativado):
    python test_stt.py
"""

from jarvis.stt.transcribe import record_command, transcribe


def main():
    print("Fale algo por alguns segundos (para automaticamente após um silêncio)...")
    audio = record_command()
    print("Transcrevendo...")
    text = transcribe(audio)
    print(f"\nVocê disse: {text!r}")


if __name__ == "__main__":
    main()
