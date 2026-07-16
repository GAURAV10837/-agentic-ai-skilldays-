import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)
groq_api_key = os.getenv("GROQ_API_KEY")

request = """
create one difficult question that i can ask different ai model to compare how well they think.
Do not make it math question.
Make a question that require decesion making and judgment.
The question should ask for an answer of 2-3 sentences that include reasoning,not just Yes or NO.
"""
request += "Reply with only question,no explanation ,no extra word."
messages=[{"role":"user", "content":request}]

messages

from openai import OpenAI

openai = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")

response = openai.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=messages,
)

question = response.choices[0].message.content
print(question)

competitors = []
answers = []
messages = [{"role":"user", "content":question}]

def record(model_name,answer):
    competitors.append(model_name)
    answers.append(answer)
    print(answer)

ollama pull llama3.2
import requests
requests.get('http://localhost:11434').content
import requests
models = requests.get('http://localhost:11434/v1/models').json()
for model in models.get("data"):
    print(model.get("id"))

 ollama = OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
model_name = "llama3.2:latest"

response = ollama.chat.completions.create(model=model_name, messages=messages)
answer = response.choices[0].message.content

record(model_name, answer)