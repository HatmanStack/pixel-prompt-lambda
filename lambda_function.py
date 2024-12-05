from prompt import inferencePrompt
from inference import inference
import json

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