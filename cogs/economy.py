import discord
import random
import math
from discord.ext.commands.cooldowns import BucketType
from discord.ext import commands, menus

# Constants
SUCCESSFUL_COLOUR = 0x2be31e
UNSUCCESSFUL_COLOUR = 0xed2b15
SUCCESS = "<:greenTick:596576670815879169>"
UNSUCCESS = "<:redTick:596576672149667840>"


class HelpSource(menus.ListPageSource):

    async def format_page(self, menu, page):
        url = "https://patreon.com/user?0=u&1=%3D&2=3&3=4&4=6&5=2&6=8&7=9&8=3&9=7&utm_medium=social&utm_source=twitter&utm_campaign=creatorshare"
        if isinstance(page, str):
            embed = discord.Embed(
                title='Server Leaderboard',
                description=f"[Join our support server](https://discord.gg/YUm2sBD) | [Support us on Patreon!]({url})" + ''.join(page),
                color=0xED791D
            )
            return embed
        else:

            embed = discord.Embed(
                title='Server Leaderboard',
                description=f"[Join our support server](https://discord.gg/YUm2sBD) | [Support us on Patreon!]({url})" + '\n'.join(page),
                color=0xED791D
            )
            return embed



async def get_prefix(bot, message):
    res = await bot.pool.fetchrow("""SELECT prefix
                                     FROM db
                                     WHERE guild_id = $1""",
                                  message.guild.id
                                  )
    if res is None:
        prefix = '+-'

    if res is not None:
        prefix = res.get("prefix")

    return prefix


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    """
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandOnCooldown):
            embed = discord.Embed(
                title="An Unexpected error occurred!",
                colour=discord.Colour.from_rgb(255, 25, 15)
            )
            ret_aft = math.ceil(error.retry_after)
            embed.add_field(
                name="Error Message",
                value=f"```tex\n$\nYou are on cooldown! Try again in {ret_aft}\n$\n```",
                inline=True
            )
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                title="An Unexpected error occurred!",
                colour=discord.Colour.from_rgb(255, 25, 15)
            )
            embed.add_field(
                name="Error Message",
                value=f"```tex\n$\n{error.original}\n$\n```",
                inline=True
            )
            embed.add_field(
                name="info",
                value="```tex\n$\nIf this occurs again, please join the support server and report this bug\n$\n```",
                inline=True
            )
            embed.add_field(
                name="Support Server",
                value="https://discord.gg/jfwXdCZ",
                inline=False
            )
            await ctx.send(embed=embed)
"""
    @commands.command()
    @commands.cooldown(1, 3600, BucketType.user)
    async def work(self, ctx):
            money = random.randint(100, 300)
            res = await self.bot.pool.fetchrow("""SELECT wit, dep, amount
                                                  FROM currency
                                                  WHERE guild_id = $1
                                                  AND user_id = $2""",
                                                  ctx.guild.id,
                                                  ctx.author.id
                                               )
            if res is None:
                await self.bot.pool.execute("""INSERT INTO currency (guild_id, user_id, dep, wit, amount)
                           VALUES ($1, $2, $3, $4, $5)
                        """, ctx.guild.id, ctx.author.id, 0, money, money)
            elif res is not None:
                wit = res.get('wit')
                dep = res.get('dep')
                wit += money
                amount = wit + dep
                await self.bot.pool.execute("""UPDATE currency
                           SET wit = $1, dep = $2, amount = $3
                           WHERE guild_id = $4
                           AND user_id = $5""", wit, dep, amount, ctx.guild.id, ctx.author.id)
            else:
                owner = self.bot.get_user(self.bot.owner_id)
                await ctx.send("Hmmm.. There seems to be an error. My owner has been notified.")
                await owner.send("There's an error with the `work` command. Probably a database error btw..")
                return

            embed = discord.Embed(
                description=f"{SUCCESS} Your hard work pays off! You earned ${money}",
                colour=SUCCESSFUL_COLOUR
            )

            await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3600, BucketType.user)
    async def slut(self, ctx):
        money = random.randint(100, 300)
        res = await self.bot.pool.fetchrow("""SELECT wit, dep, amount
                                                          FROM currency
                                                          WHERE guild_id = $1
                                                          AND user_id = $2""",
                                           ctx.guild.id,
                                           ctx.author.id
                                           )
        if res is None:
            await self.bot.pool.execute("""INSERT INTO currency (guild_id, user_id, dep, wit, amount)
                                   VALUES ($1, $2, $3, $4, $5)
                                """, ctx.guild.id, ctx.author.id, 0, money, money)
        elif res is not None:
            wit = res.get('wit')
            dep = res.get('dep')
            wit += money
            amount = wit + dep
            await self.bot.pool.execute("""UPDATE currency
                                   SET wit = $1, dep = $2, amount = $3
                                   WHERE guild_id = $4
                                   AND user_id = $5""", wit, dep, amount, ctx.guild.id, ctx.author.id)
        else:
            owner = self.bot.get_user(self.bot.owner_id)
            await ctx.send("Hmmm.. There seems to be an error. My owner has been notified.")
            await owner.send("There's an error with the `slut` command. Probably a database error btw..")
            return

        embed = discord.Embed(
            description=f"{SUCCESS} You did what strippers do and earned ${money}!",
            colour=SUCCESSFUL_COLOUR
        )

        await ctx.send(embed=embed)

    @commands.command(aliases=["leaderboard"])
    async def top(self, ctx):
        res = await self.bot.pool.fetch("""SELECT user_id
                                              FROM currency
                                              WHERE guild_id = $1
                                              ORDER BY amount DESC
                                              LIMIT 10""",
                                           ctx.guild.id
                                           )
        res2 = await self.bot.pool.fetch("""SELECT amount
                                            FROM currency
                                            WHERE guild_id = $1
                                            ORDER BY amount DESC
                                            LIMIT 10""",
                                        ctx.guild.id
                                        )
        if res is None:
            await ctx.send("No one on this server has been ranked yet!")
            return

        if res is not None:
            fdescriptions = []
            for i in range(10):
                try:
                    res[i] = str(res[i]).strip("<Record user_id=>")
                    user = self.bot.get_user(int(res[i]))
                    res2[i] = str(res2[1]).strip("<Record amount=>")
                    amount = res2[i]
                    text = f"\n**{i + 1}.** {user} **{amount}**"
                    fdescriptions.append(text)
                except IndexError:
                    break

        source = HelpSource(fdescriptions, per_page=2)
        menu = menus.MenuPages(source)
        await menu.start(ctx)

    @commands.command()
    @commands.cooldown(1, 3600, BucketType.user)
    async def crime(self, ctx):
        get_pref = await get_prefix(self.bot, ctx)
        chance = random.choice(["yes", "yes", "yes", "yes", "yes", "no", "yes", "no", "yes", "no"])
        res = await self.bot.pool.fetchrow("""SELECT wit, dep, amount
                                              FROM currency
                                              WHERE guild_id = $1
                                              AND user_id = $2""",
                                     ctx.guild.id,
                                     ctx.author.id
                                     )
        if res is None:
            await ctx.send(
                f"Sorry, you do not have any money, in bank or on you! to get money, simply type `{get_pref}work` to start working!"
            )
            return
        if int(res.get('wit')) < 350:
            await ctx.send(f"You do not have at least 350 on you! `{get_pref}withdraw`some money from your bank.")
            return
        if chance == "yes":
            money = random.randint(100, 400)

            if res is not None:

                wit = res.get('wit') + money
                dep = res.get('dep')
                amount = wit + dep
                await self.bot.pool.execute("""UPDATE currency
                                               SET wit = $1, dep = $2, amount = $3
                                               WHERE guild_id = $4
                                               AND user_id = $5""",
                                            wit,
                                            dep,
                                            amount,
                                            ctx.guild.id,
                                            ctx.author.id
                                            )
            embed = discord.Embed(
                description=f"{SUCCESS} You successfully committed a crime and earned ${money}!",
                colour=SUCCESSFUL_COLOUR
            )

            await ctx.send(embed=embed)
            return

        if chance == "no":
            money = random.randint(100, 400)

            if res is not None:
                wit = res.get('wit') - money
                dep = res.get('dep')
                amount = wit + dep
                await self.bot.pool.execute("""UPDATE currency
                                               SET wit = $1, dep = $2, amount = $3
                                               WHERE guild_id = $4
                                               AND user_id = $5""",
                                            wit,
                                            dep,
                                            amount,
                                            ctx.guild.id,
                                            ctx.author.id
                                            )

            embed=discord.Embed(
                description=f"{UNSUCCESS} You were caught committing a crime and was charged ${money}!",
                colour=UNSUCCESSFUL_COLOUR
            )

            await ctx.send(embed=embed)
            return

    @commands.command()
    @commands.cooldown(1, 3600, BucketType.user)
    async def beg(self, ctx):
        chance = random.choice(["yes", "yes", "yes", "yes", "yes", "no", "yes", "no", "yes", "no"])
        res = await self.bot.pool.fetchrow("""SELECT wit, dep, amount
                                               FROM currency
                                               WHERE guild_id = $1
                                               AND user_id = $2""",
                                           ctx.guild.id,
                                           ctx.author.id
                                           )
        if chance == "yes":
            money = random.randint(1, 100)

            if res is not None:
                wit = res.get('wit') + money
                dep = res.get('dep')
                amount = wit + dep
                await self.bot.pool.execute("""UPDATE currency
                                               SET wit = $1, dep = $2, amount = $3
                                               WHERE guild_id = $4
                                               AND user_id = $5""",
                                            wit,
                                            dep,
                                            amount,
                                            ctx.guild.id,
                                            ctx.author.id
                                            )

            embed = discord.Embed(
                description=f"{SUCCESS} You successfully committed a crime and earned ${money}!",
                colour=SUCCESSFUL_COLOUR
            )

            await ctx.send(embed=embed)

            if res is None:
                await self.bot.pool.execute("""INSERT INTO currency guild_id, user_id, dep, wit, amount
                                                   VALUES ($1, $2, $3, $4 ,$5)
                                            """,
                                            ctx.guild.id,
                                            ctx.author.id,
                                            0,
                                            money,
                                            money
                                            )

            return

        if chance == "no":

            embed = discord.Embed(
                description=f"{UNSUCCESS} You begged on the streets for about 1 hour and was not given any money!",
                colour=UNSUCCESSFUL_COLOUR
            )

            await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3600, BucketType.user)
    async def rob(self, ctx, member: discord.Member):
        get_pref = await get_prefix(self.bot, ctx)
        if member.id == ctx.author.id:
            await ctx.send("Sorry, you cannot rob yourself!")
            return
        chance = random.choice(["yes", "yes", "yes", "yes", "yes", "no", "yes", "no", "yes", "no"])
        res = await self.bot.pool.fetchrow("""SELECT wit, dep, amount
                                              FROM currency
                                              WHERE guild_id = $1
                                              AND user_id = $2""",
                                           ctx.guild.id,
                                           ctx.author.id
                                           )
        if res is None:
            await ctx.send(
                f"Sorry, you do not have any money, in bank or on you! to get money, simply type `{get_pref[2]}work` to start working!"
            )
            return
        if res.get('wit') < 350:
            await ctx.send(
                f"You do not have at least 350 on you! `{get_pref[2]}withdraw`some money from your bank.")
            return
        if chance == "yes":
            money = random.randint(100, 400)

            if res is not None:
                wit = res.get('wit') + money
                dep = res.get('dep')
                amount = wit + dep
                await self.bot.pool.fetchrow("""UPDATE currency
                                                SET wit = $1, dep = $2, amount = $3
                                                WHERE guild_id = $4
                                                AND user_id = $5""",
                                             wit,
                                             dep,
                                             amount,
                                             ctx.guild.id,
                                             ctx.author.id
                                             )
                res = await self.bot.pool.fetchrow("""SELECT wit, dep, amount
                                                              FROM currency
                                                              WHERE guild_id = $1
                                                              AND user_id = $2""",
                                                   ctx.guild.id,
                                                   member.id
                                                   )

                wit = res.get('wit') - money
                dep = res.get('dep')
                amount = wit + dep
                await self.bot.pool.execute("""UPDATE currency
                                               SET wit = $1, dep = $2, amount = $3
                                               WHERE guild_id = $4
                                               AND user_id = $5""",
                                            wit,
                                            dep,
                                            amount,
                                            ctx.guild.id,
                                            member.id
                                            )
            embed = discord.Embed(
                description=f"{SUCCESS} You successfully robbed {member.mention} for ${money}!",
                colour=SUCCESSFUL_COLOUR
            )

            await ctx.send(embed=embed)
            return

        if chance == "no":
            money = random.randint(100, 400)

            if res is not None:

                wit = res.get('wit') - money
                dep = res.get('dep')
                amount = wit + dep
                await self.bot.pool.execute("""UPDATE currency
                                               SET wit = $1, dep = $2, amount = $3
                                               WHERE guild_id = $4
                                               AND user_id = $5""",
                                            wit,
                                            dep,
                                            amount,
                                            ctx.guild.id,
                                            ctx.author.id
                                            )
            embed = discord.Embed(
                description=f"{UNSUCCESS} You were caught robbing {member.mention} and was charged ${money}!",
                colour=UNSUCCESSFUL_COLOUR
            )

            await ctx.send(embed=embed)
            return

    @commands.command(hidden=True)
    @commands.is_owner()
    async def add(self, ctx, member: discord.Member, money: int):
        res = await self.bot.pool.fetchrow("""SELECT wit, dep, amount 
                                              FROM currency
                                              WHERE guild_id = $1
                                              AND user_id = $2""",
                                           ctx.guild.id,
                                           member.id
        )
        if res is not None:
            wit = res.get('wit') + money
            dep = res.get('dep')
            amount = wit + dep
            await self.bot.pool.execute("""UPDATE currency
                                           SET wit = $1, dep = $2, amount = $3
                                           WHERE guild_id = $4
                                           AND user_id = $5""",
                                        wit,
                                        dep,
                                        amount,
                                        ctx.guild.id,
                                        member.id
                                        )
            await ctx.send(f"{member.mention}'s balance has been increased by {money}")
            return

        if res is None:
            dep = res.get('dep')
            await self.bot.pool.execute("""INSERT INTO currency (guild_id, user_id, dep, wit, amount)
                                     VALUES ($1, $2, $3, $4, $5)""",
                                  ctx.guild.id,
                                  member.id,
                                  dep,
                                  money,
                                  money
                                  )
            return

    @commands.command(hidden=True, aliases=["rmv"])
    @commands.is_owner()
    async def _remove(self, ctx, member: discord.Member, money: int):
        res = await self.bot.pool.fetchrow("""SELECT wit, dep, amount 
                                                      FROM currency
                                                      WHERE guild_id = $1
                                                      AND user_id = $2""",
                                           ctx.guild.id,
                                           member.id
                                           )
        if res is not None:
            wit = res.get('wit') - money
            dep = res.get('dep')
            amount = wit + dep
            await self.bot.pool.execute("""UPDATE currency
                                                   SET wit = $1, dep = $2, amount = $3
                                                   WHERE guild_id = $4
                                                   AND user_id = $5""",
                                        wit,
                                        dep,
                                        amount,
                                        ctx.guild.id,
                                        member.id
                                        )
            await ctx.send(f"{member.mention}'s balance has been decreased by {money}")
            return

        if res is None:
            dep = res.get('dep')
            await self.bot.pool.execute("""INSERT INTO currency (guild_id, user_id, dep, wit, amount)
                                             VALUES ($1, $2, $3, $4, $5)""",
                                        ctx.guild.id,
                                        member.id,
                                        dep,
                                        money,
                                        money
                                        )
            return

    @commands.command(aliases=["bal"])
    async def balance(self, ctx):
        get_pref = await get_prefix(self.bot, ctx)
        res = await self.bot.pool.fetchrow("""SELECT wit, dep, amount
                                              FROM currency 
                                              WHERE guild_id = $1
                                              AND user_id = $2""",
                                           ctx.guild.id,
                                           ctx.author.id
                                           )
        if res is None:
            await ctx.send(
                f"Sorry, you do not have any money, in bank or on you! to get money, simply type `{get_pref[2]}work` to start working!"
            )
            return

        embed = discord.Embed(
            title="Balance",
            colour=0x0EF7E2
        )
        embed.add_field(
            name="In bank:",
            value=f"`{res.get('dep')}`",
            inline=False
        )
        embed.add_field(
            name="On you:",
            value=f"`{res.get('wit')}`",
            inline=False
        )
        embed.add_field(
            name="Total:",
            value=f"`{res.get('amount')}`",
            inline=False
        )
        embed.set_footer(
            text="Join our support server! `https://discord.gg/YUm2sBD`",
            icon_url=self.bot.user.avatar_url_as(static_format="png")
        )

        await ctx.send(embed=embed)
        return

    @commands.command(aliases=["with"])
    async def withdraw(self, ctx, amount):
        get_pref = await get_prefix(self.bot, ctx)
        if amount == "":
            await ctx.send("Please specify an amount to withdraw!")
            return
        res = await self.bot.pool.fetchrow("""SELECT wit, dep, amount
                                              FROM currency
                                              WHERE guild_id = $1
                                              AND user_id = $2""",
                                           ctx.guild.id,
                                           ctx.author.id
                                           )
        if res is None:
            await ctx.send(
                f"Sorry, you do not have any money, in bank or on you! to get money, simply type `{get_pref[2]}work` to start working!"
            )
            return
        if res is not None:
            if amount == "all":
                wit = res.get('wit')
                wit += res.get('dep')
                tot = wit
                await self.bot.pool.execute("""UPDATE currency
                                               SET wit = $1, dep = $2, amount = $3
                                               WHERE guild_id = $4
                                               AND user_id = $5""",
                                            wit,
                                            0,
                                            tot,
                                            ctx.guild.id,
                                            ctx.author.id
                                            )
            else:
                if res.get('dep') - int(amount) < 0:
                    await ctx.send("Sorry, you cannot withdraw more than your bank balance!")
                    return
                wit = res.get('wit') + int(amount)
                dep = res.get('dep') - int(amount)
                tot = dep + wit
                await self.bot.pool.execute("""UPDATE currency
                                               SET wit = $1, dep = $2, amount = $3
                                               WHERE guild_id = $4
                                               AND user_id = $5""",
                                            wit,
                                            dep,
                                            tot,
                                            ctx.guild.id,
                                            ctx.author.id
                                            )

        res = await self.bot.pool.fetchrow("""SELECT wit, dep
                                              FROM currency
                                              WHERE guild_id = $1
                                              AND user_id = $2""",
                                           ctx.guild.id,
                                           ctx.author.id
                                           )

        embed = discord.Embed(
            title="Balance",
            colour=0x0EF7E2
        )
        embed.add_field(
            name="In bank:",
            value=f"`{res.get('dep')}`",
            inline=False
        )
        embed.add_field(
            name="On you:",
            value=f"`{res.get('wit')}`",
            inline=False
        )
        embed.add_field(
            name="Total:",
            value=f"`{res.get('dep') + res.get('wit')}`",
            inline=False
        )

        await ctx.send(embed=embed)
        return

    @commands.command(aliases=["dep"])
    async def deposit(self, ctx, amount):
        get_pref = await get_prefix(self.bot, ctx)
        if amount == "":
            await ctx.send("Please specify an amount to deposit!")
            return
        res = await self.bot.pool.fetchrow("""SELECT wit, dep, amount
                                              FROM currency
                                              WHERE guild_id = $1
                                              AND user_id = $2""",
                                           ctx.guild.id,
                                           ctx.author.id
                                           )
        if res is None:
            await ctx.send(
                f"Sorry, you do not have any money, in bank or on you! to get money, simply type `{get_pref[2]}work` to start working!"
            )
            return
        if res is not None:
            if amount == "all":
                dep = res.get('dep')
                dep += res.get('wit')
                tot = dep
                await self.bot.pool.execute("""UPDATE currency
                                               SET wit = $1, dep = $2, amount = $3
                                               WHERE guild_id = $4
                                               AND user_id = $5""",
                                            0,
                                            dep,
                                            tot,
                                            ctx.guild.id,
                                            ctx.author.id
                                            )
            else:
                if res.get('wit') - int(amount) < 0:
                    await ctx.send("sorry, you don't have that much money on you!")
                    return
                wit = res.get('wit') - int(amount)
                dep = res.get('dep') + int(amount)
                tot = dep + wit
                await self.bot.pool.execute("""UPDATE currency
                                               SET wit = $1, dep = $2, amount = $3
                                               WHERE guild_id = $4
                                               AND user_id = $5""",
                                            wit,
                                            dep,
                                            tot,
                                            ctx.guild.id,
                                            ctx.author.id
                                            )

        res = await self.bot.pool.fetchrow("""SELECT wit, dep
                                              FROM currency
                                              WHERE guild_id = $1
                                              AND user_id = $2""",
                                           ctx.guild.id,
                                           ctx.author.id
                                           )

        embed = discord.Embed(
            title="Balance",
            colour=0x0EF7E2
        )
        embed.add_field(
            name="In bank:",
            value=f"`{res.get('dep')}`",
            inline=False
        )
        embed.add_field(
            name="On you:",
            value=f"`{res.get('wit')}`",
            inline=False
        )
        embed.add_field(
            name="Total:",
            value=f"`{res.get('dep') + res.get('wit')}`",
            inline=False
        )

        await ctx.send(embed=embed)
        return

    @commands.command()
    async def give(self, ctx, member: discord.Member = None, amount: int = None):
        get_pref = await get_prefix(self.bot, ctx)
        if member is None:
            await ctx.send("Please specify a person to give money to!")
        if amount is None:
            await ctx.send("Please specify an amount to give!")

        res = await self.bot.pool.fetchrow("""SELECT wit, dep, amount
                                              FROM currency
                                              WHERE guild_id = $1
                                              AND user_id = $2""",
                                           ctx.guild.id,
                                           ctx.author.id
                                           )
        if res is None:
            await ctx.send(
                f"Sorry, you do not have any money, in bank or on you! to get money, simply type `{get_pref[2]}work` to start working!"
            )
            return
        if res is not None:
            if res[0] < int(amount):
                await ctx.send(
                    f"Sorry, you do not have enough money on you! simply type in `{get_pref[2]}withdraw {int(amount)}`"
                )
                return

            wit = res.get('wit') - int(amount)
            dep = res.get('dep')
            tot = res.get('amount')
            await self.bot.pool.execute("""UPDATE currency
                                           SET wit = $1, dep = $2, amount = $3
                                           WHERE guild_id = $4
                                           AND user_id = $5""",
                                        wit,
                                        dep,
                                        tot,
                                        ctx.guild.id,
                                        ctx.author.id
                                        )
        res = await self.bot.pool.fetchrow("""SELECT wit, dep, amount
                                              FROM currency
                                              WHERE guild_id = $1
                                              AND user_id = $2""",
                                           ctx.guild.id,
                                           member.id
                                           )
        if res is None:
            await ctx.send(
                f"Sorry, you do not have any money, in bank or on you! to get money, simply type `{get_pref[2]}work` to start working!"
            )
            return
        if res is not None:

            wit = res.get('wit') + int(amount)
            dep = res.get('dep')
            tot = res.get('amount')
            await self.bot.pool.execute("""UPDATE currency
                                           SET wit = $1, dep = $2, amount = $3
                                           WHERE guild_id = $4
                                           AND user_id = $5""",
                                        wit,
                                        dep,
                                        tot,
                                        ctx.guild.id,
                                        member.id
                                        )

        await ctx.send(f"You gave {member.mention} {amount}!")
        return

    @commands.group()
    async def shop(self, ctx, item: str = None):
        if item is None:
            embed = discord.Embed(
                title="Shop",
                description="Food",
                colour=0x0EF7E2
            )
            embed.add_field(
                name="Food",
                value="Pizza ($10) `::` Burger ($15) `::` Taco ($5)",
                inline=False
            )
            embed.add_field(
                name="Drinks",
                value="Coke ($3) `::` Sprite ($3) `::` Monster ($5)",
                inline=True
            )
            embed.set_footer(
                text="Join our support server! https://discord.gg/YUm2sBD",
                icon_url=self.bot.user.avatar_url_as(static_format="png")
            )
            await ctx.send(embed=embed)

    @shop.command()
    async def buy(self, ctx, item: str = None):
        get_pref = await get_prefix(self.bot, ctx)
        items = {
            "Pizza": 10,
            "Burger": 15,
            "Taco": 5,
            "Coke": 5,
            "Sprite": 5,
            "Monster": 8,
            "pizza": 10,
            "burger": 15,
            "taco": 5,
            "coke": 5,
            "sprite": 5,
            "monster": 8
        }

        for thing in items:
            if thing == item:
                res = await self.bot.pool.fetchrow("""SELECT wit, dep, amount
                                                   FROM currency
                                                   WHERE guild_id = $1
                                                   AND user_id = $2""",
                                                ctx.guild.id,
                                                ctx.author.id
                                                )
                if res is None:
                    await ctx.send(
                        f"Sorry, you do not have any money, in bank or on you! to get money, simply type `{get_pref[2]}work` to start working!"
                    )
                    return
                if res is not None:
                    if res.get("wit") < items[thing]:
                        await ctx.send(
                            f"Sorry, you do not have enough money on you! simply type in `{get_pref[2]}withdraw {items[thing]}`"
                        )
                    wit = res.get('wit') - items[thing]
                    dep = res.get('dep')
                    amount = res.get('amount')
                    await self.bot.pool.execute("""UPDATE currency
                                                   SET wit = $1, dep = $2, amount = $3
                                                   WHERE guild_id = $4
                                                   AND user_id = $5""",
                                                wit,
                                                dep,
                                                amount,
                                                ctx.guild.id,
                                                ctx.author.id)
                await ctx.send(f"Successfully bought {item}! delicious!")
        return


def setup(bot):
    bot.add_cog(Economy(bot))
