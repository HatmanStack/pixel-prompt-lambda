import boto3
import json
import base64
import google.genai as genai
from google.genai import types
from PIL import Image
from openai import OpenAI
from io import BytesIO
import requests
from config import gpc_api_key, recraft_api_key

def gemini_2(item):
    print("gemini_2")
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
            image_stream = part.inline_data.data
            image = Image.open(BytesIO((image_stream)))
            image.save("/tmp/response.png", overwrite=True)
            with open('/tmp/response.png', 'rb') as f:
                base64_img = base64.b64encode(f.read()).decode('utf-8')
            print(base64_img[:150])
            return base64_img

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
        image_stream = generated_image.image.image_bytes
        image = Image.open(BytesIO(image_stream))
        image.save("/tmp/response.png", overwrite=True)
        with open('/tmp/response.png', 'rb') as f:
            base64_img = base64.b64encode(f.read()).decode('utf-8')
        
        return base64_img

def recraft_3(item):
    client = OpenAI(
        base_url='https://external.api.recraft.ai/v1',
        api_key=recraft_api_key,
    )

    # Get the prompt from the item
    prompt = item.get('prompt', 'race car on a track')

    # Generate image using Recraft API
    response = client.images.generate(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )

    # Extract the URL from the response
    image_url = response.data[0].url
    print(f"Generated image URL: {image_url}")

    # Download the image from the URL
    image_response = requests.get(image_url)
    
    if image_response.status_code == 200:
        # Save the image
        image = Image.open(BytesIO(image_response.content))
        image.save("/tmp/response.png")
        
        # Convert to base64
        with open('/tmp/response.png', 'rb') as f:
            base64_img = base64.b64encode(f.read()).decode('utf-8')
        
        return base64_img
    else:
        print(f"Failed to download image. Status code: {image_response.status_code}")
        return None

