from commands import command
from schema import Permission, Context
import modules.music as music


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
        f"**Prefix**: \"{ctx.command.prefix}\"\n" +
        f"**Actual Command**: \"{ctx.command.called_command}\"\n" +
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


@command(
    "Players",
    aliases=["activemusic"],
    permissions=[Permission.MAINTAINER],
    in_guild=False
)
async def activeMusic(ctx: Context):
    guilds = []
    for id in music.lavaClient.players.keys():
        guild = ctx.bot.get_guild(id)
        if guild:
            guilds.append(guild.name)

    if guilds:
        message = "Active players:\n" + "\n".join(guilds)
    else:
        message = "No active players"

    await ctx.send(message)