from urllib.request import urlretrieve
from pathlib import Path
from configparser import ConfigParser
from zipfile import ZipFile
import os

ST_DL_URL = "https://install.speedtest.net/app/cli/ookla-speedtest-1.2.0-win64.zip"
CONFIG_PATH = "./config.ini"

config = ConfigParser()
config.read(CONFIG_PATH)

# Get and create the speedtest folder if necessary
speedtestExePath = Path(config.get("paths", "speedtestExe"))
speedtestDir = speedtestExePath.parent
speedtestDir.mkdir(exist_ok=True)
speedtestZipPath = speedtestDir / "speedtestDL.zip"

# Download the .zip file to the speedtest exe folder
urlretrieve(ST_DL_URL, speedtestZipPath)

# Extract the .exe
ZipFile(speedtestZipPath,"r").extract("speedtest.exe", speedtestDir)

# Delete the .zip file
os.remove(speedtestZipPath)
