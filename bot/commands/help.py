from commands import command, handler, has_permission
from schema import Context, CommandError, Permission, CommandModule
import discord
import modules.crud as crud
#TODO: TEST!!! I think everything should work, but go through it :)

@command(
    "Help",
    in_guild=False,
    aliases=["h"],
    usage="page-number, module, or command",
    description="Shows a list of available commands"
)
async def help(ctx: Context):
    cmds_per_page = 5
    is_cmd_list = True
    listModule = None
    inital_text = "**Hi! Thanks for using AnoBot!**\n\n"

    if ctx.command.args and len(ctx.command.args) != 0:
        if ctx.command.args[0].isdigit():
            page_number = int(ctx.command.args[0])
        elif ctx.command.args[0] in list(CommandModule):
            listModule = CommandModule[ctx.command.args[0].upper()]
        else:
            is_cmd_list = False
    else:
        page_number = 1

    prefix = crud.get_command_prefix_or_initiate(ctx.guild.id) if ctx.in_guild else "!"
    embed = discord.Embed(color=discord.Color.from_rgb(255, 255, 255))

    if is_cmd_list:
        if ctx.in_guild():
            filtered_commands = list(filter(lambda x: has_permission(handler.commands[x].permissions, ctx.author), handler.commands.keys()))
        else:
            filtered_commands = list(filter(lambda x: not handler.commands[x].in_guild, handler.commands.keys()))

        if listModule:
            page = list(filter(lambda x: listModule in handler.commands[x].modules, handler.commands.keys()))
            if not page:
                embed.description = (
                    inital_text +
                    f"No commands available to you in module **{listModule.label()}**."
                )
            else:
                embed.description = (
                    inital_text +
                    f"__List of commands available to you in module **{listModule.label()}**:__\n"
                )
        else:
            total_pages = len(filtered_commands)/cmds_per_page
            total_pages = int(total_pages) if total_pages % 1 == 0 else int(total_pages) + 1
            if page_number < 1 or page_number > total_pages:
                raise CommandError(f"{str(page_number)} is not a valid page")

            page = filtered_commands[(page_number-1)*cmds_per_page: min(page_number*cmds_per_page, len(handler.commands))]

            embed.description = (
                inital_text +
                "Use help together with a command to show more details about the command!\n" +
                f"Write: `{prefix}help command`\n\n" +
                "Use help together with a module to show commands in that module!\n" +
                f"Write: `{prefix}help module`\n\n" +
                f"Use `{prefix}help modules` to list all modules!\n\n"
                f"__List of available commands for you:__\n"
            )
            embed.set_footer(text=f"Page: {page_number}/{total_pages}\t\tUse [{prefix}help page_number] to change page")

        embed.title = "AnoBot Help Menu"

        for cmd in page:
            value = (
                f"Usage: `{prefix}{handler.commands[cmd].usage_str()}`"
            )
            embed.add_field(name=handler.commands[cmd].name, value=value, inline=False)

        await ctx.send(embed=embed)

    elif ctx.command.args[0].lower() == "modules":
        embed.description = (
            inital_text +
            "Use these modules together with help to see module specific commands.\n" +
            f"Write: `{prefix}help module`\n\n" +
            "List of available modules:\n" +
            ", ".join(["**" + module.label() + "**" for module in CommandModule])
        )
        await ctx.send(embed=embed)

    else:
        if not ctx.command.args[0].lower() in handler.command_map.keys():
            raise CommandError(msg=f"{ctx.command.args[0]}: Command not found.")

        cmd = handler.commands[handler.command_map[ctx.command.args[0]]]

        if Permission.MAINTAINER in cmd.permissions and not has_permission(Permission.MAINTAINER, ctx.author):
            raise CommandError(msg=f"{ctx.command.args[0]}: Command not found.")

        embed = discord.Embed(color=discord.Color.from_rgb(255, 255, 255))
        embed.title = f"Info about **{cmd.name}**:\n"

        embed.description = (
            (f"**Description**: *{cmd.description}*\n" if cmd.description else "") +
            f"**Usage**: `{prefix}{cmd.usage_str()}`\n" +
            (f"**Aliases**: {', '.join([f'`{alias}`' for alias in cmd.aliases])}\n" if cmd.aliases else "") +
            f"**Permissions**: {'Admin only' if Permission.ADMIN in cmd.permissions else 'Anyone'}\n" +
            f"Has to be used in a server: {'**Yes**' if cmd.in_guild else '**No**'}\n"
        )
        await ctx.send(embed=embed)