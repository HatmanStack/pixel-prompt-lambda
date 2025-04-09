import random
import re
import requests
import json
import base64
import time
from PIL import Image
from image_processing import save_image
from utils import gemini_2, imagen_3, recraft_3

def inference(item):
    #client = InferenceClient(token=token)  # token optional for some operations

    # Get the list of deployed models
    #deployed_models = client.list_deployed_models()
    #print(deployed_models)
    base64_img = "An error occurred: You're a Jerk"
    model = item.get('modelID')
    check_img = False
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
        if item.get('saftey'):
            check_img = True
        else:
            check_img = False
        save_image(base64_img, item, model, check_img)
    except Exception as e:
        print(f"An error occurred: {e}")
        base64_img = f"An error occurred: {e}"
    return {"output": base64_img, "model": model, "NSFW": check_img}