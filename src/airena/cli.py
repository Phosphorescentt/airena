import json
from collections import deque
from dotenv import load_dotenv

from airena.engine import DebateConfig, DebateEngine
from airena.db import (
    setup_db,
    get_unreviewed_conversation_history,
    write_conversation_history_point_score,
)


# TODO: Set this up better lol. This should be one function that dispatches elsewhere
# based on some subcommands, not multiple functions.
def argue():
    load_dotenv()
    setup_db()
    config = DebateConfig(
        conversation_depth=8,
        model_names=["gpt-3.5-turbo", "gpt-3.5-turbo"],
        system_prompt="You are in a debate competition. You are arguing FOR the following motion: `The death penalty should be legalised`",
    )

    engine = DebateEngine.from_config(config)
    engine.run_debate()
    history = engine.history
    engine.write_results_to_db()

    json_history = history.to_json_serialisable(engine.adapters)
    with open("history.json", "w") as f:
        json.dump(json_history, f, indent=4)

    print(json_history)


def review():
    # No load dotenv as we are not actually using APIs for anything this time.
    setup_db()
    print("Review time!")
    unreviewed_history = get_unreviewed_conversation_history()

    print(f"prompt: {unreviewed_history.system_prompt}")

    for i, message in enumerate(unreviewed_history.history):
        print(f"{i % unreviewed_history.total_participants}: {message}")
        if i < unreviewed_history.first_message:
            continue
        elif unreviewed_history.last_message and i > unreviewed_history.last_message:
            break
        else:
            while True:
                print(
                    """Who is winning?\n(1-10, 1 is agent 1 is winning, 10 is agent 2 is winning.)"""
                )
                current_score = input(">>> ")
                try:
                    current_score_float = float(current_score)
                    write_conversation_history_point_score(
                        unreviewed_history.conversation_id,
                        i,
                        current_score_float,
                    )
                    break
                except ValueError:
                    print("Invalid winner, please enter an int.")
