"""File storage abstraction (local + S3/MinIO)."""

import os
import uuid

import boto3
from botocore.exceptions import ClientError

from app.config import settings


class LocalStorage:
    def __init__(self, base_dir: str | None = None):
        self.base_dir = base_dir or settings.MEDIA_DIR
        os.makedirs(self.base_dir, exist_ok=True)

    def save(self, data: bytes, filename: str, subdir: str = "") -> str:
        dir_path = os.path.join(self.base_dir, subdir) if subdir else self.base_dir
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, filename)
        with open(file_path, "wb") as f:
            f.write(data)
        return file_path

    def delete(self, file_path: str) -> bool:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    def exists(self, file_path: str) -> bool:
        return os.path.exists(file_path)


class S3Storage:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        )
        self.bucket = settings.S3_BUCKET

    def save(self, data: bytes, key: str) -> str:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data)
        return f"{settings.S3_ENDPOINT}/{self.bucket}/{key}"

    def delete(self, key: str) -> bool:
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError:
            return False

    def get_url(self, key: str, expires_in: int = 3600) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )


def get_storage() -> LocalStorage:
    """Get the default storage backend. Switch to S3Storage for production."""
    return LocalStorage()
