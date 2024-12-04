import random
from huggingface_hub import InferenceClient, login
from gradio_client import Client, file
import re
from datetime import datetime
import json
import requests
import base64
import os 
import time
from PIL import Image
from io import BytesIO
import aiohttp
import asyncio
from dotenv import load_dotenv
import boto3
from groq import Groq

load_dotenv()
token = os.environ.get("HF_TOKEN")
groqClient = Groq (api_key=os.environ.get("GROQ_API_KEY"))
aws_id = os.environ.get("AWS_ID")
aws_secret = os.environ.get("AWS_SECRET")
prompt_model = "llama-3.1-8b-instant"
magic_prompt_model = "Gustavosta/MagicPrompt-Stable-Diffusion"
options = {"use_cache": False, "wait_for_model": True}
parameters = {"return_full_text":False, "max_new_tokens":300}
headers = {"Authorization": f"Bearer {token}", "x-use-cache":"0", 'Content-Type' :'application/json'}
API_URL = f'https://api-inference.huggingface.co/models/'
perm_negative_prompt = "watermark, lowres, low quality, worst quality, deformed, glitch, low contrast, noisy, saturation, blurry"
cwd = os.getcwd()
pictures_directory = os.path.join(cwd, 'pictures')
last_two_models = []

def getPrompt(prompt, modelID, attempts=1):
    response = {}
    print(modelID)
    try:  
        if modelID != magic_prompt_model:
            chat = [
                {"role": "user", "content": prompt_base},
                {"role": "assistant", "content": prompt_assistant},
                {"role": "user", "content": prompt},
                ]
            response = groqClient.chat.completions.create(messages=chat, temperature=1, max_tokens=2048, top_p=1, stream=False, stop=None, model=prompt_model) 
        else:
            apiData={"inputs":prompt, "parameters": parameters, "options": options, "timeout": 45}
            response = requests.post(API_URL + modelID, headers=headers, data=json.dumps(apiData))
            return response.json()
    except Exception as e:
        print(f"An error occurred: {e}")
        if attempts < 3:
            getPrompt(prompt, modelID, attempts + 1)
    return response

def inferencePrompt(itemString):
    print("Start API Inference Prompt")
    try:
        plain_response_data = getPrompt(itemString, prompt_model)
        magic_response_data = getPrompt(itemString, magic_prompt_model)
        returnJson = {"plain": plain_response_data.choices[0].message.content, "magic": itemString + magic_response_data[0]["generated_text"]}
        print(f'Return Json {returnJson}')
        return returnJson
    except Exception as e:
        returnJson = {"plain": f'An Error occured: {e}', "magic": f'An Error occured: {e}'}

async def wake_model(modelID):
    print("Waking Model")
    data = {"inputs": "wake up call", "options": options}
    headers = {"Authorization": f"Bearer {token}"}
    api_data = json.dumps(data)
    timeout = 5
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL + modelID, headers=headers, data=api_data, timeout=timeout) as response:
                if response.status == 200:
                    print('Model Waking')
                else:
                    print(f'Failed to wake model: {response.status} - {await response.text()}')
        
    except Exception as e:
        print(f"An error occurred: {e}")        

def formatReturn(result):
    print(result)
    img = Image.open(result)
    img.save("/tmp/response.png", overwrite=True)  # Overwrite if the image exists
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    base64_img = base64.b64encode(img_byte_arr).decode('utf-8')
    
    return base64_img

def save_image(base64image, item, model, NSFW):
    data = {
            "base64image": "data:image/png;base64," + base64image,
            "returnedPrompt": "Model:\n" + model + "\n\nPrompt:\n" + item.get('prompt'),
            "prompt": item.get('prompt'),
            "steps": item.get('steps'),
            "guidance": item.get('guidance'),
            "control": item.get('control'),
            "target": item.get('target')
        }
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    session = boto3.Session(aws_access_key_id=aws_id, aws_secret_access_key=aws_secret, region_name='us-west-2')
    s3_client = session.client('s3')
    if not NSFW:
        s3_key = f'images/{timestamp}.json'
        s3_client.put_object(Bucket='pixel-prompt', Key=s3_key, Body=json.dumps(data))
    s3_key = f'prompts/{timestamp}.json'
    data.pop("base64image", None)
    s3_client.put_object(Bucket='pixel-prompt', Key=s3_key, Body=json.dumps(data))
    

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
    print(response_data["body"][0,20])
    return response_data['body']

def inferenceAPI(model, item, attempts = 1):
    print(f'Inference model {model}')
    if attempts > 5:
        return 'An error occured when Processing', model
    prompt = item.get('prompt')
    if "dallinmackay" in model:
        prompt = "lvngvncnt, " + item.get('prompt')
    data = {"inputs":prompt, "negative_prompt": perm_negative_prompt, "options":options, "timeout": 45}
    api_data = json.dumps(data)
    try:
        response = requests.request("POST", API_URL + model, headers=headers, data=api_data)
        if response is None:
            inferenceAPI(get_random_model(activeModels['text-to-image']), item, attempts+1) 
        print(response.content[0:200])
        image_stream = BytesIO(response.content)
        image = Image.open(image_stream)
        image.save("/tmp/response.png",overwrite=True)
        with open('/tmp/response.png', 'rb') as f:
            base64_img = base64.b64encode(f.read()).decode('utf-8')
        return model, base64_img
    except Exception as e:
        print(f'Error When Processing Image: {e}')
        activeModels = InferenceClient().list_deployed_models()
        model = get_random_model(activeModels['text-to-image'])
        pattern = r'^(.{1,30})\/(.{1,50})$'
        if not re.match(pattern, model):
            return "error model not valid", model
        return inferenceAPI(model, item, attempts+1)  
    
    
def get_random_model(models):
    global last_two_models
    model = None
    priorities = [
        "stabilityai/stable-diffusion-3.5-large-turbo", 
        "black-forest-labs",
        "stabilityai/stable-diffusion-3.5-large-turbo",     
        "stabilityai/stable-diffusion-3.5-large-turbo",
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
            if priority in model_name and model_name not in last_two_models:
                model = models[i]
                break 
        if model is not None:
            break
    if model is None:
        print("Choosing randomly")
        model = random.choice(models)
    last_two_models.append(model)
    last_two_models = last_two_models[-5:]
    
    return model
   
def nsfw_check(item, attempts=1):
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
            return nsfw_check(item, attempts+1)
        
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
        return nsfw_check(item, attempts+1)
    
def inference(item):
    print("Start API Inference")
    activeModels = InferenceClient().list_deployed_models()
    base64_img = ""
    model = item.get('modelID')
    print(f'Start Model {model}')
    NSFW = False
    try:
        
        if item.get('image'):
            model = "stabilityai/stable-diffusion-xl-base-1.0"
            base64_img = gradioHatmanInstantStyle(item)
        
        elif "True Random" in item.get('modelID'):
            models = activeModels['text-to-image']
            model, base64_img= inferenceAPI(random.choice(models), item) 
        elif "Random" in item.get('modelID'):
            model = get_random_model(activeModels['text-to-image'])
            pattern = r'^(.{1,30})\/(.{1,50})$'
            if not re.match(pattern, model):
                raise ValueError("Model not Valid")
            model, base64_img= inferenceAPI(model, item) 
        elif "Voxel" in item.get('modelID') or "pixel" in item.get('modelID'):
            prompt = item.get('prompt')
            if "Voxel" in item.get('modelID'):
                prompt = "voxel style, " + item.get('prompt')
            base64_img = lambda_image(prompt, item.get('modelID'))
        else:
            model, base64_img = inferenceAPI(item.get('modelID'), item)
        if 'error' in base64_img:
            return {"output": base64_img, "model": model}
        NSFW = nsfw_check(item)
            
        save_image(base64_img, item, model, NSFW)
    except Exception as e:
        print(f"An error occurred: {e}") 
        base64_img = f"An error occurred: {e}"
    return {"output": base64_img, "model": model, "NSFW": NSFW}

prompt_base = 'Instructions:\
\
1. Take the provided seed string as inspiration.\
2. Generate a prompt that is clear, vivid, and imaginative.\
3. This is a visual image so any reference to senses other than sight should be avoided.\
4. Ensure the prompt is between 90 and 100 tokens.\
5. Return only the prompt.\
Format your response as follows:\
Stable Diffusion Prompt: [Your prompt here]\
\
Remember:\
\
- The prompt should be descriptive.\
- Avoid overly complex or abstract phrases.\
- Make sure the prompt evokes strong imagery and can guide the creation of visual content.\
- Make sure the prompt is between 90 and 100 tokens.'

prompt_assistant = "I am ready to return a prompt that is between 90 and 100 tokens.  What is your seed string?"

def lambda_handler(event, context):
    task = event.get('task')
    print(task)
    returnJson = {}
    if task == "text":
        returnJson = inferencePrompt(event.get('itemString'))
    else:
        returnJson = inference(event)
    
    return {
        'statusCode': 200,
        'body': json.dumps(returnJson)
    }

