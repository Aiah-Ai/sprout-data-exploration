-- Unanticipated Pillar: Internal Mobility
-- Source: curated_insight.dim_hr_employee_movements
SELECT action_for, COUNT(*) AS movements, COUNT(DISTINCT employee_database_key) AS distinct_employees
FROM prod.curated_insight.dim_hr_employee_movements
GROUP BY action_for
ORDER BY movements DESC
LIMIT 15;

-- Movement type boolean flags
SELECT
  COUNT(DISTINCT employee_database_key) AS total_movements_employees,
  SUM(CASE WHEN is_position_change = true THEN 1 ELSE 0 END) AS position_changes,
  SUM(CASE WHEN is_dept_change = true THEN 1 ELSE 0 END) AS dept_changes,
  SUM(CASE WHEN is_employment_type_change = true THEN 1 ELSE 0 END) AS emp_type_changes,
  SUM(CASE WHEN is_employment_status_change = true THEN 1 ELSE 0 END) AS status_changes
FROM prod.curated_insight.dim_hr_employee_movements;

-- Overtime coverage
SELECT
  COUNT(DISTINCT database) AS companies_with_ot,
  COUNT(*) AS total_records,
  ROUND(AVG(CASE WHEN hrOvertimeIsOrdOT IS NOT NULL THEN 1 ELSE 0 END) * 100, 1) AS ot_hours_completeness,
  MIN(hrOvertimeDate) AS min_date,
  MAX(hrOvertimeDate) AS max_date
FROM prod.raw_hr.overtime;

-- Demographics coverage in monthly agg
SELECT
  ROUND(AVG(CASE WHEN male IS NOT NULL THEN 1 ELSE 0 END) * 100, 1) AS gender_completeness,
  ROUND(AVG(CASE WHEN age_18_24 IS NOT NULL THEN 1 ELSE 0 END) * 100, 1) AS age_completeness,
  ROUND(AVG(CASE WHEN male + female = total_employees THEN 1 ELSE 0 END) * 100, 1) AS gender_sum_match_pct
FROM prod.master_insight.periods_monthly_employees_agg
WHERE level_agg = 'client';
