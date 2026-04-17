import json
from typing import Any, Dict, Optional

import requests


class APIClient:
    """Client for making API requests."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def get(self, endpoint: str) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return self.session.get(url, timeout=10)

    def post(self, endpoint: str, data: Dict[str, Any]) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        payload = json.dumps(data)
        return self.session.post(url, data=payload, timeout=10)


def create_client(url: str) -> APIClient:
    return APIClient(url)


def handle_response(response: requests.Response) -> Optional[Dict[str, Any]]:
    if response.ok:
        return response.json()
    return {}
