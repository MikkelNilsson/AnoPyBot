import discord

import os
from dotenv import dotenv_values
import logging
import logging.handlers


class MyClient(discord.Client):
    def __init__(self, intents: discord.Intents):
        self.env: dict[str, str | bool | None] = None
        self.logger: logging.Logger = None
        super().__init__(intents=intents)

    async def on_ready(self):
        self.logger.info(f"Logged on as {self.user}!")

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        self.logger.info(
            f"{message.guild.name}/{message.channel.name} - {message.author}: {message.content}",
        )

        await message.channel.send("Hello World!")


def configLog(client: MyClient):
    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)
    logging.getLogger("discord.http").setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        filename="./logs/discord.log",
        encoding="utf-8",
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )

    dt_fmt = "%d/%m/%Y %H:%M:%S"
    formatter = logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    std_err = logging.StreamHandler()
    std_err.setFormatter(formatter)
    logger.addHandler(std_err)

    client.logger = logger


def config():
    intents = discord.Intents.default()
    intents.message_content = True

    client = MyClient(intents=intents)
    client.env = dotenv_values(".env")
    configLog(client)

    token = client.env.get("DISCORD_TOKEN")
    client.run(token, log_handler=None)


if __name__ == "__main__":
    config()
