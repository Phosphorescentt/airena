from typing import List
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
                ConversationParticipant,
                ConversationHistory,
                Review,
            ]
        )


class BaseModel(Model):
    class Meta:
        database = DB


class Conversation(BaseModel):
    id = AutoField()
    total_participants = IntegerField()
    length = IntegerField()
    system_prompt = CharField()

    @staticmethod
    def get_unreviewed_conversation() -> "Conversation":
        unreviewed_conversation = (
            Conversation.select()
            .join(ConversationHistory)
            .left_outer_join(Review)
            .where(Review.score == None)
            .get_or_none()
        )

        return unreviewed_conversation


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

    @staticmethod
    def get_history(conversation: Conversation) -> List["ConversationHistory"]:
        history_points: List[ConversationHistory] = (
            ConversationHistory.select()
            .where(ConversationHistory.conversation_id == conversation.id)
            .order_by(ConversationHistory.message_number.asc())
        )
        return history_points

    def set_review_value(self, score: float):
        review = Review(
            conversation_history_id=self.id,
            score=score,
        )
        review.save()


class Review(BaseModel):
    id = AutoField()
    conversation_history_id = ForeignKeyField(ConversationHistory, unique=True)
    score = FloatField()
