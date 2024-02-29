from commands import (
    command,
    settings,
    music,
    help
)
from schema import Permission, Context


@command(
    "Debug",
    aliases=["de"],
    permissions=[Permission.MAINTAINER],
    in_guild=False,
)
async def debug(ctx: Context):
    args_list = "\", \"".join([a for a in ctx.command.args])
    message = (
        f"Debug:\n**Full Command**: \"{ctx.command.content}\"\n" +
        f"**Command**: \"{ctx.command.command}\"\n" +
        f"**Arguments**: \"{ctx.command.rest}\"\n" +
        f"**List of arguments**: \"{args_list}\"\n" +
        f"**Command Author name**: \"{ctx.author.name}\"\n"
    )
    if ctx.in_guild():
        message = message + (
            "**In Guild?**: Yes\n" +
            f"**Guild_name**: \"{ctx.guild.name}\"\n"
        )
    else:
        message = message + "**In Guild?**: No\n"
    await ctx.reply(message)