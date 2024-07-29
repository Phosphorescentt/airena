from typing import List, Optional
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

from airena.enums import DatabaseSave

DB_FILENAME = "airena.db"
DB = SqliteDatabase(DB_FILENAME)


def setup_db(db: Database):
    with db:
        db.create_tables(
            [
                Conversation,
                LanguageModel,
                Participant,
                ConversationEntry,
                ConversationReview,
            ]
        )


class BaseModel(Model):
    class Meta:
        database = DB


class Conversation(BaseModel):
    id = AutoField()
    system_prompt = CharField()

    @staticmethod
    def get_unreviewed_conversation() -> Optional["Conversation"]:
        unreviewed_conversation = (
            Conversation.select()
            .left_outer_join(ConversationReview)
            # NOTE: Must use double equals here. Ignore E711 errors.
            .where(ConversationReview.value == None)  #  noqa: E711
            .get_or_none()
        )

        return unreviewed_conversation

    def set_review_value(self, value: float) -> DatabaseSave:
        review = ConversationReview(conversation_id=self.id, value=value)
        review.save()
        return DatabaseSave.FAILURE


class LanguageModel(BaseModel):
    id = AutoField()
    model_name = CharField(unique=True)


class Participant(BaseModel):
    id = AutoField()
    model_id = ForeignKeyField(LanguageModel)

    @staticmethod
    def bulk_upsert(model_names: List[str]) -> List["Participant"]:
        models = [
            LanguageModel.get_or_create(model_name=model_name)[0]
            for model_name in model_names
        ]
        participants = [Participant(model_id=model.id) for model in models]
        [p.save() for p in participants]

        return participants


class ConversationEntry(BaseModel):
    id = AutoField()
    conversation_id = ForeignKeyField(Conversation)
    participant_id = ForeignKeyField(Participant)
    message_index = IntegerField()
    message_content = CharField()

    @staticmethod
    def get_conversation_history(
        conversation: Conversation,
    ) -> List["ConversationEntry"]:
        return ConversationEntry.select().where(
            ConversationEntry.conversation_id == conversation.id
        )


class ConversationReview(BaseModel):
    id = AutoField()
    conversation_id = ForeignKeyField(Conversation)
    value = FloatField()
