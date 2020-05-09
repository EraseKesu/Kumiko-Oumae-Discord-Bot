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
import asyncio
import datetime
import argparse, shlex
import re
import io
from collections import Counter
from utils import time, checks
from discord.ext import commands, timers
import sqlite3


class ActionReason(commands.Converter):
    async def convert(self, ctx, argument):
        ret = f'{ctx.author} (ID: {ctx.author.id}): {argument}'

        if len(ret) > 512:
            reason_max = 512 - len(ret) + len(argument)
            raise commands.BadArgument(f'Reason is too long ({len(argument)}/{reason_max})')
        return ret


def can_execute_action(ctx, user, target):
    return user.id == ctx.bot.owner_id or \
           user == ctx.guild.owner or \
           user.top_role > target.top_role


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.can_kick()
    async def kick(self, ctx, member: discord.Member = None, *args):
        if member is None:
            await ctx.send("Please specify a member!")
            return

        if member.id == ctx.author.id:
            await ctx.send("You cannot kick yourself!")
            return

        msg = ' '.join(args)

        embed = discord.Embed(
            title="Ban",
            description=f"{member.mention} has been kicked by {ctx.author.mention} for `{msg}`",
            colour=discord.Colour.from_rgb(255, 0, 0)
        )
        embed.set_footer(
            text="Join our support server! `https://discord.gg/YUm2sBD`",
            icon_url=self.bot.user.avatar_url_as(static_format="png")
        )

        await ctx.guild.kick(member)
        await ctx.send(embed=embed)

    @kick.error
    async def kick(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("I do not have enough permissions!")

        if isinstance(error, commands.BadArgument):
            await ctx.send(f"Could not find member! Please try again...")

    @commands.group(aliases=["prune", "clean", "clear"])
    @commands.guild_only()
    @checks.has_permissions(manage_messages=True)
    async def purge(self, ctx):

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    async def do_removal(self, ctx, limit, predicate, *, before=None, after=None):
        if limit > 2000:
            return await ctx.send(f'Too many messages to search given ({limit}/2000)')

        if before is None:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after is not None:
            after = discord.Object(id=after)

        try:
            deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
        except discord.Forbidden as e:
            return await ctx.send('I do not have permissions to delete messages.')
        except discord.HTTPException as e:
            return await ctx.send(f'Error: {e} (try a smaller search?)')

        spammers = Counter(m.author.display_name for m in deleted)
        deleted = len(deleted)
        messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed.']
        if deleted:
            messages.append('')
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f'**{name}**: {count}' for name, count in spammers)

        to_send = '\n'.join(messages)

        if len(to_send) > 2000:
            await ctx.send(f'Successfully removed {deleted} messages.', delete_after=10)
        else:
            await ctx.send(to_send, delete_after=10)

    @purge.command()
    async def embeds(self, ctx, search=100):
        """Removes messages that have embeds in them."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds))

    @purge.command()
    async def files(self, ctx, search=100):
        """Removes messages that have attachments in them."""
        await self.do_removal(ctx, search, lambda e: len(e.attachments))

    @purge.command()
    async def images(self, ctx, search=100):
        """Removes messages that have embeds or attachments."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds) or len(e.attachments))

    @purge.command(name='all')
    async def _remove_all(self, ctx, search=100):
        """Removes all messages."""
        await self.do_removal(ctx, search, lambda e: True)

    @purge.command()
    async def user(self, ctx, member: discord.Member, search=100):
        """Removes all messages by the member."""
        await self.do_removal(ctx, search, lambda e: e.author == member)

    @purge.command()
    async def contains(self, ctx, *, substr: str):
        """Removes all messages containing a substring.
        The substring must be at least 3 characters long.
        """
        if len(substr) < 3:
            await ctx.send('The substring length must be at least 3 characters.')
        else:
            await self.do_removal(ctx, 100, lambda e: substr in e.content)

    @purge.command(name='bot')
    async def _bot(self, ctx, prefix=None, search=100):
        """Removes a bot user's messages and messages with their optional prefix."""

        def predicate(m):
            return (m.webhook_id is None and m.author.bot) or (prefix and m.content.startswith(prefix))

        await self.do_removal(ctx, search, predicate)

    @purge.command(name='emoji', aliases=['emojis'])
    async def _emoji(self, ctx, search=100):
        """Removes all messages containing custom emoji."""
        custom_emoji = re.compile(r'<a?:[a-zA-Z0-9\_]+:([0-9]+)>')

        def predicate(m):
            return custom_emoji.search(m.content)

        await self.do_removal(ctx, search, predicate)

    @purge.command(name='reactions')
    async def _reactions(self, ctx, search=100):
        """Removes all reactions from messages that have them."""

        if search > 2000:
            return await ctx.send(f'Too many messages to search for ({search}/2000)')

        total_reactions = 0
        async for message in ctx.history(limit=search, before=ctx.message):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        await ctx.send(f'Successfully removed {total_reactions} reactions.')

    @purge.command()
    async def custom(self, ctx, *, args: str):
        """A more advanced purge command.
        This command uses a powerful "command line" syntax.
        Most options support multiple values to indicate 'any' match.
        If the value has spaces it must be quoted.
        The messages are only deleted if all options are met unless
        the `--or` flag is passed, in which case only if any is met.
        The following options are valid.
        `--user`: A mention or name of the user to remove.
        `--contains`: A substring to search for in the message.
        `--starts`: A substring to search if the message starts with.
        `--ends`: A substring to search if the message ends with.
        `--search`: How many messages to search. Default 100. Max 2000.
        `--after`: Messages must come after this message ID.
        `--before`: Messages must come before this message ID.
        Flag options (no arguments):
        `--bot`: Check if it's a bot user.
        `--embeds`: Check if the message has embeds.
        `--files`: Check if the message has attachments.
        `--emoji`: Check if the message has custom emoji.
        `--reactions`: Check if the message has reactions
        `--or`: Use logical OR for all options.
        `--not`: Use logical NOT for all options.
        """
        parser = Arguments(add_help=False, allow_abbrev=False)
        parser.add_argument('--user', nargs='+')
        parser.add_argument('--contains', nargs='+')
        parser.add_argument('--starts', nargs='+')
        parser.add_argument('--ends', nargs='+')
        parser.add_argument('--or', action='store_true', dest='_or')
        parser.add_argument('--not', action='store_true', dest='_not')
        parser.add_argument('--emoji', action='store_true')
        parser.add_argument('--bot', action='store_const', const=lambda m: m.author.bot)
        parser.add_argument('--embeds', action='store_const', const=lambda m: len(m.embeds))
        parser.add_argument('--files', action='store_const', const=lambda m: len(m.attachments))
        parser.add_argument('--reactions', action='store_const', const=lambda m: len(m.reactions))
        parser.add_argument('--search', type=int, default=100)
        parser.add_argument('--after', type=int)
        parser.add_argument('--before', type=int)

        try:
            args = parser.parse_args(shlex.split(args))
        except Exception as e:
            await ctx.send(str(e))
            return

        predicates = []
        if args.bot:
            predicates.append(args.bot)

        if args.embeds:
            predicates.append(args.embeds)

        if args.files:
            predicates.append(args.files)

        if args.reactions:
            predicates.append(args.reactions)

        if args.emoji:
            custom_emoji = re.compile(r'<:(\w+):(\d+)>')
            predicates.append(lambda m: custom_emoji.search(m.content))

        if args.user:
            users = []
            converter = commands.MemberConverter()
            for u in args.user:
                try:
                    user = await converter.convert(ctx, u)
                    users.append(user)
                except Exception as e:
                    await ctx.send(str(e))
                    return

            predicates.append(lambda m: m.author in users)

        if args.contains:
            predicates.append(lambda m: any(sub in m.content for sub in args.contains))

        if args.starts:
            predicates.append(lambda m: any(m.content.startswith(s) for s in args.starts))

        if args.ends:
            predicates.append(lambda m: any(m.content.endswith(s) for s in args.ends))

        op = all if not args._or else any

        def predicate(m):
            r = op(p(m) for p in predicates)
            if args._not:
                return not r
            return r

        args.search = max(0, min(2000, args.search))  # clamp from 0-2000
        await self.do_removal(ctx, args.search, predicate, before=args.before, after=args.after)

    @commands.command()
    @checks.can_ban()
    async def ban(self, ctx, member: discord.Member = None, *args):
        if member is None:
            await ctx.send("Please specify a member!")
            return

        if member.id == ctx.author.id:
            await ctx.send("You cannot ban yourself!")
            return

        msg = ' '.join(args)

        embed = discord.Embed(
            title="Ban",
            description=f"{member.mention} has been banned by {ctx.author.mention} for `{msg}`",
            colour=discord.Colour.from_rgb(255, 0, 0)
        )
        embed.set_footer(
            text="Join our support server! `https://discord.gg/YUm2sBD`",
            icon_url=self.bot.user.avatar_url_as(static_format="png")
        )

        await ctx.guild.ban(member)
        await ctx.send(embed=embed)

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("I do not have enough permissions!")

        if isinstance(error, commands.BadArgument):
            await ctx.send(f"Could not find member! Please try again...")

    @commands.command()
    @checks.can_ban()
    async def unban(self, ctx, member: discord.Member):
        """Un-bans a member from the server"""

        await ctx.guild.unban(member)
        await ctx.send(f"{member.mention} has been successfully unbanned!")

    @commands.command()
    @checks.can_ban()
    async def hackban(self, ctx, id):
        """Bans a member by id. this can be used to ban someone who is not in the server."""

        await ctx.guild.ban(discord.Object(id))
        await ctx.send(f"Member Has been hackbanned!")

    @commands.command()
    @checks.can_ban()
    async def unhackban(self, ctx, id):
        """Un-hackbans someone from the server"""

        await ctx.guild.unban(discord.Object(id))
        await ctx.send(f"Member's hackban has been infracted!")

    @commands.command()
    @checks.can_mute()
    async def mute(self, ctx, member: discord.Member, *args):
        """mutes someone in the server. Must have a role called Muted or muted"""
        msg = ' '.join(args)
        role = discord.utils.get(ctx.guild.roles, name="Muted" or "muted")
        embed = discord.Embed(
            title="Mute",
            description=f"{member.mention} has been muted by {ctx.author.mention} for {msg}!",
            colour=discord.Colour.from_rgb(255, 0, 0)
        )
        embed.set_footer(
            text="Join our support server! `https://discord.gg/YUm2sBD`",
            icon_url=self.bot.user.avatar_url_as(static_format="png")
        )

        await member.add_roles(role)
        await ctx.send(embed=embed)

    @commands.command()
    @checks.can_mute()
    async def unmute(self, ctx, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name="Muted" or "muted")

        await member.remove_roles(role)
        await ctx.send(f"{member.mention} has been unmuted! Try to follow the rules next time..")

    @commands.command()
    @checks.can_mute()
    async def tempmute(self, ctx, member: discord.Member, time, *args):
        msg = ' '.join(args)
        role = discord.utils.get(ctx.guild.roles, name="Muted" or "muted")
        realtime = 0

        if 'h' in time:
            time = time[:-1]
            time = int(time)
            realtime = time * 3600

        elif 'mon' in time:
            time = time[:-1]
            time = int(time)
            realtime = time * 2592000

        elif 'y' in time:
            time = time[:-1]
            time = int(time)
            realtime = time * 31536000

        elif 'm' in time:
            time = time[:-1]
            time = int(time)
            realtime = time * 60

        elif 's' in time:
            time = time[:-1]
            time = int(time)
            print(type(time))
            realtime = time * 1
        else:
            await ctx.send(f"{time} is not a valid time!")

        embed = discord.Embed(
            title="TempMute",
            description=f"Member Has been Temporarily Muted for {msg}",
            colour=0xe74c3c
        )
        embed.set_footer(
            text="Join our support server! `https://discord.gg/YUm2sBD`",
            icon_url=self.bot.user.avatar_url_as(static_format="png")
        )

        await member.add_roles(role)
        await ctx.send(embed=embed)
        await asyncio.sleep(realtime)
        await member.remove_roles(role)
        await ctx.author.send(f"{member} has been unmuted!")

    @commands.command()
    @checks.can_warn()
    async def warn(self, ctx, member: discord.Member, *args):
        msg = ' '.join(args)
        if member == ctx.author:
            await ctx.send("You can't warn yourself!")
            return
        if member == self.bot.user:
            await ctx.send("You can't warn me!")
            return
        if member is None:
            await ctx.send("Please specify a member to warn")
            return
        if msg is None:
            msg = "No reason"

        res = await self.bot.pool.fetchrow(f"SELECT warns FROM warns WHERE guild_id = {ctx.guild.id} AND user_id = {member.id}")
        if res is None:
            await self.bot.pool.execute("""INSERT INTO warns (guild_id, user_id, warns)
                                           VALUES ($1, $2, $3)""",
                                        ctx.guild.id,
                                        member.id,
                                        1
                                        )

        if res is not None:
            warns = res.get('warns') + 1
            await self.bot.pool.execute("""UPDATE warns
                                           SET warns = $1""",
                                        warns
                                        )

        embed = discord.Embed(
            title="Warn",
            description=f"{member.mention} has been warned for {msg}",
            colour=discord.Colour.from_rgb(255, 0, 0)
        )

        embed.add_field(
            name="warns",
            value=f"{res.get('warns')}",
            inline=False
        )

        embed.set_footer(
            text="Join our support server! https://discord.gg/YUm2sBD",
            icon_url=self.bot.user.avatar_url_as(static_format="png")
        )

        await ctx.send(embed=embed)

    @commands.command()
    @checks.can_warn()
    async def infract(self, ctx, member: discord.Member):
        if member == ctx.author:
            await ctx.send("You can't infract yourself!")
            return
        if member is None:
            await ctx.send("Please specify a member to warn")
            return

        res = await self.bot.pool.fetchrow(f"SELECT warns FROM warns WHERE guild_id = {ctx.guild.id} AND user_id = {member.id}")
        if res is None:
            await ctx.send("This member has no warns to be infracted!")
            return

        if res is not None:
            warns = res.get('warns') - 1
            await self.bot.pool.execute("""UPDATE warns
                                           SET warns = $1""",
                                        warns
                                        )
        await ctx.send(f"{member.mention}'s warn has been successfully infracted!")

    @commands.command()
    async def warnings(self, ctx, member: discord.Member):
        res = await self.bot.pool.fetchrow("""SELECT warns
                                              FROM warns
                                              WHERE guild_id = $1
                                              AND user_id = $2""",
                                           ctx.guild.id,
                                           member.id
                                           )
        if res is None:
            await ctx.send("This member has no warnings!")
            return

        if res is not None:
            await ctx.send(f"{member.mention} has {res.get('warns')} warns.")
            return

    @commands.command()
    @commands.guild_only()
    @checks.is_admin()
    async def massban(self, ctx, *, args):
        """Mass bans multiple members from the server.
        This command has a powerful "command line" syntax. To use this command
        you and the bot must both have Ban Members permission. **Every option is optional.**
        Users are only banned **if and only if** all conditions are met.
        The following options are valid.
        `--channel` or `-c`: Channel to search for message history.
        `--reason` or `-r`: The reason for the ban.
        `--regex`: Regex that usernames must match.
        `--created`: Matches users whose accounts were created less than specified minutes ago.
        `--joined`: Matches users that joined less than specified minutes ago.
        `--joined-before`: Matches users who joined before the member ID given.
        `--joined-after`: Matches users who joined after the member ID given.
        `--no-avatar`: Matches users who have no avatar. (no arguments)
        `--no-roles`: Matches users that have no role. (no arguments)
        `--show`: Show members instead of banning them (no arguments).
        Message history filters (Requires `--channel`):
        `--contains`: A substring to search for in the message.
        `--starts`: A substring to search if the message starts with.
        `--ends`: A substring to search if the message ends with.
        `--match`: A regex to match the message content to.
        `--search`: How many messages to search. Default 100. Max 2000.
        `--after`: Messages must come after this message ID.
        `--before`: Messages must come before this message ID.
        `--files`: Checks if the message has attachments (no arguments).
        `--embeds`: Checks if the message has embeds (no arguments).
        """

        # For some reason there are cases due to caching that ctx.author
        # can be a User even in a guild only context
        # Rather than trying to work out the kink with it
        # Just upgrade the member itself.
        if not isinstance(ctx.author, discord.Member):
            try:
                author = await ctx.guild.fetch_member(ctx.author.id)
            except discord.HTTPException:
                return await ctx.send('Somehow, Discord does not seem to think you are in this server.')
        else:
            author = ctx.author

        parser = Arguments(add_help=False, allow_abbrev=False)
        parser.add_argument('--channel', '-c')
        parser.add_argument('--reason', '-r')
        parser.add_argument('--search', type=int, default=100)
        parser.add_argument('--regex')
        parser.add_argument('--no-avatar', action='store_true')
        parser.add_argument('--no-roles', action='store_true')
        parser.add_argument('--created', type=int)
        parser.add_argument('--joined', type=int)
        parser.add_argument('--joined-before', type=int)
        parser.add_argument('--joined-after', type=int)
        parser.add_argument('--contains')
        parser.add_argument('--starts')
        parser.add_argument('--ends')
        parser.add_argument('--match')
        parser.add_argument('--show', action='store_true')
        parser.add_argument('--embeds', action='store_const', const=lambda m: len(m.embeds))
        parser.add_argument('--files', action='store_const', const=lambda m: len(m.attachments))
        parser.add_argument('--after', type=int)
        parser.add_argument('--before', type=int)

        try:
            args = parser.parse_args(shlex.split(args))
        except Exception as e:
            return await ctx.send(str(e))

        members = []

        if args.channel:
            channel = await commands.TextChannelConverter().convert(ctx, args.channel)
            before = args.before and discord.Object(id=args.before)
            after = args.after and discord.Object(id=args.after)
            predicates = []
            if args.contains:
                predicates.append(lambda m: args.contains in m.content)
            if args.starts:
                predicates.append(lambda m: m.content.startswith(args.starts))
            if args.ends:
                predicates.append(lambda m: m.content.endswith(args.ends))
            if args.match:
                try:
                    _match = re.compile(args.match)
                except re.error as e:
                    return await ctx.send(f'Invalid regex passed to `--match`: {e}')
                else:
                    predicates.append(lambda m, x=_match: x.match(m.content))
            if args.embeds:
                predicates.append(args.embeds)
            if args.files:
                predicates.append(args.files)

            async for message in channel.history(limit=min(max(1, args.search), 2000), before=before, after=after):
                if all(p(message) for p in predicates):
                    members.append(message.author)
        else:
            members = ctx.guild.members

        # member filters
        predicates = [
            lambda m: isinstance(m, discord.Member) and can_execute_action(ctx, author, m),  # Only if applicable
            lambda m: not m.bot,  # No bots
            lambda m: m.discriminator != '0000',  # No deleted users
        ]

        async def _resolve_member(member_id):
            r = ctx.guild.get_member(member_id)
            if r is None:
                try:
                    return await ctx.guild.fetch_member(member_id)
                except discord.HTTPException as e:
                    raise commands.BadArgument(f'Could not fetch member by ID {member_id}: {e}') from None
            return r

        if args.regex:
            try:
                _regex = re.compile(args.regex)
            except re.error as e:
                return await ctx.send(f'Invalid regex passed to `--regex`: {e}')
            else:
                predicates.append(lambda m, x=_regex: x.match(m.name))

        if args.no_avatar:
            predicates.append(lambda m: m.avatar is None)
        if args.no_roles:
            predicates.append(lambda m: len(getattr(m, 'roles', [])) <= 1)

        now = datetime.datetime.utcnow()
        if args.created:
            def created(member, *, offset=now - datetime.timedelta(minutes=args.created)):
                return member.created_at > offset

            predicates.append(created)
        if args.joined:
            def joined(member, *, offset=now - datetime.timedelta(minutes=args.joined)):
                if isinstance(member, discord.User):
                    # If the member is a user then they left already
                    return True
                return member.joined_at and member.joined_at > offset

            predicates.append(joined)
        if args.joined_after:
            _joined_after_member = await _resolve_member(args.joined_after)

            def joined_after(member, *, _other=_joined_after_member):
                return member.joined_at and _other.joined_at and member.joined_at > _other.joined_at

            predicates.append(joined_after)
        if args.joined_before:
            _joined_before_member = await _resolve_member(args.joined_before)

            def joined_before(member, *, _other=_joined_before_member):
                return member.joined_at and _other.joined_at and member.joined_at < _other.joined_at

            predicates.append(joined_before)

        members = {m for m in members if all(p(m) for p in predicates)}
        if len(members) == 0:
            return await ctx.send('No members found matching criteria.')

        if args.show:
            members = sorted(members, key=lambda m: m.joined_at or now)
            fmt = "\n".join(f'{m.id}\tJoined: {m.joined_at}\tCreated: {m.created_at}\t{m}' for m in members)
            content = f'Current Time: {datetime.datetime.utcnow()}\nTotal members: {len(members)}\n{fmt}'
            file = discord.File(io.BytesIO(content.encode('utf-8')), filename='members.txt')
            return await ctx.send(file=file)

        if args.reason is None:
            return await ctx.send('--reason flag is required.')
        else:
            reason = await ActionReason().convert(ctx, args.reason)

        count = 0
        for member in members:
            try:
                await ctx.guild.ban(member, reason=reason)
            except discord.HTTPException:
                pass
            else:
                count += 1

        await ctx.send(f'Banned {count}/{len(members)}')


class Arguments(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)


class plural:
    def __init__(self, value):
        self.value = value
    def __format__(self, format_spec):
        v = self.value
        singular, sep, plural = format_spec.partition('|')
        plural = plural or f'{singular}s'
        if abs(v) != 1:
            return f'{v} {plural}'
        return f'{v} {singular}'


def setup(bot):
    bot.add_cog(Moderation(bot))
