import os
from dotenv import load_dotenv

load_dotenv()

FIREWORKS_API_KEY = os.getenv('FIREWORKS_API_KEY')
FIREWORKS_API_URL = "https://api.fireworks.ai/inference/v1/chat/completions"
FIREWORKS_MODEL = "accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new"

PORT = int(os.getenv("PORT", "10000")) 
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
