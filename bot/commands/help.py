from commands import command, handler, has_permission
from schema import Context, CommandError, permission
import discord
import modules.crud as crud

@command(
    "Help",
    in_guild=False,
    aliases=["h"],
    usage="help <page-number or command>",
    description="Shows a list of available commands"
)
async def help(ctx: Context):
    cmds_per_page = 5
    is_cmd_list = True

    if ctx.command.args and len(ctx.command.args) != 0:
        if ctx.command.args[0].isdigit():
            page_number = int(ctx.command.args[0])
        else:
            is_cmd_list = False
    else:
        page_number = 1

    prefix = crud.get_command_prefix_or_initiate(ctx.guild.id) if ctx.in_guild else "!"

    if is_cmd_list:
        if ctx.in_guild():
            filtered_commands = list(filter(lambda x: has_permission(handler.commands[x].permissions, ctx.author), handler.commands.keys()))
        else:
            filtered_commands = list(filter(lambda x: not handler.commands[x].in_guild, handler.commands.keys()))

        total_pages = len(filtered_commands)/cmds_per_page
        total_pages = int(total_pages) if total_pages % 1 == 0 else int(total_pages) + 1
        if page_number < 1 or page_number > total_pages:
            raise CommandError(f"{str(page_number)} is not a valid page")

        page = filtered_commands[(page_number-1)*cmds_per_page: min(page_number*cmds_per_page, len(handler.commands))]

        command_text = "\n".join([f"**{cmd}**\nUsage: `{prefix}{handler.commands[cmd].usage}`" for cmd in page])

        inital_text = (
            "Hi! Thanks for using AnoBot!\n\n" +
            "Use help together with a command to show more details about the command!\n" +
            f"Write: `{prefix}help <name_of_command>`\n\n" +
            f"List of available commands for you: Page {page_number}/{total_pages}\n"
        )
        await ctx.reply(inital_text + command_text)

    # TODO: Create modules in help
    elif ctx.command.args[0].lower() == "module":
        pass

    elif ctx.command.args[0].lower() in handler.modules:
        pass

    else:
        if not ctx.command.args[0].lower() in handler.command_map.keys():
            await ctx.reply(f"{ctx.command.args[0]}: Command not found.")

        cmd = handler.commands[handler.command_map[ctx.command.args[0]]]

        if permission.MAINTAINER in cmd.permissions and not has_permission(permission.MAINTAINER, ctx.author):
            await ctx.reply(f"{ctx.command.args[0]}: Command not found.")

        await ctx.reply(
            f"Info about **{prefix}{cmd.name}**:\n" +
            (f"**Description**: *{cmd.description}*\n" if cmd.description else "") +
            (f"**Usage**: `{prefix}{cmd.usage}`\n" if cmd.usage else "") +
            (f"**Aliases**: {', '.join([f'`{alias}`' for alias in cmd.aliases])}\n" if cmd.aliases else "") +
            f"**Permissions**: {'Admin only' if permission.ADMIN in cmd.permissions else 'Anyone'}\n" +
            f"Has to be used in a server: {'**Yes**' if cmd.in_guild else '**No**'}\n"
        )