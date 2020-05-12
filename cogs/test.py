import discord
import json
import asyncio

from discord.ext import commands, menus


async def get_prefix(bot, message):
    res = await bot.pool.fetchrow("""SELECT prefix
                                     FROM db
                                     WHERE guild_id = $1""",
                                  message.guild.id
                                  )
    if res is None:
        prefix = commands.when_mentioned_or('+-')(bot, message)

    if res is not None:
        prefix = commands.when_mentioned_or(res.get("prefix"))(bot, message)

    return prefix


class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Test(bot))
