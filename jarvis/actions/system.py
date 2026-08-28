"""Ajustes rápidos do sistema (volume, brilho, modo escuro, print de tela,
atalhos) via AppleScript/comandos nativos do macOS."""

import subprocess
from datetime import datetime
from pathlib import Path

MIN_LEVEL = 0
MAX_LEVEL = 100

# Brilho: o macOS não tem comando nativo pra DEFINIR um valor exato (só o
# volume tem isso via AppleScript) — o jeito confiável sem instalar nada
# extra é simular as teclas de brilho, em passos.
_BRIGHTNESS_UP_KEYCODE = 144
_BRIGHTNESS_DOWN_KEYCODE = 145


def _run_applescript(script: str) -> str:
    result = subprocess.run(
        ["osascript", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def get_volume() -> int:
    return int(_run_applescript("output volume of (get volume settings)"))


def set_volume(nivel: int) -> str:
    nivel = max(MIN_LEVEL, min(MAX_LEVEL, int(nivel)))
    try:
        _run_applescript(f"set volume output volume {nivel}")
    except subprocess.CalledProcessError as exc:
        return f"Não consegui ajustar o volume ({exc.stderr.strip()})."
    return f"Volume ajustado para {nivel}%."


def adjust_volume(delta: int) -> str:
    try:
        atual = get_volume()
    except subprocess.CalledProcessError as exc:
        return f"Não consegui ler o volume atual ({exc.stderr.strip()})."
    return set_volume(atual + delta)


def mute(mudo: bool = True) -> str:
    valor = "true" if mudo else "false"
    try:
        _run_applescript(f"set volume output muted {valor}")
    except subprocess.CalledProcessError as exc:
        acao = "silenciar" if mudo else "reativar o som"
        return f"Não consegui {acao} ({exc.stderr.strip()})."
    return "Som silenciado." if mudo else "Som reativado."


def adjust_brightness(passos: int) -> str:
    if passos == 0:
        return "Nenhum ajuste de brilho pedido."
    keycode = _BRIGHTNESS_UP_KEYCODE if passos > 0 else _BRIGHTNESS_DOWN_KEYCODE
    script = "\n".join(
        f'tell application "System Events" to key code {keycode}'
        for _ in range(abs(passos))
    )
    try:
        _run_applescript(script)
    except subprocess.CalledProcessError as exc:
        return f"Não consegui ajustar o brilho ({exc.stderr.strip()})."
    direcao = "aumentado" if passos > 0 else "diminuído"
    return f"Brilho {direcao} em {abs(passos)} passo(s)."


def set_dark_mode(ativar: bool | None = None) -> str:
    if ativar is None:
        script = (
            'tell application "System Events" to tell appearance preferences '
            "to set dark mode to not dark mode"
        )
    else:
        valor = "true" if ativar else "false"
        script = (
            'tell application "System Events" to tell appearance preferences '
            f"to set dark mode to {valor}"
        )
    try:
        _run_applescript(script)
    except subprocess.CalledProcessError as exc:
        return f"Não consegui mudar o modo escuro ({exc.stderr.strip()})."
    return "Modo escuro ajustado."


def take_screenshot() -> str:
    caminho = Path.home() / "Desktop" / f"Screenshot-{datetime.now():%Y-%m-%d-%H%M%S}.png"
    try:
        subprocess.run(
            ["screencapture", "-x", str(caminho)],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        return f"Não consegui tirar o print ({exc.stderr.strip()})."
    return f"Print salvo em {caminho}."


def run_shortcut(nome: str) -> str:
    """Roda um atalho do app Atalhos (Shortcuts) pelo nome — usado para
    Modos de Foco. O usuário precisa ter criado um atalho com esse nome
    exato no app Atalhos antes; não existe comando nativo confiável para
    ativar um Modo de Foco específico direto por script."""
    try:
        subprocess.run(
            ["shortcuts", "run", nome],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        detalhe = exc.stderr.strip() if exc.stderr else "atalho não encontrado"
        return f"Não consegui rodar o atalho '{nome}' ({detalhe})."
    return f"Atalho '{nome}' executado."
