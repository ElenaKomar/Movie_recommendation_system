import requests
from typing import Optional, List


class OMDBApi:

    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://www.omdbapi.com"

    def _images_path(self, title: str) -> Optional[str]:
        body = f'{self.url}?apikey={self.api_key}&t={title}'
        web = requests.get(body)
        if 'Poster' in web.json():
            data = web.json()['Poster']
            return data


    def get_posters(self, titles: List[str]) -> List[str]:
        posters = []
        for title in titles:
            path = self._images_path(title)
            if path:
                posters.append(path)
            else:
                posters.append('assets/none.jpeg')

        return posters
