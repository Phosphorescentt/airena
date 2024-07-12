import sqlite3
import unittest.mock as mock
from typing import Optional

from tempfile import NamedTemporaryFile

import airena.db as db
import pytest
from airena.engine import DebateConfig, DebateEngine


@pytest.fixture
def mock_database():
    with NamedTemporaryFile() as ntf, mock.patch(
        "airena.db.get_db_connection"
    ) as mock_db_connection:
        con = sqlite3.connect(ntf.name)
        mock_db_connection.return_value = con
        db.setup_db()
        yield con
        con.close()


@pytest.fixture(scope="module")
def mock_adapters():
    with mock.patch("openai.OpenAI.__init__") as mock_open_ai:
        mock_open_ai.return_value = None
        yield


def test_write_history(mock_database, mock_adapters):
    engine = DebateEngine.from_config(
        DebateConfig(
            conversation_depth=2,
            model_names=["gpt-3.5-turbo", "gpt-3.5-turbo"],
            system_prompt="Test system prompt.",
        )
    )

    engine.history.rows.extend(["Message one", "Message two"])
    db.write_history(engine)

    with db.get_db_connection() as con:
        cur = con.cursor()
        cur.execute("select * from conversation")
        assert cur.fetchone() == (1, 2, 2, "Test system prompt.")

        cur.execute("select * from conversation_participant")
        assert cur.fetchall() == [
            (1, "gpt-3.5-turbo", 0, 1),
            (2, "gpt-3.5-turbo", 1, 1),
        ]

        cur.execute("select * from conversation_history")
        assert cur.fetchall() == [
            (1, 1, 0, "Message one"),
            (2, 1, 1, "Message two"),
        ]


def test_get_unreviewed_conversation_history_point(mock_database, mock_adapters):
    engine = DebateEngine.from_config(
        DebateConfig(
            conversation_depth=2,
            model_names=["gpt-3.5-turbo", "gpt-3.5-turbo"],
            system_prompt="Test system prompt.",
        )
    )

    engine.history.rows.extend(["Message one", "Message two"])
    db.write_history(engine)

    review_info = db.get_unreviewed_conversation_history()
    assert review_info.total_participants == len(engine.adapters)
    assert review_info.first_unreviewed_message == 0
    assert review_info.last_unreviewed_message is None
    assert review_info.system_prompt == engine.history.system_prompt
    assert review_info.history == engine.history.rows
