import os
from dotenv import load_dotenv

load_dotenv()

gpc_api_key = os.getenv('GPC_API_KEY')
aws_id = os.environ.get("AWS_ID")
aws_secret = os.environ.get("AWS_SECRET")
recraft_api_key = os.environ.get("RECRAFT_API_KEY")
groq_api_key = os.environ.get("GROQ_API_KEY")
prompt_model = "llama-3.3-70b-versatile"