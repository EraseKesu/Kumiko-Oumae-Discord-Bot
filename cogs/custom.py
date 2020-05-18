import discord
import json
from discord.ext import commands


class Custom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["ar", "joinrole"])
    @commands.has_permissions(administrator=True)
    async def autorole(self, ctx, rn: str):
        with open("db_files/prime.json", "r") as f:
            l = json.load(f)

        try:
            print(l[str(ctx.guild.id)])
        except KeyError:
            await ctx.send("Sorry, this a **prime only** command!")
            return

        await self.bot.poo.l.execute(f"""UPDATE db
                                         SET auto_role = $1
                                         WHERE guild_id = $2""",
                                     rn,
                                     ctx.guild.id
                                     )
        reminder = "Remember, if you don't already have one, for this to work the server must have a 'welcome' channel."

        await ctx.send(f"Ok, When a member joins the server, i will give them the {rn} role. {reminder}")

    @commands.command(aliases=["cp", "changep"])
    async def changeprefix(self, ctx, prefix: str):
        with open("db_files/prime.json", "r") as f:
            l = json.load(f)

        try:
            print(l[str(ctx.guild.id)])
        except KeyError:
            await ctx.send("Sorry, this a **prime only** command!")
            return

        await self.bot.pool.execute("""UPDATE db
                                       SET prefix = $1
                                       WHERE guild_id = $2""",
                                    prefix,
                                    ctx.guild.id
                                    )
        await ctx.send(f"Ok, The server prefix has been set to {prefix}.")

    @commands.command(aliases=["set_welcome", "wc", "setw", "sw"])
    async def welcome_channel(self, ctx, channel: discord.TextChannel = None):
        with open("db_files/prime.json", "r") as f:
            l = json.load(f)

        try:
            print(l[str(ctx.guild.id)])
        except KeyError:
            await ctx.send("Sorry, this a **prime only** command!")
            return

        if channel is None:
            await ctx.send("Please specify a channel!")
            return

        channel = str(channel).strip("<#>")

        res = await self.bot.pool.fetchrow("""SELECT welcome_channel
                                              FROM db
                                              WHERE guild_id = $1""",
                                           ctx.guild.id
                                           )
        if res is None:
            await self.bot.pool.execute("""INSERT INTO db(welcome_channel)
                                           VALUES ($1)
                                           WHERE guild_id = $2""",
                                        channel,
                                        ctx.guild.id
                                        )

            return
        if res is not None:
            await self.bot.pool.execute("""UPDATE db
                                           SET welcome_channel = $1
                                           WHERE guild_id = $2""",
                                        channel,
                                        ctx.guild.id
                                        )
            await ctx.send(f"Done! I will now send a message in {channel} whenever a member joins!")
            return


def setup(bot):
    bot.add_cog(Custom(bot))
