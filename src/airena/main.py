from dotenv import load_dotenv
from openai import OpenAI

from . import utils


# response = client.chat.completions.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {
#             "role": "system",
#             "content": "You are in a debate competition. You are arguing FOR the following motion: `The death penalty should be legalised`.",
#         },
#         {
#             "role": "user",
#             "content": "Who won the world series in 2020?",
#         },
#         {
#             "role": "assistant",
#             "content": "The Los Angeles Dodgers won the World Series in 2020.",
#         },
#         {
#             "role": "user",
#             "content": "Where was it played?",
#         },
#     ],
# )
#
# print(response.choices[0].message.content)


def main():
    load_dotenv()
    client = OpenAI()

    history = [
        {
            "role": "system",
            "content": "You are in a debate competition. You are arguing FOR the following motion: `The death penalty should be legalised`.",
        }
    ]

    for i in range(10):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=history,
        )
        new_history = {
            "role": "assistant",
            "content": response.choices[0].message.content,
        }
        print(new_history)
        history.append(new_history)
        history = utils.flip_roles(history)

    print("=============")
    print(history)


if __name__ == "__main__":
    main()
