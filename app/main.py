import discord
from discord.ext import commands as discord_commands
from config import config_startup
import commands
import logger

class BotClient(discord.Client):
    def __init__(self, intents: discord.Intents):
        self.config = None
        super().__init__(intents=intents)

    async def on_ready(self):
        logger.info(f"Logged on as {self.user}!")
        logger.info(
            "Serving the following guilds: "
            + ", ".join([guild.name for guild in self.guilds])
        )

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if (
            "replay-messages" in self.config["discord"]
            and self.config["discord"]["replay-messages"] == "true"
        ):
            logger.info(
                f"{message.guild.name}/{message.channel.name} - {message.author}: {message.content}"
            )
        await commands.exec(message)


if __name__ == "__main__":
    # intents for discord
    intents = discord.Intents.all()

    # create client
    client = BotClient(intents=intents)
    config_startup(client)
    logger.info("setup Done")

    commands.Handler()
    logger.info("discord client run starting...")
    client.run(client.config["discord"]["token"], log_handler=None)
    