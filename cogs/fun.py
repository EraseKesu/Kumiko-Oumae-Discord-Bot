"""
Copyright 2020 EraseKesu (class Erase#0027)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import discord
import json
import random
import asyncio
from game import Connect4Game
from discord.ext.commands.cooldowns import BucketType
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="An Unexpected Error Occurred!",
                description=f"""
                            ```cmd
                            {error}
                            ```
                            """,
                inline=False
            )
            await ctx.send(embed=embed)
        if isinstance(error, commands.CommandInvokeError):
            embed = discord.Embed(
                title="An Unexpected Error Occurred!",
                description=f"""
                ```cmd
                {error.original}
                ```
                """,
                inline=False
            )
            await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    @commands.cooldown(1, 5, BucketType.user)
    async def candy(self, ctx):

        embed = discord.Embed(description="🍬 | First one to take the candy gets the candy!", colour=0x0EF7E2)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🍬")

        def check(reaction, user):
            return user != self.bot.user and str(reaction.emoji) == '🍬' and reaction.message.id == msg.id

        msg0 = await self.bot.wait_for("reaction_add", check=check)

        embed.description = f"🍬 | {msg0[1].mention} got and ate the candy!"

        await msg.edit(embed=embed)

        with open("db_files/candylb.json", "r") as f:

            l = json.load(f)

        try:

            l[str(msg0[1].id)] += 1

        except KeyError:

            l[str(msg0[1].id)] = 1

        with open("db_files/candylb.json", "w") as f:

            json.dump(l, f, indent=4)

    @candy.command(aliases=["lb", "top"])
    async def leaderboard(self, ctx):

        with open("db_files/candylb.json", "r") as f:

            l = json.load(f)

        lb = sorted(l, key=lambda x: l[x], reverse=True)
        print(lb)
        res = ""

        counter = 0

        for a in lb:

            counter += 1

            if counter > 10:

                pass

            else:

                u = self.bot.get_user(int(a))
                res += f"\n**{counter}.** `{u}` - **{l[str(a)]} 🍬**"

        embed = discord.Embed(
            description=res,
            colour=0x0EF7E2
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def roll(self, ctx, *things):
        await ctx.send(random.choice(things))

    CANCEL_GAME_EMOJI = '🚫'
    DIGITS = [str(digit) + '\N{combining enclosing keycap}' for digit in range(1, 8)] + ['🚫']
    VALID_REACTIONS = [CANCEL_GAME_EMOJI] + DIGITS
    GAME_TIMEOUT_THRESHOLD = 60

    @commands.command()
    async def connect4(self, ctx, *, player2: discord.Member):
        player1 = ctx.message.author

        game = Connect4Game(
            player1.display_name,
            player2.display_name
        )

        message = await ctx.send(str(game))

        for digit in self.DIGITS:
            await message.add_reaction(digit)

        def check(reaction, user):
            return (
                user == (player1, player2)[game.whomst_turn() - 1]
                and str(reaction) in self.VALID_REACTIONS
                and reaction.message.id == message.id
            )

        while game.whomst_won() == game.NO_WINNER:
            try:
                reaction, user = await self.bot.wait_for(
                    'reaction_add',
                    check=check,
                    timeout=self.GAME_TIMEOUT_THRESHOLD
                )
            except asyncio.TimeoutError:
                game.forfeit()
                break

            await asyncio.sleep(0.2)
            try:
                await message.remove_reaction(reaction, user)
            except discord.errors.Forbidden:
                pass

            if str(reaction) == self.CANCEL_GAME_EMOJI:
                game.forfeit()
                break

            try:
                game.move(self.DIGITS.index(str(reaction)))
            except ValueError:
                pass

            await message.edit(content=str(game))

        await self.end_game(game, message)

    @classmethod
    async def end_game(cls, game, message):
        await message.edit(content=str(game))
        await cls.clear_reactions(message)

    @staticmethod
    async def clear_reactions(message):
        try:
            await message.clear_reactions()
        except discord.HTTPException:
            pass


def setup(bot):
    bot.add_cog(Fun(bot))
