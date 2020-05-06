import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
import aiohttp
import datetime
import discord
from io import BytesIO
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from PIL import Image, ImageDraw


class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.session = aiohttp.ClientSession(loop=bot.loop)

    @commands.command(aliases=["guildstatus", "statusguild", "guildpie"])
    @commands.cooldown(1, 20, BucketType.user)
    async def serverpie(self, ctx, guild_id: int = None):
        async with ctx.typing():

            if guild_id:
                g = self.bot.get_guild(guild_id)
                if not g:
                    return await ctx.send("That guild could not be found. Am I in it?")
            else:
                g = ctx.guild
            ov = {"online": 0, "idle": 0, "dnd": 0, "offline": 0, "streaming": 0}
            tot = sum(1 for m in g.members)
            for member in g.members:
                if type(member.activity) is discord.Streaming:
                    ov["streaming"] += 1
                else:
                    ov[str(member.status)] += 1
            async with self.bot.session.get(str(g.icon_url_as(format="png"))) as resp:
                img = BytesIO(await resp.read())

            color = list()
            sizes = list()
            label = list()
            for key, value in ov.items():
                if ov[key]:
                    sizes.append(value)
                    if key == "online":
                        color.append("#43b581")
                    if key == "idle":
                        color.append("#faa61a")
                    if key == "dnd":
                        color.append("#f04747")
                    if key == "offline":
                        color.append("#747f8d")
                    if key == "streaming":
                        color.append("#593695")
            for key, value in ov.items():
                if value:
                    label.append(f"{round((value / tot) * 100)}%")
            b = BytesIO()

            def create_chart():
                _, ax1 = plt.subplots()
                ax1.pie(
                    sizes,
                    startangle=90,
                    colors=color,
                    wedgeprops={"edgecolor": "w", "width": 1},
                    textprops={
                        "fontsize": "large",
                        "family": "sans-serif",
                        "color": "#ffffff",
                    },
                )
                ax1.axis("equal")
                font = font_manager.FontProperties(
                    family="sans-serif", weight="light", style="normal", size=12
                )
                ax1.set_title(f"Guild Status for {g.name}", fontsize=18, color="white")
                ax1.legend(
                    label,
                    prop=font,
                    title="Percentages",
                    loc="center left",
                    bbox_to_anchor=(0.88, 0.6, 0.8, 0.65),
                )
                plt.savefig(b, transparent=True)
                b.seek(0)
                plt.close()

            await self.bot.loop.run_in_executor(None, create_chart)
            bt = BytesIO()
            bf = BytesIO()

            def add_image():
                with Image.open(img) as im:  # create circular image
                    bigsize = (192, 192)
                    im = im.resize((192, 192), Image.ANTIALIAS)
                    size = im.size
                    mask = Image.new("L", bigsize, 0)
                    draw = ImageDraw.Draw(mask)
                    draw.ellipse((0, 0) + bigsize, fill=255)
                    mask = mask.resize(im.size, Image.ANTIALIAS)
                    im.putalpha(mask)
                    im.save(bt, "png")
                    bt.seek(0)

                with Image.open(b) as im2:
                    with Image.open(bt) as im3:
                        mk = Image.new("L", size, 0)
                        dr = ImageDraw.Draw(mk)
                        dr.ellipse((0, 0) + size, fill=255)
                        im2.paste(im3, (231, 145), mk)
                        im2.save(bf, "png")
                        bf.seek(0)

            await self.bot.loop.run_in_executor(None, add_image)
            gname = g.name.replace("@", "@\u200b")

            await ctx.send(
                f"**{gname}**'s status makeup as of `{datetime.datetime.utcnow()}`",
                file=discord.File(bf, filename="guildstatus.png"),
            )


def setup(bot):
    bot.add_cog(Images(bot))
