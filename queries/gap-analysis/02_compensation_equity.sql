-- Compensation Equity pillar coverage assessment
-- Source: raw_hr.salaries (latest snapshot)
SELECT
  'salaries' AS source,
  COUNT(DISTINCT database) AS companies_with_data,
  ROUND(AVG(CASE WHEN hrEmployeeSalary IS NOT NULL AND hrEmployeeSalary > 0 THEN 1 ELSE 0 END) * 100, 1) AS salary_populated_pct,
  ROUND(AVG(CASE WHEN hrEmployeeSalaryTotalCompensation IS NOT NULL THEN 1 ELSE 0 END) * 100, 1) AS total_comp_pct,
  ROUND(AVG(CASE WHEN hrEmployeeSalaryPerformanceRating IS NOT NULL THEN 1 ELSE 0 END) * 100, 1) AS perf_rating_pct,
  ROUND(AVG(CASE WHEN hrEmployeeSalaryPercentageIncrease IS NOT NULL THEN 1 ELSE 0 END) * 100, 1) AS pct_increase_pct
FROM prod.raw_hr.salaries
WHERE dateUtc = (SELECT MAX(dateUtc) FROM prod.raw_hr.salaries);

-- Salary distribution stats
WITH latest_salaries AS (
  SELECT database, hrEmployeeSalary,
    ROW_NUMBER() OVER (PARTITION BY database, hrEmployeeSalaryEmployeeId ORDER BY dateUtc DESC) AS rn
  FROM prod.raw_hr.salaries
  WHERE dateUtc >= '2026-01-01' AND hrEmployeeSalary > 0
)
SELECT
  COUNT(DISTINCT database) AS companies_with_salary,
  ROUND(AVG(hrEmployeeSalary), 0) AS avg_salary,
  ROUND(PERCENTILE_APPROX(hrEmployeeSalary, 0.5), 0) AS median_salary,
  ROUND(PERCENTILE_APPROX(hrEmployeeSalary, 0.25), 0) AS p25_salary,
  ROUND(PERCENTILE_APPROX(hrEmployeeSalary, 0.75), 0) AS p75_salary
FROM latest_salaries WHERE rn = 1;
