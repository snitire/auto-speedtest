import logging
from configparser import ConfigParser
import subprocess
import json

MAX_VERBOSITY = 3
CONFIG_PATH = "./config.ini"


class Speedtest:
    def __init__(self, exePath, verbosity, serverID, hostname, ipAddress, interface):
        # Set the log level
        # There's no way the config is unreadable at this point
        config = ConfigParser()
        config.read(CONFIG_PATH)
        logLevel = config.get("basic", "logLevel")

        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logLevel)

        self.__logger.debug("Initializing speedtest object")
        self.exePath = exePath

        if verbosity is None or verbosity < 0:
            verbosity = 0
        elif verbosity > MAX_VERBOSITY:
            verbosity = MAX_VERBOSITY

        if serverID < 0:
            serverID = None

        if hostname is not None and len(hostname) == 0:
            hostname = None

        if ipAddress is not None and len(ipAddress) == 0:
            ipAddress = None

        if interface is not None and len(interface) == 0:
            interface = None

        self.__verbosity = verbosity
        self.__serverID = serverID
        self.__hostname = hostname
        self.__ipAddress = ipAddress
        self.__interface = interface

    def getArgs(self):
        """
        Creates list of arguments to be used in subprocess.run()
        :rtype: list
        """
        # First argument should be the path to the exe itself
        # The output format should be JSON for future parsing
        args = [self.exePath, "--format=json-pretty"]

        if self.__verbosity == 0:
            # No log messages from the speedtest exe
            verbosity = None
        else:
            verbosity = "-" + "v" * self.__verbosity
        if verbosity is not None: args.append(verbosity)

        # Check if sID is present and valid
        if self.__serverID is None:
            serverID = None
        else:
            serverID = f"-s {self.__serverID}"
        if serverID is not None: args.append(serverID)

        if self.__hostname is not None: args.append(f"-o {self.__hostname}")
        if self.__ipAddress is not None: args.append(f"-i {self.__ipAddress}")
        if self.__interface is not None: args.append(f"-I {self.__interface}")

        self.__logger.debug(f"getArgs() result: [{' '.join(args)}]")
        return args

    def runTest(self):
        """
        Runs a single test using the defined Speedtest.exe
        :return: Parsed JSON results of the run
        :rtype: dict
        """
        self.__logger.info("Attempting a run of speedtesting")
        args = self.getArgs()
        # Call the run using the args and save stdout and stderr output
        try:
            runResult = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
        except:
            self.__logger.critical("Speedtest run failed: ", exc_info=1)
        else:
            self.__logger.debug(f"Run result STDOUT: {runResult.stdout}")
            self.__logger.debug(f"Run result STDERR: {runResult.stderr}")

        try:
            result = json.loads(runResult.stdout)
            self.__logger.debug(f"Returned dict: {result}")
            return result
        except:
            self.__logger.error(f"Failed to parse result JSON of speedtest run: {runResult.stdout}")
