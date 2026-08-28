#!/bin/bash
# Monta macos/Jarvis.app a partir do template, com os caminhos do seu
# projeto já preenchidos. Depois é só dar dois cliques nele (ou arrastar
# pro Dock/Applications) pra abrir o Jarvis quando quiser — sem terminal,
# sem iniciar sozinho no login.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="$PROJECT_DIR/jarvis/.venv/bin/python"

if [ ! -x "$PYTHON_BIN" ]; then
    echo "Erro: não encontrei o Python do venv em $PYTHON_BIN"
    echo "Rode o setup do venv primeiro (ver README.md, seção Setup)."
    exit 1
fi

APP_DEST="$SCRIPT_DIR/Jarvis.app"
rm -rf "$APP_DEST"
cp -R "$SCRIPT_DIR/Jarvis.app.template" "$APP_DEST"

sed \
    -e "s#{{PROJECT_DIR}}#$PROJECT_DIR#g" \
    -e "s#{{PYTHON_BIN}}#$PYTHON_BIN#g" \
    "$SCRIPT_DIR/Jarvis.app.template/Contents/MacOS/jarvis_launcher" > "$APP_DEST/Contents/MacOS/jarvis_launcher"

chmod +x "$APP_DEST/Contents/MacOS/jarvis_launcher"

echo "App criado em: $APP_DEST"
echo "Dê dois cliques nele pra abrir o Jarvis (o ícone aparece na barra de menu)."
echo "Se quiser mais fácil de achar, arraste pra /Applications ou pro Dock."
echo ""
echo "Se mudar o código do projeto (ou mover a pasta), rode este script de"
echo "novo pra atualizar o app."
