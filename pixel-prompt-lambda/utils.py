import boto3
import json
import base64
import openai
import requests
from PIL import Image
from io import BytesIO
from config import aws_id, aws_secret, openai_api_key, perm_negative_prompt

def dalle3(item):
    openai.api_key = openai_api_key
    prompt = item.get('prompt')
    response = openai.images.generate(
    model="dall-e-3",
    prompt= prompt,
    size="1024x1024",
    quality="standard",
    n=1,
    )
    image_url = response.data[0].url
    print(f'IMAGE URL: {image_url}')
    image_response = requests.get(image_url)
    if image_response.status_code == 200:
        print('Status from OPENAI 200')
        image_data = image_response.content
        image_stream = BytesIO(image_data)
        image = Image.open(image_stream)
        image.save(f'/tmp/{item.get('target')}-{item.get("modelID")}response.png', overwrite=True)
        with open(f'/tmp/{item.get('target')}-{item.get("modelID")}response.png', 'rb') as f:
            base64_img = base64.b64encode(f.read()).decode('utf-8')
        return base64_img
    return None

def nova_canvas(item):
    model_id = 'amazon.nova-canvas-v1:0'
    prompt = item.get('prompt')
    body = json.dumps({
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {
            "text": prompt
        },
        "imageGenerationConfig": {
            "numberOfImages": 1,
            "height": 1024,
            "width": 1024,
            "cfgScale": 8.0,
            "seed": 0
        }
    })

    session = boto3.Session(aws_access_key_id=aws_id, aws_secret_access_key=aws_secret, region_name='us-east-1')
    bedrock = session.client('bedrock-runtime')
    accept = "application/json"
    content_type = "application/json"
    response = bedrock.invoke_model(
        body=body, modelId=model_id, accept=accept, contentType=content_type
    )
    response_body = json.loads(response.get("body").read())
    base64_image = response_body.get("images")[0]
    image_data = base64.b64decode(base64_image)
    image_stream = BytesIO(image_data)
    image = Image.open(image_stream)
    image.save(f'/tmp/{item.get('target')}-{item.get("modelID")}response.png', overwrite=True)
    return base64_image

def stable_diffusion(item):
    model_id = 'stability.sd3-5-large-v1:0'
    prompt = item.get('prompt')
    body = json.dumps({
        "prompt": prompt,
        "mode": "text-to-image",
        "aspect_ratio": "1:1",
        "output_format": "png",
        "seed": 0,
        "negative_prompt": perm_negative_prompt
    })
    session = boto3.Session(aws_access_key_id=aws_id, aws_secret_access_key=aws_secret, region_name='us-west-2')
    print('SESSION CREATED')
    bedrock = session.client('bedrock-runtime')
    response = bedrock.invoke_model(
        body=body, modelId=model_id
    )
    response_body = json.loads(response.get("body").read())
    base64_image = response_body.get("images")[0]
    
    image_data = base64.b64decode(base64_image)
    image_stream = BytesIO(image_data)
    
    image = Image.open(image_stream)
    
    #For Image Checking Later image.save(f'/tmp/{item.get('target')}-{item.get("modelID")}response.png', overwrite=True)
    
    return base64_image