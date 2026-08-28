# LaunchAgent do Jarvis

Faz o app de barra de menu (`jarvis/app.py`) abrir sozinho quando você loga
no Mac, sem precisar deixar o Terminal aberto.

## Pré-requisito

O venv já precisa existir e ter todas as dependências instaladas (`jarvis/.venv`,
ver README.md principal, seção Setup) — o LaunchAgent usa o Python de dentro
dele.

## Instalar

```bash
macos/install_launch_agent.sh
```

Isso copia um `.plist` (com os caminhos do seu projeto já preenchidos) para
`~/Library/LaunchAgents/` e carrega com `launchctl`. O ícone do Jarvis
aparece na barra de menu **desligado por padrão** — clique em "Ligar" pra
ativar a escuta.

A partir daí, ele abre sozinho em todo login, sem precisar rodar o script de
novo.

## Desinstalar

```bash
macos/uninstall_launch_agent.sh
```

Remove o LaunchAgent — ele para de abrir sozinho no login. Não desinstala
nada do projeto em si, só a parte de "iniciar automaticamente".

## Logs

Como o app roda sem Terminal, a saída (`print`, erros) vai para:
```
jarvis/logs/jarvis.log
jarvis/logs/jarvis.error.log
```
Útil para depurar se o ícone não aparecer ou o Ligar/Desligar não funcionar
como esperado.

## Se algo der errado

```bash
# ver se está carregado
launchctl list | grep com.danielofd.jarvis

# forçar recarregar depois de mudar o código
launchctl unload ~/Library/LaunchAgents/com.danielofd.jarvis.plist
launchctl load -w ~/Library/LaunchAgents/com.danielofd.jarvis.plist
```
