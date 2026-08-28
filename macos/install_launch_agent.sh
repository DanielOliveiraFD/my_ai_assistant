#!/bin/bash
# Instala o Jarvis como LaunchAgent do macOS: o app de barra de menu passa a
# abrir sozinho no login, sem precisar de Terminal. Resolve os caminhos
# automaticamente a partir de onde este script está.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="$PROJECT_DIR/jarvis/.venv/bin/python"
PLIST_LABEL="com.danielofd.jarvis"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_LABEL.plist"

if [ ! -x "$PYTHON_BIN" ]; then
    echo "Erro: não encontrei o Python do venv em $PYTHON_BIN"
    echo "Rode o setup do venv primeiro (ver README.md, seção Setup)."
    exit 1
fi

mkdir -p "$PROJECT_DIR/jarvis/logs"
mkdir -p "$HOME/Library/LaunchAgents"

sed \
    -e "s#{{PROJECT_DIR}}#$PROJECT_DIR#g" \
    -e "s#{{PYTHON_BIN}}#$PYTHON_BIN#g" \
    "$SCRIPT_DIR/com.danielofd.jarvis.plist.template" > "$PLIST_DEST"

launchctl unload "$PLIST_DEST" 2>/dev/null || true
launchctl load -w "$PLIST_DEST"

echo "LaunchAgent instalado e carregado: $PLIST_DEST"
echo "O ícone do Jarvis deve aparecer na barra de menu agora (desligado por padrão — clique em Ligar)."
echo "Para reiniciar sozinho no próximo login, não precisa fazer mais nada."
echo "Para desinstalar: macos/uninstall_launch_agent.sh"
