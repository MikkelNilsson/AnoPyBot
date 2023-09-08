import discord
from commands import permissions, command, Handler
from logging import Logger
import crud
import lavalink

logger: Logger = Handler.handler.logger


@command("random", keep_args=False, aliases=["rand"])
async def random_command(msg):
    await msg.reply("Hello World!")


@command("rando", keep_args=True, aliases=["ran"])
async def random_command(msg, rest):
    await msg.reply("Hello World!" + " " + rest)


@command("setprefix", permissions=[permissions.ADMIN], keep_args=True, aliases=["sp"])
async def set_prefix(msg: discord.Message, rest: str):
    new_prefix = rest.lstrip().split(" ", 1)[0]
    crud.update_prefix(msg.guild.id, new_prefix)
    await msg.reply(f"Prefix updated to {new_prefix}")


@command("setdefaultrole", permissions=[permissions.ADMIN], keep_args=True)
async def set_default_role(msg: discord.Message, rest: str):
    role_string = rest.lstrip().split(" ", 1)[0]
    try:
        role = msg.guild.get_role(int(role_string))
    except ValueError:
        logger.info(f"{role_string} is not a valid role")
        msg.reply(f"Unfortunately, {role_string} is not a valid role.")
    else:
        crud.update_default_role(msg.guild.id, role.id)
        logger.info(f'Updated default role for "{msg.guild.name}" to "{role.name}"')
        msg.reply(f'Successfully set the default role to "{role.name}"!')


@command("play", keep_args=True, aliases=["p"])
async def Play(msg: discord.Message, rest: str):
    pass
