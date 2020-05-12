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

from discord.ext import commands, menus


class HelpSource(menus.ListPageSource):

    async def format_page(self, menu, page):
        url = "https://patreon.com/user?0=u&1=%3D&2=3&3=4&4=6&5=2&6=8&7=9&8=3&9=7&utm_medium=social&utm_source=twitter&utm_campaign=creatorshare"
        if isinstance(page, str):
            embed = discord.Embed(
                title=f'Help| Type {get_prefix(bot=None, message=CTX)}setup to setup the server',
                description=f"[Join our support server](https://discord.gg/YUm2sBD) | [Support us on Patreon!]({url})" + ''.join(page),
                color=0xED791D
            )
            embed.set_thumbnail(
                url=CTX.author.avatar_url_as(static_format="png")
            )
            return embed
        else:

            embed = discord.Embed(
                title=f'Help| Type {get_prefix(bot=None, message=CTX)}setup to setup the server',
                description=f"[Join our support server](https://discord.gg/YUm2sBD) | [Support us on Patreon!]({url})" + '\n'.join(page),
                color=0xED791D
            )
            embed.set_thumbnail(
                url=CTX.author.avatar_url_as(static_format="png")
            )
            return embed


async def get_prefix(bot, message):
    res = await bot.pool.fetchrow("""SELECT prefix
                                     FROM db
                                     WHERE guild_id = $1""",
                                  message.guild.id
                                  )
    if res is None:
        prefix = commands.when_mentioned_or('+-')(bot, message)

    if res is not None:
        prefix = commands.when_mentioned_or(res.get("prefix"))(bot, message)

    return prefix


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global BOT
        BOT = bot

    @commands.command()
    async def help(self, ctx, command: str = None):
        prefix = self.bot.command_prefix()
        global CTX
        CTX = ctx
        error = f'```css\nThat command, "{command}", does not exist!\n```'
        if command:
            embed = discord.Embed(
                title="Help",
                colour=0xED791D
            )
            cmd = self.bot.get_command(command)

            if not cmd:
                await ctx.send(error)

                return

            if not cmd.hidden:

                if cmd.parent:

                    embed.add_field(
                        name="Usage:",
                        value=f'{prefix}{cmd.parent} {cmd.name} {cmd.signature}',
                        inline=False
                    )
                else:

                    embed.add_field(
                        name="Usage:",
                        value=f'{prefix}{cmd.name} {cmd.signature}',
                        inline=False
                    )

                if cmd.aliases:

                    aliases = ""

                    for a in cmd.aliases:
                        aliases += f"\n`{a}`"

                    embed.add_field(
                        name='Aliases',
                        value=aliases,
                        inline=False
                    )

                try:

                    commands = ""

                    for a in cmd.commands:
                        commands += f"`{prefix}{cmd.name} {a.name} {a.signature}`\n"

                    embed.add_field(
                        name="Subcommands",
                        value=commands,
                        inline=False
                    )

                except:

                    pass

            else:

                await ctx.send(error)
                return

            await ctx.send(embed=embed)
            return

        fun = ""
        for a in self.bot.commands:
            print(a.cog_name)
            if a.cog_name == "Fun":
                if not a.hidden:
                    fun += f"`{prefix}{a.name}` ◍ "
                    try:
                        for b in a.commands:
                            fun += f"`{prefix}{a.name} {b.name}` ◍ "
                    except:
                        pass

        economy = ""
        for a in self.bot.commands:
            print(a.cog_name)
            if a.cog_name == "Economy":
                if not a.hidden:
                    economy += f"`{prefix}{a.name}` ◍ "
                    try:
                        for b in a.commands:
                            economy += f"`{prefix}{a.name} {b.name}` ◍ "
                    except:
                        pass

        music = ""

        for a in self.bot.commands:
            if a.cog_name == "Music":
                if not a.hidden:
                    music += f"`{prefix}{a.name}` ◍ "
                    try:
                        for b in a.commands:
                            music += f"`{prefix}{a.name} {b.name}` ◍ "
                    except:
                        pass

        userinfo = ""

        for a in self.bot.commands:
            if a.cog_name == "UserInfo":
                if not a.hidden:
                    userinfo += f"`{prefix}{a.name}` ◍ "
                    try:
                        for b in a.commands:
                            userinfo += f"`{prefix}{a.name} {b.name}` ◍ "
                    except:
                        pass

        meta = ""

        for a in self.bot.commands:
            if a.cog_name == "Meta":
                if not a.hidden:
                    meta += f"`{prefix}{a.name}` ◍ "
                    try:
                        for b in a.commands:
                            meta += f"`{prefix}{a.name} {b.name}` ◍ "
                    except:
                        pass

        moderation = ""

        for a in self.bot.commands:
            if a.cog_name == "Moderation":
                if not a.hidden:
                    moderation += f"`{prefix}{a.name}` ◍ "
                    try:
                        for b in a.commands:
                            moderation += f"`{prefix}{a.name} {b.name}` ◍ "
                    except:
                        pass

        custom = ""

        for a in self.bot.commands:
            if a.cog_name == "Custom":
                if not a.hidden:
                    custom += f"`{prefix}{a.name}` ◍ "
                    try:
                        for b in a.commands:
                            custom += f"`{prefix}{a.name} {b.name}` ◍ "
                    except:
                        pass

        image = ""

        for a in self.bot.commands:
            if a.cog_name == "Images":
                if not a.hidden:
                    image += f"`{a.name}` ◍ "
                    try:
                        for b in a.commands:
                            image += f"`{prefix}{a.name} {b.name}` ◍ "
                    except:
                        pass

        lockdown = ""

        for a in self.bot.commands:
            if a.cog_name == "Lockdown":
                if not a.hidden:
                    lockdown += f"`{prefix}{a.name}` ◍ "
                    try:
                        for b in a.commands:
                            lockdown += f"`{prefix}{a.name} {b.name}` ◍ "
                    except:
                        pass

        translator = ""

        for a in self.bot.commands:
            if a.cog_name == "Translate":
                if not a.hidden:
                    translator += f"`{prefix}{a.name}` ◍ "
                    try:
                        for b in a.commands:
                            translator += f"`{prefix}{a.name} {b.name}` ◍ "
                    except:
                        pass

        leveling = ""

        for a in self.bot.commands:
            if a.cog_name == "Leveling":
                if not a.hidden:
                    leveling += f"`{prefix}{a.name}` ◍ "
                    try:
                        for b in a.commands:
                            leveling += f"`{prefix}{a.name} {b.name}` ◍ "
                    except:
                        pass

        fdescriptions = [f"""
            **FUN**
            {fun}

            """,
                             f"""
            **ECONOMY**
            {economy}

            """,
                             f"""
            **MUSIC**
            {music}

            """,
                             f"""
            **USERINFO**
            {userinfo}

            """,
                             f"""
            **META**
            {meta}

            """,
                             f"""
            **MODERATION**
            {moderation}

            """,
                             f"""
            **IMAGE**
            {image}

            """,
                             f"""
            **LOCKDOWN**
            {lockdown}

            """,
                             f"""
            **TRANSLATION**
            {translator}

            """,
                             f"""
            **LEVELING**
            {leveling}

            """,             f"""
            **CUSTOM**
            {custom}

        """]

        source = HelpSource(fdescriptions, per_page=2)
        menu = menus.MenuPages(source)
        await menu.start(ctx)

    @commands.command(aliases=["about"])
    async def info(self, ctx):
        owner = self.bot.get_user(self.bot.owner_id)
        embed = discord.Embed(
            title="About",
            description=f"I was made by {owner}.",
            colour=0xED791D
        )
        embed.add_field(
            name="Written in:",
            value=f"Discord.py {discord.__version__}",
            inline=True
        )
        embed.add_field(
            name="Bot Version:",
            value="version 1.1",
            inline=True
        )
        embed.add_field(
            name="Support Server:",
            value="discord.gg/YUm2sBD",
            inline=True
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def support(self, ctx):
        await ctx.send("Here is an invite to my support server:\ndiscord.gg/YUm2sBD")


def setup(bot):
    bot.add_cog(Help(bot))
