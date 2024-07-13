from peewee import (
    AutoField,
    CharField,
    Database,
    FloatField,
    ForeignKeyField,
    IntegerField,
    Model,
    SqliteDatabase,
)

from airena.engine import DebateEngine
from airena.enums import DatabaseSave


DB_FILENAME = "airena.db"


db = SqliteDatabase(DB_FILENAME)


def setup_db(db: Database):
    with db:
        db.create_tables(
            [
                Conversation,
                ConversationParticipant,
                ConversationHistory,
                Review,
            ]
        )


class BaseModel(Model):
    class Meta:
        database = db


class Conversation(BaseModel):
    id = AutoField()
    total_participants = IntegerField()
    length = IntegerField()
    system_prompt = CharField()

    @staticmethod
    def write_conversation_and_history(engine: DebateEngine) -> DatabaseSave:
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


class ConversationParticipant(BaseModel):
    id = AutoField()
    model_name = CharField()
    turn_position = IntegerField()
    conversation_id = ForeignKeyField(Conversation)


class ConversationHistory(BaseModel):
    id = AutoField()
    conversation_id = ForeignKeyField(Conversation)
    message_number = IntegerField()
    message_content = CharField()


class Review(BaseModel):
    id = AutoField()
    conversation_history_id = ForeignKeyField(ConversationHistory)
    score = FloatField()
