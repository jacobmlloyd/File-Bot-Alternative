"""
tmdb_client.py

Client wrapper for TheMovieDB API to fetch movie and TV metadata.
"""
import requests
import re
from typing import Any, Dict, List, Optional

class TMDBClient:
    def __init__(self, api_key: str) -> None:
        """
        Initialize the TMDB client with the provided API key.

        Args:
            api_key: The TMDB API key.
        """
        self.api_key: str = api_key
        self.base_url: str = 'https://api.themoviedb.org/3'

    def search_movie(self, title: str, year: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Search for a movie by title and optional year.

        Args:
            title: Movie title to search for.
            year: Optional release year to filter results.

        Returns:
            The first matching movie record as a dict, or None if no match.
        """
        params = {'api_key': self.api_key, 'query': title}
        if year:
            params['year'] = year
        response = requests.get(f'{self.base_url}/search/movie', params=params)
        response.raise_for_status()
        data = response.json()
        results = data.get('results') or []
        return results[0] if results else None

    def search_tv(self, title: str, year: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Search for a TV show by title and optional first air year.

        Args:
            title: Show title to search for.
            year: Optional first air date year to filter results.

        Returns:
            The best matching TV show record as a dict, or None if no match.
        """
        params = {'api_key': self.api_key, 'query': title}
        if year:
            params['first_air_date_year'] = year
        response = requests.get(f'{self.base_url}/search/tv', params=params)
        response.raise_for_status()
        data = response.json()
        results = data.get('results') or []
        if not results:
            return None
        # Try to find exact match on show name
        def normalize(s: Optional[str]) -> str:
            return re.sub(r'\W+', '', s or '').lower()
        norm_query = normalize(title)
        for r in results:
            if normalize(r.get('name')) == norm_query:
                return r
        # Fallback to first result
        return results[0]

    def get_episode_name(
        self,
        tv_id: int,
        season: int,
        episode: int
    ) -> Optional[str]:
        """
        Retrieve the episode title given a TV show ID, season, and episode number.

        Args:
            tv_id: The TMDB ID for the TV show.
            season: The season number.
            episode: The episode number.

        Returns:
            The episode title if found, otherwise None.
        """
        url: str = f'{self.base_url}/tv/{tv_id}/season/{season}/episode/{episode}'
        response = requests.get(url, params={'api_key': self.api_key})
        response.raise_for_status()
        data: Dict[str, Any] = response.json()
        return data.get('name')
    
    def get_movie_imdb_id(self, movie_id: int) -> Optional[str]:
        """
        Retrieve the IMDB ID for a movie given its TMDB movie ID.

        Args:
            movie_id: TMDB movie identifier.

        Returns:
            The IMDB ID string if available, otherwise None.
        """
        url = f'{self.base_url}/movie/{movie_id}/external_ids'
        response = requests.get(url, params={'api_key': self.api_key})
        response.raise_for_status()
        data: Dict[str, Any] = response.json()
        return data.get('imdb_id')
    
    def get_tv_imdb_id(self, tv_id: int) -> Optional[str]:
        """
        Retrieve the IMDB ID for a TV show given its TMDB TV ID.

        Args:
            tv_id: TMDB TV show identifier.

        Returns:
            The IMDB ID string if available, otherwise None.
        """
        url = f'{self.base_url}/tv/{tv_id}/external_ids'
        response = requests.get(url, params={'api_key': self.api_key})
        response.raise_for_status()
        data: Dict[str, Any] = response.json()
        return data.get('imdb_id')