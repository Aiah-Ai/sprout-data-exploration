-- Engagement & Absence pillar coverage assessment
-- Source: raw_hr.leaves
SELECT
  'leaves' AS source,
  COUNT(DISTINCT database) AS companies_with_leave_data,
  (SELECT COUNT(DISTINCT database) FROM prod.raw_hr.employees
   WHERE dateUtc = (SELECT MAX(dateUtc) FROM prod.raw_hr.employees)) AS total_companies,
  ROUND(COUNT(DISTINCT database) * 100.0 /
    (SELECT COUNT(DISTINCT database) FROM prod.raw_hr.employees
     WHERE dateUtc = (SELECT MAX(dateUtc) FROM prod.raw_hr.employees)), 1) AS coverage_pct,
  COUNT(*) AS total_leave_records,
  COUNT(DISTINCT hrLeaveType) AS distinct_leave_types,
  ROUND(AVG(CASE WHEN hrLeaveWithPayNoOfDays IS NOT NULL THEN 1 ELSE 0 END) * 100, 1) AS with_pay_days_pct,
  ROUND(AVG(CASE WHEN hrLeaveWithoutPayNoOfDays IS NOT NULL THEN 1 ELSE 0 END) * 100, 1) AS without_pay_days_pct
FROM prod.raw_hr.leaves;

-- Aggregated leave stats since 2024
SELECT
  COUNT(DISTINCT database) AS companies_with_leaves,
  MIN(hrLeaveDateFrom) AS min_leave_date,
  MAX(hrLeaveDateFrom) AS max_leave_date,
  ROUND(AVG(hrLeaveWithPayNoOfDays + hrLeaveWithoutPayNoOfDays), 2) AS avg_leave_days
FROM prod.raw_hr.leaves
WHERE hrLeaveDateFrom >= '2024-01-01';
