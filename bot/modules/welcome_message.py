import modules.crud as crud
import discord
import logger
import models

async def on_welcome(member: discord.Member):
    server = crud.get_server_data(member.guild.id)

    # Default Role:
    if server.default_role != 0:
        await add_default_role(member, server)

    # Welcome message
    if server.welcome_channel != 0:
        await send_welcome_message(member, server)


async def add_default_role(member: discord.Member, server: models.Server):
    if not member.guild.me.guild_permissions.manage_roles:
        logger.error(f"Default role activated but does not have permission to edit roles in server {member.guild.name}.")
        return

    role = member.guild.get_role(server.default_role)
    if not role:
        logger.warning(f"Invalid default role for server {member.guild.name}")

    await member.add_roles(role)


async def send_welcome_message(member: discord.Member, server: models.Server):
    channel = member.guild.get_channel(server.welcome_channel)
    if not channel:
        logger.warning(f"Invalid welcome channel for server {member.guild.name}")


    message = str(server.welcome_message).replace("¤name¤", member.mention)
    await channel.send(message)
