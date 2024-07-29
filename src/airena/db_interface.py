from typing import TYPE_CHECKING

from airena.db import Conversation, ConversationHistory, ConversationParticipant
from airena.enums import DatabaseSave

if TYPE_CHECKING:
    from airena.engine import DebateEngine


class ConversationInterface:
    @staticmethod
    def write_conversation_and_history(engine: "DebateEngine") -> DatabaseSave:
        conversation = Conversation(
            total_participants=len(engine.adapters),
            length=engine.max_conversation_depth,
            system_prompt=engine.history.system_prompt,
        )
        conversation.save()

        for adapter in engine.adapters:
            participant = ConversationParticipant(
                model_name=adapter.model_name,
                turn_position=adapter._turn_information.position,
                conversation_id=conversation.id,
            )
            participant.save()

        for i, row in enumerate(engine.history.rows):
            history = ConversationHistory(
                conversation_id=conversation.id, message_number=i, message_content=row
            )
            history.save()

        return DatabaseSave.SUCCESS
