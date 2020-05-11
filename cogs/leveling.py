import discord
import json
from utils import checks
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType


class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    @commands.cooldown(1, 10, BucketType.user)
    async def on_message(self, message):
        with open("db_files/enable.json", "r") as f:
            l = json.load(f)
        try:
            if l[str(message.guild.id)] == 0:
                return
        except KeyError:
            l[str(message.guild.id)] = 0
            return
        else:
            if message.author.id == self.bot.user.id:
                return
            expt = 2
            res = await self.bot.pool.fetchrow("""SELECT exp, lvl
                                                  FROM levels
                                                  WHERE guild_id = $1
                                                  AND user_id = $2""",
                                               message.guild.id,
                                               message.author.id
                                              )
            if res is None:
                await self.bot.pool.execute("""INSERT INTO levels (guild_id, user_id, exp, lvl)
                                               VALUES ($1, $2, $3, $4)""",
                                            message.guild.id,
                                            message.author.id,
                                            expt,
                                            0
                                           )
                return
            if res is not None:
                exp = res.get('exp')
                level = res.get('lvl')
                exp += expt
                amount_to_next = round(4 * (level ** 5) / 5)
                if exp >= amount_to_next:
                    exp = 0
                    level += 1
                    await self.bot.pool.execute("""UPDATE levels
                                                   SET exp = $1, lvl = $2
                                                   WHERE guild_id = $3
                                                   AND user_id = $4""",
                                                exp,
                                                level,
                                                message.guild.id,
                                                message.author.id
                                                )
                    await message.channel.send(f"Level Up! **{message.author}** has leveled up to **level {level}**!")
                else:
                    await self.bot.pool.execute("""UPDATE levels
                                                   SET exp = $1
                                                   WHERE guild_id = $2
                                                   AND user_id = $3""",
                                                exp,
                                                message.guild.id,
                                                message.author.id
                                                )

    @commands.command()
    async def rank(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        res = await self.bot.pool.fetchrow("""SELECT exp, lvl
                                                      FROM levels
                                                      WHERE guild_id = $1
                                                      AND user_id = $2""",
                                           ctx.guild.id,
                                           member.id
                                           )
        if res is None:
            await ctx.send("This user has not been ranked yet!")
            return

        if res is not None:
            level = res.get('lvl')
            exp = res.get("exp")
            amount_to_next = round(10 * (level ** 3))
            embed = discord.Embed(
                title=f"Rank for {member}",
                colour=0xED791D
            )
            embed.add_field(
                name="Level",
                value=level,
                inline=True
            )
            embed.add_field(
                name="Exp",
                value=f"{exp} / {amount_to_next}",
                inline=True
            )
            embed.set_footer(
                text="Join our support server! https://discord.gg/YUm2sBD",
                icon_url=self.bot.user.avatar_url_as(static_format="png")
            )
            await ctx.send(embed=embed)

    @commands.command()
    @checks.is_mod()
    async def enable(self, ctx):
        with open("db_files/enable.json", "r") as f:
            l = json.load(f)

            l[str(ctx.guild.id)] = 1

            with open("db_files/enable.json", "w") as f:
                json.dump(l, f, indent=4)

        await ctx.send("Successfully opted in the Leveling System")

    @commands.command()
    @checks.is_mod()
    async def disable(self, ctx):
        with open("db_files/enable.json", "r") as f:
            l = json.load(f)

            l[str(ctx.guild.id)] = 0

            with open("db_files/enable.json", "w") as f:
                json.dump(l, f, indent=4)

        await ctx.send("Successfully opted out of the Leveling System!")


def setup(bot):
    bot.add_cog(Leveling(bot))
