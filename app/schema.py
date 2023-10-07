import enum
import discord
from typing import Optional
import bot

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
        self.args = msg.content.split(" ")[1:]
        self.rest = ( 
            msg.content.split(" ", 1)[1]
            if len(self.args) > 1
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
    
    def __init__(self, msg: discord.Message, command: str, client: discord.Client):
        self.command = ContextCommand(msg, command)
        self.guild = msg.guild
        self.channel = msg.channel
        self.author = msg.author
        self.message = msg
        self.voice_client = msg.guild.voice_client
        self.bot = client
    
    async def reply(self, msg: str):
        await self.message.reply(msg)
    
    def in_guild(self):
        return self.guild or False

    async def send(self, msg: str, embed: discord.Embed = None):
        await self.channel.send(msg, embed=embed)