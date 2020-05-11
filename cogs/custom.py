import discord
import json
import asyncpg
from discord.ext import commands
import googletrans

class Custom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["ar", "joinrole"])
    @commands.has_permissions(administrator=True)
    async def autorole(self, ctx, rn: str):
        conn = await asyncpg.connect('postgresql://postgres@localhost/postgres')
        query = f"""
        UPDATE db
        SET auto_role = ?
        WHERE guild_id = ?
        """
        val = (rn, ctx.guild.id)
        await conn.execute(query, val)

        await ctx.send(f"Done! Now when a member joins, they will get the {rn} role!")
        await conn.close()

    @commands.command(aliases=["cp", "changep"])
    async def changeprefix(self, ctx, prefix: str):
        with open("db_files/custom_prefix.json", "r") as f:
            l = json.load(f)

        l[str(ctx.guild.id)] = prefix

        with open("db_files/custom_prefix.json", "w") as f:
            json.dump(l, f, indent=4)

        await ctx.send(f"Server prefix is now {prefix}!")


def setup(bot):
    bot.add_cog(Custom(bot))
