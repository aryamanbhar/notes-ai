from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()  # load variables from .env into environment

api_key = os.getenv("OPENAI_API_KEY")

print("API key loaded:", api_key)  # just to verify

client = OpenAI(api_key=api_key)