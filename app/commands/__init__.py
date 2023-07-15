import logging
import discord
import enum
from crud import get_command_prefix_or_initiate


class permissions(enum.Enum):
    MAINTAINER = 0
    ADMIN = 1


class Handler:
    handler = None

    def __init__(self, logger: logging.Logger = None):
        # commands keeps track of all commands
        self.commands = {}
        # command_map maps aliases to the command name
        self.command_map = {}
        self.logger = logger
        Handler.handler = self
        from commands import root

    def get_command(self, name: str):
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
    keep_args: bool = True,
    permissions: list[permissions] = [],
    aliases: list[str] = [],
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
        Handler.handler.commands[name] = {
            "callable": func,
            "description": description,
            "keep_args": keep_args,
            "permissions": permissions,
            "aliases": aliases,
        }
        Handler.handler.command_map[name] = name
        for alias in aliases:
            Handler.handler.command_map[alias] = name

        def decorated_function(*args, **kwargs):
            return func(*args, **kwargs)

        return decorated_function

    return decorator_function


async def exec(message: discord.Message):
    h = Handler.handler

    prefix = get_command_prefix_or_initiate(message.guild.id)

    # Check if message is a command
    if message.content.startswith(prefix):
        # Get command and args
        cmd = message.content[len(prefix) :].split(" ", 1)
        command = h.get_command(cmd[0].lower())

        # Check if command exists
        if command:
            # Check if user has permission to use command
            for permission in command["permissions"]:
                if (
                    permission is permissions.ADMIN
                    and not message.author.guild_permissions.administrator
                ):
                    return
                if (
                    permission is permissions.MAINTAINER
                    and message.author.id not in h.config["bot"]["owners"]
                ):
                    return

            # Execute command
            if command["keep_args"]:
                args = cmd[1] if len(cmd) > 1 else ""
                h.logger.info(
                    "Executing: "
                    + h.command_map[cmd[0].lower()]
                    + ' with "'
                    + args
                    + '" for '
                    + str(message.author)
                )
                res = await command["callable"](message, args)

            else:
                h.logger.info(
                    f"{message.guild.name}/{message.channel.name}:"
                    + f" Executing {h.command_map[cmd[0].lower()]}"
                    + f" for {str(message.author)}"
                )
                res = await command["callable"](message)

            if res is not None:
                h.logger.warning(res)

        else:
            await message.reply("Command not found")
