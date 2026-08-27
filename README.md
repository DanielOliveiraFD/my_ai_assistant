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
    chat.py                         # histórico da conversa, agnóstico de provedor
    base.py                          # interface AIProvider
    factory.py                       # escolhe o provedor configurado (config.AI_PROVIDER)
    providers/groq_provider.py        # implementação específica do Groq
  tts/speak.py                   # fala de volta via Piper, PT/EN automático
  models/                       # .onnx dos modelos (não versionado, ver .gitignore)
```

### Módulo do cérebro (`jarvis/brain/`)

Isolado por design: `chat.py` só conhece a interface `AIProvider` (`base.py`),
nunca o SDK do Groq diretamente. Toda a lógica específica do Groq (SDK,
nome do modelo, formato da chamada) fica em `providers/groq_provider.py`.

Para trocar de provedor de IA no futuro:
1. Criar `jarvis/brain/providers/novo_provider.py` implementando `AIProvider.chat()`
2. Adicionar um ramo em `jarvis/brain/factory.py`
3. Mudar `AI_PROVIDER` em `config.py`

Nenhum outro módulo (wake word, STT, TTS, automações do macOS) precisa mudar.
