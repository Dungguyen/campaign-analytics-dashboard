# Campaign Analytics Power BI Dashboard

## Overview

This directory contains the Power BI dashboard for the Campaign Analytics
project.

The dashboard provides an analytical view of campaign delivery performance
across multiple communication channels.

## Power BI File

```text
campaign_analytics_dashboard.pbix
```

The PBIX file contains:

- Power Query transformations
- Star-schema semantic model
- DAX measures
- Interactive slicers
- KPI cards
- Campaign and channel performance visuals
- Campaign-level delivery details

## Dashboard KPIs

The Overview dashboard tracks:

- Total Campaigns
- Total Sent
- Total Delivered
- Total Failed
- Delivery Rate
- Click-Through Rate (CTR)

Additional measures include:

- Total Clicks
- Scheduled Campaigns
- Error Campaigns

## Dashboard Visuals

The report contains:

- KPI cards for campaign and delivery performance
- Sent by Day line chart
- Sent vs Delivered by Channel column chart
- Top 10 Campaigns by Clicks bar chart
- Campaign Status Distribution donut chart
- Campaign delivery detail table

The detail table contains:

```text
Campaign
Channel
Send Time
Status
Sent
Delivered
Failed
Clicks
```

Conditional formatting is used to highlight Delivered and Failed volumes.

## Filters

The dashboard supports filtering by:

- Reporting Period
- Campaign
- Channel
- Campaign Status

A Reset Filters button restores the report to its default state.

## Data Model

The report uses a star schema:

```text
                     dim_campaign
                          |
                          | 1:N
                          |
dim_calendar 1:N --> fact_delivery_log <-- N:1 dim_channel
```

Relationships use single-direction filtering from dimensions to the fact table.

See:

```text
../docs/data_model.md
```

for the complete model design and rationale.

## DAX Measures

Business metrics are implemented using DAX measures.

Examples include:

```DAX
Total Sent =
SUM(fact_delivery_log[sent])
```

```DAX
Delivery Rate =
DIVIDE(
    [Total Delivered],
    [Total Sent],
    0
)
```

```DAX
CTR =
DIVIDE(
    [Total Clicks],
    [Total Delivered],
    0
)
```

See:

```text
../docs/dax_measures.md
```

for the complete measure documentation.

## Validation

Dashboard results were validated independently against the generated source
CSV files using Python.

Full dataset baseline:

| Metric | Value |
|---|---:|
| Campaigns | 50,000 |
| Sent | 11,243,896,863 |
| Delivered | 7,249,920,636 |
| Failed | 3,993,976,227 |
| Clicks | 531,443,630 |
| Delivery Rate | 64.48% |
| CTR | 7.33% |

A second validation using only the `LINE OA` channel was also performed to
verify relationship propagation and DAX filter context.

Both Power BI and Python calculations produced matching results.

## Opening the Dashboard

1. Install Power BI Desktop.
2. Open:

```text
powerbi/campaign_analytics_dashboard.pbix
```

3. Use the slicers at the top of the dashboard to explore campaign performance.
4. Use **Reset Filters** to return to the default reporting view.

## Data Availability

Generated CSV datasets are intentionally excluded from Git because they are
reproducible from the Python data-generation pipeline.

The dataset can be regenerated from the project source code before refreshing
the Power BI model.