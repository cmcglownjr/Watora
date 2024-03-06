"""
Permission checks for Discord.py commands.

The permission system of the bot is based on a "just works" basis
- You have permissions and the bot has permissions. If you meet the permissions
required to execute the command (and the bot does as well) then it goes through
and you can execute the command.
- Certain permissions signify if the person is a moderator (Manage Server) or an
admin (Administrator). Having these signify certain bypasses.
- Of course, the owner will always be able to execute commands.
"""

from discord.ext import commands
from typing import Any, Callable, Dict, Optional, Union


async def check_permissions(
    ctx: commands.Context,
    perms: Dict[str, Union[bool, int]],
    *,
    check: Callable[[bool], bool] = all,
    guild: Optional[commands.Guild] = None,
) -> bool:
    """Check if the author has the required permissions.

    Args:
        ctx (Context): The command context.
        perms (Dict[str, Union[bool, int]]): The permissions to check.
            Keys are permission names and values are either bools (for
            allow/deny) or ints (for permission values).
        check (Callable[[bool], bool]): A function that checks if the
            permission check passed. Defaults to `all`.
        guild (Optional[Guild]): The guild to check permissions against.
            If not provided, checks against the channel.

    Returns:
        bool: Whether the author has the required permissions.
    """
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    if guild is None:
        resolved = ctx.channel.permissions_for(ctx.author)
    else:
        resolved = guild.permissions_for(ctx.author)

    return check(getattr(resolved, name, None) == value for name, value in perms.items())


def has_permissions(*, perms: Dict[str, Union[bool, int]], **kwargs) -> commands.check:
    """A decorator that checks if the author has the required permissions.

    Args:
        perms (Dict[str, Union[bool, int]]): The permissions to check.
            Keys are permission names and values are either bools (for
            allow/deny) or ints (for permission values).

    Returns:
        check: A decorator that checks if the author has the required
            permissions.
    """
    async def pred(ctx: commands.Context) -> bool:
        return await check_permissions(ctx, perms, **kwargs)

    return commands.check(pred)


def has_permissions_guild(*, perms: Dict[str, Union[bool, int]], **kwargs) -> commands.check:
    """A decorator that checks if the author has the required permissions
    against a guild.

    Args:
        perms (Dict[str, Union[bool, int]]): The permissions to check.
            Keys are permission names and values are either bools (for
            allow/deny) or ints (for permission values).

    Returns:
        check: A decorator that checks if the author has the required
            permissions against a guild.
    """
    async def pred(ctx: commands.Context) -> bool:
        return await check_permissions(ctx, perms, guild=ctx.guild, **kwargs)

    return commands.check(pred)


def has_permissions_channel(*, perms: Dict[str, Union[bool, int]], **kwargs) -> commands.check:
    """A decorator that checks if the author has the required permissions
    against a channel.

    Args:
        perms (Dict[str, Union[bool, int]]): The permissions to check.
            Keys are permission names and values are either bools (for
            allow/deny) or ints (for permission values).

    Returns:
        check: A decorator that checks if the author has the required
            permissions against a channel.
    """
    async def pred(ctx: commands.Context) -> bool:
        return await check_permissions(ctx, perms, **kwargs)

    return commands.check(pred)


def has_permissions_any(*, perms: Dict[str, Union[bool, int]], **kwargs) -> commands.check:
    """A decorator that checks if the author has any of the required
    permissions.

    Args:
        perms (Dict[str, Union[bool, int]]): The permissions to check.
            Keys are permission names and values are either bools (for
            allow/deny) or ints (for permission values).

    Returns:
        check: A decorator that checks if the author has any of the
            required permissions.
    """
    perms_iter = (perms.get(perm, None) for perm in kwargs.get("perms", tuple(perms)))
    async def pred(ctx: commands.Context) -> bool:
        return any(await check_permissions(ctx, {perm: value}, **kwargs) for perm, value in zip(perms_iter, perms_iter))

    return commands.check(pred)


# These do not take channel overrides into account

def is_mod() -> commands.check:
    """A decorator that checks if the author has the manage server permission."""
    async def pred(ctx: commands.Context) -> bool:
        return await check_permissions(ctx, {'manage_guild': True})

    return commands.
