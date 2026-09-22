import pandas as pd

from campaign_data.config import (
    END_DATE,
    RAW_DATA_DIR,
    START_DATE,
)


def generate_calendar() -> pd.DataFrame:
    dates = pd.date_range(
        start=START_DATE,
        end=END_DATE,
        freq="D",
    )

    df = pd.DataFrame(
        {
            "date": dates,
        }
    )

    df["day"] = df["date"].dt.day
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.month_name()
    df["quarter"] = "Q" + df["date"].dt.quarter.astype(str)
    df["year"] = df["date"].dt.year
    df["month_year"] = df["date"].dt.strftime("%Y-%m")
    df["day_of_week"] = df["date"].dt.day_name()

    return df


def save_calendar(df: pd.DataFrame) -> None:
    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = RAW_DATA_DIR / "dim_calendar.csv"

    df.to_csv(
        output_path,
        index=False,
        date_format="%Y-%m-%d",
    )

    print(f"Generated {len(df):,} calendar rows")
    print(
        f"Date range: "
        f"{df['date'].min().date()} -> "
        f"{df['date'].max().date()}"
    )
    print(f"Saved to: {output_path}")


def main() -> None:
    df = generate_calendar()
    save_calendar(df)


if __name__ == "__main__":
    main()