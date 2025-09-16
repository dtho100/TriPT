import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

system_msg = "You are a helpful assistant"

user_msg = "Tell me about the weather over the next 4 hours in Toronto, ON"

response = client.chat.completions.create(model="gpt-5-nano",
                                        messages=[{"role": "system", "content": system_msg},
                                                  {"role": "user", "content": user_msg}])

response