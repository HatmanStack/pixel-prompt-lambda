import random
import re
import requests
import json
import base64
import time
from PIL import Image
from io import BytesIO
from prompt import prompt_check
from huggingface_hub import InferenceClient
from config import API_URL, headers, perm_negative_prompt, options
from image_processing import save_image
from utils import dalle3, nova_canvas

def inferenceAPI(model, item, attempts=1):
    if attempts > 5:
        return 'An error occurred when Processing', model
    prompt = item.get('prompt')
    if "dallinmackay" in model:
        prompt = "lvngvncnt, " + item.get('prompt')
    data = {"inputs": prompt, "negative_prompt": perm_negative_prompt, "options": options, "timeout": 120}
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

def image_check(item, attempts=1):
    try:
        print("image check")
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
        return nsfw_score < 0.3
    except json.JSONDecodeError as e:
        print(f'JSON Decoding Error: {e}')
        return True
    except Exception as e:
        print(f'NSFW Check Error: {e}')
        if attempts > 30:
            return True
        return image_check(item, attempts+1)

def inference(item):
    print('inference start')
    #client = InferenceClient(token=token)  # token optional for some operations

    # Get the list of deployed models
    #deployed_models = client.list_deployed_models()
    #print(deployed_models)
    base64_img = "An error occurred: You're a Jerk"
    model = item.get('modelID')
    check_img = False
    if prompt_check(item.get('prompt')) and item.get('safety'):  
        return {"output": base64_img , "model": model, "NSFW": check_img}
    try:
        if "stable-diffusion" in item.get('modelID') or 'forest' in item.get('modelID'):
            model, base64_img = inferenceAPI(item.get('modelID'), item)
        elif "OpenAI Dalle3" in item.get('modelID'):
            model = 'OpenAI Dalle3' 
            base64_img = dalle3(item)
        elif "AWS Nova Canvas" in item.get('modelID'):
            model = 'AWS Nova Canvas'
            base64_img = nova_canvas(item)
        else:
            model, base64_img = item.get('modelID'), "Error in Inference"
        if 'error' in base64_img:
            return {"output": base64_img, "model": model}
        if item.get('safety'):
            check_img = image_check(item)
        else:
            check_img = False
        print(check_img)
        save_image(base64_img, item, model, check_img)
    except Exception as e:
        print(f"An error occurred: {e}")
        base64_img = f"An error occurred: {e}"
    return {"output": base64_img, "model": model, "NSFW": check_img}