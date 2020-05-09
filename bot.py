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

import config
import discord
import smtplib
import asyncio
import json
import asyncpg
from utils.db import Database
from discord.ext import commands
from psutil import Process
from os import getpid
import logging
from googletrans import Translator
translator = Translator()

loop = asyncio.get_event_loop()


def get_prefix(bot, message):
    with open("db_files/custom_prefix.json", "r") as f:
        l = json.load(f)

    try:
        prefix = l[str(message.guild.id)]
    except KeyError:
        l[str(message.guild.id)] = '+-'
        prefix = l[str(message.guild.id)]

    return prefix


class MyContext(commands.Context):
    async def tick(self, value):
        emoji = '<:greenTick:596576670815879169>' if value else '<:redTick:596576672149667840>'
        try:
            await self.message.add_reaction(emoji)
        except discord.HTTPException:
            pass

    async def email(self, name, email, topic, message):
        global CTX
        CTX = message
        your_name = "Ethan Olchik"
        your_email = "eitan.olchik@gmail.com"
        your_password = "mbppsycliqmpxbal"

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(your_email, your_password)

        full_email = (f"From: {your_name} <{your_email}>\n"
                      f"To: {name} <{email}>\n"
                      f"Subject: {topic}\n\n"
                      f"{message}"
                      )

        try:
            server.sendmail(your_email, [email], full_email)
        except Exception as e:
            await self.message.add_reaction('<:redTick:596576672149667840>')
        else:
            await self.message.add_reaction('<:greenTick:596576670815879169>')
        server.close()

    async def longembed(self):
        zwsp = '\N{zero width space}'
        e = discord.Embed(description=zwsp + '\n' * 1022 + zwsp)

        for height in 510, 510, 510, 437:
            e.add_field(name=zwsp, value=zwsp + '\n' * height + zwsp)

        await self.message.channel.send(embed=e)

    async def trans(self, query: str, language):
        res = translator.translate(query, dest=language)
        await self.message.channel.send(res.text)

    async def rtranslate(self, query: str, language):
        res = translator.translate(query, dest=language)
        return res.text


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_prefix)
        languages = open("db_files/languages.json", "r")
        self.languages = json.load(languages)

    async def _init(self):
        pool = await Database.connect()
        self.pool = pool.pool

    async def get_context(self, message, *, cls=MyContext):
        return await super().get_context(message, cls=cls)


bot = MyBot()
bot.remove_command("help")
bot.logger = logging.getLogger(__name__)


def get_members():
    x = 0
    for m in bot.guilds:
        x += len(m.members)

    return x


inital_extension = [
  'cogs.userinfo',
  'cogs.music',
  'cogs.moderation',
  'cogs.help',
  'cogs.fun',
  'cogs.meta',
  'cogs.events',
  'cogs.lockdown',
  'cogs.custom',
  'cogs.image',
  'cogs.economy',
  'cogs.translator'
]


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Streaming(
            name=f"+-help | watching {get_members()} members", url="https://twitch.tv/classErase"
        )
    )
    bot.load_extension("jishaku")
    for extension in inital_extension:
        bot.load_extension(extension)


@bot.command(aliases=['mem', 'm'], hidden=True)
@commands.is_owner()
async def memory(ctx):
    await ctx.send(f'im currently using **{round(Process(getpid()).memory_info().rss/1024/1024, 2)} MB** of memory.')


@bot.command()
async def ping(ctx):
    ping = ctx.message
    pong = await ctx.send('**:ping_pong:** Pong!')
    delta = pong.created_at - ping.created_at
    delta = int(delta.total_seconds() * 1000)
    await pong.edit(content=f':ping_pong: Pong! ({delta} ms)\n*Discord WebSocket Latency: {round(bot.latency, 5)} ms*')


async def run_bot():
    # -- set up the bot's database and run the bot --

    @bot.before_invoke
    async def before_invoke(ctx):
        # this is jank AF but i'll have to find a better way to hook into ctx
        def send_message(channel_id, content, *, tts=False, embed=None, nonce=None, allowed_mentions=None):
            r = discord.http.Route('POST', '/channels/{channel_id}/messages', channel_id=channel_id)
            payload = {}

            if content:
                payload['content'] = content

            if tts:
                payload['tts'] = True

            if embed:
                payload['embed'] = embed

            if nonce:
                payload['nonce'] = nonce
            else:
                payload['nonce'] = str(ctx.author.id)

            if allowed_mentions:
                payload['allowed_mentions'] = allowed_mentions

            return bot.http.request(r, json=payload)

        bot.http.send_message = send_message

    try:
        bot.pool = await asyncpg.create_pool(user="postgres")
    except (ConnectionError, asyncpg.exceptions.CannotConnectNowError):
        bot.logger.critical("Could not connect to postgres.")

    await bot.start(config.token)


async def close_bot():
    await bot.pool.close()
    bot.logger.info("Closed postgres database connection.")
    await bot.logout()
    bot.logger.info("Logged out bot.")
    await bot.session.close()
    bot.logger.info("Closed aiohttp ClientSession.")
    await bot.http._HTTPClient__session.close()
    bot.logger.info("Closed internal bot ClientSession.")
    for task in asyncio.all_tasks(loop=loop):
        task.cancel()
        bot.logger.info("Canceled a running task.")


try:
    loop.run_until_complete(run_bot())
except KeyboardInterrupt:
    loop.run_until_complete(close_bot())

bot.run(config.token)
