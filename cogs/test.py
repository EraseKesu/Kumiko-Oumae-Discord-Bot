import discord
import json
import asyncio

from discord.ext import commands, menus


async def get_prefix(client, message):
    with open("db_files/custom_prefix.json", "r") as f:
        l = json.load(f)

    return l[str(message.guild.id)]


class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Test(bot))
