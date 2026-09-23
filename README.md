   dim_campaign
                         1
                         │
                         *
dim_calendar 1 ─── * fact_delivery_log * ─── 1 dim_channel

dim_campaign[campaign_id]
    1 → * fact_delivery_log[campaign_id]

dim_channel[channel_id]
    1 → * fact_delivery_log[channel_id]

dim_calendar[date]
    1 → * fact_delivery_log[sent_date]