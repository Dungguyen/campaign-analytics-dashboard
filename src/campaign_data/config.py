from pathlib import Path

RANDOM_SEED = 42

NUM_CAMPAIGNS = 50_000
NUM_DELIVERY_LOGS = 500_000

START_DATE = "2024-01-01"
END_DATE = "2026-12-31"

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

CAMPAIGN_STATUSES = [
    "Scheduled",
    "Running",
    "Completed",
    "Failed",
    "Partial Success",
]

CHANNELS = [
    (1, "PWA"),
    (2, "LINE OA"),
    (3, "Email"),
    (4, "SMS"),
    (5, "Push Notification"),
]