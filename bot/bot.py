import discord
from config import config_startup
import commands
import logger
from modules import music, welcome_message

class BotClient(discord.Client):
    def __init__(self, intents: discord.Intents):
        self.config = None
        super().__init__(intents=intents)

    async def on_ready(self):
        logger.info(f"Logged on as {self.user}!")
        music.setup(client=self)
        logger.info("Lavalink Setup: Done")
        logger.info(
            "Serving the following guilds: "
            + ", ".join([guild.name for guild in self.guilds])
        )


    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if (
            "replay-messages" in self.config["discord"] and self.config["discord"]["replay-messages"]
        ):
            channel = (f"{message.guild.name}/{message.channel.name}" if message.guild else "Direct Message")
            logger.info(
                f"{channel} - {message.author}: {message.content}"
            )
        await commands.exec(message)


    async def on_member_join(self, member: discord.Member):
        await welcome_message.on_welcome(member)


if __name__ == "__main__":
    # intents for discord
    intents = discord.Intents.all()

    # create client
    client = BotClient(intents=intents)
    config_startup(client)

    logger.info("Setup: Done")

    commands.Handler(client.config["bot"]["owners"], client)
    logger.info("Command Handler Setup: Done")

    client.run(client.config["discord"]["token"], log_handler=None)
