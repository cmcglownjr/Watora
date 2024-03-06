import re
import random
import discord
from collections import Counter, OrderedDict
from typing import List, Dict, Optional

class BlindTest:
    """
    A class representing a blind test game.
    """

    def __init__(self, player):
        self.bot: discord.Bot = player.node._manager._lavalink.bot
        self.jikan = self.bot.jikan
        self.player = player
        self.songs: List[dict] = []
        self.points: Dict[str, int] = {}
        self.severity: int = 100
        self.channel: Optional[discord.TextChannel] = None
        self.current_song: Optional[dict] = None
        self.next_song: Optional[dict] = None
        self.accept_longest_word: bool = False
        self.listening_mode: bool = False
        self.current_task: List[asyncio.Task] = []
        self.timeout: int = 120
        self.percentage: str = '100,0,0'
        self.wait: int = 5
        self.source: str = 'ytsearch'

    @property
    def is_running(self) -> bool:
        """
        Returns True if the blind test game is running, False otherwise.
        """
        return bool(self.songs) or bool(self.next_song and (self.current_song != self.next_song))

    @property
    def partition(self) -> List[str]:
        """
        Returns a list of opening, ending, and ost strings based on the percentage attribute.
        """
        values = [abs(int(m)) for m in self.percentage.split(',')]
        while len(values) < 3:
            values.append(0)
        return ['opening'] * values[0] + ['ending'] * values[1] + ['ost'] * values[2]

    @property
    def bt_channel(self) -> discord.TextChannel:
        """
        Returns the text channel where the blind test game is taking place.
        """
        return self.channel

    @property
    def guild(self) -> discord.Guild:
        """
        Returns the guild where the blind test game is taking place.
        """
        return self.bot.get_guild(int(self.player.guild_id))

    def clean_tasks(self):
        """
        Cancels all current tasks.
        """
        for task in self.current_task:
            task.cancel()
        self.current_task = []

    async def stop(self, bypass: bool = False, send_final: bool = True):
        """
        Stops the blind test game.
        """
        if self.is_running or bypass:
            embed = await self.get_classement()
            if embed.fields:
                embed.title = get_str(
                    self.guild, "cmd-blindtest-final-rank", bot=self.bot)
                await self.bt_channel.send(embed=embed)
            if send_final:
                await self.send_final_embed()
        self.clean_tasks()
        settings = await SettingsDB.get_instance().get_guild_settings(int(self.player.guild_id))
        for k, v in self.points.items():
            settings.points[k] = settings.points.get(k, 0) + v
        await SettingsDB.get_instance().set_guild_settings(settings)
        self.songs = []
        self.points = {}

    async def send_final_embed(self):
        """
        Sends a final embed message.
        """
        e = discord.Embed(description=get_str(
            self.guild, "cmd-blindtest-enjoyed", bot=self.bot))
        e.description += "\n\n**[{}](https://www.patreon.com/watora)** {}".format(
            get_str(self.guild, "support-watora", bot=self.bot), get_str(self.guild, "support-watora-end", bot=self.bot))
        e.description += '\n' + get_str(self.guild, "suggest-features", bot=self.bot).format(
            f"`{get_server_prefixes(self.bot, self.guild)}suggestion`")
        await self.bt_channel.send(embed=e)

    def pop(self, next: bool = False) -> dict:
        """
        Pops a random song from the songs list.
        """
        if not self.songs:
            return None
        index = random.randrange(len(self.songs))
        song = self.songs.pop(index)
        if next:
            self.next_song = song
        else:
            self.current_song = song
        return song

    def get_song_keywords(self) -> str:
        """
        Returns the keywords for the current song.
        """
        if self.current_song.is_anime:
            search_end = ' ' + random.choice(self.partition)
            parts = self.current_song.title.split(':')
            if len(parts) > 1 and len(self.current_song.title.split(':')[0]) > 2:
              
