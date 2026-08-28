#!/bin/bash
# Dê dois cliques neste arquivo no Finder para abrir o Jarvis.
#
# Abre uma janela de Terminal por trás — necessário porque o Terminal já
# tem a permissão de microfone concedida (diferente de um .app sem
# assinatura digital, cujo acesso ao microfone o macOS nega em silêncio).
# Pode minimizar a janela do Terminal, mas não feche: fechar essa janela
# encerra o Jarvis também.
#
# Resolve os caminhos sozinho a partir de onde este arquivo está — não
# precisa editar nada nem rodar nenhum script de build antes.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="$PROJECT_DIR/jarvis/.venv/bin/python"

if [ ! -x "$PYTHON_BIN" ]; then
    echo "Erro: não encontrei o Python do venv em $PYTHON_BIN"
    echo "Rode o setup do venv primeiro (ver README.md, seção Setup)."
    read -p "Pressione Enter para fechar..."
    exit 1
fi

cd "$PROJECT_DIR"
exec "$PYTHON_BIN" -m jarvis.app
