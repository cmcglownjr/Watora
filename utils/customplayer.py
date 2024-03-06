import re
import asyncio
import lavalink
from typing import Dict, Optional
from random import randrange
from time import time as current_time

from utils.db import SettingsDB
from utils.blindtest.blindtest import BlindTest
from utils.watora import def_time

class CustomPlayer(lavalink.DefaultPlayer):
    def __init__(self, guild_id: int, node):
        super().__init__(guild_id, node)

        self.channel_id: Optional[int] = None
        self.previous = None
        self.description = None

        self.stop_votes: set = set()
        self.skip_votes: set = set()
        self.clear_votes: set = set()
        self.already_played: set = set()

        self.auto_paused = False
        self.autoplaylist = None
        self.list = None
        self.authorplaylist = None
        self.npmsg = None
        self.now = None
        self.channel = None
        self.timer_value: int = def_time  # can be edited in settings.json

        self.blindtest = BlindTest(self)

        asyncio.ensure_future(self.init_with_db(guild_id))

    async def init_with_db(self, guild_id: int):
        settings: dict = await SettingsDB.get_instance().get_guild_settings(int(guild_id))
        if not isinstance(settings, dict):
            raise TypeError("settings must be a dictionary")
        await self.set_volume(settings.get("volume", 100))

        if settings.get("timer") is not None:
            if settings["timer"] or await self.node._manager._lavalink.bot.server_is_claimed(int(guild_id)):
                self.timer_value = settings["timer"]
            else:
                del settings["timer"]
                await SettingsDB.get_instance().set_guild_settings(settings)

        if settings.get("channel"):
            self.channel = settings["channel"]

    async def play(self, track=None, **kwargs):
        if self.repeat and self.current:
            self.queue.append(self.current)

        self.current = None
        self.last_update = 0
        self.last_position = 0
        self.position_timestamp = 0
        self.paused = False

        if not track:
            if not self.queue:
                await self.stop()
                await self.node._dispatch_event(lavalink.events.QueueEndEvent(self))
                return

            if self.shuffle:
                track = self.queue.pop(randrange(len(self.queue)))
            else:
                track = self.queue.pop(0)

        self.current = track
        if not kwargs:
            kwargs = await self.optional_parameters(track.uri)
        await self.node._send(op='play', guildId=self.guild_id, track=track.track, **kwargs)
        await self.node._dispatch_event(lavalink.events.TrackStartEvent(self, track))

    async def optional_parameters(self, url: str) -> Dict[str, str]:
        kwargs: Dict[str, str] = {}
        try:
            start_time = re.findall('[&?](t|start|starts|s)=(\d+)', url)
            if start_time:
                kwargs['startTime'] = str(int(start_time[-1][-1]) * 1000)
        except re.error as e:
            print(f"Ignoring invalid regex: {e}")

        try:
            end_time = re.findall('[&?](e|end|ends)=(\d+)', url)
            if end_time:
                kwargs['endTime'] = str(int(end_time[-1][-1]) * 1000)
        except re.error as e:
            print(f"Ignoring invalid regex: {e}")

        return kwargs

    async def update_state(self, state: dict):
        """
        Updates the position of the player.
        Parameters
        ----------
        state: dict
            The state that is given to update.
        """
        self.last_update = current_time() * 1000
        self.last_position = state.get('position', 0)
        self.position_timestamp = state.get('time', 0)

        try:
            await self.update_title()
        except Exception:  # I don't want the task to finish because of a stupid thing
            pass

        event = PlayerUpdateEvent(
            self, self.last_position, self.position_timestamp)
        await self.node._dispatch_event(event)

    async def update_title(self):
        music_cog = self.node._manager._lavalink.bot.cogs.get('Music')
        if self.current:
            timestamps = self.current.extra.get('timestamps', [])
            for timestamp in reversed(timestamps):
                time, title = timestamp
                milliseconds = (
                    sum(x * int(t) for x, t
