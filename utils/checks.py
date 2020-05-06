from discord.ext import commands


async def check_permissions(ctx, perms, *, check=all):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    resolved = ctx.channel.permissions_for(ctx.author)
    return check(getattr(resolved, name, None) == value for name, value in perms.items())


async def check_guild_permissions(ctx, perms, *, check=all):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    if ctx.guild is None:
        return False

    resolved = ctx.author.guild_permissions
    return check(getattr(resolved, name, None) == value for name, value in perms.items())


def has_permissions(*, check=all, **perms):
    async def pred(ctx):
        return await check_permissions(ctx, perms, check=check)
    return commands.check(pred)


def is_mod():
    async def pred(ctx):
        return await check_guild_permissions(ctx, {'manage_guild': True})
    return commands.check(pred)


def is_admin():
    async def pred(ctx):
        return await check_guild_permissions(ctx, {'administrator': True})
    return commands.check(pred)


def is_in_guilds(*guild_ids):
    def predicate(ctx):
        guild = ctx.guild
        if guild is None:
            return False
        return guild.id in guild_ids
    return commands.check(predicate)


def can_mute():
    async def pred(ctx):
        return await check_guild_permissions(ctx, {'manage_roles': True})
    return commands.check(pred)


def can_ban():
    async def pred(ctx):
        return await check_guild_permissions(ctx, {'ban_members': True})
    return commands.check(pred)


def can_kick():
    async def pred(ctx):
        return await check_guild_permissions(ctx, {'kick_members': True})
    return commands.check(pred)


def can_purge():
    async def pred(ctx):
        return await check_guild_permissions(ctx, {'manage_messages': True})
    return commands.check(pred)


def can_warn():
    async def pred(ctx):
        return await check_guild_permissions(ctx, {'kick_members': True})
    return commands.check(pred)
