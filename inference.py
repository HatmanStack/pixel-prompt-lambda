import random
import re
import requests
import json
import base64
import time
from PIL import Image
from io import BytesIO
import openai
from gradio_client import Client, file
from huggingface_hub import InferenceClient
from config import API_URL, headers, perm_negative_prompt, options, openai_api_key, token
from image_processing import formatReturn, save_image
from aws_utils import lambda_image, nova_canvas

def inferenceAPI(model, item, attempts=1):
    if attempts > 5:
        return 'An error occurred when Processing', model
    prompt = item.get('prompt')
    if "dallinmackay" in model:
        prompt = "lvngvncnt, " + item.get('prompt')
    data = {"inputs": prompt, "negative_prompt": perm_negative_prompt, "options": options, "timeout": 45}
    api_data = json.dumps(data)
    print(f'API DATA: {api_data}')
    try:
        response = requests.request("POST", API_URL + model, headers=headers, data=api_data)
        if response is None:
            return("Error in Inference")
        
        image_stream = BytesIO(response.content)
        image = Image.open(image_stream)
        image.save("/tmp/response.png", overwrite=True)
        with open('/tmp/response.png', 'rb') as f:
            base64_img = base64.b64encode(f.read()).decode('utf-8')
        return model, base64_img
    except Exception as e:
        print(f'Error When Processing Image: {e}')
        #activeModels = InferenceClient().list_deployed_models()
        #model = get_random_model(activeModels['text-to-image'])
        #pattern = r'^(.{1,30})\/(.{1,50})$'
        #if not re.match(pattern, model):
            #return "error model not valid", model
        #return inferenceAPI(model, item, attempts + 1)
        return 'Error When Calling Model'

def get_random_model(models):
    model = None
    priorities = [
        "stabilityai/stable-diffusion-3.5-large-turbo",
        "black-forest-labs",
        "stabilityai/stable-diffusion-3.5-large-turbo",
        "deepseek-ai/Janus-Pro-7B",
        "stabilityai/stable-diffusion-3.5-large",
        "kandinsky-community",
        "Kolors-diffusers",
        "Juggernaut",
        "insaneRealistic",
        "MajicMIX",
        "digiautogpt3",
        "fluently"
    ]
    random.shuffle(priorities)

    for priority in priorities:
        for i, model_name in enumerate(models):
            if priority in model_name:
                model = models[i]
                break
    if model is None:
        print("Choosing randomly")
        model = random.choice(models)
    return model

def gradioHatmanInstantStyle(item):
    client = Client("Hatman/InstantStyle")
    image_stream = BytesIO(base64.b64decode(item.get('image').split("base64,")[1]))
    image = Image.open(image_stream)
    image.save("/tmp/style.png",overwrite=True)
    result = client.predict(
            image_pil=file("/tmp/style.png"),
            prompt=item.get('prompt'),
            n_prompt=perm_negative_prompt,
            scale=1,
            control_scale=item.get('control'),
            guidance_scale=item.get('guidance'),
            num_inference_steps=item.get('steps'),
            seed=1,
            target=item.get('target'),
            api_name="/create_image"
    )
    
    return formatReturn(result)

def image_check(item, attempts=1):
    try:
        API_URL = "https://api-inference.huggingface.co/models/Falconsai/nsfw_image_detection"
        with open('/tmp/response.png', 'rb') as f:
            data = f.read()
        response = requests.request("POST", API_URL, headers=headers, data=data)
        decoded_response = response.content.decode("utf-8")
        print("Raw response:", decoded_response)
        
        json_response = json.loads(decoded_response)
        
        if "error" in json_response:
            time.sleep(json_response["estimated_time"])
            return image_check(item, attempts+1)
        
        scores = {item['label']: item['score'] for item in json_response}
        nsfw_score = scores.get('nsfw', 0)
        print(f"NSFW Score: {nsfw_score}")
        print(f"Type of score: {type(nsfw_score)}")
        print(f"Comparison result: {nsfw_score > 0.1}")
        return nsfw_score > 0.1
    except json.JSONDecodeError as e:
        print(f'JSON Decoding Error: {e}')
        return True
    except Exception as e:
        print(f'NSFW Check Error: {e}')
        if attempts > 30:
            return True
        return image_check(item, attempts+1)

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

def inference(item):
    print('inference start')
    #client = InferenceClient(token=token)  # token optional for some operations

    # Get the list of deployed models
    #deployed_models = client.list_deployed_models()
    #print(deployed_models)
    base64_img = ""
    model = item.get('modelID')
    check_img = False
    try:
        if item.get('image'):
            model = "stabilityai/stable-diffusion-xl-base-1.0"
            base64_img = gradioHatmanInstantStyle(item)
        elif "stabilityai/stable-diffusion-3.5-large-turbo" in item.get('modelID'):
            model, base64_img = inferenceAPI(item.get('modelID'), item)
        elif "deepseek-ai/Janus-Pro-7B" in item.get('modelID'):
            model, base64_img = inferenceAPI(item.get('modelID'), item)
        elif "forest" in item.get('modelID'):
            print('test')
            model, base64_img = inferenceAPI(item.get('modelID'), item)
        elif "OpenAI Dalle3" in item.get('modelID'):
            model = 'OpenAI Dalle3' 
            base64_img = dalle3(item)
        elif "AWS Nova Canvas" in item.get('modelID'):
            model = 'AWS Nova Canvas'
            base64_img = nova_canvas(item)
        elif "stabilityai/stable-diffusion-3.5-large" in item.get('modelID'):
            model, base64_img = inferenceAPI(item.get('modelID'), item)
        elif "Voxel" in item.get('modelID') or "pixel" in item.get('modelID'):
            prompt = item.get('prompt')
            if "Voxel" in item.get('modelID'):
                prompt = "voxel style, " + item.get('prompt')
            base64_img = lambda_image(prompt, item.get('modelID'))
        else:
            model, base64_img = item.get('modelID'), "Error in Inference"
        if 'error' in base64_img:
            return {"output": base64_img, "model": model}
        check_img = image_check(item)
        save_image(base64_img, item, model, check_img)
    except Exception as e:
        print(f"An error occurred: {e}")
        base64_img = f"An error occurred: {e}"
    return {"output": base64_img, "model": model, "NSFW": check_img}