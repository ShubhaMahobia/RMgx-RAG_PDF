from app.services.storage.s3_storage import S3StorageService
from app.services.storage.base import BaseStorageService
from app.config import Config
import os
from fastapi import HTTPException
import logging

def get_storage() -> BaseStorageService:
    # Use credentials from config file
    bucket = Config.S3_BUCKET_NAME
    if not bucket:
        raise RuntimeError("S3_BUCKET_NAME not configured in config file")

    region = Config.AWS_DEFAULT_REGION
    prefix = Config.S3_UPLOAD_PREFIX

    return S3StorageService(bucket=bucket, region=region, base_prefix=prefix)



