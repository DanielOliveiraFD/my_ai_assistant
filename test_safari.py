"""Teste isolado: pesquisa e abre site no Safari via AppleScript, sem
passar pelo resto do cérebro. Não faz parte do projeto final, é só
validação manual. Só funciona no Mac — na primeira execução, o macOS deve
pedir permissão de Automação para o Python controlar o Safari.

Rodar da raiz do projeto (com o venv ativado):
    python test_safari.py
"""

from jarvis.actions import safari


def main():
    print("Testando pesquisa no Safari...")
    print(safari.search("previsão do tempo Piraí RJ"))

    print("\nTestando abrir site específico...")
    print(safari.open_site("github.com"))


if __name__ == "__main__":
    main()
