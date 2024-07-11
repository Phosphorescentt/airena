import pytest
from airena.utils import flip_roles


@pytest.mark.parametrize(
    ("messages", "expected_messages"),
    [
        (
            [{"role": "system", "content": "asdf"}],
            [{"role": "system", "content": "asdf"}],
        ),
        (
            [{"role": "system", "content": "FOR"}],
            [{"role": "system", "content": "AGAINST"}],
        ),
        (
            [{"role": "system", "content": "AGAINST"}],
            [{"role": "system", "content": "FOR"}],
        ),
        (
            [
                {"role": "user", "content": "Test data"},
            ],
            [
                {"role": "assistant", "content": "Test data"},
            ],
        ),
    ],
)
def test_flip_roles(messages, expected_messages):
    assert flip_roles(messages) == expected_messages
