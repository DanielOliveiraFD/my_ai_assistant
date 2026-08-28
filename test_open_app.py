"""Teste isolado: abre um aplicativo pelo nome via `open -a`. Não faz
parte do projeto final, é só validação manual. Só funciona no Mac.

Rodar da raiz do projeto (com o venv ativado):
    python test_open_app.py
"""

from jarvis.actions import apps


def main():
    print("Testando abrir o Safari...")
    print(apps.open_app("Safari"))

    print("\nTestando um app que não existe (deve dar erro tratado)...")
    print(apps.open_app("AplicativoQueNaoExiste123"))


if __name__ == "__main__":
    main()
