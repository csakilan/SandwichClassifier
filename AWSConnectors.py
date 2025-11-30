import boto3
import json
from datetime import datetime
from inference_sdk import InferenceHTTPClient
import os
import time

# Configuration - Update these names to match your AWS resources
S3_BUCKET_NAME = "default-images-1asdfx"
DYNAMODB_TABLE_NAME = "default-storage1asdfx"
PROCESSED_PREFIX = "processed/"  # Folder to move processed images to
UNPROCESSED_PREFIX = "uploads/"  # Folder where new images are uploaded
CHECK_INTERVAL = 30  # Seconds between checks for new images

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

# Initialize Roboflow client
CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
)


def get_unprocessed_images():
    """
    Lists all images in the unprocessed folder of the S3 bucket.
    Returns a list of image keys.
    """
    try:
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET_NAME,
            Prefix=UNPROCESSED_PREFIX
        )
        
        if 'Contents' not in response:
            return []
        
        # Filter for image files only
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        images = [
            obj['Key'] for obj in response['Contents']
            if any(obj['Key'].lower().endswith(ext) for ext in image_extensions)
            and obj['Key'] != UNPROCESSED_PREFIX  # Skip the folder itself
        ]

        return images
    except Exception as e:
        print(f"Error listing S3 objects: {e}")
        return []


def process_image(image_key):
    """
    Downloads image from S3, runs classification, stores result in DynamoDB,
    and moves the image to the processed folder.
    """
    try:
        print(f"\n{'='*60}")
        print(f"Processing image: {image_key}")
        
        # Download image from S3
        local_path = f'/tmp/{os.path.basename(image_key)}'
        s3_client.download_file(S3_BUCKET_NAME, image_key, local_path)
        print(f"Downloaded to: {local_path}")
        
        # Run inference on the image
        result = CLIENT.infer(local_path, model_id="sandwich-tqrld/1")
        
        # Determine if it's a sandwich
        is_sandwich = result['predictions'] and len(result['predictions']) > 0
        
        # Prepare data for DynamoDB
        classification = 'SANDWICH' if is_sandwich else 'NOT_SANDWICH'
        item = {
            'id': os.path.basename(image_key),
            'result': classification
        }
        
        if is_sandwich:
            print(f"✓ SANDWICH DETECTED - Confidence: {result['predictions'][0]['confidence']:.2%}")
        else:
            print(f"✗ NOT A SANDWICH")
        
        # Store result in DynamoDB
        table.put_item(Item=item)
        print(f"Stored in DynamoDB: {classification}")
        
        # Move image to processed folder
        new_key = image_key.replace(UNPROCESSED_PREFIX, PROCESSED_PREFIX)
        s3_client.copy_object(
            Bucket=S3_BUCKET_NAME,
            CopySource={'Bucket': S3_BUCKET_NAME, 'Key': image_key},
            Key=new_key
        )
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=image_key)
        print(f"Moved to: {new_key}")
        
        # Clean up temporary file
        os.remove(local_path)
        
        print(f"{'='*60}\n")
        return True
        
    except Exception as e:
        print(f"Error processing image {image_key}: {e}")
        return False


def monitor_s3_bucket():
    """
    Continuously monitors the S3 bucket for new images and processes them.
    Run this on your EC2 instance.
    """
    print(f"Starting S3 monitor for bucket: {S3_BUCKET_NAME}")
    print(f"Watching folder: {UNPROCESSED_PREFIX}")
    print(f"Check interval: {CHECK_INTERVAL} seconds")
    print(f"Press Ctrl+C to stop\n")
    
    try:
        while True:
            # Get list of unprocessed images
            images = get_unprocessed_images()
            
            if images:
                print(f"Found {len(images)} image(s) to process")
                for image_key in images:
                    process_image(image_key)
            else:
                print(f"No new images. Checking again in {CHECK_INTERVAL} seconds...")
            
            # Wait before next check
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
    except Exception as e:
        print(f"\n\nError in monitoring loop: {e}")


def test_single_image(image_key):
    """
    Test function to process a single image from S3.
    """
    print(f"Testing single image: {image_key}")
    success = process_image(image_key)
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed!")


if __name__ == "__main__":
    # Start monitoring the S3 bucket
    # This will run continuously until you stop it
    monitor_s3_bucket()
    
    # For testing a single image, comment out the line above and uncomment below:
    # test_single_image('uploads/test-sandwich.jpg')
