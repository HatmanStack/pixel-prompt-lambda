import requests
import json
from groq import Groq
from config import magic_prompt_model, API_URL, headers, parameters, prompt_model, groq_api_key, options, token

groqClient = Groq(api_key=groq_api_key)

prompt_base = 'Instructions:\
1. Take the provided seed string as inspiration.\
2. Generate a prompt that is clear, vivid, and imaginative.\
3. This is a visual image so any reference to senses other than sight should be avoided.\
4. Ensure the prompt is between 90 and 100 tokens.\
5. Return only the prompt.\
Format your response as follows:\
[Your prompt here]\
Remember:\
- The prompt should be descriptive.\
- Avoid overly complex or abstract phrases.\
- Make sure the prompt evokes strong imagery and can guide the creation of visual content.\
- Make sure the prompt is between 90 and 100 tokens.'

prompt_assistant = "I am ready to return a prompt that is between 90 and 100 tokens.  What is your seed string?"

def getPrompt(prompt, attempts=1):
    response = {}
    try:
        chat = [
                {"role": "user", "content": prompt_base},
                {"role": "assistant", "content": prompt_assistant},
                {"role": "user", "content": prompt},
            ]
        response = groqClient.chat.completions.create(
            messages=chat, temperature=1, max_tokens=2048, top_p=1, stream=False, stop=None, model=prompt_model
        )
        print(response)
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"An error occurred: {e}")
        if attempts < 3:
            getPrompt(prompt, attempts + 1)
    return response.json()

def inferencePrompt(itemString):
    try:
        response = getPrompt(itemString)
        return {"plain": response}
    except Exception as e:
        return {"plain": f'An Error occurred: {e}'}
