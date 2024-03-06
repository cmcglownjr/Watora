"""
The MIT License

Copyright (c) 2017-2020 Zenrac - Watora (https://github.com/Zenrac/Watora)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import asyncio
import aiohttp
from urllib.parse import quote_plus
from typing import Any, Dict, List, Optional, TypeVar, DefaultDict, AsyncIterable, Type

T = TypeVar('T')

class YoutubeAPI:
    """
    A class to interact with the YouTube API.
    """
    def __init__(self, youtube_token: str, loop: Optional[asyncio.AbstractEventLoop] = None,
                 aiosession: Optional[aiohttp.ClientSession] = None):
        """
        Initialize the YoutubeAPI class.

        :param youtube_token: The YouTube API token.
        :param loop: The event loop to use. Defaults to the current event loop.
        :param aiosession: The aiohttp session to use. Defaults to a new session.
        """
        self.youtube_token = youtube_token
        self.url = "https://www.googleapis.com/youtube/v3/"
        self.session = aiosession or aiohttp.ClientSession(loop=self.loop)
        self.loop = loop or asyncio.get_event_loop()

    async def make_request(self, url: str) -> Dict[str, T]:
        """
        Make a request to the YouTube API.

        :param url: The URL to request.
        :return: The JSON response as a dict.
        """
        url = f'{self.url}{url}&key={self.youtube_token}'
        try:
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    rep = await resp.json()
                    await resp.release()
                    return rep
        except asyncio.TimeoutError:
            pass
        return {}

    async def youtube_search(self, query: str) -> List[Dict[str, str]]:
        """
        Search for videos on YouTube.

        :param query: The search query.
        :return: A list of video dicts.
        """
        search_response = await self.make_request(f'search?part=snippet&q={quote_plus(query)}')
        if not search_response:
            return []
        videos = []
        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                track = {}
                track['uri'] = f'https://www.youtube.com/watch?v={search_result["id"]["videoId"]}'
                track['title'] = search_result['snippet']['title']
                videos.append(track)

        return videos

    async def get_youtube_title(self, player: Optional[Any] = None, *, id: List[str]) -> DefaultDict[str, str]:
        """
        Get the titles of YouTube videos.

        :param player: The player object.
        :param id: The IDs of the videos.
        :return: A defaultdict of video IDs to titles.
        """
        if not id:
            return {}
        found: DefaultDict[str, str] = DefaultDict(str)
        while id:
            ids = id[:45]
            ready_ids = ','.join(ids)
            rep = await self.make_request(f'videos?part=snippet&id={ready_ids}')
            for x in ids:
                id.remove(x)
            if rep and rep['items']:
                for m in rep['items']:
                    found[m['id']] = m['snippet']['title']
        return found

    async def get_youtube_infos(self, id: str) ->
