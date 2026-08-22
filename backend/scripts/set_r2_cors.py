"""
One-time infra script: apply a CORS policy to the R2 uploads bucket.

Browser-direct uploads (presigned PUT from the web app) require a bucket-level
CORS policy — the backend's CORS middleware does not cover requests to
*.r2.cloudflarestorage.com.

Usage: python -m scripts.set_r2_cors
"""

import os

import boto3
from botocore.config import Config as BotoConfig

from src.utils.config import config

# Falls back to the app's object-level R2 credentials. PutBucketCors requires
# an "Admin Read & Write" R2 token — set these env vars to override:
#   R2_ADMIN_ACCESS_KEY_ID / R2_ADMIN_SECRET_ACCESS_KEY
ACCESS_KEY_ID = os.environ.get("R2_ADMIN_ACCESS_KEY_ID") or config.access_key_id
SECRET_ACCESS_KEY = os.environ.get("R2_ADMIN_SECRET_ACCESS_KEY") or config.secret_access_key

ALLOWED_ORIGINS = [
    "https://flume.ojogulabs.xyz",
    "http://localhost:5173",
]

CORS_RULES = [
    {
        "AllowedMethods": ["PUT"],
        "AllowedOrigins": ALLOWED_ORIGINS,
        "AllowedHeaders": ["content-type"],
        "ExposeHeaders": ["etag"],
        "MaxAgeSeconds": 3600,
    }
]


def main():
    client = boto3.client(
        "s3",
        endpoint_url=config.s3_url,
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_ACCESS_KEY,
        config=BotoConfig(
            connect_timeout=10,
            read_timeout=30,
            retries={"max_attempts": 3, "mode": "adaptive"},
            signature_version="s3v4",
        ),
    )

    print(f"Applying CORS policy to bucket: {config.r2_bucket_name}")
    client.put_bucket_cors(
        Bucket=config.r2_bucket_name,
        CORSConfiguration={"CORSRules": CORS_RULES},
    )

    current = client.get_bucket_cors(Bucket=config.r2_bucket_name)
    print("Applied CORS rules:")
    for rule in current["CORSRules"]:
        print(f"  Origins:  {rule.get('AllowedOrigins')}")
        print(f"  Methods:  {rule.get('AllowedMethods')}")
        print(f"  Headers:  {rule.get('AllowedHeaders')}")
        print(f"  Expose:   {rule.get('ExposeHeaders')}")
        print(f"  MaxAge:   {rule.get('MaxAgeSeconds')}s")
        print()


if __name__ == "__main__":
    main()
