import boto3
import json
import base64
import openai
import requests
from PIL import Image
from io import BytesIO
from config import aws_id, aws_secret, openai_api_key, perm_negative_prompt, stability_api_key, gpc_api_key, recraft_api_key, bfl_api_key

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
        base64_img = base64.b64encode(image_response.content).decode('utf-8')
        return base64_img
    else:
        print(f"Failed to download image from OpenAI. Status code: {image_response.status_code}")
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
    return base64_image

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
            print(part.text) # Log any text parts
        elif part.inline_data is not None:
            # Directly encode the inline image data bytes to base64
            image_bytes = part.inline_data.data
            base64_img = base64.b64encode(image_bytes).decode('utf-8')
            print(f"Gemini 2 generated image (first 150 chars): {base64_img[:150]}")
            return base64_img # Return the base64 string

    print("No image data found in Gemini 2 response.")
    return None

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
        image.save(f'/tmp/{item.get('target')}-{item.get("modelID")}response.png', overwrite=True)
        with open(f'/tmp/{item.get('target')}-{item.get("modelID")}response.png', 'rb') as f:
            base64_img = base64.b64encode(f.read()).decode('utf-8')
        
        return base64_img

def recraft_3(item):
    client = OpenAI(
        base_url='https://external.api.recraft.ai/v1',
        api_key=recraft_api_key,
    )
    prompt = item.get('prompt', 'race car on a track')
    response = client.images.generate(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    image_url = response.data[0].url
    print(f"Generated image URL: {image_url}")
    image_response = requests.get(image_url)
    if image_response.status_code == 200:
        # Directly encode the downloaded content to base64
        base64_img = base64.b64encode(image_response.content).decode('utf-8')
        return base64_img
    else:
        print(f"Failed to download image. Status code: {image_response.status_code}")
        return None

def firework(item, model_id):
    prompt = item.get('prompt')
    base64_img = None
    headers = {}
    data = {}
    url = ""

    try:
        if "Black Forest" in model_id: # Covers Dev and Schnell
            # Fireworks AI Configuration
            url_suffix = "flux-dev" if "Dev" in model_id else "flux-pro-1.1"
            
            response = requests.post(
                f'https://api.us1.bfl.ai/v1/{url_suffix}',
                headers={
                    'accept': 'application/json',
                    'x-key': bfl_api_key,
                    'Content-Type': 'application/json',
                },
                json={
                    'prompt': prompt,
                    'width': 1024,
                    'height': 1024,
                },
            ).json()
            
            image_url = response.id
            print(f'IMAGE URL: {image_url}')
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                print('Status from BFL 200')
                base64_img = base64.b64encode(image_response.content).decode('utf-8')
            else:
                print(f"Error from {model_id}: {response.status_code} - {response.text}")

        elif "Stable Diffusion 3.5 Turbo" in model_id:
            # Stability AI Configuration
            url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
            headers = {
                "authorization": f"Bearer {stability_api_key}",
                "accept": "image/*"
            }
            files = {'none': ''} # Required for multipart/form-data
            data = {
                "prompt": prompt,
                "model": "sd3-large-turbo", # Specify the turbo model
                "output_format": "png",
                "aspect_ratio": "1:1" # Or use width/height
            }
            # Make Stability AI request
            response = requests.post(url, headers=headers, files=files, data=data)
            if response.status_code == 200:
                base64_img = base64.b64encode(response.content).decode('utf-8')
            else:
                print(f"Error from {model_id}: {response.status_code} - {response.text}")
                try:
                    print(response.json()) # Attempt to print JSON error details
                except requests.exceptions.JSONDecodeError:
                    pass # Ignore if response body isn't valid JSON

        else:
            print(f"Error: Model ID '{model_id}' not handled by firework function.")
            return None # Explicitly return None for unhandled models

        if base64_img:
            print(f"Successfully generated image from {model_id}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed for {model_id}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred in firework function for {model_id}: {e}")

    return base64_img