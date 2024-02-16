import yaml
import logger
import os
from pathlib import Path
import modules.crud as crud
import modules.music as music

class ConfigError(Exception):
    pass


def load_config():
    prefix = str(Path(__file__).parent)
    load_prod = os.getenv("IS_PROD", "False").lower() == "true"

    # load production config
    if load_prod:
        with open(prefix + "/config/config.yml", "r") as f:
            res = yaml.safe_load(f)
    # load development config
    else:
        with open(prefix + "/config/config-development.yml", "r") as f:
            res = yaml.safe_load(f)

    res["is_prod"] = load_prod
    return res


def config_startup(client):
    # add config to the client
    client.config = load_config()

    # Setup logging
    if "logging" in client.config:
        logger.setup_logging(client.config["logging"])
    else:
        logger.setup_logging({"level": "info"})

    logger.info(
        "Loaded Production Configuration"
        if client.config["is_prod"]
        else "Loaded Development Configuration"
    )

    # Setup Database
    client.config["connection-string"] = client.config["connection-string"].format(
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        database=os.environ["POSTGRES_DB"],
        port=os.environ["POSTGRES_PORT"],
    )
    crud.setup_database(client.config["connection-string"])
    logger.info("Database Setup: Done")

    # get token from environment variables
    try:
        if "discord" not in client.config:
            client.config["discord"] = {}
        client.config["discord"]["token"] = os.environ["PYBOTTOKEN"]
    except KeyError:
        logger.Logger.error("No token found in environment variables")
        exit(1)
    logger.info("Bot Token: Loaded")
