-- Hiring Momentum pillar coverage assessment
-- Source: periods_monthly_employees_agg (client level)
SELECT
  'monthly_agg_client_level' AS source,
  COUNT(DISTINCT client_id) AS clients_with_data,
  ROUND(AVG(CASE WHEN new_hire IS NOT NULL THEN 1 ELSE 0 END) * 100, 1) AS new_hire_completeness,
  ROUND(AVG(CASE WHEN new_hire_ratio IS NOT NULL THEN 1 ELSE 0 END) * 100, 1) AS new_hire_ratio_completeness,
  SUM(CASE WHEN new_hire > 0 THEN 1 ELSE 0 END) AS rows_with_hires,
  COUNT(*) AS total_rows
FROM prod.master_insight.periods_monthly_employees_agg
WHERE level_agg = 'client';
