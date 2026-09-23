# Data Quality Report

Generated: 2026-09-23 23:56:06

## Summary

| Metric | Result |
|---|---:|
| Overall Status | PASS |
| Total Checks | 29 |
| Passed | 29 |
| Failed | 0 |
| Warnings | 0 |

## Dataset Overview

| Dataset | Rows | Columns |
|---|---:|---:|
| dim_campaign | 50,000 | 5 |
| dim_channel | 5 | 2 |
| dim_calendar | 1,096 | 8 |
| fact_delivery_log | 500,000 | 9 |

## Validation Results

| Category | Dataset | Check | Violations | Status |
|---|---|---|---:|---|
| Completeness | dim_campaign | Required fields must not be null | 0 | PASS |
| Completeness | dim_channel | Required fields must not be null | 0 | PASS |
| Completeness | dim_calendar | Required fields must not be null | 0 | PASS |
| Completeness | fact_delivery_log | Required fields must not be null | 0 | PASS |
| Uniqueness | dim_campaign | campaign_id must be unique | 0 | PASS |
| Uniqueness | dim_channel | channel_id must be unique | 0 | PASS |
| Uniqueness | dim_calendar | date must be unique | 0 | PASS |
| Uniqueness | fact_delivery_log | delivery_log_id must be unique | 0 | PASS |
| Validity | dim_campaign | Campaign status must be valid | 0 | PASS |
| Validity | fact_delivery_log | sent must be non-negative | 0 | PASS |
| Validity | fact_delivery_log | delivered must be non-negative | 0 | PASS |
| Validity | fact_delivery_log | failed must be non-negative | 0 | PASS |
| Validity | fact_delivery_log | clicks must be non-negative | 0 | PASS |
| Referential Integrity | fact_delivery_log | campaign_id must exist in dim_campaign | 0 | PASS |
| Referential Integrity | fact_delivery_log | channel_id must exist in dim_channel | 0 | PASS |
| Referential Integrity | fact_delivery_log | sent_date must exist in dim_calendar | 0 | PASS |
| Consistency | dim_campaign | scheduled_date must not be before created_date | 0 | PASS |
| Consistency | fact_delivery_log | sent_date must match date component of sent_at | 0 | PASS |
| Consistency | fact_delivery_log | sent_at must not be before scheduled_date | 0 | PASS |
| Consistency | dim_calendar | day must match date | 0 | PASS |
| Consistency | dim_calendar | month must match date | 0 | PASS |
| Consistency | dim_calendar | year must match date | 0 | PASS |
| Consistency | dim_calendar | quarter must match date | 0 | PASS |
| Consistency | dim_calendar | month_year must match date | 0 | PASS |
| Consistency | dim_calendar | day_of_week must match date | 0 | PASS |
| Business Rule | fact_delivery_log | delivered + failed must equal sent | 0 | PASS |
| Business Rule | fact_delivery_log | clicks must not exceed delivered | 0 | PASS |
| Business Rule | fact_delivery_log | Scheduled campaigns must not have delivery logs | 0 | PASS |
| Business Rule | fact_delivery_log | Fact must contain at least 500,000 rows | 0 | PASS |