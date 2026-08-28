#!/bin/bash
# Remove o LaunchAgent do Jarvis: ele para de abrir sozinho no login.
set -euo pipefail

PLIST_LABEL="com.danielofd.jarvis"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_LABEL.plist"

if [ -f "$PLIST_DEST" ]; then
    launchctl unload "$PLIST_DEST" 2>/dev/null || true
    rm "$PLIST_DEST"
    echo "LaunchAgent removido: $PLIST_DEST"
else
    echo "Nenhum LaunchAgent instalado em $PLIST_DEST"
fi
