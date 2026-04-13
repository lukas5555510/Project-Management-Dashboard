import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

from app.config.settings import get_settings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class S3Client:

    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=get_settings().aws_access_key_id,
            aws_secret_access_key=get_settings().aws_secret_access_key,
            region_name=get_settings().aws_region,
        )
        self.bucket_name = get_settings().s3_bucket_name

    def upload_file(self, file: UploadFile, s3_path: str) -> str:
        """Upload a file to S3."""
        try:
            self.s3.upload_fileobj(file.file, self.bucket_name, s3_path, ExtraArgs={"ContentType": file.content_type})
            return s3_path
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise

    def download_file(self, key: str):
        """Download a file from S3."""
        try:
            response = self.s3.get_object(
                Bucket=self.bucket_name,
                Key=key
            )

            # Streaming body (file-like object)
            return response

        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise FileNotFoundError()
            raise

    def delete_file(self, s3_path: str):
        """Delete a file from S3."""
        try:
            self.s3.delete_object(Bucket =self.bucket_name,Key= s3_path)
        except ClientError as e:
            logger.error(f"S3 deletion failed: {e}")
            raise

    def delete_file_and_zip(self, s3_path: str):
        """Delete a file and zip from S3."""
        try:
            self.delete_file(s3_path)
            zip_path = f'zipped/{s3_path.split("/", 1)[-1]}.zip'
            self.delete_file(zip_path)
        except ClientError:
            raise