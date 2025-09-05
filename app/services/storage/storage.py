from app.services.storage.s3_storage import S3StorageService
from app.services.storage.base import BaseStorageService
import os
from fastapi import HTTPException
import logging

def get_storage() -> BaseStorageService:
    bucket = os.getenv("S3_BUCKET_NAME")
    if not bucket:
        raise RuntimeError("S3_BUCKET_NAME not configured")

    region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    prefix = os.getenv("S3_UPLOAD_PREFIX", "storage_01/")

    return S3StorageService(bucket=bucket, region=region, base_prefix=prefix)



