from collections import deque
from copy import copy
from dataclasses import dataclass
from typing import Any, Dict, List, Type

from airena.db import write_history_to_db
from airena.enums import DatabaseSave
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

    def run_debate(self):
        queue = deque(copy(self.adapters))
        for i in range(self.max_conversation_depth):
            print(f"{i+1}/{self.max_conversation_depth}")
            current_adapter = queue.popleft()
            message = current_adapter.get_next_message(self.history)
            self.history.add_message(message)
            queue.append(current_adapter)

    def write_results_to_db(self) -> DatabaseSave:
        """
        Ideally I'd have some kind of manager class to do this instead of this.
        This class is only supposed to manage the debating back and forth, not
        also the saving of the data to the database.
        """

        return write_history_to_db(
            [adapter.to_json() for adapter in self.adapters],
            self.history.to_json_serialisable(self.adapters),
        )
