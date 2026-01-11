"""
CityPulse Validators
Validation utilities for API inputs.
"""
from typing import List
from fastapi import HTTPException, UploadFile

MAX_IMAGES = 3
MAX_IMAGE_SIZE_MB = 10
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024


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
        image.file.seek(0, 2)
        size = image.file.tell()
        image.file.seek(0)

        if size > MAX_IMAGE_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"Image '{image.filename}' exceeds maximum size of {MAX_IMAGE_SIZE_MB} MB"
            )
