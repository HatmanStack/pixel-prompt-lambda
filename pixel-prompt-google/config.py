import os
from dotenv import load_dotenv

load_dotenv()

gpc_api_key = os.getenv('GPC_API_KEY')
aws_id = os.environ.get("AWS_ID")
aws_secret = os.environ.get("AWS_SECRET")