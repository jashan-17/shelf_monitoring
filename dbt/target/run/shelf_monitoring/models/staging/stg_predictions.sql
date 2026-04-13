
  create view "shelf_monitoring"."public"."stg_predictions__dbt_tmp"
    
    
  as (
    select
    id,
    image_name,
    actual_label,
    predicted_label,
    confidence,
    created_at
from raw_predictions
  );