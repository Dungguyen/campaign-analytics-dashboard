# Campaign Analytics Dashboard

An end-to-end Data Engineering and Business Intelligence project for analyzing
campaign delivery performance across multiple communication channels.

The project generates a reproducible synthetic campaign dataset, validates data
quality with automated Python checks, models the data using a star schema, and
presents business KPIs through an interactive Power BI dashboard.

## Project Overview

Marketing campaigns can be delivered through multiple channels such as PWA,
LINE OA, Email, SMS, and Push Notification.

The goal of this project is to provide a reliable analytical layer for
monitoring campaign delivery performance and answering questions such as:

- How many campaigns have been created?
- How many messages were sent, delivered, or failed?
- What is the overall delivery rate?
- What is the click-through rate (CTR)?
- Which channels generate the highest delivery volume?
- Which campaigns generate the most clicks?
- How does campaign performance change over time?

## Architecture

The project follows this analytical workflow:

```text
Business Requirements
        |
        v
Synthetic Data Generation
Python + Faker + NumPy + Pandas
        |
        v
Raw CSV Dataset
        |
        v
Automated Data Quality Validation
        |
        v
Power Query
        |
        v
Power BI Star Schema
        |
        v
DAX Semantic Layer
        |
        v
Interactive Campaign Dashboard
```

Generated raw datasets are intentionally excluded from Git because they can be
reproduced from the Python generation pipeline.

## Tech Stack

| Area | Technology |
|---|---|
| Language | Python 3.12 |
| Environment / Dependency Management | uv |
| Data Generation | Faker, NumPy, Pandas |
| Data Validation | Python, pytest |
| Data Transformation | Power Query |
| Data Modeling | Star Schema |
| Analytics | DAX |
| Visualization | Power BI |
| Version Control | Git, GitHub |

## Dataset

The synthetic dataset contains:

| Table | Rows | Purpose |
|---|---:|---|
| `dim_campaign` | 50,000 | Campaign attributes and lifecycle status |
| `dim_channel` | 5 | Delivery channel definitions |
| `dim_calendar` | 1,096 | Reporting dates from 2024 through 2026 |
| `fact_delivery_log` | 500,000 | Campaign delivery events and performance metrics |

Supported channels:

- PWA
- LINE OA
- Email
- SMS
- Push Notification

Campaign statuses:

- Scheduled
- Running
- Completed
- Failed
- Partial Success

## Data Model

The Power BI semantic model uses a star schema.

```text
                     dim_campaign
                          |
                          | 1:N
                          |
dim_calendar 1:N --> fact_delivery_log <-- N:1 dim_channel
```

The grain of `fact_delivery_log` is:

> One campaign + one channel + one send timestamp.

This allows a campaign to be delivered through multiple channels and to have
multiple delivery events over time.

All dimension-to-fact relationships use single-direction filtering.

See `docs/data_model.md` for the complete modeling decisions and rationale.

## Business Metrics

The dashboard provides the following core KPIs:

- Total Campaigns
- Total Sent
- Total Delivered
- Total Failed
- Total Clicks
- Delivery Rate
- Click-Through Rate (CTR)
- Scheduled Campaigns
- Error Campaigns

Core definitions:

```text
Delivery Rate = Delivered / Sent

CTR = Clicks / Delivered
```

DAX uses safe division to handle zero denominators.

See `docs/dax_measures.md` for measure definitions and filter-context behavior.

## Data Quality

The project includes automated validation before the dataset is consumed by
Power BI.

Validation covers areas including:

- completeness;
- primary-key uniqueness;
- foreign-key integrity;
- valid campaign statuses;
- date consistency;
- non-negative metrics;
- delivery business rules;
- campaign lifecycle rules.

Important business constraints include:

```text
Delivered + Failed = Sent

Clicks <= Delivered

Scheduled campaigns have no delivery events
```

Final validation result:

```text
29 / 29 checks passed
0 failed
0 warnings
```

The generated dataset also passes the automated pytest suite.

The latest validation report is available at:

```text
reports/data_quality_report.md
```

## Power BI Dashboard

The Power BI dashboard contains:

- six primary KPI cards;
- Sent by Day trend analysis;
- Sent vs Delivered by Channel;
- Top 10 Campaigns by Clicks;
- Campaign Status Distribution;
- campaign delivery detail table;
- conditional formatting;
- interactive slicers;
- Reset Filters functionality.

Available filters include:

- Reporting Period
- Campaign
- Channel
- Campaign Status

Power BI artifact:

```text
powerbi/campaign_analytics_dashboard.pbix
```

See `powerbi/README.md` for dashboard-specific documentation.

## Validation Results

Power BI calculations were independently compared with calculations performed
directly against the generated CSV dataset using Python.

Full dataset baseline:

| Metric | Validated Result |
|---|---:|
| Total Campaigns | 50,000 |
| Total Sent | 11,243,896,863 |
| Total Delivered | 7,249,920,636 |
| Total Failed | 3,993,976,227 |
| Total Clicks | 531,443,630 |
| Delivery Rate | 64.48% |
| CTR | 7.33% |

A second validation was performed using only the LINE OA channel to verify
relationship propagation and DAX filter context.

Python and Power BI produced matching results.

## Project Structure

```text
campaign-analytics-dashboard/
|
|-- data/
|   |-- raw/
|   `-- processed/
|
|-- docs/
|   |-- requirements.md
|   |-- data_dictionary.md
|   |-- data_model.md
|   `-- dax_measures.md
|
|-- powerbi/
|   |-- campaign_analytics_dashboard.pbix
|   `-- README.md
|
|-- reports/
|   `-- data_quality_report.md
|
|-- src/
|   `-- campaign_data/
|       |-- config.py
|       |-- generate_campaigns.py
|       |-- generate_channels.py
|       |-- generate_calendar.py
|       |-- generate_delivery_logs.py
|       `-- validate.py
|
|-- tests/
|-- pyproject.toml
|-- uv.lock
`-- README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Dungguyen/campaign-analytics-dashboard.git
cd campaign-analytics-dashboard
```

### 2. Install dependencies

The project uses `uv` for Python environment and dependency management.

```bash
uv sync
```

Python 3.12 is used by the project.

### 3. Run automated tests

```bash
uv run pytest
```

### 4. Run data-quality validation

After generating the datasets:

```bash
uv run python src/campaign_data/validate.py
```

The validation report is written to:

```text
reports/data_quality_report.md
```

### 5. Open the Power BI dashboard

Open:

```text
powerbi/campaign_analytics_dashboard.pbix
```

in Power BI Desktop.

Because the Power BI data source uses local project files, the Power Query
source path may need to be updated when the repository is cloned to a different
location.

## Documentation

Detailed project documentation is available in:

- `docs/requirements.md` — business and dataset requirements
- `docs/data_dictionary.md` — field definitions
- `docs/data_model.md` — star-schema design and modeling decisions
- `docs/dax_measures.md` — DAX measures and semantic behavior
- `reports/data_quality_report.md` — automated data-quality results
- `powerbi/README.md` — Power BI dashboard documentation

## Key Engineering Decisions

Several design decisions were made deliberately:

- Fact-table grain was defined before metric generation.
- Campaign and channel attributes are modeled as dimensions.
- Delivery outcomes are stored at delivery-event grain.
- A dedicated calendar dimension is used for reporting.
- Relationships remain single-direction.
- Generated datasets are excluded from Git and remain reproducible.
- Data-quality rules are validated before BI consumption.
- Power BI metrics were cross-validated against Python calculations.

These decisions keep the project reproducible, testable, and easier to extend.