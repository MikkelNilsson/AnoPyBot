import sys
import json
import logging
import os
from pathlib import Path
import crud


def configLog(client):
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
    prefix = str(Path(__file__).parent)
    # load production config
    if len(sys.argv) > 1 and sys.argv[1].lower() == "prod":
        print("Loading production config")
        with open(prefix + "/config/config.json", "r") as f:
            return json.load(f)
    # load development config
    else:
        print("Loading development config")
        with open(prefix + "/config/config-development.json", "r") as f:
            return json.load(f)


def config_startup(client):
    # add config to the client
    client.config = load_config()
    client.config["connection-string"] = client.config["connection-string"].format(
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        database=os.environ["POSTGRES_DB"],
        port=os.environ["POSTGRES_PORT"],
    )
    crud.setup_database(client.config["connection-string"])

    # configure logging
    configLog(client)

    # get token from environment variables
    try:
        if "discord" not in client.config:
            client.config["discord"] = {}
        client.config["discord"]["token"] = os.environ["PYBOTTOKEN"]
    except KeyError:
        client.logger.error("No token found in environment variables")
        exit(1)
