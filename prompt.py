import requests
import json
from config import magic_prompt_model, API_URL, headers, parameters, prompt_model, groq_api_key, options, token

def getPrompt(prompt, attempts=1):
    response = {}
    try:
        apiData = {"inputs": prompt, "parameters": parameters, "options": options, "timeout": 45}
        response = requests.post(API_URL + "gokaygokay/Flux-Prompt-Enhance", headers=headers, data=json.dumps(apiData))
        return response.json()
    except Exception as e:
        print(f"An error occurred: {e}")
        if attempts < 3:
            getPrompt(prompt, attempts + 1)
    return response.json()

def inferencePrompt(itemString):
    try:
        response = getPrompt(itemString)
        return {"plain": response[0]["generated_text"]}
    except Exception as e:
        return {"plain": f'An Error occurred: {e}'}
