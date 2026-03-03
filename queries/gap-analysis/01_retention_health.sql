-- Retention Health pillar coverage assessment
-- Source: periods_monthly_employees_agg (client level)
SELECT
  COUNT(DISTINCT client_id) AS clients_with_data,
  COUNT(*) AS total_rows,
  ROUND(AVG(CASE WHEN exit_rate_pct IS NOT NULL THEN 1 ELSE 0 END) * 100, 1) AS exit_rate_completeness,
  ROUND(AVG(CASE WHEN exits IS NOT NULL THEN 1 ELSE 0 END) * 100, 1) AS exits_completeness,
  ROUND(AVG(CASE WHEN exit_voluntary IS NOT NULL THEN 1 ELSE 0 END) * 100, 1) AS voluntary_completeness,
  ROUND(AVG(CASE WHEN active_employees IS NOT NULL THEN 1 ELSE 0 END) * 100, 1) AS active_emp_completeness,
  COUNT(DISTINCT month_period) AS periods,
  MIN(month_period) AS min_period,
  MAX(month_period) AS max_period
FROM prod.master_insight.periods_monthly_employees_agg
WHERE level_agg = 'client';
