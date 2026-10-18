from google import genai

from chatbot.llm import ask_llm

client = genai.Client()
prompt = "You are Pixel, a pirate-themed assistant. Answer in one short sentence and talk like a pirate."
print(ask_llm("Who are you?", client, "gemini-flash-latest", system_prompt=prompt))