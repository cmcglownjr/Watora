import discord
from discord.ext import commands
from discordTogether import DiscordTogether
from utils.watora import get_str, get_color

class DiscordTogetherCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.togetherControl = DiscordTogether(bot)

    async def start_activity(self, ctx, activity_name, link_text):
        if not ctx.author.voice:
            return await ctx.send(get_str(ctx, "music-join-no-channel"))
        link = await self.togetherControl.create_link(ctx.author.voice.channel.id, activity_name)

        embed=discord.Embed(
            title=f"{activity_name.capitalize()} Together",
            description=f"[Click Here]({link})",
            color=get_color(ctx.guild)
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=['youtube'])
    async def youtubetogether(self, ctx):
        await self.start_activity(ctx, 'youtube', 'youtube')

    @commands.command(aliases=['poker'])
    async def pokertogether(self, ctx):
        await self.start_activity(ctx, 'poker', 'poker')

    @commands.command(aliases=['chess'])
    async def chesstogether(self, ctx):
        await self.start_activity(ctx, 'chess', 'chess')

    @commands.command(aliases=['betrayal'])
    async def betrayaltogether(self, ctx):
        await self.start_activity(ctx, 'betrayal', 'betrayal')

    @commands.command(aliases=['fishing'])
    async def fishingtogether(self, ctx):
        await self.start_activity(ctx, 'fishing', 'fishing')

def setup(bot):
    bot.add_cog(DiscordTogetherCog(bot))
