"""Interface que todo provedor de IA usado como cérebro do assistente deve implementar.

Trocar de provedor no futuro significa criar uma nova classe que implemente
esta interface — nenhum outro módulo do projeto (wake word, STT, TTS,
automações do macOS) precisa mudar.
"""

from abc import ABC, abstractmethod


class AIProvider(ABC):
    @abstractmethod
    def chat(self, messages: list[dict]) -> str:
        """Envia o histórico de mensagens (formato [{"role", "content"}, ...])
        e retorna a resposta em texto."""
