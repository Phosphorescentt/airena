from collections import deque
from copy import copy
from dataclasses import dataclass
from typing import Any, Dict, List, Type

from airena.adapters import Adapter, OpenAIAdapter

MODEL_NAME_TO_ADAPTER_MAP: Dict[str, Type[Adapter]] = {
    "gpt-3.5-turbo": OpenAIAdapter,
}


@dataclass
class TurnInformation:
    position: int
    total_participants: int


@dataclass
class DebateConfig:
    conversation_depth: int
    database_connection_string: str
    model_names: List[str]
    system_prompt: str


@dataclass
class DebateHistory:
    """Stores the history of a debate and the initial prompt.

    Needs a serialise method to turn this object into a string that can be put into
    a database.
    """

    system_prompt: str
    rows: List[str]

    @staticmethod
    def from_prompt(prompt: str) -> "DebateHistory":
        return DebateHistory(system_prompt=prompt, rows=[])

    def add_message(self, message: str):
        self.rows.append(message)

    def to_json_serialisable(self, adapters: List[Adapter]) -> List[Dict[str, Any]]:
        total_participants = adapters[0]._turn_information.total_participants

        history: List[Dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt}
        ]

        for i, row in enumerate(self.rows):
            history.append({"adapter_no": i % total_participants, "content": row})

        return history


@dataclass
class DebateEngine:
    """Manages running the debate.

    Takes the current DebateHistory, sends it off to a model, appends the model's
    repsonse to the DebateHistory, repeats for the other model up to a defined limit.
    """

    # In most cases this will be len 2 but maybe we will want 3 talking to
    # eachother at some point.
    adapters: List[Adapter]
    history: DebateHistory
    max_conversation_depth: int

    @staticmethod
    def from_config(config: DebateConfig) -> "DebateEngine":
        return DebateEngine(
            adapters=[
                MODEL_NAME_TO_ADAPTER_MAP[
                    model_name
                ].from_model_name_and_turn_information(
                    model_name,
                    TurnInformation(
                        position=i, total_participants=len(config.model_names)
                    ),
                )
                for i, model_name in enumerate(config.model_names)
            ],
            max_conversation_depth=config.conversation_depth,
            history=DebateHistory.from_prompt(config.system_prompt),
        )

    def run_debate(self) -> DebateHistory:
        queue = deque(copy(self.adapters))
        for _ in range(self.max_conversation_depth):
            current_adapter = queue.popleft()
            message = current_adapter.get_next_message(self.history)
            self.history.add_message(message)
            queue.append(current_adapter)

        return self.history
