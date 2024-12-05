from groq import Groq
import requests
import json
from config import magic_prompt_model, API_URL, headers, parameters, prompt_model, groq_api_key, options

groqClient = Groq(api_key=groq_api_key)

def getPrompt(prompt, modelID, attempts=1):
    response = {}
    try:
        if modelID != magic_prompt_model:
            chat = [
                {"role": "user", "content": prompt_base},
                {"role": "assistant", "content": prompt_assistant},
                {"role": "user", "content": prompt},
            ]
            response = groqClient.chat.completions.create(
                messages=chat, temperature=1, max_tokens=2048, top_p=1, stream=False, stop=None, model=prompt_model
            )
        else:
            apiData = {"inputs": prompt, "parameters": parameters, "options": options, "timeout": 45}
            response = requests.post(API_URL + modelID, headers=headers, data=json.dumps(apiData))
            return response.json()
    except Exception as e:
        print(f"An error occurred: {e}")
        if attempts < 3:
            getPrompt(prompt, modelID, attempts + 1)
    return response

def inferencePrompt(itemString):
    try:
        plain_response_data = getPrompt(itemString, prompt_model)
        magic_response_data = getPrompt(itemString, magic_prompt_model)
        return {"plain": plain_response_data.choices[0].message.content, "magic": itemString + magic_response_data[0]["generated_text"]}
    except Exception as e:
        return {"plain": f'An Error occurred: {e}', "magic": f'An Error occurred: {e}'}

prompt_base = 'Instructions:\
1. Take the provided seed string as inspiration.\
2. Generate a prompt that is clear, vivid, and imaginative.\
3. This is a visual image so any reference to senses other than sight should be avoided.\
4. Ensure the prompt is between 90 and 100 tokens.\
5. Return only the prompt.\
Format your response as follows:\
Stable Diffusion Prompt: [Your prompt here]\
Remember:\
- The prompt should be descriptive.\
- Avoid overly complex or abstract phrases.\
- Make sure the prompt evokes strong imagery and can guide the creation of visual content.\
- Make sure the prompt is between 90 and 100 tokens.'

prompt_assistant = "I am ready to return a prompt that is between 90 and 100 tokens.  What is your seed string?"