from prompt import inferencePrompt
from inference import inference
from config import aws_id, aws_secret, global_limit, ip_limit
import json
import boto3
import os
from datetime import datetime, timedelta

def lambda_handler(event, context):
    task = event.get('task')
    print(task)
    returnJson = {}

    session = boto3.Session(aws_access_key_id=aws_id, aws_secret_access_key=aws_secret, region_name='us-west-2')
    s3_client = session.client('s3')
    
    if rate_limit_exceeded(s3_client, event.get('ip')):
        print("Rate limit exceeded")
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

def rate_limit_exceeded(s3_client, ip):
    bucket_name = 'pixel-prompt'
    key = 'rate-limit/ratelimit.json'
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        rate_limit_data = json.loads(response['Body'].read().decode('utf-8'))
    except s3_client.exceptions.NoSuchKey:
        rate_limit_data = {
            "global_requests": [],
            "ip_requests": {}
        }
    
    current_time = datetime.now().isoformat()
    one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
    one_day_ago = (datetime.now() - timedelta(days=1)).isoformat()
    
    # Clean up and update global requests (all requests regardless of IP)
    rate_limit_data["global_requests"] = [ts for ts in rate_limit_data["global_requests"] if ts > one_hour_ago]
    rate_limit_data["global_requests"].append(current_time)
    
    # Initialize IP entry if it doesn't exist
    if ip not in rate_limit_data["ip_requests"]:
        rate_limit_data["ip_requests"][ip] = []
    
    # Clean up and update IP-specific requests
    rate_limit_data["ip_requests"][ip] = [ts for ts in rate_limit_data["ip_requests"][ip] if ts > one_day_ago]
    rate_limit_data["ip_requests"][ip].append(current_time)
    
    # Save updated rate limit data
    s3_client.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=json.dumps(rate_limit_data)
    )
    
    if len(rate_limit_data["global_requests"]) > global_limit:
        return True
    
    if len(rate_limit_data["ip_requests"][ip]) > ip_limit:
        return True
    
    return False