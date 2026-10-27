from google import genai

from chatbot.config import get_api_key, load_env

load_env()
client = genai.Client(api_key=get_api_key())

for model in client.models.list():
    print(model.name)