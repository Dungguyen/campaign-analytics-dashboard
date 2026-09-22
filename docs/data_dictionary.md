dim_campaign
-------------
campaign_id       PK
campaign_name
created_date
scheduled_date
status

dim_channel
-----------
channel_id        PK
channel_name

fact_delivery_log
-----------------
delivery_log_id   PK
campaign_id       FK
channel_id        FK
sent_at
sent
delivered
failed
clicks

dim_calendar
------------
date              PK
month
quarter
year