from commands import command, CommandError
import schema
import discord
import crud
import logger

@command("setprefix", permissions=[schema.permission.ADMIN], keep_args=True, aliases=["sp"])
async def set_prefix(msg: discord.Message, rest: str):
    new_prefix = rest.lstrip().split(" ", 1)[0]
    crud.update_prefix(msg.guild.id, new_prefix)
    await msg.reply(f"Prefix updated to {new_prefix}")


@command("setdefaultrole", permissions=[schema.permission.ADMIN], keep_args=True)
async def set_default_role(msg: discord.Message, rest: str):
    role_string = rest.lstrip().split(" ", 1)[0]
    try:
        role = msg.role_mentions[0]
    except Exception:
        logger.info(f"{role_string} is not a valid role")
        await msg.reply(f"Unfortunately, {role_string} is not a valid role.")
    else:
        crud.update_default_role(msg.guild.id, role.id)
        logger.info(f'Updated default role for "{msg.guild.name}" to "{role.name}"')
        await msg.reply(f'Successfully set the default role to "{role.name}"!')
