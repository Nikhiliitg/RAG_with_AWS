# import boto3
# from botocore.exceptions import ClientError
# from config import Config

# class S3Storage:
#     def __init__(self):
#         """Initialize S3 client with best security practices."""
#         try:
#             self.s3 = boto3.client('s3')  # Uses AWS default credentials
#             self.bucket = Config.AWS_BUCKET_NAME
#         except Exception as e:
#             raise RuntimeError(f"Failed to initialize S3 client: {e}")

#     def upload_file(self, file_obj, filename):
#         """Upload file to S3 and handle errors properly."""
#         try:
#             self.s3.upload_fileobj(file_obj, self.bucket, filename)
#             return True
#         except ClientError as e:
#             print(f"Error uploading file: {e}")
#             raise RuntimeError(f"Failed to upload {filename} to S3.")

#     def get_file(self, filename):
#         """Retrieve file from S3 and return its content."""
#         try:
#             response = self.s3.get_object(Bucket=self.bucket, Key=filename)
#             return response['Body'].read()
#         except ClientError as e:
#             print(f"Error retrieving file: {e}")
#             raise FileNotFoundError(f"{filename} not found in S3.")
try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    boto3 = None
    ClientError = Exception  # Fallback for exception handling

from config import Config

class S3Storage:
    def __init__(self):
        """Initialize S3 client, or fallback to mock if AWS isn't available."""
        self.bucket = Config.AWS_BUCKET_NAME

        if boto3 is None or Config.MOCK_S3:
            print("⚠️  Using Mock S3 Storage (boto3 not available or MOCK_S3=True)")
            self.s3 = None
            self.mock_mode = True
            self.local_store = {}
        else:
            try:
                self.s3 = boto3.client('s3')
                self.mock_mode = False
            except Exception as e:
                print(f"Error initializing S3: {e}")
                self.s3 = None
                self.mock_mode = True
                self.local_store = {}

    def upload_file(self, file_obj, filename):
        """Upload file to S3 or mock store."""
        if self.mock_mode:
            self.local_store[filename] = file_obj.read()
            print(f"[Mock Upload] Stored {filename} in memory.")
            return True
        try:
            self.s3.upload_fileobj(file_obj, self.bucket, filename)
            return True
        except ClientError as e:
            print(f"Error uploading file: {e}")
            raise RuntimeError(f"Failed to upload {filename} to S3.")

    def get_file(self, filename):
        """Retrieve file from S3 or mock store."""
        if self.mock_mode:
            if filename in self.local_store:
                print(f"[Mock Get] Retrieving {filename} from memory.")
                return self.local_store[filename]
            else:
                raise FileNotFoundError(f"{filename} not found in mock storage.")
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=filename)
            return response['Body'].read()
        except ClientError as e:
            print(f"Error retrieving file: {e}")
            raise FileNotFoundError(f"{filename} not found in S3.")
