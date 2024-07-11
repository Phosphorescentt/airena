import json
from dotenv import load_dotenv

from airena.engine import DebateConfig, DebateEngine


# TODO: Set this up better lol. This should be one function that dispatches elsewhere
# based on some subcommands, not multiple functions.
def argue():
    load_dotenv()
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
    print("review!")
