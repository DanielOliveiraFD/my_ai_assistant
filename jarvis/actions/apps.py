"""Abrir aplicativos do macOS pelo nome, via `open -a` (nativo do sistema,
não precisa de AppleScript nem de permissão de Automação separada)."""

import subprocess


def open_app(nome: str) -> str:
    try:
        subprocess.run(
            ["open", "-a", nome],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        detalhe = exc.stderr.strip() if exc.stderr else "aplicativo não encontrado"
        return f"Não consegui abrir '{nome}' ({detalhe})."
    return f"'{nome}' aberto."
