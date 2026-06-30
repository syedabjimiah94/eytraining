import re

from guardrails.constants import MAX_CITY_LENGTH


def validate_city(city: str):
    """
    Validate user input before sending
    request to Weather Service.
    """

    # Remove leading/trailing spaces
    city = city.strip()

    # Empty
    if not city:
        return False, "City name cannot be empty."

    # Too long
    if len(city) > MAX_CITY_LENGTH:
        return False, "City name is too long."

    # Alphabets and spaces only
    if not re.fullmatch(r"[A-Za-z ]+", city):
        return False, "Only alphabets and spaces are allowed."

    # Normalize
    city = city.title()

    return True, city