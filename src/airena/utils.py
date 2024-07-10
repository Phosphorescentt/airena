from copy import deepcopy
from typing import Dict, List


def flip_roles(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    copied_messages = deepcopy(messages)
    for message in copied_messages:
        if message["role"] == "user":
            message["role"] = "assistant"
        elif message["role"] == "assistant":
            message["role"] = "user"
        elif message["role"] == "system":
            if "FOR" in message["content"]:
                message["content"] = message["content"].replace("FOR", "AGAINST")
            elif "AGAINST" in message["content"]:
                message["content"] = message["content"].replace("AGAINST", "FOR")

    return copied_messages
