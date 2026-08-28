# Rodando o Jarvis sem Terminal

## Caminho recomendado: app clicável (não inicia sozinho)

Cria um `Jarvis.app` de verdade — dá dois cliques quando quiser usar, fecha
quando não quiser. Não abre sozinho no login.

### Pré-requisito

O venv já precisa existir e ter todas as dependências instaladas
(`jarvis/.venv`, ver README.md principal, seção Setup).

### Montar o app

```bash
macos/build_app.sh
```

Isso gera `macos/Jarvis.app` com os caminhos do seu projeto já preenchidos.
Depois:
- Dê dois cliques nele pra abrir — o ícone aparece na barra de menu
  (desligado por padrão, clique em "Ligar")
- Se quiser mais fácil de achar, arraste `macos/Jarvis.app` pro Dock ou pra
  pasta `/Applications`

Se você mudar o código do projeto ou mover a pasta, rode `macos/build_app.sh`
de novo pra atualizar o app.

`macos/Jarvis.app` não é versionado no Git (tem caminhos específicos da sua
máquina) — só o template (`Jarvis.app.template/`) é. Cada máquina precisa
rodar `build_app.sh` uma vez.

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

Como o app roda sem Terminal, a saída (`print`, erros) vai para:
```
jarvis/logs/jarvis.log
jarvis/logs/jarvis.error.log
```
Útil para depurar se o ícone não aparecer ou o Ligar/Desligar não funcionar
como esperado.
