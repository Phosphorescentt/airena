from dataclasses import dataclass
from typing import List, Protocol, Iterable, TYPE_CHECKING

from openai import OpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from airena.types import JsonType


if TYPE_CHECKING:
    from airena.engine import DebateHistory, TurnInformation


class CompletionException(Exception):
    pass


class Adapter(Protocol):
    _turn_information: "TurnInformation"

    @staticmethod
    def from_model_name_and_turn_information(
        model_name: str, turn_information: "TurnInformation"
    ) -> "Adapter": ...

    def to_json(self) -> JsonType: ...
    def serialise_history(self, history: "DebateHistory") -> Iterable: ...
    def get_next_message(self, history: "DebateHistory") -> str: ...


@dataclass
class OpenAIAdapter(Adapter):
    """Manages sending information off to OpenAI and reading it back.

    There will be some function somewhere taking a "DebateHistory" and returning
    the string from the API.
    """

    model_name: str
    _turn_information: "TurnInformation"
    _client: OpenAI

    @staticmethod
    def from_model_name_and_turn_information(
        model_name: str, turn_information: "TurnInformation"
    ) -> "OpenAIAdapter":
        return OpenAIAdapter(
            model_name=model_name,
            _turn_information=turn_information,
            _client=OpenAI(),
        )

    def to_json(self) -> JsonType:
        return {"provider": "OpenAI", "model_name": self.model_name}

    def serialise_history(self, history: "DebateHistory"):
        openai_history: List[ChatCompletionMessageParam] = [
            ChatCompletionSystemMessageParam(
                content=history.system_prompt, role="system"
            )
        ]

        for i, row in enumerate(history.rows):
            if (
                i % self._turn_information.total_participants
            ) == self._turn_information.position:
                message = ChatCompletionAssistantMessageParam(
                    content=row, role="assistant"
                )
            else:
                message = ChatCompletionUserMessageParam(content=row, role="user")

            openai_history.append(message)

        return openai_history

    def get_next_message(self, history: "DebateHistory") -> str:
        messages = self.serialise_history(history)
        response = self._client.chat.completions.create(
            model=self.model_name, messages=messages
        )
        if len(response.choices) == 0:
            raise CompletionException(
                "No completion choices were returned by the OpenAI API."
            )

        if next_message := response.choices[0].message.content:
            return next_message

        raise CompletionException
