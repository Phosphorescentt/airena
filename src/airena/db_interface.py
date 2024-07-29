from itertools import cycle
from typing import TYPE_CHECKING

from airena.db import (
    Conversation,
    ConversationEntry,
    Participant,
)
from airena.enums import DatabaseSave

if TYPE_CHECKING:
    from airena.engine import DebateEngine


class ConversationInterface:
    @staticmethod
    def write_conversation_and_history(engine: "DebateEngine") -> DatabaseSave:
        conversation = Conversation(
            system_prompt=engine.history.system_prompt,
        )
        conversation.save()

        sorted_adapters = sorted(
            engine.adapters, key=lambda x: x._turn_information.position
        )
        participants = Participant.bulk_upsert(
            model_names=[adapter.model_name for adapter in sorted_adapters]
        )

        for i, (participant, row) in enumerate(
            zip(cycle(participants), engine.history.rows)
        ):
            history = ConversationEntry(
                conversation_id=conversation.id,
                message_index=i,
                message_content=row,
                participant_id=participant.id,
            )
            history.save()

        return DatabaseSave.SUCCESS

    @staticmethod
    def read_conversation_and_history(engine: "DebateEngine"):
        pass
