import os
import re
import discord
import logging
import mimetypes
import datetime
from time import time
from glob import glob
from typing import Any, Dict, List, Optional, Union
from utils.dataIO import dataIO
from discord.ext import commands
from TextToOwO import owo

# Constants
CONFIG_DIR = "config"
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")
I18N_DIR = os.path.join(CONFIG_DIR, "i18n")

# Regex patterns
URL_RX = re.compile(r'https?://(?:www\.)?.+')
LOCAL_RX = re.compile(r'.*\.[a-zA-Z0-9]+$')
ILLEGAL_RX = re.compile(r"[///:*?\"<>|@]")
TIME_RX = re.compile(r'[0-9]+')


class VoiceConnectionError(commands.CommandError):
    """Custom Exception for cases of connection errors."""


class NoVoiceChannel(VoiceConnectionError):
    """Exception for cases of no voice channel to join."""


class Jikan:
    """Class to make an object from a dict."""

    def __init__(self, d: Dict[str, Union[str, List["Jikan"]]]):
        """Initialize Jikan object from a dictionary."""
        for key, value in d.items():
            if isinstance(value, (list, tuple)):
                setattr(self, key, [Jikan(x) if isinstance(x, dict) else x for x in value])
            else:
                setattr(self, key, Jikan(value) if isinstance(value, dict) else value)


def get_server_prefixes(bot: commands.Bot, server: Optional[discord.Guild]) -> List[str]:
    """Gets the server prefix"""
    if not server:  # Assuming DMs
        return globprefix
    prefix = bot.prefixes_map.get(server.id, globprefix)
    return prefix


def get_str(
    ctx: Union[commands.Context, discord.Guild],
    cmd: str,
    bot: Optional[commands.Bot] = None,
    can_owo: bool = True,
) -> str:
    """Funct to get answers from i18n folder."""
    lang = 'english'
    weeb = False

    if isinstance(ctx, commands.context.Context) and ctx.guild:
        gid = ctx.guild.id
        bot = ctx.bot
        lang = bot.languages_map.get(gid, 'english')
        weeb = bot.owo_map.get(gid, False)
        texthelp = ""
    elif isinstance(ctx, discord.Guild):
        gid = ctx.id
        if bot:
            lang = bot.languages_map.get(gid, 'english')
            weeb = bot.owo_map.get(gid, False)
    else:
        bot = ctx.bot

    if bot.loaded_languages:
        lang = [l for l in bot.loaded_languages if l.lower() == lang]
        if lang:
            lang = lang[0]
        else:
            lang = 'english'
        current_lang = bot.loaded_languages[lang]
    else:
        current_lang = no_lang_loaded
    try:
        text = current_lang[cmd]
    except KeyError:
        try:
            text = no_lang_loaded[cmd]
        except KeyError:
            # I didn't translated the help for weeb commands.
            if 'Weeb' not in bot.cogs or (
                cmd.split("-")[1] not in [g.name for g in bot.cogs['Weeb'].get_commands()]):
                log.error(f"TranslationError {lang} : {cmd} is not existing.")
            if '-help' in cmd and 'cmd-' in cmd:
                realcmd = cmd[4:].replace('-help', '')
                texthelp = bot.get_command(realcmd).help.split("\n")[-1]
            text = texthelp or "This translation isn't working, please report this command and what you done to my dev with `=bug`."

    if weeb and can_owo:
        text = owo.text_to_owo(text)
        if 'help' in cmd or 'bot' in cmd or 'success' in cmd or 'failed' in cmd or 'dm' in cmd or 'warning' in cmd or '```' in text:
            #  I've to admit that it's ugly but it's a lazy way to check if Watora sends a code block
            # basically if it's in a code block remove back slashes cus they are displayed
            text = text.replace('\\', '')
    return text


def _list_cogs() -> List[str]:
    """Displays all cogs."""
    cogs = [os.path.basename(f) for f in glob("cogs/*.py")]
    return [os.path.splitext(f)[0] for f in cogs]


def get_color(guild: Optional[discord.Guild] = None) -> int:
    """Gets the top role color otherwise select the Watora's main color"""
    if not guild or str(guild.me.color) == "#000000":
        return int("FF015B", 16)
    return guild.me.color


def get_color_name
