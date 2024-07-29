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
            # TODO: Test if using `cond is None` works here
            # I know that it breaks SQLAlchemy.
            .where(ConversationReview.score is None)
            .get_or_none()
        )

        return unreviewed_conversation


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


class ConversationReview(BaseModel):
    id = AutoField()
    score = FloatField()
