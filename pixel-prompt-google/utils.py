import boto3
import json
import base64
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from config import aws_id, aws_secret, gpc_api_key, 

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

