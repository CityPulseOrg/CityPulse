"""
CityPulse Validators
Validation utilities for API inputs.
"""
from typing import List, Optional
from fastapi import HTTPException, UploadFile


def sanitize_api_key(text: str, api_key: Optional[str]) -> str:
    """Sanitize text to prevent API key leakage in logs or error messages."""
    if api_key and api_key in text:
        return text.replace(api_key, "[REDACTED]")
    return text

MAX_IMAGES = 3
MAX_IMAGE_SIZE_MB = 10
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024

IMAGE_SIGNATURES = {
    b'\xff\xd8\xff': 'image/jpeg',
    b'\x89PNG\r\n\x1a\n': 'image/png',
    b'GIF87a': 'image/gif',
    b'GIF89a': 'image/gif',
    b'RIFF': 'image/webp',
}


def is_valid_image(file: UploadFile) -> bool:
    """Check if file content matches a known image signature."""
    header = file.file.read(12)
    file.file.seek(0)

    for signature in IMAGE_SIGNATURES:
        if header.startswith(signature):
            if signature == b'RIFF':
                return header[8:12] == b'WEBP'
            return True
    return False


def validate_images(images: List[UploadFile]) -> None:
    """
    Validate image uploads for count and file size limits.

    Raises HTTPException with 400 status if validation fails.
    """
    if len(images) > MAX_IMAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Too many images. Maximum allowed: {MAX_IMAGES}"
        )

    for image in images:
        if not is_valid_image(image):
            raise HTTPException(
                status_code=400,
                detail=f"File '{image.filename}' is not a valid image format"
            )

        image.file.seek(0, 2)
        size = image.file.tell()
        image.file.seek(0)

        if size > MAX_IMAGE_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"Image '{image.filename}' exceeds maximum size of {MAX_IMAGE_SIZE_MB} MB"
            )
