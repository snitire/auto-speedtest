from datetime import datetime
import sqlite3
from configparser import ConfigParser
import logging.config
from pathlib import Path

CONFIG_PATH = "./config.ini"
connection: sqlite3.Connection = None
logger: logging.Logger = None

# At this point the config should be safe
config = ConfigParser()
config.read(CONFIG_PATH)

logLevel = config.get("basic", "logLevel")
dbPath = Path(config.get("paths", "dbPath"))
migrationsDir = Path(config.get("paths", "migrationsDir"))


def setupDb():
    global connection, logger
    # Define logger here, so it is created after being configured by .yaml in app.py
    logger = logging.getLogger(__name__)
    logger.setLevel(logLevel)
    logger.debug(f"DB path: '{dbPath.resolve()}'")
    logger.debug(f"Migration file path: '{migrationsDir.resolve()}'")

    if dbPath.exists():
        logger.debug("Connecting to an existing DB")
    else:
        logger.debug("Creating and connectinng to a new DB")

    try:
        connection = sqlite3.connect(dbPath)
    except:
        logger.critical(f"Unable to establish DB connection in '{dbPath.resolve()}': ", exc_info=1)

    # Check migrations table and see if any are needed
    checkAddedMigrations()


def getCursor():
    global connection
    return connection.cursor()


def checkAddedMigrations():
    # Check existence of the migrations table, create it if there isn't one
    if not hasTable("migrations"):
        logger.debug("No 'migrations' table found in DB. Adding new one")
        migrateIntoDb(migrationsDir / "add-migrations-table.sql")

    for migration in migrationsDir.iterdir():
        migName = migration.stem

        if migration.suffix != ".sql":
            logger.debug(f"Skipping non-SQL file '{migration.name}' in migration folder")
            continue

        if not hasMigration(migName):
            logger.debug(f"New DB migration found: '{migName}'")
            migrateIntoDb(migration)


def migrateIntoDb(migration):
    cursor = getCursor()
    migName = migration.stem

    # Execute the migration
    with open(migration, "r") as migFile:
        migSql = migFile.read()
        try:
            cursor.executescript(migSql)
        except:
            logger.error(f"Unable to execute migration '{migration.resolve()}': ", exc_info=1)
        else:
            logger.debug(f"Successfully added migration '{migName}'")

    # Log migration in migrations table
    dateNow = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    addRecord("migrations", ["name","mig_date"], [f"'{migName}'", f"'{dateNow}'"])
    cursor.close()


def hasMigration(migName):
    cursor = getCursor()

    cursor.execute(
        f"SELECT name FROM migrations WHERE name='{migName}';"
    )

    result = cursor.fetchall()
    cursor.close()

    if len(result) >= 1:
        logger.debug(f"Found existing migration '{migName}'")
        return True
    else:
        logger.debug(f"Did not find '{migName}' in 'migrations' table")
        return False


def hasTable(table):
    cursor = getCursor()

    cursor.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';"
    )

    result = cursor.fetchall()
    cursor.close()

    if len(result) >= 1:
        logger.debug(f"Found table '{table}'")
        return True
    else:
        logger.debug(f"Did not find table '{table}'")
        return False


def addRecord(table, cols, values):
    global connection
    cursor = getCursor()

    try:
        query = f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join(values)})"

        logger.debug(f"Adding new record to table '{table}': {query}")
        cursor.execute(query)
    except:
        logger.error(f"Unexpected error while adding new record to DB: ", exc_info=1)

    connection.commit()
    cursor.close()
