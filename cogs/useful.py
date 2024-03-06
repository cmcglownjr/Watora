import asyncio
import aiohttp
import discord
from discord.ext import commands
from datetime import datetime
from collections import Counter, OrderedDict
from utils.db import SettingsDB
from utils.watora import globprefix, log, owner_id, ver, get_uptime, get_server_prefixes, is_basicpatron, is_patron, is_lover, get_str, sweet_bar, format_mentions, get_image_from_url
from cogs.gestion import cmd_help_msg as cmds

class Useful(commands.Cog):
    """The useful cog"""

    def __init__(self, bot):
        self.bot = bot
        self.next_cost = ['80.00', '90.00', '105.00', '120.00', '150.00']

    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    @commands.command(name="marry", aliases=["married", "mary", "mariage", "epouse", "epouser"])
    async def _marry(self, ctx, *, user: discord.Member = None):
        """
            {command_prefix}marry [user]

        {help}
        """
        husband_role_id = 501330901653782558

        settings = await SettingsDB.get_instance().get_glob_settings()
        embed = discord.Embed()
        embed.color = 0xFF0000

        if user == ctx.author:
            return await ctx.send(get_str(ctx, "cmd-weeb-alone"))
        if user == ctx.me:
            if ctx.guild:
                ids = [r.id for r in ctx.author.roles]
                if husband_role_id in ids:  # Watora's Husband can marry Watora
                    embed.title = "❤ " + get_str(ctx, "cmd-marry-happily")
                    embed.description = get_str(
                        ctx, "cmd-marry-success").format(f"**{ctx.author.name}**", f"**{user.name}**")
                    await ctx.send(embed=embed)
                    if str(user.id) in settings.marry:
                        before = settings.marry[str(user.id)]['id']
                        del settings.marry[before]  # Watora divorces before

                    date = datetime.today().strftime("%d %b %Y")

                    settings.marry[str(ctx.author.id)] = {}
                    settings.marry[str(ctx.author.id)]['id'] = str(user.id)
                    settings.marry[str(ctx.author.id)]['date'] = date
                    # stock the name in case of a day where the user is not on any bot servers anymore.
                    settings.marry[str(ctx.author.id)]['name'] = user.name

                    settings.marry[str(user.id)] = {}
                    settings.marry[str(user.id)]['id'] = str(ctx.author.id)
                    settings.marry[str(user.id)]['date'] = date
                    # stock the name in case of a day where the user is not on any bot servers anymore.
                    settings.marry[str(user.id)]['name'] = ctx.author.name

                    await SettingsDB.get_instance().set_glob_settings(settings)
                    return

            if not await is_lover(self.bot, ctx.author):
                return await ctx.send(get_str(ctx, "cmd-weeb-dont-touch-me"))
            else:
                #return await ctx.send(get_str(ctx, "cmd-marry-too-young") + " {}".format("<:WatoraHyperBlush:458349268944814080>"))
                embed = discord.Embed(color=13596669)
                embed.set_image(url="https://cdn.discordapp.com/emojis/458349268944814080.png")
                return await ctx.send(content=get_str(ctx, "cmd-marry-too-young"), embed=embed)

        if not user:
            if str(ctx.author.id) in settings.marry:
                embed.title = "❤ {} ({})".format(get_str(ctx, "cmd-marry-married-to").format(
                    await self.bot.safe_fetch('user', int(settings.marry[str(ctx.author.id)]["id"]))
                    or settings.marry[str(ctx.author.id)]['name']),
                    settings.marry[str(ctx.author.id)]['date'])
                try:
                    return await ctx.send(embed=embed)
                except discord.Forbidden:
                    return await ctx.send(get_str(ctx, "need-embed-permission"), delete_after=20)
            else:
                return await self.bot.send_cmd_help(ctx)

        embed.title = "💍 " + \
            get_str(ctx, "cmd-marry-proposed").format(ctx.author.name, user.name)

        if str(user.id) in settings.marry:
            married_with = (await self.bot.safe_fetch('user', int(settings.marry[str(user.id)]['id']))
                            or settings.marry[str(user.id)]['name'])
            married_since = settings.marry[str(user.id)]['date']
            embed.description = "{} ({})".format(get_str(
                ctx, "cmd-marry-user-a-married").format(user.name
