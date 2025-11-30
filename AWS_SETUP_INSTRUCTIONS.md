# AWS Setup Instructions - EC2 Polling Method

## Required AWS Resources

### 1. S3 Bucket
**Name to create:** `default-images-1`

**Folder structure to create:**
- `uploads/` - Upload new images here
- `processed/` - Processed images are automatically moved here

### 2. DynamoDB Table
**Name to create:** `default-storage1`
- **Partition Key:** `id` (String)
- **Sort Key:** None (leave empty)

**Table Schema:**
- `id`: Image filename (e.g., "sandwich1.jpg") - Partition Key
- `result`: "SANDWICH" or "NOT_SANDWICH"

### 3. EC2 Instance Setup
**No Lambda needed!** Just an EC2 instance running your Python script.

**Steps:**
1. Launch an EC2 instance (t2.micro is fine for testing)
2. SSH into your instance
3. Install Python and dependencies:
   ```bash
   sudo yum update -y  # or apt-get for Ubuntu
   sudo yum install python3 python3-pip -y
   pip3 install boto3 inference-sdk
   ```
4. Upload `AWSConnectors.py` to the instance
5. Configure AWS credentials:
   ```bash
   aws configure
   # Enter your AWS Access Key ID, Secret Key, and region
   ```
6. Run the monitoring script:
   ```bash
   python3 AWSConnectors.py
   ```

**To run in background (keeps running after you disconnect):**
```bash
nohup python3 AWSConnectors.py > output.log 2>&1 &
```

**IAM Role/Policy for EC2:**
Attach this policy to your EC2 instance's IAM role:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::default-images-1",
        "arn:aws:s3:::default-images-1/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/default-storage1"
    }
  ]
}
```

## How It Works
1. Upload an image to the S3 bucket `default-images-1` in the `uploads/` folder
2. EC2 instance checks the `uploads/` folder every 30 seconds
3. When a new image is found:
   - Downloads it
   - Runs sandwich classification
   - Stores result in DynamoDB
   - Moves image to `processed/` folder
4. Process repeats continuously

**Advantages of this approach:**
- No Lambda complexity
- Easy to debug (just check the script output)
- No cold starts
- Can run on your local machine for testing
- Only uses EC2, S3, and DynamoDB

**Configuration:**
Edit these variables in the code if needed:
- `CHECK_INTERVAL`: How often to check for new images (default: 30 seconds)
- `UNPROCESSED_PREFIX`: Where to look for new images (default: "uploads/")
- `PROCESSED_PREFIX`: Where to move processed images (default: "processed/")
