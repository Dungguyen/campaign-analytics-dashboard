import random
from datetime import timedelta

import pandas as pd
from faker import Faker

from campaign_data.config import (
    CAMPAIGN_STATUSES,
    END_DATE,
    NUM_CAMPAIGNS,
    RANDOM_SEED,
    RAW_DATA_DIR,
    START_DATE,
)


def generate_campaigns() -> pd.DataFrame:
    fake = Faker()
    fake.seed_instance(RANDOM_SEED)
    random.seed(RANDOM_SEED)

    start_date = pd.Timestamp(START_DATE)
    end_date = pd.Timestamp(END_DATE)

    campaigns = []

    for i in range(1, NUM_CAMPAIGNS + 1):
        campaign_id = f"CMP{i:06d}"

        created_date = fake.date_between(
            start_date=start_date.date(),
            end_date=end_date.date(),
        )

        max_delay = min(
            30,
            (end_date.date() - created_date).days,
        )

        schedule_delay = random.randint(0, max_delay)

        scheduled_date = created_date + timedelta(
            days=schedule_delay
        )

        campaign_name = (
            f"{fake.word().title()} "
            f"{fake.word().title()} "
            f"{scheduled_date.year}"
        )

        status = random.choice(CAMPAIGN_STATUSES)

        campaigns.append(
            {
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "created_date": created_date,
                "scheduled_date": scheduled_date,
                "status": status,
            }
        )

    return pd.DataFrame(campaigns)


def save_campaigns(df: pd.DataFrame) -> None:
    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = RAW_DATA_DIR / "dim_campaign.csv"

    df.to_csv(
        output_path,
        index=False,
    )

    print(f"Generated {len(df):,} campaigns")
    print(f"Saved to: {output_path}")


def main() -> None:
    df = generate_campaigns()
    save_campaigns(df)


if __name__ == "__main__":
    main()