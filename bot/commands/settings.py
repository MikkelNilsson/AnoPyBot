from commands import command
from schema import (
    permission,
    Context,
    CommandError,
    CommandUsageError
)
import modules.crud as crud
import logger

@command(
    "setprefix",
    permissions=[permission.ADMIN],
    aliases=["sp"],
    description="Sets the prefix to use for this server.",
    usage="setprefix <prefix>"
)
async def set_prefix(ctx: Context):
    if ctx.command.args and len(ctx.command.args) > 0:
        new_prefix = ctx.command.args[0]
        crud.update_prefix(ctx.guild.id, new_prefix)
        await ctx.reply(f"Prefix updated to {new_prefix}")
    else:
        raise CommandUsageError(f"The {ctx.command.command} command needs an argument")


@command(
    "setdefaultrole",
    permissions=[permission.ADMIN],
    description="Set the role which should be added to users that joins the server.",
    usage="setdefaultrole <@default_role>"
)
async def set_default_role(ctx: Context):
    if not ctx.command.args or len(ctx.command.args) == 0:
        raise CommandUsageError(f"The {ctx.command.command} command needs an argument")
    role_string = ctx.command.args[0]
    try:
        role = ctx.message.role_mentions[0]
    except Exception:
        logger.info(f"{role_string} is not a valid role")
        await ctx.reply(f"{role_string} is not a valid role.")
    else:
        crud.update_default_role(ctx.guild.id, role.id)
        logger.info(f'Updated default role for "{ctx.guild.name}" to "{role.name}"')
        await ctx.reply(
            f'Successfully set the default role to **{role.name}**!\n' +
            f'Make sure the **AnoBot** role is above the **{role.name}** in the servers role settings!'
        )


@command(
    "removedefaultrole",
    permissions=[permission.ADMIN],
    description="Removes the role applied to users who joins the server."
)
async def remove_default_role(ctx: Context):
    crud.update_default_role(ctx.guild.id, 0)
    await ctx.send("Removed default role.")


@command(
    "setwelcomemessage",
    permissions=[permission.ADMIN],
    description="Sets the message sent when a new user joins the server.\nUse ¤name¤ to mention thenew user.\nThe message is everything within the \"_\", including line shifts.",
    usage="setwelcomemessage <#channel-to-send-the-message-in> \"<The message to be sent>\""
)
async def set_welcome_message(ctx: Context):
    if not ctx.command.args or len(ctx.command.args) != 2:
        raise CommandUsageError(f"The {ctx.command.command} command needs two arguments")

    if not ctx.message.channel_mentions:
        await ctx.reply(f"{ctx.command.args[0]} is not a valid channel.")
        return

    channel_id = ctx.message.channel_mentions[0].id
    channel = ctx.guild.get_channel(channel_id)
    if not channel:
        CommandError(f"**{ctx.message.channel_mentions[0].name}** is not a valid channel in a server")

    crud.update_welcome_message(ctx.guild.id, channel_id, ctx.command.args[1].strip("\""))
    await ctx.send(f"Welcome message updated, and will be sent in **{channel.name}**!")


@command(
    "removewelcomemessage",
    permissions=[permission.ADMIN],
    description="Removes the welcome message for the server."
)
async def remove_welcome_message(ctx: Context):
    crud.update_welcome_message(ctx.guild.id, 0, "")
    await ctx.send("Removed welcome message.")
