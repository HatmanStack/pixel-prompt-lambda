import boto3
import json
import base64
from PIL import Image
from io import BytesIO
from config import aws_id, aws_secret

def lambda_image(prompt, modelID):
    data = {
        "prompt": prompt,
        "modelID": modelID
    }
    serialized_data = json.dumps(data)
    try:
        session = boto3.Session(aws_access_key_id=aws_id, aws_secret_access_key=aws_secret, region_name='us-west-1')
        lambda_client = session.client('lambda')
        response = lambda_client.invoke(
            FunctionName='pixel_prompt_lambda',
            InvocationType='RequestResponse',
            Payload=serialized_data
        )
        response_payload = response['Payload'].read()
        response_data = json.loads(response_payload)
    except Exception as e:
        print(f"An error occurred: {e}")
    return response_data['body']

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
    image.save("/tmp/response.png", overwrite=True)
    return base64_image  # Directly return the base64 encoded string