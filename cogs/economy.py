import discord
import random
import json
import math
from discord.ext.commands.cooldowns import BucketType
from discord.ext import commands

# Constants
SUCCESSFUL_COLOUR = 0x2be31e
UNSUCCESSFUL_COLOUR = 0xed2b15
SUCCESS = "<:greenTick:596576670815879169>"
UNSUCCESS = "<:redTick:596576672149667840>"


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandOnCooldown):
            embed = discord.Embed(
                title="An Unexpected error occurred!",
                colour=discord.Colour.from_rgb(255, 25, 15)
            )
            ret_aft = math.ceil(error.retry_after)
            embed.add_field(
                name="Error Message",
                value=f"```tex\n$\nYou are on cooldown! Try again in {error.retry_after}\n$\n```",
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

    def get_prefix(self, message):
        with open("db_files/custom_prefix.json", "r") as f:
            l = json.load(f)

        try:
            prefix = l[str(message.guild.id)]
        except KeyError:
            l[str(message.guild.id)] = '+-'
            prefix = l[str(message.guild.id)]

        return prefix

    @commands.group(invoke_without_command=True)
    @commands.cooldown(1, 3600, BucketType.user)
    async def work(self, ctx):
            money = random.randint(100, 300)
            qry = self.bot.cursor.execute(f"SELECT wit, dep, amount FROM currency WHERE guild_id = {ctx.guild.id} AND user_id = {ctx.author.id};")
            res = list(qry.fetchone())
            if res is None:
                query = """INSERT INTO currency (guild_id, user_id, dep, wit, amount)
    VALUES (?, ?, ?, ?, ?)
                """
                val = (
                    ctx.guild.id,
                    ctx.author.id,
                    0,
                    money,
                    money
                )
            elif res is not None:
                query = """UPDATE currency SET wit = ?, dep = ?, amount = ? WHERE guild_id = ? AND user_id = ?"""
                res[0] += money
                res[2] = res[0] + res[1]
                val = (
                    res[0],
                    res[1],
                    res[2],
                    ctx.guild.id,
                    ctx.author.id
                )
            else:
                owner = self.bot.get_user(self.bot.owner_id)
                await ctx.send("Hmmm.. There seems to be an error. My owner has been notified.")
                await owner.send("There's an error with the `work` command. Probably a database error btw..")
                return

            self.bot.db.execute(query, val)
            self.bot.db.commit()

            embed = discord.Embed(
                description=f"{SUCCESS} Your hard work pays off! You earned ${money}",
                colour=SUCCESSFUL_COLOUR
            )

            await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3600, BucketType.user)
    async def slut(self, ctx):
        money = random.randint(100, 400)
        qry = self.bot.cursor.execute(f"SELECT (wit, dep, amount) FROM currency WHERE guild_id = {ctx.guild.id} AND user_id = {ctx.author.id}")
        res = list(qry.fetchone())
        if res is None:
            query = """INSERT INTO currency (guild_id, user_id, dep, wit, amount)
        VALUES (?, ?, ?, ?, ?)
                    """
            val = (
                ctx.guild.id,
                ctx.author.id,
                0,
                money,
                money
            )
            embed = discord.Embed(
                description=f"{SUCCESS} You did some inappropriate things with your body and earned ${money}!",
                colour=SUCCESSFUL_COLOUR
            )

            await ctx.send(embed=embed)

        elif res is not None:
            query = """UPDATE currency SET (wit = ?, dep = ?, amount = ?) WHERE guild_id = ? AND user_id = ?"""
            res[0] += money
            res[2] = res[0] + res[1]
            val = (
                res[0],
                res[1],
                res[2],
                ctx.guild.id,
                ctx.author.id
            )
            embed = discord.Embed(
                description=f"{SUCCESS} You did some inappropriate things with your body and earned ${money}!",
                colour=SUCCESSFUL_COLOUR
            )

            await ctx.send(embed=embed)

        else:
            owner = self.bot.get_user(self.bot.owner_id)
            await ctx.send("Hmmm.. There seems to be an error. My owner has been notified.")
            await owner.send("There's an error with the `slut` command. Probably a database error btw..")
            return

        self.bot.db.execute(query, val)
        self.bot.db.commit()

    @commands.command(aliases=["leaderboard"])
    async def top(self, ctx):
        x = 0
        qry = self.bot.cursor.execute(f"""SELECT amount FROM currency WHERE guild_id = {ctx.guild.id} AND user_id = {ctx.author.id}""")
        res = list(qry.fetchone())
        lb = sorted(res, key=lambda x: res, reverse=True)
        res = ""

        counter = 0

        for a in lb:

            counter += 1

            if counter > 10:

                pass

            else:
                res1 = self.bot.cursor.execute(f"SELECT user_id FROM currency WHERE guild_id = {ctx.guild.id}")
                u = self.bot.get_user(res1[x])
                res += f"\n**{counter}.** `{u}` - **{res[0]} $**"
                x += 1
                if x == len(res1):
                    break

        embed = discord.Embed(
            description=res,
            colour=0x0EF7E2
        )
        embed.set_footer(
            text="Join our support server! https://discord.gg/YUm2sBD",
            icon_url=self.bot.user.avatar_url_as(static_format="png")
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3600, BucketType.user)
    async def crime(self, ctx):
        chance = random.choice(["yes", "yes", "yes", "yes", "yes", "no", "yes", "no", "yes", "no"])
        qry = self.bot.cursor.execute(
            f"SELECT wit, dep, amount FROM currency WHERE guild_id = {ctx.guild.id} AND user_id = {ctx.author.id}")
        res = list(qry.fetchone())
        if res is None:
            await ctx.send(
                f"Sorry, you do not have any money, in bank or on you! to get money, simply type `{self.get_prefix(ctx)}work` to start working!"
            )
            return
        if int(res[0]) < 350:
            await ctx.send(f"You do not have at least 350 on you! `{self.get_prefix(ctx)}withdraw`some money from your bank.")
            return
        if chance == "yes":
            money = random.randint(100, 400)

            if res is not None:
                q = "UPDATE currency SET wit = ?, dep = ?, amount = ? WHERE guild_id = ? AND user_id = ?"
                wit = res[0] + money
                dep = res[1]
                amount = wit + dep
                val = (
                    wit,
                    dep,
                    amount,
                    ctx.guild.id,
                    ctx.author.id
                )
                self.bot.db.execute(q, val)
                self.bot.db.commit()

            embed = discord.Embed(
                description=f"{SUCCESS} You successfully committed a crime and earned ${money}!",
                colour=SUCCESSFUL_COLOUR
            )

            await ctx.send(embed=embed)
            return

        if chance == "no":
            money = random.randint(100, 400)

            if res is not None:
                q = "UPDATE currency SET wit = ?, dep = ?, amount = ? WHERE guild_id = ? AND user_id = ?"
                wit = res[0] - money
                dep = res[1]
                amount = wit + dep
                val = (
                    wit,
                    dep,
                    amount,
                    ctx.guild.id,
                    ctx.author.id
                )
                self.bot.db.execute(q, val)
                self.bot.db.commit()

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
        qry = self.bot.cursor.execute(
            f"SELECT wit, dep, amount FROM currency WHERE guild_id = {ctx.guild.id} AND user_id = {ctx.author.id}")
        res = list(qry.fetchone())
        if chance == "yes":
            money = random.randint(1, 100)

            if res is not None:
                q = "UPDATE currency SET wit = ?, dep = ?, amount = ? WHERE guild_id = ? AND user_id = ?"
                wit = res[0] + money
                dep = res[1]
                amount = wit + dep
                val = (
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
                    q = """INSERT INTO currency (guild_id, user_id, dep, wit, amount)
                VALUES (?, ?, ?, ?, ?)
                            """
                    val = (
                        ctx.guild.id,
                        ctx.author.id,
                        0,
                        money,
                        money
                    )

            self.bot.db.execute(q, val)
            self.bot.db.commit()
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
        chance = random.choice(["yes", "yes", "yes", "yes", "yes", "no", "yes", "no", "yes", "no"])
        qry = self.bot.cursor.execute(
            f"SELECT wit, dep, amount FROM currency WHERE guild_id = {ctx.guild.id} AND user_id = {ctx.author.id}")
        res = qry.fetchone
        if res is None:
            await ctx.send(
                f"Sorry, you do not have any money, in bank or on you! to get money, simply type `{self.get_prefix(ctx)}work` to start working!"
            )
            return
        if int(res[0]) < 350:
            await ctx.send(
                f"You do not have at least 350 on you! `{self.get_prefix(ctx)}withdraw`some money from your bank.")
            return
        if chance == "yes":
            money = random.randint(100, 400)

            if res is not None:
                q = "UPDATE currency SET wit = ?, dep = ?, amount = ? WHERE guild_id = ? AND user_id = ?"
                wit = res[0] + money
                dep = res[1]
                amount = wit + dep
                val = (
                    wit,
                    dep,
                    amount,
                    ctx.guild.id,
                    ctx.author.id
                )
                self.bot.db.execute(q, val)
                self.bot.db.commit()
                q = "UPDATE currency SET wit = ?, dep = ?, amount = ? WHERE guild_id = ? AND user_id = ?"
                wit = res[0] - money
                dep = res[1]
                amount = wit + dep
                val = (
                    wit,
                    dep,
                    amount,
                    ctx.guild.id,
                    member.id
                )
                self.bot.db.execute(q, val)
                self.bot.db.commit()

            embed = discord.Embed(
                description=f"{SUCCESS} You successfully robbed {member.mention} for ${money}!",
                colour=SUCCESSFUL_COLOUR
            )

            await ctx.send(embed=embed)
            return

        if chance == "no":
            money = random.randint(100, 400)

            if res is not None:
                q = "UPDATE currency SET wit = ?, dep = ?, amount = ? WHERE guild_id = ? AND user_id = ?"
                wit = res[0] - money
                dep = res[1]
                amount = wit + dep
                val = (
                    wit,
                    dep,
                    amount,
                    ctx.guild.id,
                    ctx.author.id
                )
                self.bot.db.execute(q, val)
                self.bot.db.commit()

            embed = discord.Embed(
                description=f"{UNSUCCESS} You were caught robbing {member.mention} and was charged ${money}!",
                colour=UNSUCCESSFUL_COLOUR
            )

            await ctx.send(embed=embed)
            return

    @commands.command(hidden=True)
    @commands.is_owner()
    async def add(self, ctx, member: discord.Member, amount: int):
        qry = self.bot.cursor.execute(
            f"SELECT wit, dep, amount FROM currency WHERE guild_id = {ctx.guild.id} AND user_id = {member.id}"
        )
        res = list(qry.fetchone())
        if res is not None:
            q = f"UPDATE currency SET wit = ?, dep = ?, amount = ? WHERE guild_id = ? AND user_id = ?"
            res[1] += amount
            res[2] = res[0] + res[1]
            val = (
                res[0],
                res[1],
                res[2],
                ctx.guild.id,
                member.id
            )
            self.bot.db.execute(q, val)
            self.bot.commit()
            await ctx.send(f"{member.mention}'s balance has been increased by {amount}")
            return

        if res is None:
            q = """INSERT INTO currency (guild_id, user_id, dep, wit, amount)
                            VALUES (?, ?, ?, ?, ?)
                                        """
            val = (
                ctx.guild.id,
                ctx.author.id,
                amount,
                0,
                amount
            )
            self.bot.db.execute(q, val)
            self.bot.db.commit()
            return

    @commands.command(hidden=True, aliases=["rmv"])
    @commands.is_owner()
    async def _remove(self, ctx, member: discord.Member, amount: int):
        qry = self.bot.cursor.execute(
            f"SELECT wit, dep, amount FROM currency WHERE guild_id = {ctx.guild.id} AND user_id = {member.id}"
        )
        res = list(qry.fetchone())
        if res is not None:
            q = f"UPDATE currency SET wit = ?, dep = ?, amount = ? WHERE guild_id = ? AND user_id = ?"
            res[1] -= amount
            res[2] = res[0] + res[1]
            val = (
                res[0],
                res[1],
                res[2],
                ctx.guild.id,
                member.id
            )
            self.bot.db.execute(q, val)
            self.bot.db.commit()
            return

        if res is None:
            await ctx.send("This user doesn't have an account!")

        await ctx.send(f"{member.mention}'s balance has been decreased by {amount}")
        return

    @commands.command(aliases=["bal"])
    async def balance(self, ctx):
        get_pref = self.get_prefix(self.bot, ctx)
        qry = self.bot.cursor.execute(
            f"SELECT wit, dep, amount FROM currency WHERE guild_id = {ctx.guild.id} AND user_id = {ctx.author.id}")
        res = qry.fetchone
        if res is None:
            await ctx.send(
                f"Sorry, you do not have any money, in bank or on you! to get money, simply type `{get_pref[1]}work` to start working!"
            )
            return

        embed = discord.Embed(
            title="Balance",
            colour=0x0EF7E2
        )
        embed.add_field(
            name="In bank:",
            value=f"`{res[1]}`",
            inline=False
        )
        embed.add_field(
            name="On you:",
            value=f"`{res[0]}`",
            inline=False
        )
        embed.add_field(
            name="Total:",
            value=f"`{res[2]}`",
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
        get_pref = self.get_prefix(self.bot, ctx)
        if amount == "":
            await ctx.send("Please specify an amount to withdraw!")
            return
        qry = self.bot.db.execute(
            f"SELECT wit, dep, amount FROM currency WHERE guild_id = {ctx.guild.id} AND user_id = {ctx.author.id}")
        res = list(qry.fetchone())
        if res is None:
            await ctx.send(
                f"Sorry, you do not have any money, in bank or on you! to get money, simply type `{get_pref[1]}work` to start working!"
            )
            return
        if res is not None:
            q = "UPDATE currency SET wit = ?, dep = ?, amount = ? WHERE guild_id = ? AND user_id = ?"
            if amount == "all":
                res[0] += res[1]
                res[1] = 0
                res[2] = res[0]
                val = (
                    res[0],
                    res[1],
                    res[1],
                    ctx.guild.id,
                    ctx.author.id
                )
                self.bot.db.execute(q, val)
                self.bot.db.commit()
            else:
                res[0] += int(amount)
                res[1] -= int(amount)
                res[2] = res[0] + res[1]
                val = (
                    res[0],
                    res[1],
                    res[1],
                    ctx.guild.id,
                    ctx.author.id
                )
                self.bot.db.execute(q, val)
                self.bot.db.commit()

        embed = discord.Embed(
            title="Balance",
            colour=0x0EF7E2
        )
        embed.add_field(
            name="In bank:",
            value=f"`{res[1]}`",
            inline=False
        )
        embed.add_field(
            name="On you:",
            value=f"`{res[0]}`",
            inline=False
        )
        embed.add_field(
            name="Total:",
            value=f"`{res[2]}`",
            inline=False
        )

        await ctx.send(embed=embed)
        return

    @commands.command(aliases=["dep"])
    async def deposit(self, ctx, amount):
        if amount == "":
            await ctx.send("Please specify an amount to deposit!")
            return
        qry = self.bot.cursor.execute(
            f"SELECT wit, dep, amount FROM currency WHERE guild_id = {ctx.guild.id} AND user_id = {ctx.author.id}")
        res = list(qry.fetchone())
        if res is None:
            await ctx.send(
                f"Sorry, you do not have any money, in bank or on you! to get money, simply type `{self.get_prefix(ctx)}work` to start working!"
            )
            return
        if res is not None:
            q = "UPDATE currency SET wit = ?, dep = ?, amount = ? WHERE guild_id = ? AND user_id = ?"
            if amount == "all":
                res[1] += res[0]
                res[0] = 0
                res[2] = res[0] + res[1]
                val = (
                    res[0],
                    res[1],
                    res[1],
                    ctx.guild.id,
                    ctx.author.id
                )
                self.bot.db.execute(q, val)
                self.bot.db.commit()
            else:
                res[0] -= int(amount)
                res[1] += int(amount)
                res[2] = res[0] + res[1]
                val = (
                    res[0],
                    res[1],
                    res[1],
                    ctx.guild.id,
                    ctx.author.id
                )
                self.bot.db.execute(q, val)
                self.bot.db.commit()

        embed = discord.Embed(
            title="Balance",
            colour=0x0EF7E2
        )
        embed.add_field(
            name="In bank:",
            value=f"`{res[1]}`",
            inline=False
        )
        embed.add_field(
            name="On you:",
            value=f"`{res[0]}`",
            inline=False
        )
        embed.add_field(
            name="Total:",
            value=f"`{res[2]}`",
            inline=False
        )

        await ctx.send(embed=embed)
        return

    @commands.command()
    async def give(self, ctx, member: discord.Member = None, amount: int = None):
        if member is None:
            await ctx.send("Please specify a person to give money to!")
        if amount is None:
            await ctx.send("Please specify an amount to give!")

        qry = self.bot.cursor.execute(
            f"SELECT wit, dep, amount FROM currency WHERE guild_id = {ctx.guild.id} AND user_id = {ctx.author.id}")
        res = list(qry.fetchone())
        if res is None:
            await ctx.send(
                f"Sorry, you do not have any money, in bank or on you! to get money, simply type `{self.get_prefix(ctx)}work` to start working!"
            )
            return
        if res is not None:
            if res[0] < int(amount):
                await ctx.send(
                    f"Sorry, you do not have enough money on you! simply type in `{self.get_prefix(ctx)}withdraw {int(amount)}`"
                )
                return
            q = "UPDATE currency SET wit = ?, dep = ?, amount = ? WHERE guild_id = ? AND user_id = ?"
            res[0] -= int(amount)
            res[2] = res[0] + res[1]
            val = (
                res[0],
                res[1],
                res[1],
                ctx.guild.id,
                ctx.author.id
            )
            self.bot.db.execute(q, val)
            self.bot.db.commit()

        qry = self.bot.cursor.execute(
            f"SELECT wit, dep, amount FROM currency WHERE guild_id = {ctx.guild.id} AND user_id = {ctx.author.id}")
        res = list(qry.fetchone())
        if res is None:
            await ctx.send(
                f"Sorry, you do not have any money, in bank or on you! to get money, simply type `{self.get_prefix(ctx)}work` to start working!"
            )
            return
        if res is not None:
            q = "UPDATE currency SET wit = ?, dep = ?, amount = ? WHERE guild_id = ? AND user_id = ?"
            res[0] += int(amount)
            res[2] = res[0] + res[1]
            val = (
                res[0],
                res[1],
                res[1],
                ctx.guild.id,
                member.id
            )
            self.bot.db.execute(q, val)
            self.bot.db.commit()

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
                qry = self.bot.cursor.execute(
                    f"SELECT wit, dep, amount FROM currency WHERE guild_id = {ctx.guild.id} AND user_id = {ctx.author.id};")
                res = list(qry.fetchone())
                if res is None:
                    await ctx.send(
                        f"Sorry, you do not have any money, in bank or on you! to get money, simply type `{self.get_prefix(ctx)}work` to start working!"
                    )
                    return
                if res is not None:
                    if res.get("wit") < items[thing]:
                        await ctx.send(
                            f"Sorry, you do not have enough money on you! simply type in `{self.get_prefix(ctx)}withdraw {items[thing]}`"
                        )
                    q = "UPDATE currency SET wit = ?, dep = ?, amount = ? WHERE guild_id = ? AND user_id = ?"
                    res[0] -= items[item]
                    res[2] = res[0] + res[1]
                    val = (
                        res[0],
                        res[1],
                        res[2],
                        ctx.guild.id,
                        ctx.author.id
                    )
                    self.bot.db.execute(q, val)
                    self.bot.db.commit()

                await ctx.send(f"Successfully bought {item}! delicious!")
        return


def setup(bot):
    bot.add_cog(Economy(bot))
