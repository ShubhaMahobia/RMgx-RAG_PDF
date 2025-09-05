import os
import uuid
import logging
import mimetypes
from typing import Dict, List, Optional
from fastapi import UploadFile
import os

logger = logging.getLogger(__name__)

# ---------- Interface ----------
class BaseStorageService:
    def save_upload(self, file: UploadFile) -> Dict:
        raise NotImplementedError

    def list_files(self, prefix: str) -> List[str]:
        raise NotImplementedError

    def delete(self, key_or_path: str) -> None:
        raise NotImplementedError

    def url_for(self, key_or_path: str, expires_in: int = 3600) -> Optional[str]:
        return None  # not applicable for local

    def upload_directory(self, local_dir: str, prefix: str) -> None:
        raise NotImplementedError

    def download_directory(self, prefix: str, local_dir: str) -> None:
        raise NotImplementedError





