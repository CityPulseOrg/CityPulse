"""Reverse geocoding utilities for CityPulse."""

import logging
from typing import Optional

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

# Shared geocoder with basic rate limiting to avoid hammering the service
_geolocator = Nominatim(user_agent="citypulse-geocoder", timeout=10)
_reverse = RateLimiter(_geolocator.reverse, min_delay_seconds=1, swallow_exceptions=True)


def reverse_geocode(latitude: Optional[float], longitude: Optional[float]) -> Optional[str]:
    """Return a human-readable address for the given coordinates.

    Uses OpenStreetMap Nominatim; returns None on failure or missing coords.
    """
    if latitude is None or longitude is None:
        return None
    try:
        location = _reverse((latitude, longitude), exactly_one=True, language="en")
        if location and location.address:
            return location.address
    except Exception as exc:  # geopy can raise various errors
        logger.warning("Reverse geocoding failed for (%s, %s): %s", latitude, longitude, exc)
    return None
