"""Teste isolado: conversa por TEXTO com o cérebro (Groq + memória de longo
prazo), sem precisar de wake word nem microfone. Digite 'sair' para encerrar.

Usa o banco de memória REAL (jarvis/memory.sqlite3) e chamadas REAIS ao
Groq — não é uma simulação. Dá para validar aqui a maioria dos pontos de
teste de memória do tutorial (salvar, categorias, transparência, expiração,
exclusão com confirmação, preferências) antes mesmo do wake word estar
pronto.

Rodar da raiz do projeto (com o venv ativado):
    python test_brain.py
"""

from jarvis.brain.chat import Brain


def main():
    brain = Brain()
    print("Conversando por texto com o cérebro. Digite 'sair' para encerrar.\n")

    while True:
        user_text = input("Você: ").strip()
        if user_text.lower() in ("sair", "exit", "quit"):
            break
        if not user_text:
            continue

        reply = brain.ask(user_text)
        print(f"Nyx: {reply}\n")


if __name__ == "__main__":
    main()
