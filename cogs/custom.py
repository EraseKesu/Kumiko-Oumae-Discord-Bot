import discord
from discord.ext import commands


class Custom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["ar", "joinrole"])
    @commands.has_permissions(administrator=True)
    async def autorole(self, ctx, rn: str):
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
        await self.bot.pool.execute("""UPDATE db
                                       SET prefix = $1
                                       WHERE guild_id = $2""",
                                    prefix,
                                    ctx.guild.id
                                    )
        await ctx.send(f"Ok, The server prefix has been set to {prefix}.")

    @commands.command(aliases=["set_welcome", "wc", "setw", "sw"])
    async def welcome_channel(self, ctx, channel: discord.TextChannel):
        res = await self.bot.pool.fetchrow("""SELECT welcome_channel
                                              FROM db
                                              WHERE guild_id = $1""",
                                           ctx.guild.id
                                           )


def setup(bot):
    bot.add_cog(Custom(bot))
