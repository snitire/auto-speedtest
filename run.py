import logging.config
import yaml
from configparser import ConfigParser
from os import system

CONFIG_PATH = "./config.ini"
LOG_CONFIG_PATH = "./app_log_config.yaml"

# Logger setup
with open(LOG_CONFIG_PATH) as file:
    conf = yaml.safe_load(file.read())
    logging.config.dictConfig(conf)
logger = logging.getLogger(__name__)

logger.info("Reading values from config file")
try:
    config = ConfigParser()
    config.read(CONFIG_PATH)

    logLevel = config.get("basic", "logLevel")
    runInBackground = config.getboolean("basic", "runInBackground")

    if runInBackground:
        exeName = config.get("paths", "pythonwExe")
    else:
        exeName = config.get("paths", "pythonExe")

    logger.setLevel(logLevel)

    logger.debug(f"Read values logLevel={logLevel}, runInBackground={runInBackground}, exeName={exeName}")
except:
    logger.critical(f"Unable to read values from config file at {CONFIG_PATH}: ", exc_info=1)
else:
    try:
        launchCommand = f"{exeName} app/app.py"
        logger.debug(f"App launch command: {launchCommand}")

        # Launch app with either pythonw (if running in background) or python
        system(launchCommand)
    except:
        logger.critical(f"Unable to launch app after reading config: ", exc_info=1)