"""
parser.py

Provides filename parsing utilities for movie and TV show files.
"""
import os
import re
from typing import Any, Dict, Optional

def parse_movie(filename: str) -> Optional[Dict[str, Any]]:
    """
    Parse a movie filename to extract the movie title and release year.

    Args:
        filename: The file name including extension.

    Returns:
        A dict with:
            'title': str, the cleaned movie title.
            'year': Optional[int], the release year if found.
        None if no movie pattern is detected.
    """
    name, _ = os.path.splitext(filename)
    # Split the base name by dots or spaces
    parts = re.split(r'[.\s]+', name)

    # Detect a 4-digit year token
    for idx, token in enumerate(parts):
        if re.fullmatch(r'(19\d{2}|20\d{2})', token):
            title = ' '.join(parts[:idx])
            return {'title': title, 'year': int(token)}

    # Fallback: detect common resolution tokens like '1080p' or '4k'
    if len(parts) >= 2 and re.fullmatch(r'(?:\d{3,4}p|4k)',
                                        parts[1], re.IGNORECASE):
        return {'title': parts[0], 'year': None}

    return None

def parse_tv(filename: str) -> Optional[Dict[str, Any]]:
    """
    Parse a TV show filename to extract show name, season number, and episode number.

    Args:
        filename: The file name including extension.

    Returns:
        A dict with:
            'show': str, the cleaned show name.
            'season': int, the season number.
            'episode': int, the episode number.
        None if no TV show pattern is detected.
    """
    name, _ = os.path.splitext(filename)

    # Regex pattern to match 'Show.Name.S02E04' or 'Show Name - S02E04' etc. (case-insensitive)
    # Allows any non-word characters or underscores before 'SxxExx'
    pattern = r'(?i)(?P<show>.+?)[\W_]+S(?P<season>\d{1,2})E(?P<episode>\d{2})'
    match = re.search(pattern, name)
    if not match:
        return None

    show = match.group('show').replace('.', ' ').strip()
    season = int(match.group('season'))
    episode = int(match.group('episode'))
    return {'show': show, 'season': season, 'episode': episode}