import discord
import config
import commands
import logging
import logging.handlers


class BotClient(discord.Client):
    client = None
    db_client = None

    def __init__(self, intents: discord.Intents):
        if BotClient.client is not None:
            raise Exception("Client already exists")
        self.config = None
        self.logger: logging.Logger = None
        super().__init__(intents=intents)
        BotClient.client = self

    async def on_ready(self):
        self.logger.info(f"Logged on as {self.user}!")

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if (
            "replay-messages" in self.config["discord"]
            and self.config["discord"]["replay-messages"] == "true"
        ):
            self.logger.info(
                f"{message.guild.name}/{message.channel.name} - {message.author}: {message.content}"
            )
        await commands.exec(message)


if __name__ == "__main__":
    client = config.config()
    commands.Handler(client.logger)
    client.run(client.config["discord"]["token"], log_handler=None)
