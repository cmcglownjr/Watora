import random
import discord
import asyncio
import aiohttp
import unidecode
from io import BytesIO
from utils import checks
from utils.db import SettingsDB
from discord.ext import commands
from pyfiglet import figlet_format
from utils.watora import get_server_prefixes, is_lover, is_basicpatron, get_str, format_mentions, get_image_from_url

class Fun(commands.Cog):
    """The fun cog"""

    def __init__(self, bot):
        self.bot = bot

    def to_keycap(self, c):
        return '\N{KEYCAP TEN}' if c == 10 else str(c) + '\u20e3'

    @commands.command(name="8ball", aliases=["8balls", "eightball"])
    async def _8ball(self, ctx, *, more: str):
        """
            {command_prefix}8ball [question]

        {help}
        """
        await ctx.send(random.choice(get_str(ctx, "cmd-8ball-options").split("|")))

    @commands.command(aliases=['wp', 'watopingd', 'wpd'])
    async def watoping(self, ctx):
        """
            {command_prefix}watoping

        Best emoji ever.
        """
        if 'd' in ctx.invoked_with.lower():
            ctx.command.reset_cooldown(ctx)
            try:
                await ctx.message.delete()
            except discord.HTTPException:
                pass

        embed = discord.Embed(color=13596669)
        embed.set_image(url="https://cdn.discordapp.com/emojis/458349269875949569.png")
        await ctx.send(content=None, embed=embed)

    @commands.cooldown(rate=1, per=2.0, type=commands.BucketType.user)
    @commands.command(name="ily", aliases=["jtm"])
    async def _ily(self, ctx, more=None):
        """
            {command_prefix}ily

        {help}
        """
        fetched_member = await is_lover(self.bot, ctx.author, fetch=True)
        if more and not fetched_member:
            await ctx.send(get_str(ctx, "cmd-ily-nope"))
        elif more:
            embed = discord.Embed(color=13596669)
            embed.set_image(url="https://cdn.discordapp.com/emojis/458349266495078413.png")
            await ctx.send(content=None, embed=embed)
        elif fetched_member:
            await ctx.send(random.choice(get_str(ctx, "cmd-ily-yes").split("|")))
        else:
            await ctx.send(random.choice(get_str(ctx, "cmd-ily-no").split("|")))

    @commands.command()
    async def roll(self, ctx, maxi: str = 100, mini: int = 0):
        """
            {command_prefix}roll [number_of_dice]d[number_of_face]
            {command_prefix}roll [min] [max]
            {command_prefix}roll [max]
            {command_prefix}roll

        {help}
        """
        if not str(maxi).isdigit():
            numbers = maxi.split('d')
            if not len(numbers) == 2:
                return await self.bot.send_cmd_help(ctx)

            number, face = numbers

            try:
                number = min(int(number), 10)
                face = min(int(face), 10000)
            except ValueError:
                return await self.bot.send_cmd_help(ctx)

            results = []

            for m in range(number):
                results.append(random.randint(1, face))

            if number != 1:
                roll = '{} ({})'.format(
                    sum(results), ' + '.join([str(m) for m in results]))
            else:
                roll = sum(results)
        elif int(maxi) <= mini:
            roll = random.randint(int(maxi), mini)
        else:
            roll = random.randint(mini, int(maxi))

        await ctx.send(":game_die: " + get_str(ctx, "cmd-roll").format(ctx.author.name, roll))

    @commands.command()
   
