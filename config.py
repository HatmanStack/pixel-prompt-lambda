import os
from dotenv import load_dotenv

load_dotenv()

groq_api_key = os.environ.get("GROQ_API_KEY")
openai_api_key = os.getenv('OPENAI_API_KEY')  
token = os.environ.get("HF_TOKEN")
aws_id = os.environ.get("AWS_ID")
aws_secret = os.environ.get("AWS_SECRET")
options = {"use_cache": False, "wait_for_model": True}
parameters = {"max_new_tokens": 250}
headers = {"Authorization": f"Bearer {token}", "x-use-cache": "0", 'Content-Type': 'application/json'}
API_URL = f'https://api-inference.huggingface.co/models/'
perm_negative_prompt = "watermark, lowres, low quality, worst quality, deformed, glitch, low contrast, noisy, saturation, blurry"