import discord
import logger
import modules.crud as crud
from schema import (
    Command,
    permission,
    Context,
    CommandError,
    CommandPermissionError,
    CommandUsageError
)

handler = None

class Handler:

    def __init__(self, owners: list[int], client: discord.Client):
        # commands keeps track of all commands
        global handler
        if not handler:
            self.bot = client
            self.owners = owners
            self.commands = {}
            # command_map maps aliases to the command name
            self.command_map = {}
            handler = self
            from commands import root


    def get_command(self, name: str) -> Command:
        """Returns the command with the given name

        Args:
            name (str): name of the command

        Returns:
            Command: Returns the command info object. None if not found.
        """
        if name in self.command_map:
            return self.commands[self.command_map[name]]
        else:
            return None


def command(
    name: str,
    description: str = None,
    usage: str = None,
    permissions: list[permission] = [],
    aliases: list[str] = [],
    in_guild: bool = True,
    pre_hook: callable = None,
    post_hook: callable = None,
):
    """Decorator for commands, adds the command to the list of available commands.

    Args:
        name (str): command name
        description (str, optional): Defaults to None.
        keep_args (bool, optional): if True the command function will recieve the rest of the message in a str. Defaults to True.
        permissions (list[permissions], optional): Specific permissions for the command. Defaults to [].
        aliases (list[str], optional): Other phrases which calls this command. Defaults to [].
    """

    def decorator_function(func):
        handler.commands[name] = Command(
            method=func,
            name=name,
            description=description,
            usage=usage,
            permissions=permissions,
            aliases=aliases,
            in_guild=in_guild,
            pre_hook=pre_hook,
            post_hook=post_hook
        )
        handler.command_map[name] = name
        for alias in aliases:
            handler.command_map[alias] = name

        def decorated_function(*args, **kwargs):
            return func(*args, **kwargs)

        return decorated_function

    return decorator_function


async def exec(message: discord.Message):
    if message.guild:
        prefix = crud.get_command_prefix_or_initiate(message.guild.id)
    else:
        prefix = "!"

    # Check if message is a command
    if message.content.startswith(prefix):

        # Get command and args
        cmd = message.content[len(prefix) :].split(" ", 1)
        command: Command = handler.get_command(cmd[0].lower())

        # Check if command exists
        if command:
            ctx: Context = Context(message, command.name, handler.bot)

            try:
                if command.in_guild and not ctx.in_guild():
                    raise CommandError("Command has to be executed in a server!")

                # Check if user has permission to use command
                if not has_permission(command_permissions=command.permissions, author=message.author):
                    raise CommandPermissionError()

                logger.info(
                    "Executing: "
                    + ctx.command.command
                    + ' with args: "'
                    + ctx.command.rest
                    + '" for '
                    + ctx.author.name
                )

                # Pre command hook
                if command.pre_hook:
                    await command.pre_hook(ctx)
                # Execute command
                res = await command.method(ctx)

                # post command hook
                if command.post_hook:
                    await command.post_hook(ctx, res)

                if res:
                    print(res)

            except CommandUsageError as cmderr:
                await message.channel.send(
                    (cmderr.message + "\n" if cmderr.message else "") +
                    f"Usage: {prefix}{command.usage}"
                )
            except CommandError as cmderr:
                await message.channel.send(cmderr.message)

        else:
            await message.reply("Command not found")


def has_permission(command_permissions: list[permission], author: discord.Member):
    for permission in command_permissions:
        if (
            permission is permission.ADMIN
            and not author.guild_permissions.administrator
        ):
            return False
        if (
            permission is permission.MAINTAINER
            and author.id not in handler.owners
        ):
            return False
    return True