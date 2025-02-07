import boto3
from botocore.exceptions import ClientError
from config import Config

class S3Storage:
    def __init__(self):
        """Initialize S3 client with best security practices."""
        try:
            self.s3 = boto3.client('s3')  # Uses AWS default credentials
            self.bucket = Config.AWS_BUCKET_NAME
        except Exception as e:
            raise RuntimeError(f"Failed to initialize S3 client: {e}")

    def upload_file(self, file_obj, filename):
        """Upload file to S3 and handle errors properly."""
        try:
            self.s3.upload_fileobj(file_obj, self.bucket, filename)
            return True
        except ClientError as e:
            print(f"Error uploading file: {e}")
            raise RuntimeError(f"Failed to upload {filename} to S3.")

    def get_file(self, filename):
        """Retrieve file from S3 and return its content."""
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=filename)
            return response['Body'].read()
        except ClientError as e:
            print(f"Error retrieving file: {e}")
            raise FileNotFoundError(f"{filename} not found in S3.")