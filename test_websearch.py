"""Teste isolado: busca na web via Groq Compound, sem passar pelo resto do
cérebro (memória, wake word, etc.). Não faz parte do projeto final, é só
validação manual.

Rodar da raiz do projeto (com o venv ativado):
    python test_websearch.py
"""

from jarvis.websearch import client


def main():
    pergunta = "Qual a temperatura em Piraí, RJ, hoje?"
    print(f"Perguntando: {pergunta}")
    resposta = client.search(pergunta)
    print(f"\nResposta: {resposta}")


if __name__ == "__main__":
    main()
