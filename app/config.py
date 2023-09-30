import sys
import json
import logger
import os
from pathlib import Path
import crud

class ConfigError(Exception):
    pass



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
    
    # Setup logging    
    if "logging" in client.config:
        logger.setup_logging(client.config["logging"])
    else:
        logger.setup_logging({"level": "info"})
    
    # Setup Database
    client.config["connection-string"] = client.config["connection-string"].format(
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        database=os.environ["POSTGRES_DB"],
        port=os.environ["POSTGRES_PORT"],
    )
    crud.setup_database(client.config["connection-string"])

    # get token from environment variables
    try:
        if "discord" not in client.config:
            client.config["discord"] = {}
        client.config["discord"]["token"] = os.environ["PYBOTTOKEN"]
    except KeyError:
        logger.Logger.error("No token found in environment variables")
        exit(1)
