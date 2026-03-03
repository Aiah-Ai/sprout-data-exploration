-- Workforce Stability pillar coverage assessment
-- Source: periods_monthly_employees_agg (client level)
SELECT
  'monthly_agg_client_level' AS source,
  COUNT(DISTINCT client_id) AS clients_with_data,
  ROUND(AVG(CASE WHEN tenure_0_3_months IS NOT NULL THEN 1 ELSE 0 END) * 100, 1) AS tenure_buckets_completeness,
  ROUND(AVG(CASE WHEN manager IS NOT NULL THEN 1 ELSE 0 END) * 100, 1) AS manager_completeness,
  ROUND(AVG(CASE WHEN manager_exit IS NOT NULL THEN 1 ELSE 0 END) * 100, 1) AS manager_exit_completeness,
  ROUND(AVG(CASE WHEN manager_short_tenure IS NOT NULL THEN 1 ELSE 0 END) * 100, 1) AS manager_short_tenure_completeness
FROM prod.master_insight.periods_monthly_employees_agg
WHERE level_agg = 'client';
