from io import BytesIO
from PIL import Image


ALLOWED_MIME = {"image/jpeg", "image/png"}


def validate_image(content_type: str, data: bytes) -> Image.Image:
    if content_type not in ALLOWED_MIME:
        raise ValueError("invalid_type")
    if len(data) > 5 * 1024 * 1024:
        raise ValueError("too_large")
    try:
        image = Image.open(BytesIO(data))
        image.verify()
        image = Image.open(BytesIO(data))
        return image.convert("RGB")
    except Exception as exc:
        raise ValueError("invalid_image") from exc
