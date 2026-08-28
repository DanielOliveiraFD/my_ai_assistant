# Rodando o Jarvis sem digitar comando

## Caminho recomendado: `Jarvis.command` (não inicia sozinho)

Dê dois cliques em `macos/Jarvis.command` sempre que quiser abrir o Jarvis.
Não precisa digitar nada nem rodar nenhum script antes — os caminhos são
resolvidos sozinhos.

Isso abre uma **janela de Terminal por trás**. É proposital: o Terminal já
tem a permissão de microfone concedida nos testes anteriores, e é o jeito
mais confiável de garantir que o microfone funcione sem o macOS negar
acesso em silêncio (ver nota abaixo sobre o `.app`). Pode minimizar essa
janela, mas não feche — fechar a janela encerra o Jarvis também.

Se quiser mais fácil de achar, arraste `macos/Jarvis.command` pro Dock.

Não abre sozinho no login — só quando você clicar.

### Pré-requisito

O venv já precisa existir e ter todas as dependências instaladas
(`jarvis/.venv`, ver README.md principal, seção Setup).

---

## `Jarvis.app` (experimental, com problema conhecido de permissão)

Também existe um `macos/build_app.sh` que gera um `Jarvis.app` de verdade,
sem janela de Terminal visível. **Ele tem um problema não resolvido**: como
não é assinado digitalmente pela Apple, o macOS não consegue ligar o
processo do Python ao app corretamente, e nega a permissão de microfone em
silêncio (sem mostrar nem o prompt de permissão). Resolver isso direito
exigiria assinatura de código mais elaborada — fora do escopo agora. Fica
disponível no repositório, mas **use o `Jarvis.command` acima**, que é o
caminho testado e funcionando.

---

## Alternativa (opcional): iniciar sozinho no login via LaunchAgent

Só use isso se você **quiser** que o Jarvis abra automaticamente toda vez
que você loga no Mac, sem precisar clicar em nada. Por padrão o projeto não
usa isso.

```bash
macos/install_launch_agent.sh
```

Copia um `.plist` para `~/Library/LaunchAgents/` e carrega com `launchctl`.
O ícone aparece sozinho a partir do próximo login (desligado por padrão,
clique em "Ligar").

### Desinstalar

```bash
macos/uninstall_launch_agent.sh
```

---

## Logs

O `Jarvis.command` mostra a saída direto na janela de Terminal que abre
(mesmo formato de quando você roda `python -m jarvis.app` manualmente).

O `Jarvis.app` (experimental) manda a saída para:
```
jarvis/logs/jarvis.log
jarvis/logs/jarvis.error.log
```
