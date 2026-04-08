# lambda/file_processor/handler.py

import json
import boto3
import zipfile
from io import BytesIO
import os

s3 = boto3.client("s3")


def lambda_handler(event, context):
    results = []

    for record in event["Records"]:
        bucket_name = record["s3"]["bucket"]["name"]
        object_key = record["s3"]["object"]["key"]

        # Skip already zipped files to avoid infinite loop
        if object_key.endswith(".zip"):
            continue

        # Only process PDF and DOCX
        if not (object_key.endswith(".pdf") or object_key.endswith(".docx")):
            continue

        try:
            # --------------------------
            # Download file from S3
            # --------------------------
            file_obj = s3.get_object(Bucket=bucket_name, Key=object_key)
            file_content = file_obj["Body"].read()

            # --------------------------
            # Create ZIP in memory
            # --------------------------
            zip_buffer = BytesIO()

            filename = os.path.basename(object_key)
            zip_filename = f"{filename}.zip"

            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr(filename, file_content)

            zip_buffer.seek(0)

            # --------------------------
            # Upload ZIP back to S3
            # --------------------------
            zipped_key = f"zipped/{zip_filename}"

            s3.put_object(
                Bucket=bucket_name,
                Key=zipped_key,
                Body=zip_buffer.getvalue(),
                ContentType="application/zip"
            )

            results.append({
                "original": object_key,
                "zipped": zipped_key
            })

        except Exception as e:
            print(f"Error processing {object_key}: {str(e)}")
            raise e

    return {
        "statusCode": 200,
        "body": json.dumps(results)
    }