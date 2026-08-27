"""Teste isolado: confirma que os arquivos .onnx das vozes Piper (PT e EN)
estão íntegros e tocam áudio. Não faz parte do projeto final, é só
validação manual.

Rodar da raiz do projeto (com o venv ativado):
    python test_piper.py
"""

from jarvis.tts.speak import speak


def main():
    print("Testando voz em português (pt_BR-faber-medium)...")
    speak("Oi, esta é a voz em português. Se você está me ouvindo, está funcionando.")

    print("Testando voz em inglês (en_US-lessac-medium)...")
    speak("Hi, this is the English voice. If you can hear me, it's working.")

    print("\nOK: as duas vozes tocaram sem erro.")


if __name__ == "__main__":
    main()
