from airena.db_interface import ConversationInterface
from conftest import mock_database
import unittest.mock as mock

from airena.db import Conversation, ConversationEntry, LanguageModel, Participant
from airena.engine import DebateEngine, DebateConfig

import pytest


@pytest.fixture(scope="module")
def mock_adapters():
    with mock.patch("openai.OpenAI.__init__") as mock_open_ai:
        mock_open_ai.return_value = None
        yield


class TestConversation:
    def test_write_conversation_and_history(self, mock_database, mock_adapters):
        # TODO: Decouple this `write_conversation_and_history` method a bit more.
        # I should be able to test this without having to write a bunch of engine
        # boilerplate and mocking the adapters.
        engine = DebateEngine.from_config(
            DebateConfig(
                conversation_depth=2,
                model_names=["gpt-3.5-turbo", "gpt-3.5-turbo"],
                system_prompt="Test system prompt.",
            )
        )

        engine.history.rows.extend(["Message one", "Message two"])
        ConversationInterface.write_conversation_and_history(engine)

        c = Conversation.select().namedtuples().first()
        assert c.system_prompt == engine.history.system_prompt

        models = LanguageModel.select().namedtuples()
        assert len(models) == 1
        model = models[0]
        assert model.model_name == "gpt-3.5-turbo"

        cps = Participant.select().namedtuples()
        assert cps[0].model_id == model.id
        assert cps[1].model_id == model.id

        chs = ConversationEntry.select().namedtuples()
        assert chs[0].message_index == 0
        assert chs[0].message_content == engine.history.rows[0]
        assert chs[0].conversation_id == c.id

        assert chs[1].message_index == 1
        assert chs[1].message_content == engine.history.rows[1]
        assert chs[1].conversation_id == c.id


# def test_write_history(mock_database, mock_adapters):
#     engine = DebateEngine.from_config(
#         DebateConfig(
#             conversation_depth=2,
#             model_names=["gpt-3.5-turbo", "gpt-3.5-turbo"],
#             system_prompt="Test system prompt.",
#         )
#     )
#
#     engine.history.rows.extend(["Message one", "Message two"])
#     db.write_history(engine)
#
#     with db.get_db_connection() as con:
#         cur = con.cursor()
#         cur.execute("select * from conversation")
#         assert cur.fetchone() == (1, 2, 2, "Test system prompt.")
#
#         cur.execute("select * from conversation_participant")
#         assert cur.fetchall() == [
#             (1, "gpt-3.5-turbo", 0, 1),
#             (2, "gpt-3.5-turbo", 1, 1),
#         ]
#
#         cur.execute("select * from conversation_history")
#         assert cur.fetchall() == [
#             (1, 1, 0, "Message one"),
#             (2, 1, 1, "Message two"),
#         ]