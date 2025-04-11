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

def string_to_bool(value):
    if isinstance(value, str):
        return value.lower() == 'true'
    return bool(value)
    
def inference(item):
    print('inference start')
    base64_img = "An error occurred: You're a Jerk"
    model = item.get('modelID')
    
    if string_to_bool(prompt_check(item.get('prompt'))):  
        return {"output": base64_img , "model": model, "NSFW": True}
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
        
        save_image(base64_img, item, model)
    except Exception as e:
        print(f"An error occurred: {e}")
        base64_img = f"An error occurred: {e}"
    return {"output": base64_img, "model": model, "NSFW": False}