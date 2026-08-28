"""Teste isolado: ajustes de sistema (volume, brilho, modo escuro, print),
sem passar pelo resto do cérebro. Não faz parte do projeto final, é só
validação manual. Só funciona no Mac.

CUIDADO: isso mexe de verdade no volume/brilho/modo escuro do seu Mac.

Rodar da raiz do projeto (com o venv ativado):
    python test_system.py
"""

from jarvis.actions import system


def main():
    print("Volume atual:", system.get_volume())

    print(system.set_volume(30))
    print(system.adjust_volume(10))
    print(system.mute(True))
    print(system.mute(False))

    print(system.adjust_brightness(2))
    print(system.adjust_brightness(-1))

    print(system.set_dark_mode())  # alterna

    print(system.take_screenshot())

    print(system.run_shortcut("AtalhoQueNaoExiste123"))  # deve dar erro tratado


if __name__ == "__main__":
    main()
