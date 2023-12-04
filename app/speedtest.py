import logging
from configparser import ConfigParser
import subprocess
import json

CONFIG_PATH = "./config.ini"


class Speedtest:
    INVALID_RUN = {"status": "fail"}
    MAX_VERBOSITY = 3

    def __init__(self, exePath, verbosity, serverID, hostname, ipAddress, interface):
        # Set the log level
        # There's no way the config is unreadable at this point
        config = ConfigParser()
        config.read(CONFIG_PATH)
        logLevel = config.get("basic", "logLevel")

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logLevel)

        self.logger.debug("Initializing speedtest object")
        self.exePath = exePath

        if verbosity is None or verbosity < 0:
            verbosity = 0
        elif verbosity > self.MAX_VERBOSITY:
            verbosity = self.MAX_VERBOSITY

        if serverID < 0:
            serverID = None

        if hostname is not None and len(hostname) == 0:
            hostname = None

        if ipAddress is not None and len(ipAddress) == 0:
            ipAddress = None

        if interface is not None and len(interface) == 0:
            interface = None

        self.verbosity = verbosity
        self.serverID = serverID
        self.hostname = hostname
        self.ipAddress = ipAddress
        self.interface = interface

    def getArgs(self):
        """
        Creates list of arguments to be used in subprocess.run()
        :rtype: list
        """
        # First argument should be the path to the exe itself
        # The output format should be JSON for future parsing
        args = [self.exePath, "--format=json", "--accept-gdpr", "--accept-license"]

        if self.verbosity == 0:
            # No log messages from the speedtest exe
            verbosity = None
        else:
            verbosity = "-" + "v" * self.verbosity

        if verbosity is not None:
            args.append(verbosity)

        # Check if sID is present and valid
        if self.serverID is not None:
            args.append(f"-s {self.serverID}")

        if self.hostname is not None:
            args.append(f"-o {self.hostname}")

        if self.ipAddress is not None:
            args.append(f"-i {self.ipAddress}")

        if self.interface is not None:
            args.append(f"-I {self.interface}")

        self.logger.debug(f"getArgs() result: [{' '.join(args)}]")
        return args

    def runTest(self):
        """
        Runs a single test using the defined Speedtest.exe
        :return: Parsed JSON results of the run
        :rtype: dict
        """
        self.logger.debug("Attempting a run of speedtesting")
        args = self.getArgs()

        # Call the run using the args and save stdout and stderr output
        try:
            runResult = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
        except:
            self.logger.critical("Speedtest run failed: ", exc_info=1)
            return self.INVALID_RUN
        else:
            self.logger.debug(f"Run result STDOUT: {runResult.stdout}")
            self.logger.debug(f"Run result STDERR: {runResult.stderr}")

        try:
            result = json.loads(runResult.stdout)

            result["status"] = "ok"
            # Converting bytes per second to megabits per second for readability
            result["download"]["bandwidthMbps"] = result["download"]["bandwidth"] / 125000
            result["upload"]["bandwidthMbps"] = result["upload"]["bandwidth"] / 125000

            self.logger.debug(f"Returned dict: {result}")
            return result
        except:
            self.logger.error(f"Failed to parse result JSON of speedtest run: {runResult.stdout}")
            return self.INVALID_RUN
