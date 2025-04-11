import base64
from PIL import Image
from io import BytesIO
import json
from datetime import datetime
import boto3
from config import aws_id, aws_secret

def save_image(base64image, item, model):
    print('save_image start')
    data = {
        "base64image": "data:image/png;base64," + base64image,
        "returnedPrompt": "Model:\n" + model + "\n\nPrompt:\n" + item.get('prompt'),
        "prompt": item.get('prompt'),
        "steps": item.get('steps'),
        "guidance": item.get('guidance'),
        "control": item.get('control'),
        "target": item.get('target'),
        "ip": item.get('ip')
    }
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    session = boto3.Session(aws_access_key_id=aws_id, aws_secret_access_key=aws_secret, region_name='us-west-2')
    s3_client = session.client('s3')
    
    s3_key = f'group-images/{item.get('target')}/{timestamp}.json'
    print(s3_key)
    print(json.dumps(data))
    
    s3_client.put_object(Bucket='pixel-prompt', Key=s3_key, Body=json.dumps(data))



