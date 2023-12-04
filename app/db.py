from datetime import datetime
import sqlite3
from configparser import ConfigParser
import logging
from pathlib import Path

CONFIG_PATH = "./config.ini"
connection: sqlite3.Connection = None

# At this point the config should be safe
config = ConfigParser()
config.read(CONFIG_PATH)

logger = logging.getLogger(__name__)
logLevel = config.get("basic", "logLevel")
logger.setLevel(logLevel)

dbPath = Path(config.get("paths", "dbPath"))
migrationsDir = Path(config.get("paths", "migrationsDir"))
logger.debug(f"DB path: {dbPath.resolve()}")


def setupDb():
    global connection

    if dbPath.exists():
        logger.debug("Connecting to an existing DB")
    else:
        logger.debug("Creating and connectinng to a new DB")

    connection = sqlite3.connect(dbPath)
    cursor = getCursor()

    # Check migrations table and see if any are needed
    checkAddedMigrations()


def getCursor():
    global connection
    return connection.cursor()


def checkAddedMigrations():
    # Check existence of the migrations table, create it if there isn't one
    if not hasTable("migrations"):
        migrateIntoDb(migrationsDir / "add-migrations-table.sql")

    for migration in migrationsDir.iterdir():
        if migration.suffix != ".sql":
            continue

        migName = migration.stem

        if not hasMigration(migName):
            migrateIntoDb(migration)


def migrateIntoDb(migration):
    cursor = getCursor()

    # Execute the migration
    with open(migration, "r") as migFile:
        migSql = migFile.read()
        cursor.executescript(migSql)

    # Log migration in migrations table
    dateNow = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    addRecord("migrations", ["name","mig_date"], [f"'{migration.stem}'", f"'{dateNow}'"])
    cursor.close()


def hasMigration(migName):
    cursor = getCursor()

    cursor.execute(
        f"SELECT name FROM migrations WHERE name='{migName}';"
    )

    result = cursor.fetchall()
    cursor.close()
    return len(result) == 1


def hasTable(table):
    cursor = getCursor()

    cursor.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';"
    )

    result = cursor.fetchall()
    cursor.close()

    return len(result) == 1


def addRecord(table, cols, values):
    cursor = getCursor()

    cursor.execute(
        f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join(values)})"
    )
    global connection
    connection.commit()
    cursor.close()
