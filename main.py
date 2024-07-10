from dotenv import load_dotenv
from openai import OpenAI

import utils

load_dotenv()

client = OpenAI()


response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": "You are in a debate competition. You are arguing FOR the following motion: `The death penalty should be legalised`.",
        },
        {
            "role": "user",
            "content": "Who won the world series in 2020?",
        },
        {
            "role": "assistant",
            "content": "The Los Angeles Dodgers won the World Series in 2020.",
        },
        {
            "role": "user",
            "content": "Where was it played?",
        },
    ],
)

print(response.choices[0].message.content)

history = [
    {
        "role": "system",
        "content": "You are in a debate competition. You are arguing FOR the"
        "following motion: `The death penalty should be legalised`.",
    }
]

for i in range(10):
    pass
