import logging.config
import db
import yaml
from configparser import ConfigParser
from speedtest import Speedtest
from time import sleep

# When launched by run.py, the CWD does not change from ./ to ./app/
CONFIG_PATH = "./config.ini"
LOG_CONFIG_PATH = "./app_log_config.yaml"


def doPeriodicTest():
    testResult = speedtest.runTest()
    logger.debug(f"Received test results: {testResult}")

    testDate = f"'{testResult['timestamp']}'"
    ping = f"'{testResult['ping']['latency']}'"
    downloadMbps = f"'{testResult['download']['bandwidthMbps']}'"
    uploadMbps = f"'{testResult['upload']['bandwidthMbps']}'"
    packetLoss = f"'{testResult['packetLoss']}'"
    url = f"'{testResult['result']['url']}'"

    db.addRecord("results",
                 ["test_date", "ping", "download_mbps", "upload_mbps", "packet_loss", "url"],
                 [testDate, ping, downloadMbps, uploadMbps, packetLoss, url]
                 )

# Logger setup and config reading
with open(LOG_CONFIG_PATH) as file:
    conf = yaml.safe_load(file.read())
    logging.config.dictConfig(conf)

logger = logging.getLogger(__name__)

logger.info("Starting main app")
logger.info("Reading values from config file")

try:
    config = ConfigParser()
    config.read(CONFIG_PATH)

    interval = config.getfloat("basic", "testInterval")
    logLevel = config.get("basic", "logLevel")

    st_logVerbosity = config.getint("speedtest", "logVerbosity")
    st_serverID = config.getint("speedtest", "serverID")
    st_hostname = config.get("speedtest", "hostname")
    st_ipAddress = config.get("speedtest", "ipAddress")
    st_interface = config.get("speedtest", "interface")

    speedtestExe = config.get("paths", "speedtestExe")

    logger.setLevel(logLevel)

    logger.debug(f"Read values interval={interval}, logLevel={logLevel}, logVerbosity={st_logVerbosity}, "
                 f"serverID={st_serverID}, hostname={st_hostname}, ipAddress={st_ipAddress}, interface={st_interface}")
except:
    logger.critical(f"Unable to read values from config file at {CONFIG_PATH}: ", exc_info=1)
    exit()

# Initialize object for interaction with the Speedtest exe
speedtest = Speedtest(speedtestExe, st_logVerbosity, st_serverID, st_hostname, st_ipAddress, st_interface)
logger.debug(f"Speedtest object created: {speedtest}")

# Initialize database for test results
db.setupDb()

# Start periodic testing
delay = interval * 60  # Interval in seconds

logger.info(f"Starting periodic speedtest running and collecting of results every {interval} minutes")
if interval < 1.1:
    logger.warning("A very short interval between tests (<1 minute) may cause issues")

while True:
    logger.info("New periodic test started")
    doPeriodicTest()
    logger.debug(f"Finished test, now waiting for {interval} minutes")
    sleep(delay)
