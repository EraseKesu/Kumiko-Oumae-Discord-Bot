import discord
import json

from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 336642139381301249:
            return

        res = await self.bot.pool.fetchrow("""SELECT auto_role, welcome_channel
                                              FROM db
                                              WHERE guild_id = $1""",
                                           member.guild.id
                                           )
        role = discord.utils.get(member.guild.roles, name=res.get('auto_role'))
        channel = discord.utils.get(member.guild.channels, name=res.get('welcome_channel'))
        embed = discord.Embed(
            title="Member has joined the server!",
            description=f"{member.mention} has joined the server! Make sure to read the rules and have a nice stay!",
            colour=0x0EF7E2
        )
        embed.add_field(
            name="Total members:",
            value=member.guild.member_count,
            inline=False
        )
        await channel.send(embed=embed)
        await member.add_roles(role)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        with open("db_files/prime.json", "r") as f:
            l = json.load(f)

        try:
            print(l[str(guild.id)])
        except KeyError:
            await guild.leave()

        await self.bot.pool.execute(f"""INSERT INTO db(guild_id, prefix, auto_role, welcome_channel)
                                        VALUES ($1, $2, $3, $4)""",
                                    guild.id,
                                    '+-',
                                    'null',
                                    'welcome'
                                    )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.bot.pool.execute("""DELETE FROM db
                                        WHERE guild_id = $1""",
                                    guild.id
                                    )
        await self.bot.pool.execute("""DELETE FROM currency
                                        WHERE guild_id = $1""",
                                    guild.id
                                    )
        await self.bot.pool.execute("""DELETE FROM warns
                                        WHERE guild_id = $1""",
                                    guild.id
                                    )
        await self.bot.pool.execute("""DELETE FROM levels
                                       WHERE guild_id = $1""",
                                    guild.id
                                    )


def setup(bot):
    bot.add_cog(Events(bot))
