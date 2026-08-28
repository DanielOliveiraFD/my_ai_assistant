"""Ações no Safari via AppleScript (osascript).

Exige que o macOS conceda permissão de Automação pro Python controlar o
Safari — na primeira vez, uma janela de permissão deve aparecer (Ajustes
do Sistema > Privacidade e Segurança > Automação).
"""

import subprocess
import urllib.parse

_OPEN_URL_APPLESCRIPT = """
on run argv
    set targetURL to item 1 of argv
    tell application "Safari"
        activate
        if (count of windows) = 0 then
            make new document with properties {URL:targetURL}
        else
            tell window 1
                set current tab to (make new tab with properties {URL:targetURL})
            end tell
        end if
    end tell
end run
"""


def _open_url(url: str) -> None:
    subprocess.run(
        ["osascript", "-e", _OPEN_URL_APPLESCRIPT, url],
        check=True,
        capture_output=True,
        text=True,
    )


def search(query: str) -> str:
    url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
    try:
        _open_url(url)
    except subprocess.CalledProcessError as exc:
        return f"Não consegui abrir o Safari ({exc.stderr.strip()})."
    return f"Pesquisa aberta no Safari: {query}"


def open_site(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        _open_url(url)
    except subprocess.CalledProcessError as exc:
        return f"Não consegui abrir o Safari ({exc.stderr.strip()})."
    return f"Site aberto no Safari: {url}"
