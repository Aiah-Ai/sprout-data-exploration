# Session Log

## Session 1 Handoff

**Date**: 2026-03-02
**Catalogs scanned**: 1 (prod — as directed)
**Schemas scanned**: 21
**Total tables**: 107
**Tier 1 tables**: 22 — raw_hr.employees, raw_hr.salaries, raw_hr.leaves, raw_hr.employee_movements, raw_hr.overtime, raw_hr.departments, master_hr.employees, staged_hr.employees, staged_hr.companies, curated_hr.attendance_requests, curated_insight.dim_hr_employees, curated_insight.dim_hr_companies, curated_insight.dim_hr_departments, curated_insight.dim_hr_employee_movements, master_insight.periods_monthly_employees_agg, master_insight.periods_weekly_employees_agg, master_insight.periods_yearly_employees_agg, master_insight.periods_monthly/weekly/yearly_employees, curated_requests.company_attrition_rates, curated_requests.company_active_headcount, curated_requests.client_attrition_rates, curated_requests.client_active_headcount
**Tier 2 tables**: 16 — curated_pyo.*, raw_payroll.*, curated_billing.*, master_fintech.*, curated_requests.payroll_*
**PII columns flagged**: 40+ columns across 8 tables (names, addresses, gov't IDs, bank accounts, passwords, DOB)
**Cross-table relationships found**: 8 validated relationship paths
**Companies in dataset**: 2,216 distinct company databases in raw_hr; 1,477 clients in monthly agg
**Date range**: Raw snapshots 2024-06-24 to 2026-03-01; Monthly agg 2024-01 to 2026-02 (26 periods); Attrition history 2020-2026

**Key data quality issues**:
1. Sentinel date `1900-01-01` used for null termination/separation dates — requires filtering
2. ~50% of salary rows missing performance rating and supplemental compensation fields (likely schema evolution)
3. Employee status uses both numeric codes (1, 5) in raw and text strings (Regular, Resigned) in curated — 18 distinct numeric codes, 16 text statuses
4. Some hire dates in far future (2219) — bad data, needs filtering; 3,221 employees with hire dates before 1990
5. hrEmployeeHrManagerId and hrLeaveDateApprovedHr are 100% null — HR-level approval not used
6. Overtime data only covers 62.2% of companies — lowest coverage among core tables
7. Monthly agg covers only 564 companies (vs 2,216 in raw) — likely filters for active/qualifying companies only
8. **Employee type breakdown is 96% broken in monthly agg** — manager+officer+rank_and_file <> total_employees for 30,926/32,133 client rows; type column has 17.5% blank/null values plus stray codes
9. **Attrition rate outliers** — 497 rows >100%, max 12,067%; likely denominator issues in micro-companies or double-scaling bug
10. **Micro-company problem** — 496 clients (33.6%) have avg headcount <5; 657 (44.5%) have <10. These produce wildly unstable metrics.
11. **Salary outliers** — 134,547 records with salary=0; max salary 72.4M; needs filtering/capping
12. **Gender sums mismatch** — 760 rows (2.4%) in monthly agg where male+female <> total_employees
13. **Tenure sums mismatch** — 928 rows (2.9%) where tenure buckets don't sum to total_employees
14. **767 ghost client-months** with zero active employees; 28 of those still report exits
15. **Incomplete time series** — only 1,051 of 1,477 clients (71.2%) have all 26 months; 426 have partial histories

**Star table for Health Score**: `prod.master_insight.periods_monthly_employees_agg` — contains pre-computed monthly metrics for attrition, tenure, demographics, hiring, and exits at client/company/department level across 26 months and 1,477 clients.

**Ready for**: Session 1.5 (Gap Analysis & Pillar Confirmation)

---

## Session 1.5 Handoff

**Date**: 2026-03-03
**Pillars assessed**: 6
**Fully supported**: Retention Health, Compensation Equity, Hiring Momentum, Workforce Stability
**Partially supported**: Absence Rate (renamed from Engagement & Absence — no engagement survey data, leave data only; 88.1% company coverage), Performance Distribution (93.4% companies have some ratings but only 41.5% of employees rated; 776 companies with >50% coverage)
**Not supported**: None dropped entirely
**New pillars discovered**: Internal Mobility (recommend merge into Workforce Stability), Workforce Demographics (recommend as dashboard enrichment only, not scored), Overtime Patterns (62.2% coverage too low for pillar)
**Data requests generated**: 1 (Performance rating clarification)
**Document location**: output/pillar_recommendations.md
**Status**: AWAITING HUMAN APPROVAL — do not start Session 2
