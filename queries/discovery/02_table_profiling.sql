-- Session 1: Table Profiling Queries
-- Executed: 2026-03-02

-- Company count in employees
SELECT COUNT(DISTINCT database) AS company_count FROM prod.raw_hr.employees;
-- Result: 2,216

-- Date ranges for employees
SELECT
  MIN(hrEmployeeHireDate) AS earliest_hire,
  MAX(hrEmployeeHireDate) AS latest_hire,
  MIN(dateUtc) AS earliest_snapshot,
  MAX(dateUtc) AS latest_snapshot
FROM prod.raw_hr.employees
WHERE hrEmployeeHireDate > '1900-01-02';
-- Result: earliest_hire=1900-01-11, latest_hire=2219-04-08 (some bad data), snapshots 2024-06-24 to 2026-03-01

-- Company coverage across key tables
SELECT COUNT(DISTINCT database) AS companies_salaries FROM prod.raw_hr.salaries;       -- 1,927
SELECT COUNT(DISTINCT database) AS companies_leaves FROM prod.raw_hr.leaves;           -- 1,649
SELECT COUNT(DISTINCT database) AS companies_movements FROM prod.raw_hr.employee_movements; -- 1,846
SELECT COUNT(DISTINCT database) AS companies_overtime FROM prod.raw_hr.overtime;        -- 1,378

-- Monthly agg coverage
SELECT
  COUNT(DISTINCT client_id) AS clients,
  COUNT(DISTINCT company_id) AS companies,
  MIN(month_period) AS earliest,
  MAX(month_period) AS latest,
  COUNT(DISTINCT month_period) AS periods,
  COUNT(DISTINCT level_agg) AS levels
FROM prod.master_insight.periods_monthly_employees_agg;
-- Result: 1,477 clients, 564 companies, 2024-01-01 to 2026-02-01, 26 periods, 3 levels

-- Monthly agg level breakdown
SELECT level_agg, COUNT(*) AS cnt
FROM prod.master_insight.periods_monthly_employees_agg
GROUP BY level_agg;
-- Result: client=32,133 | client_company=97,640 | client_company_department=757,810

-- Attrition rates coverage
SELECT
  COUNT(DISTINCT hr_client_id) AS clients,
  COUNT(DISTINCT hr_company_id) AS companies,
  MIN(year) AS min_year,
  MAX(year) AS max_year
FROM prod.curated_requests.company_attrition_rates;
-- Result: 1,979 clients, 672 companies, 2020-2026

-- Dim employees coverage
SELECT
  COUNT(DISTINCT client_id) AS clients,
  COUNT(DISTINCT employee_database) AS databases
FROM prod.curated_insight.dim_hr_employees;
-- Result: 1,515 clients, 1,509 databases
