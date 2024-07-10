import pytest
import airena


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
    assert airena.utils.flip_roles(messages) == expected_messages
