select
    predicted_label as stock_level,
    count(*) as total_images,
    round(avg(confidence)::numeric, 2) as avg_confidence
from "shelf_monitoring"."public"."stg_predictions"
group by predicted_label
order by total_images desc