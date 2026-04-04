import boto3
from botocore.exceptions import ClientError
from app.config.settings import settings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class S3Client:
    """Wrapper around boto3 S3 with pre-signed URLs and Lambda support."""

    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
        self.bucket_name = settings.s3_bucket_name

    def upload_file(self, file_path: str, key: str) -> str:
        """Upload a file to S3."""
        try:
            self.s3.upload_file(file_path, self.bucket_name, key)
            return key
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise

    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a pre-signed URL for downloading a file."""
        try:
            url = self.s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            logger.error(f"Presigned URL generation failed: {e}")
            raise

    def delete_file(self, key: str):
        """Delete a file from S3."""
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=key)
        except ClientError as e:
            logger.error(f"S3 deletion failed: {e}")
            raise

    def trigger_lambda(self, lambda_name: str, payload: dict):
        """Invoke AWS Lambda for file processing."""
        lambda_client = boto3.client(
            "lambda",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
        response = lambda_client.invoke(
            FunctionName=lambda_name,
            InvocationType="Event",
            Payload=bytes(str(payload), encoding="utf8"),
        )
        return response
