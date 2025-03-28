from prompt import inferencePrompt
from inference import inference
from config import aws_id, aws_secret
import json
import boto3
from datetime import datetime, timedelta

def lambda_handler(event, context):
    task = event.get('task')
    print(task)
    returnJson = {}

    session = boto3.Session(aws_access_key_id=aws_id, aws_secret_access_key=aws_secret, region_name='us-west-2')
    s3_client = session.client('s3')
    
    if rate_limit_exceeded(s3_client):
        returnJson = {'output': 'Rate limit exceeded'}
    else:
        if task == "text":
            returnJson = inferencePrompt(event)
        elif task == "image":
            
            print(f'EVENT STRING: {event}')
            returnJson = inference(event)
    return {
        'statusCode': 200,
        'body': json.dumps(returnJson)
    }

def rate_limit_exceeded(s3_client):
    bucket_name = 'pixel-prompt'
    key = 'rate-limit/ratelimit.json'
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        rate_limit_data = json.loads(response['Body'].read().decode('utf-8'))
    except s3_client.exceptions.NoSuchKey:
        rate_limit_data = {"timestamps": []}
    
    one_hour_ago = datetime.now() - timedelta(hours=1)
    recent_timestamps = [datetime.fromisoformat(ts) for ts in rate_limit_data["timestamps"] if datetime.fromisoformat(ts) > one_hour_ago]
    
    rate_limit_data["timestamps"] = [ts.isoformat() for ts in recent_timestamps]
    
    if len(recent_timestamps) >= 8:  
        return True
    
    return False