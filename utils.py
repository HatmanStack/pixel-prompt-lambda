import boto3
import json
import base64
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from config import aws_id, aws_secret, gpc_api_key

def gemini_2(item):
    client = genai.Client(api_key=gpc_api_key)

    contents = item.get('prompt')

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp-image-generation",
        contents=contents,
        config=types.GenerateContentConfig(
        response_modalities=['Text', 'Image']
        )
    )

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = Image.open(BytesIO((part.inline_data.data)))
            image.save("/tmp/response.png", overwrite=True)
            return part.inline_data.data
            
def imagen_3(item):
    client = genai.Client(api_key=gpc_api_key)
    prompt = item.get('prompt')
    response = client.models.generate_images(
        model='imagen-3.0-generate-002',
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images= 1,
        )
    )
    for generated_image in response.generated_images:
        image = Image.open(BytesIO(generated_image.image.image_bytes))
        image.save("/tmp/response.png", overwrite=True)
        # make sure this returns a base64 encoded string
        print(f'IMAGE: {generated_image.image.image_bytes}')
        return generated_image.image.image_bytes


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
        image.save("/tmp/response.png", overwrite=True)
        print('Image Saved')
        base64_image = base64.b64encode(image_data).decode('utf-8')
        return base64_image
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
    image.save("/tmp/response.png", overwrite=True)
    return base64_image  # Directly return the base64 encoded string