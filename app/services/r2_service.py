from datetime import datetime, timezone
datetime.now(timezone.utc)
import uuid
import boto3

from app.config.settings import (
    R2_BUCKET,
    R2_ACCESS_KEY_ID,
    R2_SECRET_ACCESS_KEY,
    R2_ENDPOINT_URL,
    R2_PUBLIC_BASE_URL,
)


class R2Service:
    @staticmethod
    def _client():
        return boto3.client(
            "s3",
            endpoint_url=R2_ENDPOINT_URL,
            aws_access_key_id=R2_ACCESS_KEY_ID,
            aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        )

    @staticmethod
    def _generate_key(user_id: int, extension: str) -> str:
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
        random_id = uuid.uuid4().hex
        return f"users/{user_id}/{timestamp}_{random_id}.{extension}"

    @staticmethod
    def upload(user_id: int, data: bytes, extension: str, content_type: str) -> str:
        key = R2Service._generate_key(user_id, extension)
        client = R2Service._client()

        client.put_object(
            Bucket=R2_BUCKET,
            Key=key,
            Body=data,
            ContentType=content_type,
        )

        return f"{R2_PUBLIC_BASE_URL}/{key}"

    # Helper for SVG specifically
    @staticmethod
    def upload_svg(user_id: int, svg_text: str) -> str:
        return R2Service.upload(
            user_id=user_id,
            data=svg_text.encode("utf-8"),
            extension="svg",
            content_type="image/svg+xml",
        )

    # Helper for PNG/JPG
    @staticmethod
    def upload_image(user_id: int, image_bytes: bytes, extension: str) -> str:
        content_type = f"image/{extension}"
        return R2Service.upload(
            user_id=user_id,
            data=image_bytes,
            extension=extension,
            content_type=content_type,
        )