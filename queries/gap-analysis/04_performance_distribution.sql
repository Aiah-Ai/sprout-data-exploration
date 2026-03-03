-- Performance Distribution pillar coverage assessment
-- Source: raw_hr.salaries (performance rating field)

-- Overall coverage
WITH latest AS (
  SELECT database, hrEmployeeSalaryPerformanceRating,
    ROW_NUMBER() OVER (PARTITION BY database, hrEmployeeSalaryEmployeeId ORDER BY dateUtc DESC) AS rn
  FROM prod.raw_hr.salaries
  WHERE dateUtc >= '2026-01-01'
)
SELECT
  COUNT(DISTINCT database) AS companies_total,
  COUNT(DISTINCT CASE WHEN hrEmployeeSalaryPerformanceRating IS NOT NULL THEN database END) AS companies_with_ratings,
  ROUND(COUNT(DISTINCT CASE WHEN hrEmployeeSalaryPerformanceRating IS NOT NULL THEN database END) * 100.0 / COUNT(DISTINCT database), 1) AS coverage_pct,
  COUNT(CASE WHEN rn = 1 AND hrEmployeeSalaryPerformanceRating IS NOT NULL THEN 1 END) AS employees_with_ratings,
  COUNT(CASE WHEN rn = 1 THEN 1 END) AS total_employees
FROM latest WHERE rn = 1;

-- Per-company depth of rating coverage
WITH company_ratings AS (
  SELECT database,
    COUNT(*) AS total_emp,
    SUM(CASE WHEN hrEmployeeSalaryPerformanceRating IS NOT NULL THEN 1 ELSE 0 END) AS with_rating,
    ROUND(SUM(CASE WHEN hrEmployeeSalaryPerformanceRating IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS rating_pct
  FROM (
    SELECT database, hrEmployeeSalaryEmployeeId, hrEmployeeSalaryPerformanceRating,
      ROW_NUMBER() OVER (PARTITION BY database, hrEmployeeSalaryEmployeeId ORDER BY dateUtc DESC) AS rn
    FROM prod.raw_hr.salaries WHERE dateUtc >= '2026-01-01'
  ) WHERE rn = 1
  GROUP BY database
)
SELECT
  COUNT(*) AS total_companies,
  SUM(CASE WHEN rating_pct > 50 THEN 1 ELSE 0 END) AS companies_gt50pct_rated,
  SUM(CASE WHEN rating_pct > 0 AND rating_pct <= 50 THEN 1 ELSE 0 END) AS companies_1_to_50pct_rated,
  SUM(CASE WHEN rating_pct = 0 THEN 1 ELSE 0 END) AS companies_no_ratings,
  ROUND(AVG(rating_pct), 1) AS avg_rating_coverage
FROM company_ratings;
