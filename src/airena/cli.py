import itertools
import json

from dotenv import load_dotenv

from airena.db import DB, Conversation, ConversationEntry, Participant, setup_db
from airena.engine import DebateConfig, DebateEngine


# TODO: Set this up better lol. This should be one function that dispatches elsewhere
# based on some subcommands, not multiple functions.
def argue():
    load_dotenv()
    setup_db(DB)
    config = DebateConfig(
        conversation_depth=2,
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
    setup_db(DB)
    print("Review time!")

    # Get the raw data from the database
    unreviewed_conversation = Conversation.get_unreviewed_conversation()
    if not unreviewed_conversation:
        print("No unreviewed conversations left!")
        return

    conversation_entries = ConversationEntry.get_conversation_history(
        unreviewed_conversation
    )
    participants = set(
        Participant.select().where(
            Participant.id in [entry.participant_id for entry in conversation_entries]
        )
    )

    participants = [entry.participant_id for entry in conversation_entries]
    print(f"prompt: {unreviewed_conversation.system_prompt}")

    for i, (participant, entry) in enumerate(
        zip(itertools.cycle(participants), conversation_entries)
    ):
        print(f"{i % len(participants)}: {entry.message_content}")

    print(
        """Who is winning?\n(1-10, 1 is agent 1 is winning, 10 is agent 2 is winning.)"""
    )
    while True:
        current_score = input(">>> ")
        try:
            current_score_float = float(current_score)
            unreviewed_conversation.set_review_value(current_score_float)
            break
        except ValueError:
            print("Invalid winner, please enter an int.")
