# AWS Setup Instructions

## Required AWS Resources

### 1. S3 Bucket
**Name to create:** `images-1`
- This bucket will store uploaded images
- Configure S3 trigger to invoke the Lambda function on object creation

### 2. DynamoDB Table
**Name to create:** `storage1`
- **Primary Key:** `image_key` (String)
- **Sort Key (optional):** `timestamp` (String)

**Table Schema:**
- `image_key`: S3 object key (e.g., "images/sandwich1.jpg")
- `timestamp`: ISO format timestamp of classification
- `is_sandwich`: Boolean (true/false)
- `classification`: String ("SANDWICH" or "NOT_SANDWICH")
- `confidence`: String (confidence score if sandwich detected)
- `predictions`: JSON string with full prediction details
- `bucket`: Source S3 bucket name

### 3. Lambda Function Setup
1. Create a new Lambda function (Python 3.9+)
2. Upload the code from `AWSConnectors.py`
3. Set environment variable: `ROBOFLOW_API_KEY` with your API key
4. Increase timeout to at least 30 seconds
5. Increase memory to at least 512 MB

**Required Lambda Layers:**
- boto3 (usually included)
- inference-sdk (need to create custom layer)

**IAM Role Permissions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::images-1/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/storage1"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

### 4. S3 Event Trigger Configuration
- **Event type:** All object create events
- **Prefix (optional):** Leave empty or specify folder
- **Suffix (optional):** `.jpg`, `.jpeg`, `.png`

## How It Works
1. Upload an image to the S3 bucket `images-1`
2. S3 triggers the Lambda function automatically
3. Lambda downloads the image, runs classification
4. Results are stored in DynamoDB table `storage1`
5. You can query the DynamoDB table to see all classification results
