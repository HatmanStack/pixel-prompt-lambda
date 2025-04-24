import os
from dotenv import load_dotenv

load_dotenv()

groq_api_key = os.environ.get("GROQ_API_KEY")
openai_api_key = os.getenv('OPENAI_API_KEY')  
token = os.environ.get("HF_TOKEN")
gpc_api_key = os.getenv('GPC_API_KEY')
recraft_api_key = os.environ.get("RECRAFT_API_KEY")
aws_id = os.environ.get("AWS_ID")
aws_secret = os.environ.get("AWS_SECRET")
stability_api_key = os.environ.get("STABILITY_API_KEY")
bfl_api_key = os.environ.get("BFL_API_KEY")
holder=os.environ.get("GLOBAL_LIMIT")
holder1=os.environ.get("IP_LIMIT")
ip_include = os.environ.get("IP_INCLUDE")
global_limit = int(holder)  
ip_limit = int(holder1)
prompt_model = os.environ.get("PROMPT_MODEL")
perm_negative_prompt = "watermark, lowres, low quality, worst quality, deformed, glitch, low contrast, noisy, saturation, blurry"