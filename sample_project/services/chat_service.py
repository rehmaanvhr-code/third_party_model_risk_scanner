import os
from openai import OpenAI
import anthropic

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
claude = anthropic.Anthropic()


def answer(question):
    r = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": question}])
    return r.choices[0].message.content


def summarize(text):
    r = claude.messages.create(model="claude-sonnet-4-5", max_tokens=300,
                               messages=[{"role": "user", "content": text}])
    return r.content[0].text
