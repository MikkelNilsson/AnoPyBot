import enum
import discord
from typing import Optional

class permission(enum.Enum):
    MAINTAINER = 0
    ADMIN = 1


class CommandError(Exception):
    message: str
    
    def __init__(self, msg: str) -> None:
        super().__init__()
        self.message = msg


class CommandPermissionError(Exception):
    pass


class Command():
    method: callable
    name: str
    description: str
    permissions: list[permission]
    aliases: list[str]
    in_guild: bool
    pre_hook: Optional[callable]
    post_hook: Optional[callable]

    def __init__(
        self,
        method: callable,
        name: str,
        description: str = "",
        permissions: list[permission] = [],
        aliases: list[str] = [],
        in_guild: bool = True,
        pre_hook: Optional[callable] = None,
        post_hook: Optional[callable] = None
    ) -> None:
        self.method = method
        self.name = name
        self.description = description
        self.permissions = permissions
        self.aliases = aliases
        self.in_guild = in_guild
        self.pre_hook = pre_hook
        self.post_hook = post_hook


class ContextCommand():
    command: str
    rest: str
    args: list[str]

    def __init__(self, msg: discord.Message, command: str) -> None:
        self.command = command
        self.content = msg.content
        self.rest = msg.content.split(" ", 1)[1:]
        self.args = msg.content.split(" ")[1:]
        

class Context():
    command: ContextCommand
    guild: discord.Guild
    channel: discord.abc.MessageableChannel
    author: discord.User | discord.Member
    message: discord.Message
    
    def __init__(self, msg: discord.Message, command: str):
        self.command = Command(msg, command)
        self.guild = msg.guild
        self.channel = msg.channel
        self.author = msg.author
        self.message = msg
    
    async def reply(self, msg: str):
        await self.message.reply(msg)
    
    def in_guild(self):
        return self.guild or False