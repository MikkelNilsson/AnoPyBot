import discord
import config
import logging
import logging.handlers


class MyClient(discord.Client):
    def __init__(self, intents: discord.Intents):
        self.config = None
        self.logger: logging.Logger = None
        super().__init__(intents=intents)

    async def on_ready(self):
        self.logger.info(f"Logged on as {self.user}!")

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        self.logger.info(
            f"{message.guild.name}/{message.channel.name} - {message.author}: {message.content}"
        )

        await message.channel.send("Hello World!")


if __name__ == "__main__":
    client = config.config()
    client.run(client.config["discord"]["token"], log_handler=None)
