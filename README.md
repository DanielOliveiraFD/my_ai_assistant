# Jarvis

Assistente de voz pessoal, local e gratuito. Ativado por "Ei Arima", com Groq
como cérebro (STT + chat) e Piper para fala de volta, bilíngue PT/EN.

Veja o plano completo do projeto para contexto de fases e decisões de design.

## Status

**Fase 1 (MVP conversacional) — código pronto, ainda não testado.**
Este código só roda de fato e só deve ser testado no MacBook. As partes
específicas do macOS (LaunchAgent, ícone de barra de menu) **ainda não foram
implementadas** — ficam para depois que este núcleo for validado no Mac.

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

3. **Modelo de wake word customizado ("Ei Arima")**
   Ainda não existe um modelo pronto para essa frase — precisa treinar um.
   Use o [Outspoken](https://outspoken.cloud/): gera dados de voz sintética,
   treina e entrega um modelo `.onnx` pronto em ~45 minutos, sem precisar de
   GPU local. Baixe o resultado e salve como:
   ```
   jarvis/models/hey_arima.onnx
   ```
   Alternativa oficial (mais manual): [openWakeWord Training Center](https://openwakeword.com/train).

4. **Vozes do Piper (PT e EN)**
   Baixe os dois modelos de voz do repositório oficial
   ([rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices)) e
   salve em `jarvis/models/`:
   - `pt_BR-faber-medium.onnx` (+ `.onnx.json`)
   - `en_US-lessac-medium.onnx` (+ `.onnx.json`)

5. **Permissões do macOS**
   Na primeira execução, o macOS vai pedir permissão de microfone. Aceite em
   Ajustes > Privacidade e Segurança.

## Rodando

```bash
python -m jarvis.orchestrator
```

Diga "Ei Arima", espere o reconhecimento, fale o que quiser conversar. Ainda
não há nenhuma ferramenta/ação conectada — é só conversa livre com a IA, para
validar a pipeline de voz de ponta a ponta antes de avançar.

## Pontos de teste desta entrega (Fase 1, parte 1)

Siga o documento de plano, seção 8. Nesta entrega específica, valide nesta
ordem:
1. Detecção confiável de "Ei Arima" (sem disparo falso).
2. Transcrição bate com o que foi falado.
3. Conversa simples funciona (Groq responde coerente).
4. Ciclo completo falar → ouvir resposta funciona.
5. Escuta inteligente com pausa: teste deixando silêncios propositais no meio
   de uma frase e ajuste `SILENCE_TIMEOUT_SECONDS` em `jarvis/config.py`
   (linha ajustável) até parecer natural.
6. Bilíngue: fale em português, depois em inglês, confirme que a voz troca
   corretamente — inclusive trocando de idioma no meio da sessão.

**Depois de validar tudo isso no Mac, voltamos para implementar o
LaunchAgent e o ícone de barra de menu — código exclusivo de macOS que não
pode ser escrito nem testado fora dele.**

## Estrutura

```
jarvis/
  config.py                     # chaves, caminhos, parâmetros ajustáveis
  orchestrator.py                # loop principal (Fase 1)
  wakeword/listener.py            # detecção de "Ei Arima" via openWakeWord
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
  tts/speak.py                   # fala de volta via Piper, PT/EN automático
  models/                       # .onnx dos modelos (não versionado, ver .gitignore)
  memory.sqlite3                # banco de memória de longo prazo (não versionado)
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

Preferências (`tipo = "preferencia"`) são carregadas automaticamente no
prompt do sistema assim que o programa inicia — não dependem da IA decidir
buscar.

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
