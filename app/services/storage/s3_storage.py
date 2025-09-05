import boto3
from botocore.config import Config as BotoConfig
from boto3.s3.transfer import TransferConfig
from app.services.storage.base import BaseStorageService
from typing import Optional, Dict, List
import os
import uuid
import mimetypes
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)

class S3StorageService(BaseStorageService):
    def __init__(self,
                 bucket: str,
                 region: Optional[str] = None,
                 base_prefix: str = "storage_01/"):
        self.bucket = bucket
        self.region = region or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.base_prefix = base_prefix if base_prefix.endswith("/") else base_prefix + "/"

        # multipart threshold ~8MB
        self.client = boto3.client("s3", config=BotoConfig(region_name=self.region))
        self.transfer_cfg = TransferConfig(multipart_threshold=8 * 1024 * 1024,
                                           max_concurrency=8,
                                           multipart_chunksize=8 * 1024 * 1024)

    def _key_for(self, filename: str) -> str:
        ext = os.path.splitext(filename)[1] or ".bin"
        return f"{self.base_prefix}{uuid.uuid4().hex}{ext}"

    def save_upload(self, file: UploadFile) -> Dict:
        key = self._key_for(file.filename)
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"

        file.file.seek(0)
        self.client.upload_fileobj(
            Fileobj=file.file,
            Bucket=self.bucket,
            Key=key,
            ExtraArgs={
                "ContentType": content_type,
                "Metadata": {"original_filename": file.filename},
                "ServerSideEncryption": "AES256"
            },
            Config=self.transfer_cfg
        )

        logger.info(f"Uploaded to s3://{self.bucket}/{key}")
        return {
            "storage": "s3",
            "bucket": self.bucket,
            "key": key,
            "original_filename": file.filename,
            "content_type": content_type,
            "url": self.url_for(key)  # presigned
        }

    def list_files(self, prefix: str = "") -> List[str]:
        full_prefix = f"{self.base_prefix}{prefix}".lstrip("/")
        keys: List[str] = []
        paginator = self.client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket, Prefix=full_prefix):
            for obj in page.get("Contents", []):
                keys.append(obj["Key"])
        return keys

    def delete(self, key_or_path: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key_or_path)

    def url_for(self, key_or_path: str, expires_in: int = 3600) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key_or_path},
            ExpiresIn=expires_in
        )


    def delete_all_files(self, prefix: str = "") -> int:
        """
        Delete all files from S3 bucket with optional prefix filter.
        
        Args:
            prefix (str): Optional prefix to filter files for deletion
            
        Returns:
            int: Number of files deleted
        """
        try:
            full_prefix = f"{self.base_prefix}{prefix}".lstrip("/")
            deleted_count = 0
            
            logger.info(f"Starting bulk deletion of files with prefix: {full_prefix}")
            
            # List all objects with the prefix
            paginator = self.client.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=self.bucket, Prefix=full_prefix):
                if "Contents" in page:
                    # Prepare objects for deletion
                    objects_to_delete = []
                    for obj in page["Contents"]:
                        objects_to_delete.append({"Key": obj["Key"]})
                    
                    if objects_to_delete:
                        # Delete objects in batches (max 1000 per request)
                        response = self.client.delete_objects(
                            Bucket=self.bucket,
                            Delete={"Objects": objects_to_delete}
                        )
                        
                        deleted_count += len(response.get("Deleted", []))
                        
                        # Log any errors
                        if "Errors" in response:
                            for error in response["Errors"]:
                                logger.error(f"Failed to delete {error['Key']}: {error['Message']}")
            
            logger.info(f"Successfully deleted {deleted_count} files from S3")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to delete all files from S3: {str(e)}")
            raise