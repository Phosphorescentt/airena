import json
from dotenv import load_dotenv

from airena.engine import DebateConfig, DebateEngine


# def main():
#     load_dotenv()
#     client = OpenAI()
#
#     history = [
#         {
#             "role": "system",
#             "content": "You are in a debate competition."
#             "You are arguing FOR the following motion:"
#             "`The death penalty should be legalised`.",
#         }
#     ]
#
#     for _ in range(10):
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=history,
#         )
#         new_history = {
#             "role": "assistant",
#             "content": response.choices[0].message.content,
#         }
#         print(new_history)
#         history.append(new_history)
#         history = utils.flip_roles(history)
#
#     print("=============")
#     print(history)


def main():
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


if __name__ == "__main__":
    main()
