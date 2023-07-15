import discord
from commands import permissions, command
from crud import update_prefix


@command("random", keep_args=False, aliases=["rand"])
async def random_command(msg):
    await msg.reply("Hello World!")


@command("rando", keep_args=True, aliases=["ran"])
async def random_command(msg, rest):
    await msg.reply("Hello World!" + " " + rest)


@command("setprefix", keep_args=True, aliases=["sp"])
async def set_prefix(msg: discord.Message, rest: str):
    new_prefix = rest.split(" ", 1)[0]
    update_prefix(msg.guild.id, new_prefix)
    await msg.reply(f"Prefix updated to {new_prefix}")
