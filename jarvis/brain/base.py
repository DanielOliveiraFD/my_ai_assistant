"""Interface que todo provedor de IA usado como cérebro do assistente deve implementar.

Trocar de provedor no futuro significa criar uma nova classe que implemente
esta interface — nenhum outro módulo do projeto (wake word, STT, TTS,
memória, automações do macOS) precisa mudar.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass
class ChatResult:
    content: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)

    @property
    def is_tool_call(self) -> bool:
        return bool(self.tool_calls)


class AIProvider(ABC):
    @abstractmethod
    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> ChatResult:
        """Envia o histórico de mensagens e, opcionalmente, ferramentas
        disponíveis (schema no formato OpenAI/Groq function calling).

        Retorna um ChatResult: texto final (`content`), ou uma lista de
        chamadas de ferramenta pendentes (`tool_calls`) que o chamador deve
        executar e devolver como mensagens de role "tool" antes de chamar
        `chat` de novo.
        """
