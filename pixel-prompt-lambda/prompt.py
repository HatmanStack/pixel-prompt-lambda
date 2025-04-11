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
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"An error occurred: {e}")
        if attempts < 3:
            getPrompt(prompt, attempts + 1)
    return response.json()

def prompt_check(prompt):
    try:
        chat = [
                {"role": "user", "content": prompt_check_base},
                {"role": "assistant", "content": prompt_check_assistant},
                {"role": "user", "content": f'Thank you. Now analyze this prompt: {prompt}'},
            ]
        response = groqClient.chat.completions.create(
            messages=chat, temperature=1, max_tokens=2048, top_p=1, stream=False, stop=None, model=prompt_model
        )
        response_content = response.choices[0].message.content.strip().lower()
        print(response_content)
        if "true" in response_content:
            return True
        elif "false" in response_content:
            return False
        else:
            raise ValueError(f"Unexpected response content: {response_content}")
    except Exception as e:
        print(f"An error occurred in prompt_check: {e}")
        return False 

def string_to_bool(value):
    if isinstance(value, str):
        return value.lower() == 'true'
    return bool(value)
    
def inferencePrompt(item):
    try:
        prompt_check_response = False
        if True:#item.get('safety'):
            prompt_check_response = string_to_bool(prompt_check(item.get('prompt')))
        if prompt_check_response:
            return {"plain": f'Sorry, that seed prompt doesn\'t work for me'}
        else:
            response = getPrompt(item.get('itemString'))
        return {"plain": response}
    except Exception as e:
        return {"plain": f'An Error occurred: {e}'}
