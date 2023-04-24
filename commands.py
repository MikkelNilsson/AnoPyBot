import logging
import discord
import enum


class permissions(enum.Enum):
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
        import commands_root

    def get_command(self, name: str):
        if name in self.command_map:
            return self.commands[self.command_map[name]]
        else:
            return None


def command(
    name: str,
    description: str = None,
    usage: str = None,
    keep_args: bool = True,
    permissions: list[permissions] = [],
    aliases: list[str] = [],
):
    def decorator_function(func):
        Handler.handler.commands[name] = {
            "callable": func,
            "description": description,
            "usage": usage,
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


async def exec(message: discord.Message, prefix: str = "!"):
    h = Handler.handler
    if message.content.startswith(prefix):
        cmd = message.content[len(prefix) :].split(" ", 1)
        command = h.get_command(cmd[0].lower())
        if command:
            for permission in command["permissions"]:
                if (
                    permission is permissions.ADMIN
                    and not message.author.guild_permissions.administrator
                ):
                    return

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
                await command["callable"](message, args)

            else:
                h.logger.info(
                    f"{message.guild.name}/{message.channel.name}:"
                    + f" Executing {h.command_map[cmd[0].lower()]}"
                    + f" for {str(message.author)}"
                )
                await command["callable"](message)

        else:
            message.channel.send("Command not found")
