import logging.config
import yaml
from configparser import ConfigParser

# When launched by run.py, the CWD does not change!!!
CONFIG_PATH = "./config.ini"
LOG_CONFIG_PATH = "./app_log_config.yaml"

# Logger setup
with open(LOG_CONFIG_PATH) as file:
    conf = yaml.safe_load(file.read())
    logging.config.dictConfig(conf)
logger = logging.getLogger(__name__)

logger.info("Starting main app")
logger.info("Reading values from config file")
try:
    config = ConfigParser()
    config.read(CONFIG_PATH)

    interval = config.getint("basic", "testInterval")
    logLevel = config.get("basic", "logLevel")

    st_logVerbosity = config.getint("speedtest", "logVerbosity")
    st_serverID = config.getint("speedtest", "serverID")
    st_hostname = config.get("speedtest", "hostname")
    st_ipAddress = config.get("speedtest", "ipAddress")
    st_interface = config.get("speedtest", "interface")

    logger.setLevel(logLevel)

    logger.debug(f"Read values interval={interval}, logLevel={logLevel}, logVerbosity={st_logVerbosity}, "
                 f"serverID={st_serverID}, hostname={st_hostname}, ipAddress={st_ipAddress}, interface={st_interface}")
except:
    logger.critical(f"Unable to read values from config file at {CONFIG_PATH}: ", exc_info=1)
