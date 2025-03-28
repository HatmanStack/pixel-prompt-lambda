import base64
from PIL import Image
from io import BytesIO
import json
from datetime import datetime
import boto3
from config import aws_id, aws_secret

def update_timestamps(s3_client):
    bucket_name = 'pixel-prompt'
    key = 'rate-limit/ratelimit.json'
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        rate_limit_data = json.loads(response['Body'].read().decode('utf-8'))
    except s3_client.exceptions.NoSuchKey:
        rate_limit_data = {"timestamps": []}
    
    rate_limit_data["timestamps"].append(datetime.now().isoformat())
    
    s3_client.put_object(Bucket=bucket_name, Key=key, Body=json.dumps(rate_limit_data), ContentType='application/json')


def save_image(base64image, item, model, NSFW):
    print('save_image start')
    data = {
        "base64image": "data:image/png;base64," + base64image,
        "returnedPrompt": "Model:\n" + model + "\n\nPrompt:\n" + item.get('prompt'),
        "prompt": item.get('prompt'),
        "steps": item.get('steps'),
        "guidance": item.get('guidance'),
        "control": item.get('control'),
        "target": item.get('target')
    }
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    session = boto3.Session(aws_access_key_id=aws_id, aws_secret_access_key=aws_secret, region_name='us-west-2')
    s3_client = session.client('s3')
    if not NSFW:
        s3_key = f'images/{timestamp}.json'
        s3_client.put_object(Bucket='pixel-prompt', Key=s3_key, Body=json.dumps(data))
    else:
        s3_key = f'nondisplay_images/{timestamp}.json'
        s3_client.put_object(Bucket='pixel-prompt', Key=s3_key, Body=json.dumps(data))
    s3_key = f'prompts/{timestamp}.json'
    data.pop("base64image", None)
    s3_client.put_object(Bucket='pixel-prompt', Key=s3_key, Body=json.dumps(data))
    update_timestamps(s3_client)

