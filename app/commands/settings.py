from commands import command, CommandError
import schema
import crud
import logger

@command("setprefix", permissions=[schema.permission.ADMIN], aliases=["sp"])
async def set_prefix(ctx: schema.Context):
    if ctx.command.args and len(ctx.command.args) > 0:
        new_prefix = ctx.command.args[0]
        crud.update_prefix(ctx.guild.id, new_prefix)
        await ctx.reply(f"Prefix updated to {new_prefix}")
    else:
        raise CommandError("Failed ")


@command("setdefaultrole", permissions=[schema.permission.ADMIN])
async def set_default_role(ctx: schema.Context):
    if not ctx.command.args or len(ctx.command.args) == 0:
        raise CommandError(f"The {ctx.command.command} command needs an argument")
    role_string = ctx.command.args[0]
    try:
        role = ctx.message.role_mentions[0]
    except Exception:
        logger.info(f"{role_string} is not a valid role")
        await ctx.reply(f"Unfortunately, {role_string} is not a valid role.")
    else:
        crud.update_default_role(ctx.guild.id, role.id)
        logger.info(f'Updated default role for "{ctx.guild.name}" to "{role.name}"')
        await ctx.reply(f'Successfully set the default role to "{role.name}"!')
