from commands import (
    command,
    settings,
    music
)
import schema

@command("random", aliases=["rand"])
async def random_command(ctx: schema.Context):
    await ctx.reply("Hello World!")

@command("rando", permissions=[schema.permission.MAINTAINER], aliases=["ran"])
async def random_command(ctx: schema.Context):
    await ctx.reply("Hello World!" + " " + ctx.command.rest)




