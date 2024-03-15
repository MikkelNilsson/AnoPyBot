import discord
import logger
import modules.crud as crud
from schema import (
    Command,
    Permission,
    Context,
    CommandError,
    CommandPermissionError,
    CommandUsageError,
    CommandModule
)

handler = None

class Handler:

    def __init__(self, owners: list[int], client: discord.Client):
        # commands keeps track of all commands
        global handler
        if not handler:
            self.bot = client
            self.owners = owners
            self.commands: dict[str, Command] = {}
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
    modules: list[CommandModule] = [],
    description: str = None,
    usage: str = None,
    permissions: list[Permission] = [],
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
        handler.commands[name.lower()] = Command(
            method=func,
            modules=modules,
            name=name,
            description=description,
            usage=usage,
            permissions=permissions,
            aliases=aliases,
            in_guild=in_guild,
            pre_hook=pre_hook,
            post_hook=post_hook
        )
        handler.command_map[name.lower()] = name.lower()
        for alias in aliases:
            handler.command_map[alias.lower()] = name.lower()

        def decorated_function(*args, **kwargs):
            return func(*args, **kwargs)

        return decorated_function

    return decorator_function


async def check_for_command(message: discord.Message) -> tuple[Command, Context]:
    # Check for the correct prefix
    if message.guild:
        prefix = crud.get_command_prefix_or_initiate(message.guild.id)
    else:
        prefix = "!"

    # Make it lower case and remove prefixed or trailing whitespaces
    cmd_message = message.content.lower().strip()

    # Ensure that the !help command will always go through, even if the prefix is not "!"
    # It basically just replaces the "!" with the actual prefix of the message.
    if message.content.startswith("!help"):
        cmd_message = prefix + message.content[1:]

    # check that the message is actually a command.
    if cmd_message.startswith(prefix):
        # Find the command
        command = handler.get_command(
            cmd_message[len(prefix):].split(" ", 1)[0]
        )

        # Command not found
        if not command:
            await message.reply("Command not found")
            return (None, None)

        context = Context(
            message,
            prefix,
            command.name.lower(),
            handler.bot
        )

        return (command, context)


async def exec(message: discord.Message):

    (command, ctx) = await check_for_command(message)

    if not command:
        return

    try:
        # ----- Checks -----
        if command.in_guild and not ctx.in_guild():
            raise CommandError("Command has to be executed in a server!")

        # Check if user has permission to use command
        if not has_permission(command_permissions=command.permissions, author=message.author):
            raise CommandPermissionError()

        # ----- Logging -----
        logger.info(
            f"Executing: {ctx.command.command} with args: \"{ctx.command.rest}\" for {ctx.author.name}"
        )

        # ----- Executing -----
        # Pre command hook
        if command.pre_hook:
            await command.pre_hook(ctx)

        # Execute command
        res = await command.method(ctx)

        # post command hook
        if command.post_hook:
            await command.post_hook(ctx, res)

    except CommandUsageError as cmderr:
        if cmderr.log:
            logger.warning(cmderr.log)
        await message.reply(
            (cmderr.message + "\n" if cmderr.message else "") +
            f"Usage: `{ctx.command.prefix}{command.usage_str()}`"
        )
    except CommandError as cmderr:
        if cmderr.log:
            logger.warning(cmderr.log)
        await message.reply(cmderr.message)


def has_permission(command_permissions: list[Permission], author: discord.Member | discord.User):
    for permission in command_permissions:
        if (
            isinstance(author, discord.Member) and permission == permission.ADMIN
            and not author.guild_permissions.administrator
        ):
            return False
        if (
            permission == permission.MAINTAINER
            and author.id not in handler.owners
        ):
            return False
    return True
