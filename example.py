import bitmap_matcher
from PIL import Image
import time
import numpy as np


#1. Converting a base64 string to a bitmap
bitmap_from_base64 = bitmap_matcher.create_bitmap_from_base64("iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==")
"""
bitmap_matcher.create_bitmap_from_base64
    Reads a base64 string and converts it into a PIL Image object for searching.

    Args:
        base64_string (str): The base64-encoded image data.

    Returns:
        PIL.Image.Image: The bitmap image object in RGBA mode.
        None: If the base64 string is invalid or cannot be processed.
"""

#2. Reading an image file and converting it to a bitmap
bitmap_from_file = Image.open("screenshot.png").convert('RGBA')

#3. Creating a bitmap with pillow Image
new_bitmap = Image.new('RGBA', (10, 1), '#f0f0f0ff')

#3. Searching for a bitmap within a bitmap (needle in a haystack)
res = bitmap_matcher.find_bitmap_cython(bitmap_from_file, bitmap_from_base64)
if res:
    print(f"Found bitmap at: {res}")
else:
    print(f"Could not find bitmap")
"""
bitmap_matcher.find_bitmap_cython
Works with alpha channels. This function will only compare non-transparent pixels
Supports both RGB and RGBA channels

Python wrapper for the Cython bitmap matching function

Args:
    main_image: PIL Image object to search in
    bitmap_image: PIL Image object to search for
    x: X coordinate of search area (default: 0)
    y: Y coordinate of search area (default: 0)
    w: Width of search area (default: None for full width)
    h: Height of search area (default: None for full height)
    variance: Allowed color variance per channel 0-255 (default: 0 for exact match)

Returns:
    tuple: (x, y) coordinates of the match, or None if not found
"""

#3. Search for all instances of a bitmap within a bitmap (needle in a haystack)
res = bitmap_matcher.find_all_bitmap_cython(bitmap_from_file, bitmap_from_base64)
if res:
    print(f"Found bitmap at: {res}")
else:
    print(f"Could not find bitmap")
"""
bitmap_matcher.find_all_bitmap_cython
Python wrapper to find all matching locations of a bitmap in the main image.

Args:
    main_image: PIL Image object to search in
    bitmap_image: PIL Image object to search for
    x: X coordinate of search area (default: 0)
    y: Y coordinate of search area (default: 0)
    w: Width of search area (default: None for full width)
    h: Height of search area (default: None for full height)
    variance: Allowed color variance per channel 0-255 (default: 0 for exact match)
    max_matches: Maximum number of matches to find (default: -1 for all matches)

Returns:
    list: List of (x, y) tuples representing match locations
"""