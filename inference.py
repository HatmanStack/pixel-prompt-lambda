import random
import re
import requests
import json
import base64
import time
from PIL import Image
from io import BytesIO
from prompt import prompt_check
from image_processing import save_image
from utils import dalle3, nova_canvas, stable_diffusion, gemini_2, imagen_3, recraft_3, firework

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
        model_id = item.get('modelID') # Get model ID once

        # Define handlers: mapping substrings to (display_name, function, needs_model_id)
        # needs_model_id indicates if the function requires the model_id as an argument
        model_handlers = {
            "Black Forest Dev": ('Black Forest Dev', firework, True),
            "Black Forest Pro": ('Black Forest Pro', firework, True),
            "Stable Diffusion 3.5 Turbo": ('Stable Diffusion 3.5 Turbo', firework, True),
            "Stable Diffusion 3.5 Large": ('Stable Diffusion 3.5 Large', stable_diffusion, False),
            "OpenAI Dalle3": ('OpenAI Dalle3', dalle3, False),
            "AWS Nova Canvas": ('AWS Nova Canvas', nova_canvas, False),
            "Gemini": ('Gemini 2.0', gemini_2, False),
            "Imagen": ('Imagen 3.0', imagen_3, False),
            "Recraft": ('Recraft v3', recraft_3, False),
        }

        handler_found = False
        for key_substring, (display_name, handler_func, needs_id) in model_handlers.items():
            if key_substring in model_id:
                model = display_name
                if needs_id:
                    base64_img = handler_func(item, model_id)
                else:
                    base64_img = handler_func(item)
                handler_found = True
                break # Exit loop once a handler is found

        if not handler_found:
            print(f"No specific inference logic found for modelID: {model_id}. Using default error.")
            # Keep original model_id as model name
            base64_img = "Error in Inference: Model not recognized"

        save_image(base64_img, item, model)
    except Exception as e:
        print(f"An Error occurred: {e}")
        base64_img = f"An Error occurred: {e}"
    return {"output": base64_img, "model": model, "NSFW": False}