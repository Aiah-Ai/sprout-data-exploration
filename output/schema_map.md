# Schema Map — Databricks Warehouse (prod catalog)
**Generated**: 2026-03-02
**Catalog**: prod
**Schemas scanned**: 21
**Total tables found**: 107
**Tier 1 (Core HR)**: 22 tables
**Tier 2 (HR-Adjacent)**: 16 tables
**Tier 3 (Contextual)**: 22 tables
**Tier 0 (Not relevant / system)**: ~47 tables

---

## Key Architecture Notes

- **Company identifier**: The `database` column in raw_hr tables acts as the company key (format: `HRIS_<COMPANY_NAME>`)
- **Hierarchy**: client → company → department → employee. A single client can have multiple companies.
- **Snapshot pattern**: raw_hr tables contain daily snapshots (`dateUtc`); the `master_insight` schema contains pre-aggregated monthly/weekly/yearly rollups
- **Best table for Health Score**: `prod.master_insight.periods_monthly_employees_agg` — pre-computed monthly aggregates with attrition, tenure, demographics, exits, new hires at client/company/department levels

---

## Tier 1 Tables — Core HR

### prod.raw_hr.employees
- **Tier**: 1
- **Rows**: 194,928,827 (daily snapshots across all companies)
- **Date range**: Snapshots from 2024-06-24 to 2026-03-01; hire dates from ~2010 to present
- **Companies**: 2,216 distinct `database` values
- **PII columns**: ⚠️ hrEmployeeFirstName, hrEmployeeLastName, hrEmployeeMiddleName, hrEmployeeEmail, hrEmployeePhone, hrEmployeeAddress1/2, hrEmployeeCity, hrEmployeeState, hrEmployeeZip, hrEmployeeSss, hrEmployeeTin, hrEmployeePhilHealth, hrEmployeePagIbigNo, hrEmployeePassportNumber, hrEmployeeBirthday, hrEmployeeBankAccountNo, hrEmployeeBank, hrEmployeePassword, hrEmployeeSpouse, hrEmployeeUserName
- **Key columns**: hrEmployeeId (PK per database), hrEmployeeCompanyId, hrEmployeeDepartmentId, hrEmployeeStatus, hrEmployeeHireDate, hrEmployeeTerminationDate, hrEmployeeSeparationDate, hrEmployeeRegularizationDate, hrEmployeeType (rank and file/manager/officer), hrEmployeeGender, hrEmployeeCivilStatus, database (company key), dateUtc (snapshot date)
- **Null rates**: hrEmployeeEmail 97.6%, hrEmployeeAddress1 95.1%, hrEmployeeTerminationDate 7.8%, hrEmployeeType 7.2%, hrEmployeeRegularizationDate 15.0%
- **Relationships**: → raw_hr.salaries (via hrEmployeeId+database), → raw_hr.leaves, → raw_hr.employee_movements, → raw_hr.overtime, → raw_hr.departments (via hrEmployeeDepartmentId+database)
- **Notes**: Sentinel value `1900-01-01` used for null termination/separation dates. hrEmployeeStatus values include numeric codes and text (Regular, Resigned, etc.)

### prod.raw_hr.salaries
- **Tier**: 1
- **Rows**: 390,888,020 (daily snapshots)
- **Companies**: 1,927 distinct databases
- **PII columns**: None (salary amounts are not PII in aggregate context)
- **Key columns**: hrEmployeeSalaryInfoId, hrEmployeeSalaryEmployeeId, hrEmployeeSalary (base), hrEmployeeSalaryAllowances, hrEmployeeSalaryTotalCompensation, hrEmployeeSalaryMonthlyGross, hrEmployeeSalaryPercentageIncrease, hrEmployeeSalaryActionFor (Promotion, etc.), hrEmployeeSalaryDateFrom/To
- **Null rates**: hrEmployeeSalaryPerformanceRating 49.6%, hrEmployeeSalaryMonthlyGross 52.2%, hrEmployeeSalaryActionFor 52.9%, many supplemental columns ~49.6%
- **Notes**: ~50% of rows have null performance/compensation details — likely half the snapshots are from a schema version without these fields. Core salary field (hrEmployeeSalary) is 99.99% populated.

### prod.raw_hr.leaves
- **Tier**: 1
- **Rows**: 11,302,262
- **Companies**: 1,649 distinct databases
- **Key columns**: hrLeaveId, hrLeaveEmployeeId, hrLeaveType, hrLeaveDateFrom/To, hrLeaveWithPayNoOfDays, hrLeaveWithoutPayNoOfDays, hrLeaveStatus, hrLeaveStatusId, database
- **Null rates**: hrLeaveDateApprovedHr 100%, hrLeaveHrManagerId 100% (HR approval not used), hrLeaveReason <0.1%
- **Notes**: Leave status tracked at supervisor level. Types are numeric codes (20, 21, 22, etc.)

### prod.raw_hr.employee_movements
- **Tier**: 1
- **Rows**: 772,540,530 (daily snapshots)
- **Companies**: 1,846 distinct databases
- **PII columns**: ⚠️ hrEmployeeMovementFromSupervisor, hrEmployeeMovementToSupervisor (person names)
- **Key columns**: hrEmployeeMovementId, hrEmployeeMovementEmployeeId, hrEmployeeMovementDtFrom/To, hrEmployeeMovementActionFor, hrEmployeeMovementFPosition/TPosition, hrEmployeeMovementFDepartment/TDepartment, hrEmployeeMovementFEmploymentType/TEmploymentType, hrEmployeeMovementFEmploymentStatus/TEmploymentStatus
- **Null rates**: hrEmployeeMovementFromLocation 50.5%, hrEmployeeMovementToLocation 49.5%
- **Notes**: ActionFor values: Employment Status, Immediate Supervisor, Department, Location, Position, etc.

### prod.raw_hr.overtime
- **Tier**: 1
- **Rows**: 15,525,961
- **Companies**: 1,378 distinct databases
- **Key columns**: hrOvertimeId, hrOvertimeEmployeeId, hrOvertimeDate, hrOvertimeStatus/StatusId, hrOvertimeIsOrdOT (hours), database
- **Null rates**: ~32% of OT hour columns null
- **Notes**: Detailed OT breakdown by type (ordinary, rest day, holiday, night differential, etc.)

### prod.raw_hr.departments
- **Tier**: 1
- **Rows**: 140,410
- **Key columns**: hrDepartmentId, hrDepartmentCompanyId, hrDepartmentName, hrDepartmentManagerId, hrDepartmentIsDel, database
- **PII columns**: ⚠️ hrDepartmentManagerName (person name)
- **Null rates**: hrDepartmentManagerId 79.7%, hrDepartmentCode 49.7%

### prod.master_hr.employees
- **Tier**: 1
- **Rows**: (not profiled — likely single point-in-time master)
- **Notes**: Single-table master employee view

### prod.staged_hr.employees / prod.staged_hr.companies
- **Tier**: 1
- **Rows**: (intermediate staging tables)

### prod.curated_hr.attendance_requests
- **Tier**: 1
- **Notes**: Attendance request records

---

## Tier 1 — Curated Insight (Dimension Tables)

### prod.curated_insight.dim_hr_employees
- **Tier**: 1
- **Rows**: 707,052 (latest snapshot only — one row per employee)
- **Clients**: 1,515 | **Databases**: 1,509
- **PII columns**: ⚠️ first_name, last_name, middle_name, email, phone, address_1/2, city, state, zip, sss, tin, phil_health, pag_ibig_no, passport_number, birthday, bank_account_no, bank, password, user_name
- **Key columns**: employee_key (MD5 hash), company_database_key, employee_database_key, id, client_id, client_name, company_id, company_name, department_id, department_name, hire_date, regularization_date, separation_date, termination_date, exit_date, exit_voluntary, exit_involuntary, status, type, gender, employee_database, date_utc
- **Null rates**: separation_date 57.7% (= active employees), exit_voluntary 66.0%, type 6.3%
- **Notes**: Clean dimension table with joined client+company+department context. Best single source for employee-level analysis.

### prod.curated_insight.dim_hr_companies
- **Tier**: 1
- **Rows**: 8,670 (client-company combinations)
- **Key columns**: company_key, company_database_key, client_id, client_name, client_database_name, company_id, company_name, company_code, company_country, company_city
- **PII columns**: ⚠️ client_api_password, client_api_user_name, client_hmac_secret_key (credentials)
- **Null rates**: company_id 20.5% (clients without companies)

### prod.curated_insight.dim_hr_departments
- **Tier**: 1
- **Notes**: Department dimension table

### prod.curated_insight.dim_hr_employee_movements
- **Tier**: 1
- **Rows**: 4,312,933 (deduplicated movements — one row per movement event)
- **PII columns**: ⚠️ from_supervisor, to_supervisor (person names)
- **Key columns**: employee_movement_entry_key, employee_database_key, movement_id, employee_id, movement_from/to, action_for, is_employment_status_change, is_supervisor_change, is_position_change, is_dept_change, is_employment_type_change, is_location_change, from_*/to_* (status, position, department, type, location)
- **Notes**: Boolean flags for each movement type make filtering efficient. Clean version of raw_hr.employee_movements.

---

## Tier 1 — Master Insight (Pre-Aggregated Time Series) ⭐ KEY TABLES

### prod.master_insight.periods_monthly_employees_agg
- **Tier**: 1 ⭐ GOLDMINE
- **Rows**: 887,583
- **Clients**: 1,477 | **Companies**: 564 | **Periods**: 26 months (2024-01-01 to 2026-02-01)
- **Aggregation levels**: `client` (32,133 rows), `client_company` (97,640 rows), `client_company_department` (757,810 rows)
- **Key columns**:
  - **Headcount**: total_employees, active_employees
  - **Attrition**: exits, exit_voluntary, exit_involuntary, exit_rate_pct, voluntary_exit_pct, involuntary_exit_pct
  - **Tenure**: tenure_0_3_months/4_12_months/1_3_years/3_5_years/5_plus_years (counts and pct)
  - **Demographics**: age_18_24 through age_60p (counts and pct), male/female (counts and pct)
  - **Employee type**: manager, officer, rank_and_file (counts and pct)
  - **Hiring**: new_hire, new_hire_ratio
  - **Management risk**: manager_exit, manager_short_tenure
  - **Historical attrition**: attrition_rate_3m_ago, attrition_rate_6m_ago, attrition_rate_1y_ago, active_attrition_rate_3m/6m/1y
  - **Historical headcount**: beginning_headcount_3m/6m/1y_ago, beginning_active_headcount_3m/6m/1y_ago
- **Null rates**: voluntary_exit_pct 89.8% (null when zero exits), historical fields null for early periods (no lookback available)
- **Notes**: This is the primary table for the Health Score. Pre-computed monthly aggregates with complete workforce metrics. The `level_agg` column allows analysis at client, company, or department level.

### prod.master_insight.periods_weekly_employees_agg
- **Tier**: 1
- **Notes**: Weekly granularity version of above

### prod.master_insight.periods_yearly_employees_agg
- **Tier**: 1
- **Notes**: Yearly granularity version of above

### prod.master_insight.periods_monthly_employees / periods_weekly_employees / periods_yearly_employees
- **Tier**: 1
- **Notes**: Non-aggregated periodic employee-level snapshots (large)

---

## Tier 1 — Curated Requests (Attrition & Headcount)

### prod.curated_requests.company_attrition_rates
- **Tier**: 1
- **Rows**: 275,335
- **Clients**: 1,979 | **Companies**: 672 | **Year range**: 2020–2026
- **Key columns**: hr_client_id, hr_client_name, hr_company_id, hr_company_name, month_number, month, year, attrition_rate
- **PII columns**: None
- **Notes**: Long-running monthly attrition series going back to 2020 — much deeper history than master_insight. ⚠️ Contains real company names.

### prod.curated_requests.company_adjusted_attrition_rates
- **Tier**: 1
- **Notes**: Adjusted attrition calculation

### prod.curated_requests.client_attrition_rates / client_adjusted_attrition_rates
- **Tier**: 1
- **Notes**: Client-level attrition views

### prod.curated_requests.company_active_headcount
- **Tier**: 1
- **Rows**: 1,339,314
- **Key columns**: hr_client_id, hr_client_name, hr_company_id, hr_company_name, hubspot_company_record_id, date, hr_headcount, payroll_headcount
- **Null rates**: hr_headcount 44.3%, payroll_headcount 48.7%, date 42.6%
- **Notes**: Daily headcount with both HR and payroll perspectives. ⚠️ Contains real company names.

### prod.curated_requests.client_active_headcount
- **Tier**: 1
- **Notes**: Client-level headcount view

---

## Tier 2 Tables — HR-Adjacent

### prod.curated_pyo.employees
- **Tier**: 2
- **Notes**: Payroll outsourcing employee data

### prod.curated_pyo.employment_status_changes
- **Tier**: 2
- **Rows**: 2,366
- **Key columns**: hr_client_id, hr_client_name, hr_company_name, hr_employee_id, previous_hr_employment_status, new_hr_employment_status, date_of_change
- **PII columns**: ⚠️ hr_employee_name, hr_employee_id_no
- **Notes**: Small table tracking employment status changes (Probationary → Regular, etc.)

### prod.raw_payroll.payrolls / payroll_details / payroll_transactions / payroll_transactions_overtime / payroll_overtime_amount
- **Tier**: 2
- **Notes**: Payroll processing data — transactions, pay details, OT amounts

### prod.raw_payroll.employees / employee_statuses
- **Tier**: 2
- **Notes**: Payroll-side employee records

### prod.raw_payroll.external_adjustments / payroll_adjustment_types
- **Tier**: 2
- **Notes**: Payroll adjustments

### prod.curated_billing.processed_payroll_headcount_just_payroll / instawage / readywage
- **Tier**: 2
- **Notes**: Billing headcount derived from payroll

### prod.master_fintech.employees / employee_contact / employee_emails / clients_companies / company_configuration / payroll_external_adjustments
- **Tier**: 2
- **Notes**: Fintech master data linking HR and financial products

### prod.curated_requests.payroll_transactions / payroll_users / hr_users / netbank_employees
- **Tier**: 2
- **Notes**: Request-layer payroll and user data

---

## Tier 3 Tables — Contextual / Reference

### prod.raw_hr.companies / clients / client_classifications / company_settings
- **Tier**: 3 — Company/client reference data

### prod.raw_hr.civil_statuses / genders / countries / employment_statuses / employee_types / employee_payroll_types / schedule_types / feature_flags / feature_flag_keys
- **Tier**: 3 — Lookup/reference tables

### prod.raw_hr.employee_emails / primary_mobile_numbers / employee_extentions
- **Tier**: 3 — Contact info (PII)

### prod.raw_hr.certificate_of_attendance / schedule_adjustments / official_business
- **Tier**: 3 — Attendance-adjacent records

### prod.raw_payroll.banks / bank_account_types / clients
- **Tier**: 3 — Payroll reference tables

### prod.curated_readycash.* / curated_readywage.* / raw_readycash.* / raw_readywage.* / staged_readycash.* / staged_readywage.*
- **Tier**: 3 — Financial products (loans, advances) — not HR core

### prod.curated_requests.active_clients
- **Tier**: 3 — Active client list

---

## Tier 0 Tables — Not Relevant

### prod.ai_sidekick_central.*
- AI system trace/log tables (5 tables)

### prod.ai_payroll_outsourcing_platform.*
- Empty schema (0 tables)

---

## Simulation Data (Development)

### prod.curated_insight.simulation_data_employees / simulation_data_companies
- **Rows**: 5,968 employees
- **Notes**: Synthetic test data sourced from `dev.raw_hr.employees`. Client IDs start at 1,000,000,000+. Useful for testing but NOT for production scoring.

---

## Cross-Table Relationships

```
raw_hr.employees ──(hrEmployeeId + database)──→ raw_hr.salaries
raw_hr.employees ──(hrEmployeeId + database)──→ raw_hr.leaves
raw_hr.employees ──(hrEmployeeId + database)──→ raw_hr.employee_movements
raw_hr.employees ──(hrEmployeeId + database)──→ raw_hr.overtime
raw_hr.employees ──(hrEmployeeDepartmentId + database)──→ raw_hr.departments

curated_insight.dim_hr_employees ──(employee_database_key)──→ curated_insight.dim_hr_employee_movements
curated_insight.dim_hr_employees ──(client_id)──→ curated_insight.dim_hr_companies
curated_insight.dim_hr_employees ──(company_database_key)──→ curated_insight.dim_hr_companies

master_insight.periods_monthly_employees_agg ──(client_id)──→ curated_insight.dim_hr_companies
master_insight.periods_monthly_employees_agg ──(client_id)──→ curated_requests.company_attrition_rates (hr_client_id)

curated_requests.company_attrition_rates ──(hr_client_id)──→ curated_insight.dim_hr_companies (client_id)
curated_requests.company_active_headcount ──(hr_client_id)──→ curated_insight.dim_hr_companies (client_id)
```

**Important**: Within raw_hr tables, relationships require BOTH the ID column AND the `database` column (company key), since IDs are only unique within a given company database.

---

## Company Index

| Metric | Count |
|---|---|
| Total distinct companies (databases) in raw_hr.employees | 2,216 |
| Companies with salary data | 1,927 (87.0%) |
| Companies with leave data | 1,649 (74.4%) |
| Companies with movement data | 1,846 (83.3%) |
| Companies with overtime data | 1,378 (62.2%) |
| Clients in dim_hr_employees | 1,515 |
| Clients in monthly agg | 1,477 |
| Companies in monthly agg | 564 |
| Clients in attrition_rates | 1,979 |
| Client-company entries in dim_hr_companies | 8,670 |

**Date coverage**:
- Raw HR snapshots: 2024-06-24 to 2026-03-01
- Monthly aggregations: 2024-01-01 to 2026-02-01 (26 periods)
- Attrition rates history: 2020 to 2026 (up to 6 years)

---

## PII Register

All PII columns across profiled tables (names only — no values):

| Table | PII Columns |
|---|---|
| raw_hr.employees | ⚠️ hrEmployeeFirstName, hrEmployeeLastName, hrEmployeeMiddleName, hrEmployeeEmail, hrEmployeePhone, hrEmployeeAddress1/2, hrEmployeeCity, hrEmployeeState, hrEmployeeZip, hrEmployeeSss, hrEmployeeTin, hrEmployeePhilHealth, hrEmployeePagIbigNo, hrEmployeePassportNumber, hrEmployeeBirthday, hrEmployeeBankAccountNo, hrEmployeeBank, hrEmployeePassword, hrEmployeeSpouse, hrEmployeeUserName |
| raw_hr.departments | ⚠️ hrDepartmentManagerName |
| raw_hr.employee_movements | ⚠️ hrEmployeeMovementFromSupervisor, hrEmployeeMovementToSupervisor |
| curated_insight.dim_hr_employees | ⚠️ first_name, last_name, middle_name, email, phone, address_1/2, city, state, zip, sss, tin, phil_health, pag_ibig_no, passport_number, birthday, bank_account_no, bank, password, user_name |
| curated_insight.dim_hr_companies | ⚠️ client_api_password, client_api_user_name, client_hmac_secret_key |
| curated_insight.dim_hr_employee_movements | ⚠️ from_supervisor, to_supervisor |
| curated_pyo.employment_status_changes | ⚠️ hr_employee_name, hr_employee_id_no |
| curated_insight.simulation_data_employees | ⚠️ Same PII columns as dim_hr_employees (synthetic data) |

**Credentials detected**: raw_hr.employees contains hashed passwords; dim_hr_companies contains API credentials. These must never appear in any output.
