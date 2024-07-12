# AIrena

Forcing LLMs to argue with each other and convince their counterpart that they are right.

## Setup

1. Clone the repo
1. Create a `.env` file and add the following: `OPENAI_API_KEY=<INSERT OPEN AI API KEY HERE>`
1. Do all the standard python setup stuff:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

4. Profit!

## Usage

Currently this package has two commands: `argue` and `review`.

- `argue`: Tell the package to start a conversation between two agents with the config as defined in `src/airena/cli.py:argue`
- `review`: Attempt to review any fragments of conversation that do not have a score against them in the `review` table.
