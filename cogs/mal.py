import re
import pytz
import json
import discord
import asyncio
import traceback
import aiohttp
from lxml import etree
from utils.dataIO import dataIO
from discord.ext import commands
from datetime import datetime, timedelta
from urllib.parse import parse_qs, quote_plus
from bs4 import BeautifulSoup
from jikanpy import AioJikan
from jikanpy.exceptions import JikanException

class Mal(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.bot.jikan = AioJikan()
        self.temp = None

    async def cog_unload(self):
        if self.bot.jikan is not None:
            self.bot.jikan.close()
        if self.session is not None:
            await self.session.close()

    def remove_html(self, arg: str) -> str:
        arg = arg.replace("&quot;", "\"").replace(
            "<br />", "").replace("[i]", "*").replace("[/i]", "*")
        arg = arg.replace("&ldquo;", "\"").replace(
            "&rdquo;", "\"").replace("&#039;", "'").replace("&mdash;", "—")
        arg = arg.replace("&ndash;", "–")
        return arg

    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    @commands.command(aliases=["infoanime", "animeinfo"])
    async def anime(self, ctx: commands.Context, *, anime: str):
        """
            {command_prefix}anime [anime_title]

        {help}
        """
        fetch = await ctx.send(get_str(ctx, "is-searching"))
        await ctx.trigger_typing()
        found = await self.google_results('anime', anime)
        if not found:
            return await ctx.send(get_str(ctx, "no-result"))
        try:
            selection = await self.bot.jikan.anime(found)
            selection = Jikan(selection)
        except (JikanException, aiohttp.ClientError):
            return await ctx.send(get_str(ctx, "no-result"))

        em = discord.Embed(colour=0x0066CC)
        synopsis = selection.synopsis
        if synopsis:
            synopsis = self.remove_html(synopsis)
            if len(synopsis) > 300:
                em.description = " ".join(synopsis.split(
                    " ")[0:40]) + "[ Read more»](%s)" % selection.url
        em.set_author(name=selection.title, url=selection.url,
                      icon_url='https://i.imgur.com/vEy5Zaq.png')
        if selection.title_english:
            if selection.title_english.lower() not in selection.title.lower():
                em.add_field(name=get_str(ctx, "cmd-anime-english-title"),
                             value=selection.title_english, inline=False)
        try:
            em.add_field(name="{}".format(get_str(ctx, "cmd-anime-episodes") if int(selection.episodes)
                                          > 1 else get_str(ctx, "cmd-anime-episode")), value=selection.episodes)
        except TypeError:
            pass
        em.add_field(name=get_str(ctx, "cmd-anime-type"), value=selection.type)
        em.add_field(name=get_str(ctx, "cmd-anime-ranked"),
                     value=("#" + str(selection.rank)) if selection.rank else 'N/A')
        em.add_field(name=get_str(ctx, "cmd-anime-popularity"), value=("#" +
                                                                       str(selection.popularity)) if selection.popularity else 'N/A')
        score = round((selection.score or 0), 2)
        if score == 0:
            score = "N/A"
        em.add_field(name=get_str(ctx, "cmd-anime-score"), value=score)
        em.set_thumbnail(url=selection.image_url)
        status = selection.status
        em.add_field(name=get_str(ctx, "cmd-anime-status"), value=status)
        aired = selection.aired
        a = getattr(aired
