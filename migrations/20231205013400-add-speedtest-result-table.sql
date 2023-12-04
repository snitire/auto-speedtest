CREATE TABLE `results` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    `test_date` TEXT,
    `ping` REAL,
    `download_mbps` REAL,
    `upload_mbps` REAL,
    `packet_loss` REAL,
    `url` TEXT
)