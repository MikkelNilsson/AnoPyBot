import sys
import json
import logging
import discord
import os
from main import BotClient


def configLog(client: BotClient):
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


def load_config():
    if len(sys.argv) > 1 and sys.argv[1].lower() == "prod":
        print("Loading production config")
        with open("config.json", "r") as f:
            return json.load(f)
    else:
        print("Loading development config")
        with open("config-development.json", "r") as f:
            return json.load(f)


def config():
    intents = discord.Intents.default()
    intents.message_content = True

    client = BotClient(intents=intents)
    client.config = load_config()
    configLog(client)
    try:
        if "discord" not in client.config:
            client.config["discord"] = {}
        client.config["discord"]["token"] = os.environ["PyBotToken"]
    except KeyError:
        client.logger.error("No token found in environment variables")
        exit(1)

    return client
