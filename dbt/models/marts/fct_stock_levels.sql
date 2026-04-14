select
    predicted_label as stock_level,
    count(*) as total_images,
    round(avg(confidence)::numeric, 2) as avg_confidence
from {{ ref('stg_predictions') }}
group by predicted_label
order by total_images desc