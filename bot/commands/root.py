from commands import (
    command,
    settings,
    music,
    help
)
import schema


@command("Random", aliases=["rand"])
async def random_command(ctx: schema.Context):
    await ctx.reply("Hello World!")


@command("Rando", permissions=[schema.permission.MAINTAINER], aliases=["ran"])
async def random_command(ctx: schema.Context):
    await ctx.reply("Hello World!" + " " + ctx.command.rest)
