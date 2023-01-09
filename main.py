import discord

import os
from dotenv import load_dotenv

import commands


class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        print(f'{message.guild.name}#{message.channel.name} - {message.author}: {message.content}')
        await message.channel.send("Hello World!")


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents, command_prefix='!', help_command=None, tree_cls=commands.MyCommandTree)

client.run("TOKEN")
