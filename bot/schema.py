import enum
import discord
from typing import Any, Optional
import re

class Permission(enum.Enum):
    MAINTAINER = 0
    ADMIN = 1


class CommandModule(enum.Enum):
    SETTINGS = "Settings"
    NEWUSER = "NewUser"
    DEFAULTROLE = "DefaultRole"
    WELCOMEMESSAGE = "WelcomeMessage"
    MUSIC = "Music"

    def label(self):
        return self.value

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, str):
            return self.value.lower() == __value.lower()
        return super().__eq__(__value)

class CommandError(Exception):
    message: str
    log: str

    def __init__(self, msg: str, log: str = None) -> None:
        super().__init__()
        self.message = msg
        self.log = log

class CommandUsageError(CommandError):
    pass

class CommandPermissionError(CommandError):
    def __init__(self) -> None:
        super().__init__("You do not have permission to execute this command.")


class Command():
    method: callable
    name: str
    modules: list[CommandModule]
    description: str
    usage: str
    permissions: list[Permission]
    aliases: list[str]
    in_guild: bool
    pre_hook: Optional[callable]
    post_hook: Optional[callable]

    def __init__(
        self,
        method: callable,
        name: str,
        modules: list[CommandModule],
        description: str = "",
        usage: str = "",
        permissions: list[Permission] = [],
        aliases: list[str] = [],
        in_guild: bool = True,
        pre_hook: Optional[callable] = None,
        post_hook: Optional[callable] = None
    ) -> None:
        self.method = method
        self.name = name
        self.modules = modules
        self.description = description
        self.usage = usage
        self.permissions = permissions
        self.aliases = aliases
        self.in_guild = in_guild
        self.pre_hook = pre_hook
        self.post_hook = post_hook

    def usage_str(self) -> str:
        return f"{self.name.lower()}" + (f" {self.usage}" if self.usage else "")


pattern = r"(\"[^\"]*\"|[^ ]+)"
class ContextCommand():
    command: str
    rest: str
    args: list[str]

    def __init__(self, np_message: str, command: str) -> None:
        self.command = command
        self.content = np_message.strip()
        self.args = re.findall(pattern, np_message[len(command) + 1:].strip())
        self.rest = (
            np_message.strip().split(" ", 1)[1]
            if len(self.args) > 0
            else ""
        )


class Context():
    command: ContextCommand
    guild: discord.Guild
    channel: discord.TextChannel
    voice_client: discord.VoiceProtocol | None
    author: discord.User | discord.Member
    message: discord.Message
    bot: discord.Client

    def __init__(self, msg: discord.Message, np_message: str, command: str, client: discord.Client):
        self.command = ContextCommand(np_message, command)
        self.guild = msg.guild
        self.channel = msg.channel
        self.author = msg.author
        self.message = msg
        self.voice_client = msg.guild.voice_client if msg.guild else None
        self.bot = client

    async def reply(self, msg: str):
        await self.message.reply(msg)

    def in_guild(self):
        return bool(self.guild)

    async def send(self, msg: str = None, embed: discord.Embed = None):
        await self.channel.send(msg, embed=embed)