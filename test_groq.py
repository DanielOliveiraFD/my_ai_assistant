"""Teste isolado: confirma que a GROQ_API_KEY e a conexão com o Groq estão
funcionando. Não faz parte do projeto final, é só validação manual.

Rodar da raiz do projeto (com o venv ativado):
    python test_groq.py
"""

from jarvis import config
from jarvis.brain.providers.groq_provider import GroqProvider


def main():
    if not config.GROQ_API_KEY:
        print("ERRO: GROQ_API_KEY não configurada. Confira o arquivo .env.")
        return

    provider = GroqProvider(api_key=config.GROQ_API_KEY)
    messages = [
        {"role": "system", "content": "Responda em uma frase curta."},
        {"role": "user", "content": "Diga 'oi, estou funcionando' em português."},
    ]

    print("Enviando mensagem de teste para o Groq...")
    result = provider.chat(messages)

    if result.is_tool_call:
        print("Resposta inesperada: veio como chamada de ferramenta, não texto.")
        return

    print(f"Resposta do Groq: {result.content}")
    print("\nOK: chave e conexão funcionando.")


if __name__ == "__main__":
    main()
