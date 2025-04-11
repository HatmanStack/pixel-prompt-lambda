import random
import re
import requests
import json
import base64
import time
from PIL import Image
from image_processing import save_image
from groq import Groq
from config import  prompt_model, groq_api_key
from utils import gemini_2, imagen_3, recraft_3

def string_to_bool(value):
    if isinstance(value, str):
        return value.lower() == 'true'
    return bool(value)

def inference(item):
    #client = InferenceClient(token=token)  # token optional for some operations

    # Get the list of deployed models
    #deployed_models = client.list_deployed_models()
    #print(deployed_models)
    base64_img = "An error occurred: You're a Jerk"
    model = item.get('modelID')
    if string_to_bool(prompt_check(item.get('prompt'))):  
        return {"output": base64_img , "model": model, "NSFW": True}
    try:
        if "Gemini" in item.get('modelID'):
            model = 'Gemini 2.0'
            base64_img = gemini_2(item)
            
        elif "Imagen" in item.get('modelID'):
            model = 'Imagen 3.0'
            base64_img = imagen_3(item)
        elif "Recraft" in item.get('modelID'):
            model = 'Recraft v3'
            base64_img = recraft_3(item)
        else:
            model, base64_img = item.get('modelID'), "Error in Inference"
        
        save_image(base64_img, item, model)
    except Exception as e:
        print(f"An error occurred: {e}")
        base64_img = f"An error occurred: {e}"
    return {"output": base64_img, "model": model, "NSFW": False}


    

groqClient = Groq(api_key=groq_api_key)

prompt_check_base = """
You are an expert content analyzer specializing in evaluating text prompts intended for diffusion text-to-image models. Your sole task is to determine whether a given prompt contains vulgar, explicit, inappropriate, or NSFW content.

For each prompt submitted to you, carefully analyze the text and return ONLY a single word response:
- Return "True" if the prompt contains vulgar, explicit, sexual, offensive, or inappropriate content
- Return "False" if the prompt contains only appropriate, safe-for-work content

When analyzing prompts, consider:
- Explicit sexual references or terminology
- Graphic violence or gore descriptions
- Hate speech or discriminatory language
- Drug use or illegal activity descriptions
- Obscene language or profanity
- Implicit vulgar content through euphemisms or innuendo
- Content that would be inappropriate in professional settings

Examples:
Prompt: "A beautiful mountain landscape at sunset with purple sky"
Response: False

Prompt: "Naked woman in provocative pose"
Response: True

Prompt: "Colorful birds flying over a tropical forest"
Response: False

Prompt: "Man violently attacking another person with blood"
Response: True

Do not explain your reasoning or provide any additional text in your response. Return ONLY "True" or "False" based on your analysis.
"""

prompt_check_assistant = """
I'll analyze the text prompt for any vulgar, explicit, inappropriate, or NSFW content that would be unsuitable for generating images.

Based on my analysis, I'll return either True (contains vulgar content) or False (does not contain vulgar content).
"""


def prompt_check(prompt):
    print(f'start prompt check: {prompt}')
    try:
        chat = [
                {"role": "user", "content": prompt_check_base},
                {"role": "assistant", "content": prompt_check_assistant},
                {"role": "user", "content": f'Thank you. Now analyze this prompt: {prompt}'},
            ]
        response = groqClient.chat.completions.create(
            messages=chat, temperature=1, max_tokens=2048, top_p=1, stream=False, stop=None, model=prompt_model
        )
        print(response.choices[0].message.content)
        return response.choices[0].message.content
    except Exception as e:
        return {"plain": f'An Error occurred: {e}'}


