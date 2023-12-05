import os
from pathlib import Path
from configparser import ConfigParser

CONFIG_PATH = "./config.ini"

# Change to usual run.py CWD (auto-speedtest/)
os.chdir("..")


def checkConfig(configPath):
    print("Checking " + configPath)

    print("Check if config is present:")
    assert Path(CONFIG_PATH).exists()
    print("Pass")

    # Getting the config for further testing
    config = ConfigParser()
    config.read(CONFIG_PATH)

    print("Check if all 'basic' values are present")
    assert config.has_section("basic")
    assert config.has_option("basic", "runInBackground")
    assert config.has_option("basic", "testInterval")
    assert config.has_option("basic", "logLevel")
    print("Pass")

    print("Check if all 'speedtest' values are present")
    assert config.has_section("speedtest")
    assert config.has_option("speedtest", "logVerbosity")
    assert config.has_option("speedtest", "serverID")
    assert config.has_option("speedtest", "hostname")
    assert config.has_option("speedtest", "ipAddress")
    assert config.has_option("speedtest", "interface")
    print("Pass")

    print("Check if all 'paths' values are present")
    assert config.has_section("paths")
    assert config.has_option("paths", "speedtestExe")
    assert config.has_option("paths", "migrationsDir")
    assert config.has_option("paths", "dbPath")
    assert config.has_option("paths", "pythonExe")
    assert config.has_option("paths", "pythonwExe")
    print("Pass")


# Test normal config
checkConfig(CONFIG_PATH)
print()
# Test template
checkConfig(CONFIG_PATH + ".template")
