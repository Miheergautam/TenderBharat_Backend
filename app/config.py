import os
from dotenv import load_dotenv

load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_API_URL = os.getenv("LLM_API_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
MONGODB_URI = os.getenv("MONGO_CONNECTION_STRING")
