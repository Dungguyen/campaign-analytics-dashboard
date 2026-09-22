from dataclasses import dataclass

import pandas as pd
from datetime import datetime
from campaign_data.config import (
    CAMPAIGN_STATUSES,
    NUM_DELIVERY_LOGS,
    RAW_DATA_DIR,
)


@dataclass
class ValidationResult:
    category: str
    dataset: str
    check: str
    violations: int
    severity: str = "ERROR"

    @property
    def status(self) -> str:
        if self.violations == 0:
            return "PASS"

        if self.severity == "WARNING":
            return "WARN"

        return "FAIL"

def load_datasets() -> dict[str, pd.DataFrame]:
    paths = {
        "dim_campaign": RAW_DATA_DIR / "dim_campaign.csv",
        "dim_channel": RAW_DATA_DIR / "dim_channel.csv",
        "dim_calendar": RAW_DATA_DIR / "dim_calendar.csv",
        "fact_delivery_log": RAW_DATA_DIR / "fact_delivery_log.csv",
    }

    missing_files = [
        str(path)
        for path in paths.values()
        if not path.exists()
    ]

    if missing_files:
        raise FileNotFoundError(
            "Missing required datasets:\n"
            + "\n".join(missing_files)
        )

    return {
        name: pd.read_csv(path)
        for name, path in paths.items()
    }


def validate_completeness(
    datasets: dict[str, pd.DataFrame],
) -> list[ValidationResult]:
    required_columns = {
        "dim_campaign": [
            "campaign_id",
            "campaign_name",
            "created_date",
            "scheduled_date",
            "status",
        ],
        "dim_channel": [
            "channel_id",
            "channel_name",
        ],
        "dim_calendar": [
            "date",
            "day",
            "month",
            "month_name",
            "quarter",
            "year",
            "month_year",
            "day_of_week",
        ],
        "fact_delivery_log": [
            "delivery_log_id",
            "campaign_id",
            "channel_id",
            "sent_at",
            "sent_date",
            "sent",
            "delivered",
            "failed",
            "clicks",
        ],
    }

    results = []

    for dataset_name, columns in required_columns.items():
        df = datasets[dataset_name]

        missing_columns = [
            column
            for column in columns
            if column not in df.columns
        ]

        if missing_columns:
            results.append(
                ValidationResult(
                    category="Completeness",
                    dataset=dataset_name,
                    check="Required columns exist",
                    violations=len(missing_columns),
                )
            )
            continue

        null_count = int(
            df[columns]
            .isnull()
            .sum()
            .sum()
        )

        results.append(
            ValidationResult(
                category="Completeness",
                dataset=dataset_name,
                check="Required fields must not be null",
                violations=null_count,
            )
        )

    return results


def validate_uniqueness(
    datasets: dict[str, pd.DataFrame],
) -> list[ValidationResult]:
    primary_keys = {
        "dim_campaign": "campaign_id",
        "dim_channel": "channel_id",
        "dim_calendar": "date",
        "fact_delivery_log": "delivery_log_id",
    }

    results = []

    for dataset_name, primary_key in primary_keys.items():
        df = datasets[dataset_name]

        violations = int(
            df[primary_key]
            .duplicated()
            .sum()
        )

        results.append(
            ValidationResult(
                category="Uniqueness",
                dataset=dataset_name,
                check=f"{primary_key} must be unique",
                violations=violations,
            )
        )

    return results


def validate_validity(
    datasets: dict[str, pd.DataFrame],
) -> list[ValidationResult]:
    campaign = datasets["dim_campaign"]
    fact = datasets["fact_delivery_log"]

    results = []

    invalid_statuses = int(
        (~campaign["status"].isin(CAMPAIGN_STATUSES)).sum()
    )

    results.append(
        ValidationResult(
            category="Validity",
            dataset="dim_campaign",
            check="Campaign status must be valid",
            violations=invalid_statuses,
        )
    )

    for column in [
        "sent",
        "delivered",
        "failed",
        "clicks",
    ]:
        violations = int(
            (fact[column] < 0).sum()
        )

        results.append(
            ValidationResult(
                category="Validity",
                dataset="fact_delivery_log",
                check=f"{column} must be non-negative",
                violations=violations,
            )
        )

    return results


def validate_referential_integrity(
    datasets: dict[str, pd.DataFrame],
) -> list[ValidationResult]:
    campaign = datasets["dim_campaign"]
    channel = datasets["dim_channel"]
    calendar = datasets["dim_calendar"]
    fact = datasets["fact_delivery_log"]

    results = []

    invalid_campaign_fk = int(
        (~fact["campaign_id"].isin(
            campaign["campaign_id"]
        )).sum()
    )

    results.append(
        ValidationResult(
            category="Referential Integrity",
            dataset="fact_delivery_log",
            check="campaign_id must exist in dim_campaign",
            violations=invalid_campaign_fk,
        )
    )

    invalid_channel_fk = int(
        (~fact["channel_id"].isin(
            channel["channel_id"]
        )).sum()
    )

    results.append(
        ValidationResult(
            category="Referential Integrity",
            dataset="fact_delivery_log",
            check="channel_id must exist in dim_channel",
            violations=invalid_channel_fk,
        )
    )

    fact_dates = pd.to_datetime(
        fact["sent_date"]
    ).dt.date

    calendar_dates = pd.to_datetime(
        calendar["date"]
    ).dt.date

    invalid_date_fk = int(
        (~fact_dates.isin(calendar_dates)).sum()
    )

    results.append(
        ValidationResult(
            category="Referential Integrity",
            dataset="fact_delivery_log",
            check="sent_date must exist in dim_calendar",
            violations=invalid_date_fk,
        )
    )

    return results


def validate_business_rules(
    datasets: dict[str, pd.DataFrame],
) -> list[ValidationResult]:
    campaign = datasets["dim_campaign"]
    fact = datasets["fact_delivery_log"]

    results = []

    delivery_equation_violations = int(
        (
            fact["delivered"]
            + fact["failed"]
            != fact["sent"]
        ).sum()
    )

    results.append(
        ValidationResult(
            category="Business Rule",
            dataset="fact_delivery_log",
            check="delivered + failed must equal sent",
            violations=delivery_equation_violations,
        )
    )

    click_violations = int(
        (
            fact["clicks"]
            > fact["delivered"]
        ).sum()
    )

    results.append(
        ValidationResult(
            category="Business Rule",
            dataset="fact_delivery_log",
            check="clicks must not exceed delivered",
            violations=click_violations,
        )
    )

    scheduled_campaign_ids = set(
        campaign.loc[
            campaign["status"] == "Scheduled",
            "campaign_id",
        ]
    )

    scheduled_fact_rows = int(
        fact["campaign_id"]
        .isin(scheduled_campaign_ids)
        .sum()
    )

    results.append(
        ValidationResult(
            category="Business Rule",
            dataset="fact_delivery_log",
            check="Scheduled campaigns must not have delivery logs",
            violations=scheduled_fact_rows,
        )
    )

    insufficient_rows = int(
        len(fact) < NUM_DELIVERY_LOGS
    )

    results.append(
        ValidationResult(
            category="Business Rule",
            dataset="fact_delivery_log",
            check=(
                f"Fact must contain at least "
                f"{NUM_DELIVERY_LOGS:,} rows"
            ),
            violations=insufficient_rows,
        )
    )

    return results


def run_validation(
    datasets: dict[str, pd.DataFrame],
) -> list[ValidationResult]:

    results = []

    results.extend(
        validate_completeness(datasets)
    )

    results.extend(
        validate_uniqueness(datasets)
    )

    results.extend(
        validate_validity(datasets)
    )

    results.extend(
        validate_referential_integrity(datasets)
    )

    results.extend(
        validate_consistency(datasets)
    )

    results.extend(
        validate_business_rules(datasets)
    )

    return results

def validate_consistency(
    datasets: dict[str, pd.DataFrame],
) -> list[ValidationResult]:
    campaign = datasets["dim_campaign"]
    calendar = datasets["dim_calendar"]
    fact = datasets["fact_delivery_log"]

    results = []

    # --------------------------------------------------------
    # Campaign date consistency
    # --------------------------------------------------------

    created_date = pd.to_datetime(
        campaign["created_date"]
    )

    scheduled_date = pd.to_datetime(
        campaign["scheduled_date"]
    )

    invalid_campaign_dates = int(
        (scheduled_date < created_date).sum()
    )

    results.append(
        ValidationResult(
            category="Consistency",
            dataset="dim_campaign",
            check="scheduled_date must not be before created_date",
            violations=invalid_campaign_dates,
        )
    )

    # --------------------------------------------------------
    # Fact sent_date vs sent_at
    # --------------------------------------------------------

    sent_at = pd.to_datetime(
        fact["sent_at"]
    )

    sent_date = pd.to_datetime(
        fact["sent_date"]
    )

    invalid_sent_dates = int(
        (
            sent_at.dt.normalize()
            != sent_date.dt.normalize()
        ).sum()
    )

    results.append(
        ValidationResult(
            category="Consistency",
            dataset="fact_delivery_log",
            check="sent_date must match date component of sent_at",
            violations=invalid_sent_dates,
        )
    )

    # --------------------------------------------------------
    # Fact sent_at vs campaign scheduled_date
    # --------------------------------------------------------

    fact_campaign = fact[
        [
            "campaign_id",
            "sent_at",
        ]
    ].merge(
        campaign[
            [
                "campaign_id",
                "scheduled_date",
            ]
        ],
        on="campaign_id",
        how="left",
    )

    invalid_send_timing = int(
        (
            pd.to_datetime(
                fact_campaign["sent_at"]
            )
            <
            pd.to_datetime(
                fact_campaign["scheduled_date"]
            )
        ).sum()
    )

    results.append(
        ValidationResult(
            category="Consistency",
            dataset="fact_delivery_log",
            check="sent_at must not be before scheduled_date",
            violations=invalid_send_timing,
        )
    )

    # --------------------------------------------------------
    # Calendar attribute consistency
    # --------------------------------------------------------

    calendar_date = pd.to_datetime(
        calendar["date"]
    )

    calendar_checks = {
        "day must match date": (
            calendar["day"]
            != calendar_date.dt.day
        ),
        "month must match date": (
            calendar["month"]
            != calendar_date.dt.month
        ),
        "year must match date": (
            calendar["year"]
            != calendar_date.dt.year
        ),
        "quarter must match date": (
            calendar["quarter"]
            != (
                "Q"
                + calendar_date.dt.quarter.astype(str)
            )
        ),
        "month_year must match date": (
            calendar["month_year"]
            != calendar_date.dt.strftime("%Y-%m")
        ),
        "day_of_week must match date": (
            calendar["day_of_week"]
            != calendar_date.dt.day_name()
        ),
    }

    for check_name, invalid_mask in calendar_checks.items():
        results.append(
            ValidationResult(
                category="Consistency",
                dataset="dim_calendar",
                check=check_name,
                violations=int(
                    invalid_mask.sum()
                ),
            )
        )

    return results


def generate_markdown_report(
    results: list[ValidationResult],
    datasets: dict[str, pd.DataFrame],
) -> None:
    report_dir = RAW_DATA_DIR.parent.parent / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    report_path = report_dir / "data_quality_report.md"

    passed = sum(result.status == "PASS" for result in results)
    failed = sum(result.status == "FAIL" for result in results)
    warnings = sum(result.status == "WARN" for result in results)

    if failed > 0:
        overall_status = "FAIL"
    elif warnings > 0:
        overall_status = "PASS WITH WARNINGS"
    else:
        overall_status = "PASS"

    lines = [
        "# Data Quality Report",
        "",
        f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}",
        "",
        "## Summary",
        "",
        "| Metric | Result |",
        "|---|---:|",
        f"| Overall Status | {overall_status} |",
        f"| Total Checks | {len(results)} |",
        f"| Passed | {passed} |",
        f"| Failed | {failed} |",
        f"| Warnings | {warnings} |",
        "",
        "## Dataset Overview",
        "",
        "| Dataset | Rows | Columns |",
        "|---|---:|---:|",
    ]

    for dataset_name, df in datasets.items():
        lines.append(
            f"| {dataset_name} | {len(df):,} | {len(df.columns)} |"
        )

    lines.extend([
        "",
        "## Validation Results",
        "",
        "| Category | Dataset | Check | Violations | Status |",
        "|---|---|---|---:|---|",
    ])

    for result in results:
        lines.append(
            f"| {result.category} "
            f"| {result.dataset} "
            f"| {result.check} "
            f"| {result.violations:,} "
            f"| {result.status} |"
        )

    report_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print(f"Data quality report: {report_path}")

def main() -> None:
    datasets = load_datasets()
    results = run_validation(datasets)

    print("\nDATA QUALITY VALIDATION")
    print("=" * 80)

    for result in results:
        print(
            f"[{result.status:<4}] "
            f"{result.category:<22} "
            f"{result.dataset:<20} "
            f"{result.check} "
            f"(violations={result.violations})"
        )

    generate_markdown_report(
        results,
        datasets,
    )

    failed = [
        result
        for result in results
        if result.status == "FAIL"
    ]

    print("=" * 80)

    if failed:
        print(
            f"Overall Status: FAIL "
            f"({len(failed)} failed checks)"
        )
        raise SystemExit(1)

    print(
        f"Overall Status: PASS "
        f"({len(results)} checks)"
    )


if __name__ == "__main__":
    main()