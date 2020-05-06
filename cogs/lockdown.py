import discord
from discord.ext import commands


class Lockdown(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def lockdown(self, ctx, ete, *args):
        msg = ' '.join(args)
        staff_role = discord.utils.get(ctx.guild.roles, name="staff")
        for channel in ctx.guild.channels:
            await channel.set_permissions(ctx.guild.default_role, send_messages=False)

        embed = discord.Embed(
            title="SERVER HAS BEEN LOCKED",
            description=f"The server has been locked by {ctx.author.mention}.",
            colour=discord.Colour.from_rgb(255, 15, 15)
        )
        embed.add_field(
            name=f"{ctx.author.mention}:",
            value=f"The server has been locked. reason: {msg}",
            inline=True
        )
        embed.add_field(
            name="Estimated time of lockdown lift:",
            value=ete,
            inline=True
        )
        embed.add_field(
            name="If there is any problem, please contact the following:",
            value=f"{ctx.author.mention}\n {staff_role.mention}",
            inline=True
        )

        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unlock(self, ctx):
        staff_role = discord.utils.get(ctx.guild.roles, name="staff")
        for channel in ctx.guild.channels:
            await channel.set_permissions(ctx.guild.default_role, send_messages=True)

        await ctx.send(f"{ctx.guild.default_role} **SERVER LOCKDOWN HAS BEEN LIFTED!**")


def setup(bot):
    bot.add_cog(Lockdown(bot))
