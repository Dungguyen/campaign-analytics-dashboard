# DAX Measures

## 1. Overview

This document describes the core DAX measures used by the Campaign Analytics
Dashboard.

The measures are designed to work with the star schema and respect the current
Power BI filter context, including:

- Reporting period
- Campaign
- Channel
- Campaign status

---

## 2. Core Delivery Measures

### Total Campaigns

```DAX
Total Campaigns =
DISTINCTCOUNT(dim_campaign[campaign_id])
```

Counts unique campaigns rather than rows from the delivery fact table.

`DISTINCTCOUNT` is required because one campaign can have multiple delivery
events across different channels and send timestamps.

---

### Total Sent

```DAX
Total Sent =
SUM(fact_delivery_log[sent])
```

Total number of delivery attempts within the current filter context.

---

### Total Delivered

```DAX
Total Delivered =
SUM(fact_delivery_log[delivered])
```

Total number of successfully delivered messages.

---

### Total Failed

```DAX
Total Failed =
SUM(fact_delivery_log[failed])
```

Total number of failed delivery attempts.

The generated dataset follows the business rule:

```text
Sent = Delivered + Failed
```

---

### Total Clicks

```DAX
Total Clicks =
SUM(fact_delivery_log[clicks])
```

Total number of clicks generated from delivered messages.

This measure is used by the Top Campaigns by Clicks visual and CTR calculation.

---

## 3. Rate Measures

### Delivery Rate

```DAX
Delivery Rate =
DIVIDE(
    [Total Delivered],
    [Total Sent],
    0
)
```

Measures the proportion of sent messages that were successfully delivered.

Business definition:

```text
Delivery Rate = Delivered / Sent
```

`DIVIDE()` is used instead of the `/` operator because it safely handles cases
where the denominator is zero.

The measure is formatted as a percentage in Power BI.

---

### CTR

```DAX
CTR =
DIVIDE(
    [Total Clicks],
    [Total Delivered],
    0
)
```

CTR represents the proportion of successfully delivered messages that resulted
in clicks.

Business definition:

```text
CTR = Clicks / Delivered
```

The denominator is `Delivered`, not `Sent`, because the project defines CTR
based on messages that successfully reached the recipient.

The measure is formatted as a percentage.

---

## 4. Campaign Status Measures

### Scheduled Campaigns

```DAX
Scheduled Campaigns =
CALCULATE(
    [Total Campaigns],
    dim_campaign[status] = "Scheduled"
)
```

Counts campaigns whose current status is Scheduled.

Scheduled campaigns intentionally have no rows in `fact_delivery_log` because
they have not yet produced delivery events.

---

### Error Campaigns

```DAX
Error Campaigns =
CALCULATE(
    [Total Campaigns],
    dim_campaign[status] IN {
        "Failed",
        "Partial Success"
    }
)
```

Counts campaigns classified as either:

- Failed
- Partial Success

These statuses represent campaigns that experienced complete or partial
delivery problems.

---

## 5. Filter Context

The measures are designed to respond to Power BI filter context.

For example, selecting:

```text
Channel = LINE OA
```

filters `dim_channel`, which propagates through the relationship:

```text
dim_channel
     |
     | 1:N
     v
fact_delivery_log
```

As a result, delivery measures such as:

- Total Sent
- Total Delivered
- Total Failed
- Total Clicks
- Delivery Rate
- CTR

are recalculated only for LINE OA delivery events.

The model uses single-direction dimension-to-fact relationships rather than
bidirectional filtering.

---

## 6. Important Semantic Behavior

### Campaign Count vs Delivery Rows

`Total Campaigns` does not use:

```DAX
COUNTROWS(fact_delivery_log)
```

because the fact table is at delivery-event grain.

A campaign may appear multiple times because it can:

- use multiple channels;
- have multiple send timestamps.

Therefore campaign counting must happen using the campaign dimension.

### Scheduled Campaigns and Delivery Metrics

Scheduled campaigns do not have delivery events.

Therefore, when the report is filtered to:

```text
Status = Scheduled
```

delivery metrics can be blank or zero depending on the measure and visual
configuration.

This is expected business behavior rather than missing delivery data.

---

## 7. Validation Baseline

The final dataset was independently validated against the source CSV files.

### Full Dataset

| Metric | Expected Value |
|---|---:|
| Total Campaigns | 50,000 |
| Total Sent | 11,243,896,863 |
| Total Delivered | 7,249,920,636 |
| Total Failed | 3,993,976,227 |
| Total Clicks | 531,443,630 |
| Delivery Rate | 64.48% |
| CTR | 7.33% |

The following business equation was also validated:

```text
7,249,920,636 + 3,993,976,227
= 11,243,896,863

Delivered + Failed = Sent
```

### LINE OA Validation

A second validation was performed with:

```text
Channel = LINE OA
```

Expected results:

| Metric | Expected Value |
|---|---:|
| Total Sent | 2,693,928,399 |
| Total Delivered | 1,732,937,509 |
| Total Failed | 960,990,890 |
| Total Clicks | 173,100,714 |
| Delivery Rate | 64.33% |
| CTR | 9.99% |

The Python source calculation and Power BI results matched for both the
full dataset and the LINE OA filtered context.

---

## 8. Measure Design Principles

The dashboard follows these principles:

1. Business calculations are implemented as measures rather than calculated
   columns when the result depends on report filter context.
2. Additive delivery metrics use `SUM`.
3. Campaign counts use `DISTINCTCOUNT`.
4. Ratios use `DIVIDE` to safely handle zero denominators.
5. Measures reuse existing measures where possible.
6. Dimension filters propagate to the fact table through the star schema.
7. Business definitions are documented alongside their DAX implementation.