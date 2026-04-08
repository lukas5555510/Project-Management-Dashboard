import boto3
from botocore.exceptions import ClientError
from app.config.settings import settings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class S3Client:

    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
        self.bucket_name = settings.s3_bucket_name

    def upload_file(self, file_path: str, s3_path: str) -> str:
        """Upload a file to S3."""
        try:
            self.s3.upload_file(file_path, self.bucket_name, s3_path)
            return s3_path
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise

    def download_file(self, file_path: str, s3_path: str) -> str:
        """Download a file from S3."""
        try:
            self.s3.download_file(file_path, self.bucket_name, s3_path)
            return s3_path
        except ClientError as e:
            logger.error(f"S3 download failed: {e}")
            raise

    def delete_file(self, s3_path: str):
        """Delete a file from S3."""
        try:
            self.s3.delete_object(self.bucket_name, s3_path)
        except ClientError as e:
            logger.error(f"S3 deletion failed: {e}")
            raise