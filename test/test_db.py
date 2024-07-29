import unittest.mock as mock

import pytest
from airena.db import Conversation
from conftest import mock_database


class TestConversation:
    @pytest.fixture(autouse=True)
    def mock_database(self, mock_database):
        yield

    def test_get_unreviewed_conversation(self):
        conversation = Conversation(system_prompt="Test Prompt")
        conversation.save()

        assert Conversation.get_unreviewed_conversation() == conversation
