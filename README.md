# Jarvis

Assistente de voz pessoal, local e gratuito. Ativado por "Ok Nyx", com Groq
como cérebro (STT + chat) e Piper para fala de volta, bilíngue PT/EN.

Veja o plano completo do projeto para contexto de fases e decisões de design.

## Status

**Fase 1 (MVP conversacional + memória) — validada no Mac.** Wake word,
transcrição, cérebro com memória de longo prazo, fala e a janela de
acompanhamento pós-resposta já foram testados de ponta a ponta com voz real.

**LaunchAgent + ícone de barra de menu — validado no Mac.** `macos/Jarvis.command`
é o caminho recomendado (ver `macos/README.md` — o `.app` puro esbarra num
problema de permissão de microfone sem solução no momento).

**Busca na web (Tavily) — validada no Mac.** O assistente pesquisa
informação atual quando não sabe a resposta, sem abrir navegador nenhum.

**Fase 2 (em andamento) — ações no macOS.** Primeira ação real: pesquisar e
abrir sites no Safari (`jarvis/actions/`). Código pronto, ainda não testado
— só pode ser testado no Mac (ver seção de testes abaixo).

## Setup (fazer no Mac, antes de testar)

1. **Ambiente Python**
   ```bash
   cd jarvis
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r ../requirements.txt
   ```

2. **Chave da API**
   ```bash
   cp .env.example .env
   # edite .env e cole sua GROQ_API_KEY (a mesma usada pelo FreeFlow)
   ```
   Confirme em console.groq.com → Data Controls que **Zero Data Retention**
   está ativado.

3. **Modelo de wake word customizado ("Ok Nyx")**
   Ainda não existe um modelo pronto para essa frase — precisa treinar um.
   Use o [Outspoken](https://outspoken.cloud/): gera dados de voz sintética,
   treina e entrega um modelo `.onnx` (duração real varia com o tier e o
   tamanho do dataset — no tier gratuito "Balanced" costuma ficar em torno
   de 1h, rodando na nuvem deles, sem precisar de GPU local nem deixar a
   aba aberta). Baixe o resultado e salve como:
   ```
   jarvis/models/ok_nyx.onnx
   ```
   Nota: o Outspoken ainda não treina em português (só inglês, holandês,
   alemão e francês). "Ok Nyx" foi escolhido por ter pronúncia parecida
   nos dois idiomas, o que reduz o desalinhamento fonético do treino em
   inglês.
   Alternativa oficial (mais manual): [openWakeWord Training Center](https://openwakeword.com/train).

4. **Vozes do Piper (PT e EN)**
   Baixe os dois modelos de voz do repositório oficial
   ([rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices)) e
   salve em `jarvis/models/`:
   - `pt_BR-cadu-medium.onnx` (+ `.onnx.json`)
   - `en_US-lessac-medium.onnx` (+ `.onnx.json`)

5. **Permissões do macOS**
   Na primeira execução, o macOS vai pedir permissão de microfone. Aceite em
   Ajustes > Privacidade e Segurança.

## Rodando

```bash
python -m jarvis.orchestrator
```

Diga "Ok Nyx", espere o reconhecimento, fale o que quiser conversar. Ainda
não há nenhuma ferramenta/ação conectada — é só conversa livre com a IA, para
validar a pipeline de voz de ponta a ponta antes de avançar.

## Pontos de teste desta entrega (Fase 1, parte 1)

Siga o documento de plano, seção 8. Nesta entrega específica, valide nesta
ordem:
1. Detecção confiável de "Ok Nyx" (sem disparo falso).
2. Transcrição bate com o que foi falado.
3. Conversa simples funciona (Groq responde coerente).
4. Ciclo completo falar → ouvir resposta funciona.
5. Escuta inteligente com pausa: teste deixando silêncios propositais no meio
   de uma frase e ajuste `SILENCE_TIMEOUT_SECONDS` em `jarvis/config.py`
   (linha ajustável) até parecer natural.
6. Bilíngue: fale em português, depois em inglês, confirme que a voz troca
   corretamente — inclusive trocando de idioma no meio da sessão.

## Estrutura

```
jarvis/
  config.py                     # chaves, caminhos, parâmetros ajustáveis
  orchestrator.py                # loop principal (Fase 1), aceita stop_event
  app.py                          # app de barra de menu (Ligar/Desligar)
  wakeword/listener.py            # detecção de "Ok Nyx" via openWakeWord
  stt/transcribe.py                # gravação + transcrição via Groq Whisper
  brain/
    chat.py                         # loop de conversa + ferramentas, agnóstico de provedor
    base.py                          # interface AIProvider (suporta tool calling)
    factory.py                       # escolhe o provedor configurado (config.AI_PROVIDER)
    providers/groq_provider.py        # implementação específica do Groq
  memory/
    db.py                             # conexão + schema do SQLite
    repository.py                      # CRUD da memória de longo prazo
    tools.py                            # ferramentas de memória expostas à IA
  websearch/
    client.py                          # busca via Tavily
    tools.py                            # ferramenta buscar_na_web exposta à IA
  actions/
    apps.py                             # abrir qualquer app pelo nome
    safari.py                            # pesquisar/abrir site no Safari (AppleScript)
    system.py                             # volume, brilho, modo escuro, print, atalhos
    tools.py                               # ferramentas de ação expostas à IA
  tts/speak.py                   # fala de volta via Piper, PT/EN automático
  models/                       # .onnx dos modelos (não versionado, ver .gitignore)
  logs/                          # saída do LaunchAgent (não versionado)
  memory.sqlite3                # banco de memória de longo prazo (não versionado)
macos/
  Jarvis.command                         # clicável, recomendado — abre com Terminal por trás
  Jarvis.app.template/                    # modelo do app clicável (experimental, ver macos/README.md)
  build_app.sh                             # monta macos/Jarvis.app (não versionado)
  com.danielofd.jarvis.plist.template    # modelo do LaunchAgent (opcional, auto-início)
  install_launch_agent.sh                 # instala e carrega o LaunchAgent
  uninstall_launch_agent.sh               # remove o LaunchAgent
  README.md                               # instruções detalhadas
```

### Módulo do cérebro (`jarvis/brain/`)

Isolado por design: `chat.py` só conhece a interface `AIProvider` (`base.py`),
nunca o SDK do Groq diretamente. Toda a lógica específica do Groq (SDK,
nome do modelo, formato da chamada, tool calling) fica em
`providers/groq_provider.py`.

Para trocar de provedor de IA no futuro:
1. Criar `jarvis/brain/providers/novo_provider.py` implementando `AIProvider.chat()`
2. Adicionar um ramo em `jarvis/brain/factory.py`
3. Mudar `AI_PROVIDER` em `config.py`

Nenhum outro módulo (wake word, STT, TTS, memória, automações do macOS)
precisa mudar.

### Módulo de memória (`jarvis/memory/`)

Também isolado: só o `brain/chat.py` importa daqui, nunca o contrário.
Curto prazo (dentro da mesma conversa) continua sendo só o histórico em
memória do programa. Longo prazo usa um banco SQLite local
(`jarvis/memory.sqlite3`, nunca versionado — é dado pessoal seu).

A IA decide sozinha quando usar cada ferramenta de memória durante a
conversa (`salvar_memoria`, `listar_categorias`, `buscar_memorias`,
`listar_memorias_transparencia`). A exceção é exclusão: `excluir_memoria`
só **propõe** o que seria apagado — nunca apaga nada sozinha. A exclusão de
fato só acontece se, na resposta seguinte, você confirmar em voz e a IA
chamar `confirmar_exclusao`. Sem essa segunda confirmação, nada é apagado.

**Rotinas (`tipo = "rotina"`) — schema pronto, funcionalidade adiada.** O
banco já tem a coluna `passos` e aceita esse tipo, mas ainda não existe
nenhuma ferramenta (`salvar_rotina`/`verificar_rotina`) que crie ou dispare
rotinas. Decisão consciente: uma rotina só faz sentido quando existir pelo
menos uma ação real pra executar (abrir um app, mexer em arquivo, etc.) —
isso é Fase 2 em diante. Implementar rotinas agora resultaria em um teste
que só confirma "ele fala sobre executar", não que ele executa de fato.

Preferências (`tipo = "preferencia"`) são carregadas automaticamente no
prompt do sistema assim que o programa inicia — não dependem da IA decidir
buscar.

### Módulo de busca na web (`jarvis/websearch/`)

Isolado, mesmo padrão dos outros: só `brain/chat.py` importa daqui. Usa a
API da Tavily (precisa de `TAVILY_API_KEY` no `.env` — conta grátis em
[tavily.com](https://tavily.com/)). Devolve só os resultados brutos da
busca, nunca uma resposta pronta — quem formula a resposta final falada é
o cérebro principal, que já segue o idioma do usuário corretamente.

### Módulo de ações (`jarvis/actions/`) — Fase 2

Ações reais no macOS via AppleScript/comandos nativos (`osascript`,
`screencapture`, `shortcuts`), isoladas do resto do projeto. Hoje tem
Safari (`pesquisar_no_safari`, `abrir_site_no_safari`), abrir qualquer app
pelo nome (`abrir_aplicativo`), e ajustes de sistema (volume, brilho, modo
escuro, print, atalhos — ver abaixo). Mais ações (arquivos, calendário,
etc.) entram aqui conforme a Fase 2 avança. Exige permissão de Automação
do macOS na primeira execução (Ajustes do Sistema > Privacidade e
Segurança > Automação).

**Limitações conhecidas dos ajustes de sistema:**
- **Brilho**: só relativo (sobe/desce em passos) — o macOS não tem comando
  nativo para definir uma porcentagem exata, diferente do volume.
- **Modo de Foco**: não existe comando nativo para ativar um Modo de Foco
  específico. `ativar_modo_foco` roda um atalho do app Atalhos pelo nome
  — o usuário precisa **criar esse atalho manualmente no app Atalhos
  primeiro** (ex: um atalho chamado "Foco Trabalho" que ativa esse modo).
  Sem o atalho criado, a ferramenta retorna erro.

## Pontos de teste desta entrega (Safari — Fase 2)

Primeira ação real do projeto. Só pode ser testado no Mac:

```bash
python test_safari.py
```

- [ ] Na primeira execução, o macOS pede permissão de Automação para o
      Python controlar o Safari — aceite
- [ ] `pesquisar_no_safari` abre o Safari numa aba nova com os resultados
      do Google para o termo pedido
- [ ] `abrir_site_no_safari` abre o site certo numa aba nova (teste com
      domínio simples, tipo `github.com`, e com URL completa)
- [ ] Testado por voz/`test_brain.py`: pedir para "pesquisar X" e "abrir o
      site Y" numa conversa normal, confirmando que a IA escolhe a
      ferramenta certa para cada pedido
- [ ] Testar um comando ambíguo (ex: "abre o Google") e ver como reage

## Pontos de teste desta entrega (ajustes de sistema — Fase 2)

Só pode ser testado no Mac. **Cuidado**: mexe de verdade no volume/brilho/
modo escuro da máquina.

```bash
python test_system.py
```

- [ ] Volume: definir um valor exato ("coloca o volume em 30%") e ajustar
      relativo ("aumenta o volume", "abaixa um pouco")
- [ ] Silenciar e reativar o som
- [ ] Brilho: só relativo ("aumenta o brilho") — confirmar que reage em
      passos, sem tentar pedir uma porcentagem exata
- [ ] Modo escuro: ligar, desligar, e alternar sem especificar
- [ ] Print de tela: confirmar que salva um arquivo `.png` na Área de
      Trabalho
- [ ] Modo de Foco: criar um atalho de teste no app Atalhos (ex:
      "Foco Teste") e confirmar que `ativar_modo_foco` consegue rodá-lo;
      testar também pedir um Modo de Foco **sem** atalho criado e
      confirmar que a IA avisa que precisa criar o atalho primeiro, em
      vez de fingir que funcionou

## Pontos de teste desta entrega (memória de longo prazo)

Além dos pontos já validados na Fase 1 (voz), valide especificamente a
memória, seguindo a seção 7 do documento de arquitetura de memória:

- [ ] Salvar uma memória e confirmar que ela é lembrada em uma conversa
      posterior — **reiniciando o programa** entre uma coisa e outra (isso
      prova que é persistência real em disco, não só o histórico da sessão).
- [ ] Salvar duas informações que deveriam cair na mesma categoria e
      confirmar que a IA reaproveita a categoria existente, sem duplicar.
- [ ] Testar o comando de transparência ("o que você sabe sobre mim?") e
      confirmar que a resposta falada é clara e correta.
- [ ] Salvar uma informação com expiração curta (ex: pedir pra expirar em
      poucos minutos, só para teste) e confirmar que ela deixa de aparecer
      nas buscas depois de expirada.
- [ ] Pedir para apagar uma memória e confirmar que a IA **pergunta antes**
      — nunca apaga direto na mesma resposta. Só depois de você confirmar
      em voz é que deve sumir de fato (confira reiniciando o programa e
      pedindo pra listar de novo).
- [ ] Salvar uma preferência (ex: "prefiro respostas curtas") e confirmar
      que o comportamento do assistente muda de fato nas respostas
      seguintes, mesmo em uma sessão nova.

## Pontos de teste desta entrega (app de barra de menu)

Fecha a Fase 1. Só pode ser testado no Mac. Por padrão o Jarvis **não** abre
sozinho no login — você abre quando quiser, como qualquer outro app.

1. **Direto por Python primeiro** (mais rápido de iterar):
   ```bash
   python -m jarvis.app
   ```
   - [ ] O ícone "⚪ Jarvis" aparece na barra de menu
   - [ ] Clicar em "Ligar" muda pra "🟢 Jarvis" e o assistente passa a
         responder a "Ok Nyx" normalmente
   - [ ] Clicar em "Desligar" muda de volta pra "⚪ Jarvis" e ele **para de
         responder** ao wake word (mesmo no meio de uma escuta) — não deve
         travar nem demorar mais que ~1s pra parar
   - [ ] Ligar de novo depois de desligar funciona sem precisar reiniciar o
         programa
   - [ ] "Sair" fecha o app completamente (não aparece mais na barra)

2. **Clicável sem Terminal** — `macos/Jarvis.command` (ver `macos/README.md`
   para detalhes e por que não é um `.app` puro):
   - [ ] Dois cliques em `macos/Jarvis.command` abre uma janela de Terminal
         e o Jarvis inicia nela (mesmo comportamento do item 1)
   - [ ] Fechar o Jarvis (Sair no menu) e abrir de novo com dois cliques
         funciona normalmente
   - [ ] Reiniciar o Mac: o Jarvis **não** abre sozinho (comportamento
         esperado — só abre quando você clicar)

   `macos/Jarvis.app` (gerado por `macos/build_app.sh`) é experimental e
   tem um problema conhecido de permissão de microfone sem solução no
   momento — não é o caminho recomendado, ver `macos/README.md`.

O LaunchAgent (auto-início no login) continua disponível como opção à parte
em `macos/README.md`, mas não é o caminho padrão do projeto.
