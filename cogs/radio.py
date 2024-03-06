import aiohttp
import asyncio
import listenmoe
from discord.ext import commands
# from monstercatFM import monstercat  # Unused import statement removed
from utils.watora import log

class Radio(commands.Cog):
    """A cog for handling radio streams."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tasks = []
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        asyncio.create_task(self.start())

    def cog_unload(self):
        for task in self.tasks:
            task.cancel()
        asyncio.create_task(self.session.close())

    async def players_update(self, kpop: bool = False, mc: bool = False):
        """Update all players."""
        try:
            if not mc:
                await self.bot.cogs['Music'].update_all_listen_moe_players(kpop)
            else:
                # Monstercat is disabled, so this will never be called
                await self.bot.cogs['Music'].update_all_mc_players()
        except Exception as e:
            log.warning(
                f"[LISTEN.moe] Updating {'K-POP' if kpop else 'J-POP'} players failed with error : {e}")

    async def hand(self, msg: listenmoe.message.BaseMessage):
        before = self.bot.now

        if msg.type == listenmoe.message.SONG_INFO:
            self.bot.now = msg
        else:
            self.bot.now = msg.raw

        if before != self.bot.now:  # avoid the first useless updates when starting the bot / loading the cog
            await self.players_update()

    async def handkpop(self, msg: listenmoe.message.BaseMessage):
        before = self.bot.nowkpop

        if msg.type == listenmoe.message.SONG_INFO:
            self.bot.nowkpop = msg
        else:
            self.bot.nowkpop = msg.raw

        if before != self.bot.nowkpop:  # avoid the first useless updates when starting the bot / loading the cog
            await self.players_update(kpop=True)

    async def mchand(self, msg: listenmoe.message.BaseMessage):
        before = self.bot.mcnow
        self.bot.mcnow = msg

        if msg != before:
            await self.players_update(mc=True)

    async def start(self):
        """Start the cog."""
        await self.bot.wait_until_ready()

        kp = listenmoe.client.Client(loop=self.bot.loop, kpop=True)
        kp.register_handler(self.handkpop)
        task = asyncio.create_task(kp.start())
        self.tasks.append(task)

        cl = listenmoe.client.Client(loop=self.bot.loop)
        cl.register_handler(self.hand)
        task = asyncio.create_task(cl.start())
        self.tasks.append(task)

        # Monstercat is disabled, so this is commented out
        # mc = monstercat.Client(loop=self.bot.loop, aiosession=self.session)
        # mc.register_handler(self.mchand)
        # task = asyncio.create_task(mc.start())
        # self.tasks.append(task)

async def setup(bot: commands.Bot):
    """Create and add the cog to the bot."""
    await bot.add_cog(Radio(bot))
