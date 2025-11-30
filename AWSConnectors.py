import boto3
import json
from datetime import datetime
from inference_sdk import InferenceHTTPClient
import os

# Configuration - Update these names to match your AWS resources
S3_BUCKET_NAME = "images-1"
DYNAMODB_TABLE_NAME = "storage1"
ROBOFLOW_API_KEY = "YOUR_ROBOFLOW_API_KEY"  # Replace with your API key

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

# Initialize Roboflow client
CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=ROBOFLOW_API_KEY
)

def lambda_handler(event, context):
    """
    AWS Lambda function triggered by S3 upload events.
    Classifies images and stores results in DynamoDB.
    """
    
    # Get S3 bucket and object key from the event
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        print(f"Processing image: {key} from bucket: {bucket}")
        
        # Download image from S3 to /tmp (Lambda's temporary storage)
        local_path = f'/tmp/{os.path.basename(key)}'
        s3_client.download_file(bucket, key, local_path)
        
        # Run inference on the image
        result = CLIENT.infer(local_path, model_id="sandwich-tqrld/1")
        
        # Determine if it's a sandwich
        is_sandwich = result['predictions'] and len(result['predictions']) > 0
        
        # Prepare data for DynamoDB
        item = {
            'image_key': key,
            'timestamp': datetime.utcnow().isoformat(),
            'is_sandwich': is_sandwich,
            'classification': 'SANDWICH' if is_sandwich else 'NOT_SANDWICH',
            'predictions': json.dumps(result['predictions']),
            'bucket': bucket
        }
        
        # Add confidence score if sandwich detected
        if is_sandwich:
            item['confidence'] = str(result['predictions'][0]['confidence'])
        
        # Store result in DynamoDB
        table.put_item(Item=item)
        
        print(f"Result: {item['classification']}")
        print(f"Stored in DynamoDB: {item}")
        
        # Clean up temporary file
        os.remove(local_path)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Processing complete')
    }


# For local testing
def test_local(image_path):
    """
    Test function to run locally without AWS Lambda.
    """
    result = CLIENT.infer(image_path, model_id="sandwich-tqrld/1")
    
    is_sandwich = result['predictions'] and len(result['predictions']) > 0
    
    print(f"Image: {image_path}")
    print(f"Result: {'THIS IS A SANDWICH' if is_sandwich else 'THIS ISN\\'T A SANDWICH'}")
    
    if is_sandwich:
        print(f"Confidence: {result['predictions'][0]['confidence']:.2%}")
    
    return result


if __name__ == "__main__":
    # Local testing
    test_local('DataImages/hamSandwich.jpg')
