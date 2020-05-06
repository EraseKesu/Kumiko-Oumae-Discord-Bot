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
    # TODO: make a botvar to access a json file that contains user ids and their set language.

    @commands.command(aliases=["setlang", "sl"])
    async def setlanguage(self, ctx, language: str = None):
        if language not in googletrans.LANGUAGES or googletrans.LANGCODES:
            await ctx.send(f"```bf\n{googletrans.LANGUAGES}\n```\n```bf\n{googletrans.LANGCODES}\n```")
            return
        else:
            with open("db_files/languages.json", "r") as f:
                l = json.load(f)

            l[str(ctx.author.id)] = language

            with open("db_files/languages.json", "w") as f:
                json.dump(l, f, indent=4)
            try:
                await ctx.trans(
                    f"Ok,{ctx.author.mention}, from now on i will talk to you in {language}",
                    language
                )
            except ValueError:
                await ctx.send("Invalid destination lang!")


def setup(bot):
    bot.add_cog(Custom(bot))
