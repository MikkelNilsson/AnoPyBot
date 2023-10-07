import logging
from logging import handlers
from collections import defaultdict

Logger: logging.Logger | None = None

class LogConfigError(Exception):
    pass

def setup_logging(log_config):
    level_dict = defaultdict(lambda: logging.NOTSET)
    if log_config and "level" in log_config.keys():
        level_dict = _get_logging_level_settings(log_config["level"])

    handler = handlers.RotatingFileHandler(
        filename="./logs/bot.log",
        encoding="utf-8",
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )

    dt_fmt = "%d/%m/%Y %H:%M:%S"
    formatter = logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
    )
    handler.setFormatter(formatter)
    
    std_err = logging.StreamHandler()
    std_err.setFormatter(formatter) 
      
    discord_logger = logging.getLogger("discord")
    discord_logger.setLevel(level_dict["discord"])
    discord_logger.addHandler(handler)
    discord_logger.addHandler(std_err)
    discord_http_logger = logging.getLogger("discord.http")
    discord_http_logger.setLevel(level_dict["discord.http"])
    discord_http_logger.addHandler(handler)
    discord_http_logger.addHandler(std_err)

    bot_logger = logging.Logger(name="AnoBot", level=level_dict["bot"])
    bot_logger.addHandler(handler)
    bot_logger.addHandler(std_err)
    
    global Logger
    Logger = bot_logger
    
    info("Logging setup: Done")

def _get_logging_level_settings(level_config):
    levels = {
        "notset": logging.NOTSET,
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "warn": logging.WARNING,
        "errror": logging.ERROR,
        "critical": logging.CRITICAL,
        "fatal": logging.CRITICAL,
    }
    if type(level_config) == type(dict()):
        if "default" not in level_config:
            LogConfigError(f"no default logging level set")
        
        res = defaultdict(lambda: levels[level_config["default"]])
        for k, v in level_config.items():
            
            if v in levels.keys():
                res[k] = levels[v]
            else:
                raise LogConfigError(f"Logging setup ({k}): No logging level called {v}")
        return res
    else:
        if level_config in levels.keys():
            return defaultdict(lambda: levels[level_config])
        
        raise LogConfigError(f"No default logging level called {level_config}")

def debug(msg: str):
    if Logger:
        Logger.debug(msg)

def info(msg: str):
    if Logger:
        Logger.info(msg)

def warning(msg: str):
    if Logger:
        Logger.warning(msg)

def error(msg: str):
    if Logger:
        Logger.error(msg)

def critical(msg: str):
    if Logger:
        Logger.critical(msg)
