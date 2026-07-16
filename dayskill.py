# Digital Twin - standalone script version (run with: python twin_app.py)
# Place this file in your project folder (next to the "twin" folder)

import os
import json

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

MODEL = "llama-3.3-70b-versatile"  # more reliable with tool calls than gpt-oss-20b

# --- Connect to Groq (OpenAI-compatible endpoint) ---
load_dotenv(override=True)
openai = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

# --- Load your context: LinkedIn PDF + summary ---
reader = PdfReader("twin/linkedin.pdf")
linkedin = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin += text

with open("twin/summary.txt", "r", encoding="utf-8") as f:
    summary = f.read()

# --- Tool: record a visitor's email(s) ---
def record_email_tool(email):
    print(f"Recording email: {email}")
    with open("emails.txt", "a", encoding="utf-8") as f:
        f.write(email + "\n")

record_email_json = {
    "name": "record_emails",
    "description": "Record one or more email addresses of a visitor who wants to get in touch. If the visitor gives several emails, include ALL of them in a single call.",
    "parameters": {
        "type": "object",
        "properties": {
            "emails": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Every email address the visitor provided",
            }
        },
        "required": ["emails"],
    },
}

tools = [{"type": "function", "function": record_email_json}]

# --- System prompt ---
system_prompt = f"""

# Your role

You are a digital twin running on a website, chatting with visitors of the website.
You represent the person who's website you are on.
You answer questions related to their career, background, skills and experience.

Here are the details of the person you are representing:

{summary}

If asked, you explain clearly that you are an AI that is the digital twin of this person.

# Context

Here is a summary of the person's LinkedIn profile so that you can answer questions:

{linkedin}

# Rules

Engage with the user. Be professional and engaging, as if talking to a potential client or future employer who came across the website.
Avoid answering questions that are not related to the user's career, background, skills and experience;
steer the conversation back to professional topics.

Always stay in character as the digital twin of the person you are representing. Represent the person.

IMPORTANT: If you don't know the answer, say so. Never make up an answer.
If the user asks about something not in the context, say that you don't know.
"""

# --- Chat function with tool-call loop (agent loop) ---
def chat(message, history):
    messages = [{"role": "system", "content": system_prompt}] + history + [
        {"role": "user", "content": message}
    ]
    response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)

    while response.choices[0].finish_reason == "tool_calls":
        msg = response.choices[0].message
        messages.append(msg)
        for tool_call in msg.tool_calls:
            emails = json.loads(tool_call.function.arguments).get("emails", [])
            for email in emails:
                record_email_tool(email)
            messages.append(
                {"role": "tool", "content": f"Recorded {len(emails)} email(s)", "tool_call_id": tool_call.id}
            )
        response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)

    return response.choices[0].message.content

# --- Launch the Gradio UI ---
if __name__ == "__main__":
    gr.ChatInterface(chat).launch(inbrowser=True)