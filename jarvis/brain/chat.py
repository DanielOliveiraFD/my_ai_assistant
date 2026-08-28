"""Cérebro do assistente: mantém o histórico da conversa, injeta as
preferências salvas no início da sessão, e executa o loop de chamadas de
ferramenta (memória + busca na web) até a IA produzir uma resposta final.
"""

import json

from jarvis import config
from jarvis.brain.factory import get_provider
from jarvis.memory import repository
from jarvis.memory.tools import DISPATCH as MEMORY_DISPATCH
from jarvis.memory.tools import TOOLS as MEMORY_TOOLS
from jarvis.memory.tools import normalize_arguments
from jarvis.websearch.tools import DISPATCH as WEBSEARCH_DISPATCH
from jarvis.websearch.tools import TOOLS as WEBSEARCH_TOOLS

TOOLS = MEMORY_TOOLS + WEBSEARCH_TOOLS
DISPATCH = {**MEMORY_DISPATCH, **WEBSEARCH_DISPATCH}

MAX_TOOL_ROUNDS = 5


def _build_system_prompt() -> str:
    preferences = repository.list_preferences()
    if not preferences:
        return config.SYSTEM_PROMPT

    prefs_text = "\n".join(f"- {p['texto']}" for p in preferences)
    return (
        f"{config.SYSTEM_PROMPT}\n\n"
        "Preferências conhecidas do usuário sobre como você deve se comportar:\n"
        f"{prefs_text}"
    )


class Brain:
    def __init__(self, debug: bool = False):
        self._provider = get_provider()
        self.history = [{"role": "system", "content": _build_system_prompt()}]
        self._pending_deletion_id = None
        self._debug = debug

    def ask(self, user_text: str) -> str:
        self.history.append({"role": "user", "content": user_text})

        for _ in range(MAX_TOOL_ROUNDS):
            result = self._provider.chat(self.history, tools=TOOLS)

            if not result.is_tool_call:
                self.history.append({"role": "assistant", "content": result.content})
                return result.content

            self.history.append(
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": call.id,
                            "type": "function",
                            "function": {
                                "name": call.name,
                                "arguments": json.dumps(call.arguments, ensure_ascii=False),
                            },
                        }
                        for call in result.tool_calls
                    ],
                }
            )

            for call in result.tool_calls:
                tool_result = self._execute_tool(call.name, call.arguments)
                self.history.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": json.dumps(tool_result, ensure_ascii=False),
                    }
                )

        fallback = "Desculpa, não consegui concluir isso agora."
        self.history.append({"role": "assistant", "content": fallback})
        return fallback

    def _execute_tool(self, name: str, arguments: dict) -> dict:
        arguments = normalize_arguments(arguments)
        if self._debug:
            print(f"[debug] chamou {name}({arguments})")

        if name == "excluir_memoria":
            result = self._propose_deletion(arguments)
        elif name == "confirmar_exclusao":
            result = self._confirm_deletion()
        else:
            handler = DISPATCH.get(name)
            result = (
                {"erro": f"ferramenta desconhecida: {name}"}
                if handler is None
                else handler(**arguments)
            )

        if self._debug:
            print(f"[debug] {name} retornou: {result}")
        return result

    def _propose_deletion(self, arguments: dict) -> dict:
        memory_id = arguments.get("id")
        descricao = arguments.get("descricao")

        if isinstance(memory_id, str) and memory_id.strip().isdigit():
            memory_id = int(memory_id.strip())

        if memory_id is not None:
            memoria = repository.get_memory(memory_id)
            candidatos = [memoria] if memoria else []
        elif descricao:
            candidatos = repository.find_memories_by_text(descricao)
        else:
            candidatos = []

        if len(candidatos) != 1:
            self._pending_deletion_id = None
            return {
                "status": "ambiguo_ou_nao_encontrado",
                "candidatos": candidatos,
                "instrucao": (
                    "Não prossiga sem uma identificação exata. Pergunte ao "
                    "usuário qual memória específica ele quer apagar."
                ),
            }

        self._pending_deletion_id = candidatos[0]["id"]
        return {
            "status": "aguardando_confirmacao",
            "memoria": candidatos[0],
            "instrucao": (
                "Pergunte ao usuário se ele confirma a exclusão desta memória "
                "específica. Só chame confirmar_exclusao se a resposta for "
                "afirmativa e inequívoca."
            ),
        }

    def _confirm_deletion(self) -> dict:
        if self._pending_deletion_id is None:
            return {"status": "erro", "motivo": "nenhuma exclusão pendente para confirmar"}

        memory_id = self._pending_deletion_id
        self._pending_deletion_id = None
        excluded = repository.delete_memory(memory_id)
        return {"status": "excluida" if excluded else "nao_encontrada", "id": memory_id}

    def reset(self):
        self.history = self.history[:1]
        self._pending_deletion_id = None
