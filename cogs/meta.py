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
import datetime

from discord.ext import commands, timers


class Meta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def source(self, ctx):
        embed = discord.Embed(
            title="Source",
            description="https://github.com/EraseKesu/Chorus"
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def feedback(self, ctx, *feedback):
        msg = ' '.join(feedback)

        embed = discord.Embed(
            title="Feedback",
            description=f"""
```css
[ {msg} ] ~{ctx.author}
```         """,
            colour=0x0EF7E2
        )
        emb = discord.Embed(
            title="Thanks For Your Feedback!",
            description="Thanks for your feedback! We will try to improve as soon as possible!",
            colour=0x0EF7E2
        )
        emb.set_footer(
            text="Join our support server! `https://discord.gg/YUm2sBD`",
            icon_url=self.bot.user.avatar_url_as(static_format="png")
        )

        channel = await self.bot.fetch_channel(694887120669507635)
        await channel.send(embed=embed)
        await ctx.send(embed=emb)

    @commands.command()
    async def invite(self, ctx):
        await ctx.send("https://discordapp.com/api/oauth2/authorize?client_id=685521236646035490&permissions=8&scope=bot")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        staff = await ctx.guild.create_role(name="staff")
        muted = await ctx.guild.create_role(name="Muted")
        await staff.edit(administrator=True)
        await muted.edit(send_messages=False)
        embed = discord.Embed(
            title="Setup complete",
            description="I have created the 'staff' and the 'Muted' role please change their permissions to your liking"
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def remind(self, ctx, time, timeval=None, *, text):
        x = ""
        unit = ""
        if "/" in time:
            date = datetime.datetime(*map(int, time.split("/")))
        if timeval is not None:
            if timeval == "week":
                x = "in "
                unit = "week"
                date = datetime.timedelta(weeks=time)
            if timeval == "weeks":
                x = "in "
                unit = "weeks"
                date = datetime.timedelta(weeks=time)
            if timeval == "month":
                x = "in "
                unit = "month"
                date = datetime.timedelta(weeks=time*4)
            if timeval == "months":
                x = "in "
                unit = "months"
                date = datetime.timedelta(weeks=time*4)
            if timeval == "year":
                x = "in "
                unit = "year"
                date = datetime.timedelta(weeks=time*52)
            if timeval == "years":
                x = "in "
                unit = "years"
                date = datetime.timedelta(weeks=time*52)
            if timeval == "day":
                x = "in "
                unit = "day"
                date = datetime.timedelta(days=time)
            if timeval == "days":
                x = "in "
                unit = "days"
                date = datetime.timedelta(days=time)
            else:
                text = timeval + " " + text
            if time == "tomorrow":
                unit = ""
                x = ""
                date = datetime.timedelta(days=1)
        timers.Timer(self.bot, "reminder", date, args=(ctx.channel.id, ctx.author.id, text)).start()
        await ctx.send(f"Ok, {ctx.author.mention}, i will remind you {x}{time}{unit}: {text}")

    @commands.Cog.listener()
    async def on_reminder(self, channel_id, author_id, text):
        channel = self.bot.get_channel(channel_id)
        author = self.bot.get_user(author_id)
        await channel.send(f"Hey {author.mention}, Im just pinging you so you don't forget to {text}")


def setup(bot):
    bot.add_cog(Meta(bot))
