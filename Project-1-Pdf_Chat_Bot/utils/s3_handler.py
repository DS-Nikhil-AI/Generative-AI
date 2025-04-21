import boto3
import os

# Set your AWS credentials and bucket
AWS_ACCESS_KEY = "your-access-key"
AWS_SECRET_KEY = "your-secret-key"
S3_BUCKET = "your-bucket-name"
S3_FOLDER = "vector_store"  # optional folder path inside the bucket

# Files to upload
files_to_upload = ["documents.pkl", "metadata.pkl", "embeddings.pt"]
local_dir = "vector_store_data"  # path where the files are stored locally

# Create S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

# Upload each file
for filename in files_to_upload:
    local_path = os.path.join(local_dir, filename)
    s3_key = f"{S3_FOLDER}/{filename}"  # Key = path inside the bucket

    if os.path.exists(local_path):
        s3.upload_file(local_path, S3_BUCKET, s3_key)
        print(f"Uploaded {filename} to s3://{S3_BUCKET}/{s3_key}")
    else:
        print(f"File not found: {local_path}")
