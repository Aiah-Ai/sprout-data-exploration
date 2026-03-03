# Pillar Recommendation — Awaiting Human Approval
**Status**: PENDING APPROVAL — do not start Session 2 until approved
**Date**: 2026-03-03
**Assessed by**: Claude Code (Session 1.5)

---

## Recommended Pillar Set

| # | Pillar Name | Status | Source Tables | Clients | Confidence |
|---|---|---|---|---|---|
| 1 | Retention Health | Confirmed | `periods_monthly_employees_agg`, `company_attrition_rates` | 1,477 (agg) / 1,979 (attrition) | **High** |
| 2 | Compensation Equity | Confirmed | `raw_hr.salaries` | 1,791 | **High** |
| 3 | Hiring Momentum | Confirmed | `periods_monthly_employees_agg` | 1,477 | **High** |
| 4 | Workforce Stability | Confirmed | `periods_monthly_employees_agg`, `dim_hr_employee_movements` | 1,477 | **High** |
| 5 | Absence Rate | Confirmed (renamed) | `raw_hr.leaves` | 1,654 (88.1% coverage) | **Medium-High** |
| 6 | Performance Distribution | Partially Supported | `raw_hr.salaries` (performance rating field) | 1,689 companies (93.4%), but only 41.5% of employees rated | **Medium** |

---

## Detailed Pillar Assessments

### Pillar 1: Retention Health
**Core concept**: Attrition rate vs. peer benchmark — voluntary and involuntary exits
**Required data**: Exit counts, exit rates, headcount denominator, voluntary/involuntary split, time series

**Coverage assessment**:
| Requirement | Table found | Companies covered | Completeness | Notes |
|---|---|---|---|---|
| Exit counts | `periods_monthly_employees_agg` | 1,477 clients | 100% | exits, exit_voluntary, exit_involuntary |
| Exit rate | `periods_monthly_employees_agg` | 1,477 clients | 100% | exit_rate_pct pre-computed |
| Historical attrition | `periods_monthly_employees_agg` | 1,477 clients | Partial (null for early periods) | attrition_rate_3m/6m/1y_ago |
| Long-run attrition history | `company_attrition_rates` | 1,979 clients | 100% | 2020–2026, 6 years of history |
| Headcount denominator | `periods_monthly_employees_agg` | 1,477 clients | 100% | active_employees, total_employees |

**Verdict**: **Fully Supported**
**Recommended action**: Keep as-is. This is the strongest pillar.
**Data quality caveats**: 497 rows with exit_rate_pct >100% (micro-company denominator issues). Filter to companies with ≥10 active employees for stable benchmarking. 767 ghost client-months with zero active employees need filtering.

---

### Pillar 2: Compensation Equity
**Core concept**: Pay distribution fairness — salary spread, Gini coefficient, band utilization
**Required data**: Individual salary amounts, company grouping, time series

**Coverage assessment**:
| Requirement | Table found | Companies covered | Completeness | Notes |
|---|---|---|---|---|
| Base salary | `raw_hr.salaries` | 1,791 companies | 90.5% non-null & >0 | Core salary field |
| Total compensation | `raw_hr.salaries` | 1,791 companies | 49.4% | hrEmployeeSalaryTotalCompensation |
| Salary change % | `raw_hr.salaries` | 1,791 companies | 47.2% | hrEmployeeSalaryPercentageIncrease |
| Time series | `raw_hr.salaries` | Daily snapshots | Since 2024-06 | Via dateUtc |

**Verdict**: **Fully Supported**
**Recommended action**: Keep as-is. Use base salary (hrEmployeeSalary) as primary metric — 90.5% populated. Compute Gini coefficient and inter-quartile ratio per company.
**Data quality caveats**: Total compensation only 49.4% populated — use base salary only. 134,547 records with salary=0 (likely unpaid/interns) — filter out. Max salary 72.4M — cap outliers. Salary data is in raw_hr (daily snapshots), not pre-aggregated — will require custom aggregation in Session 2.

**Salary distribution** (latest snapshot): Median ₱20,000 / P25 ₱13,000 / P75 ₱30,000 / Avg ₱28,120. This is Philippine peso-denominated payroll data.

---

### Pillar 3: Hiring Momentum
**Core concept**: Hiring velocity — new hires as % of headcount, hiring trends over time
**Required data**: New hire counts, headcount denominator, time series

**Coverage assessment**:
| Requirement | Table found | Companies covered | Completeness | Notes |
|---|---|---|---|---|
| New hire count | `periods_monthly_employees_agg` | 1,477 clients | 100% | new_hire column |
| New hire ratio | `periods_monthly_employees_agg` | 1,477 clients | 100% | new_hire_ratio pre-computed |
| Time series | `periods_monthly_employees_agg` | 26 months | 100% | 2024-01 to 2026-02 |

**Verdict**: **Fully Supported**
**Recommended action**: Keep as-is. Note: "time-to-fill" (days from job opening to hire) is **not available** in this dataset. Pillar will be based on hire volume/velocity only, not hiring speed.
**Data quality caveats**: 71% of clients (22,828/32,133 client-months) show at least one hire. The remaining 29% are zero-hire months (small companies or seasonal patterns) — these are valid zeros, not missing data.

---

### Pillar 4: Workforce Stability
**Core concept**: Tenure distribution health, organizational depth, management continuity
**Required data**: Tenure buckets, manager counts, manager exits, span of control

**Coverage assessment**:
| Requirement | Table found | Companies covered | Completeness | Notes |
|---|---|---|---|---|
| Tenure buckets | `periods_monthly_employees_agg` | 1,477 clients | 100% | 5 buckets: 0-3mo, 4-12mo, 1-3yr, 3-5yr, 5yr+ |
| Manager count | `periods_monthly_employees_agg` | 1,477 clients | 100% | manager column |
| Manager exits | `periods_monthly_employees_agg` | 1,477 clients | 100% | manager_exit column |
| Manager short tenure | `periods_monthly_employees_agg` | 1,477 clients | 100% | manager_short_tenure column |
| Org depth / span of control | NONE | — | — | Not available in dataset |
| Internal mobility | `dim_hr_employee_movements` | 872K+ employees | Position/dept/type flags | 4.3M movement records |

**Verdict**: **Fully Supported**
**Recommended action**: Keep as-is. Rename to "Workforce Stability & Structure" if desired. Tenure distribution + management continuity metrics are strong. Span of control is absent but not critical — tenure and management data compensate well. Internal mobility data from movements table can enrich this pillar (position changes, department transfers, promotions).
**Data quality caveats**: Tenure bucket sums mismatch total_employees in 2.9% of rows. Employee type breakdown (manager/officer/rank_and_file) has a known 96% mismatch issue in the monthly agg — use the boolean flags in dim_hr_employee_movements as a cross-check.

---

### Pillar 5: Engagement & Absence (renamed from "Engagement & Absence")
**Core concept**: Absence rates as proxy for engagement — no direct engagement survey data exists
**Required data**: Leave records, leave days, headcount denominator

**Coverage assessment**:
| Requirement | Table found | Companies covered | Completeness | Notes |
|---|---|---|---|---|
| Leave records | `raw_hr.leaves` | 1,654 companies | 88.1% coverage | 11.3M records |
| Paid leave days | `raw_hr.leaves` | 1,654 companies | 100% | hrLeaveWithPayNoOfDays |
| Unpaid leave days | `raw_hr.leaves` | 1,654 companies | 100% | hrLeaveWithoutPayNoOfDays |
| Leave types | `raw_hr.leaves` | 1,654 companies | 2,951 distinct types | Numeric codes, not standardized |
| Engagement scores | NONE | — | — | No engagement survey data in dataset |

**Verdict**: **Partially Supported — rename to "Absence Rate"**
**Recommended action**: Rename from "Engagement & Absence" to **"Absence Rate"**. No engagement survey data exists. Use leave data as a standalone absence metric: compute monthly absence rate (total leave days / headcount / working days). This is a weaker but still meaningful signal.
**Proxy metric**: Monthly absence rate = (total leave days per company-month) / (active employees × ~22 working days). Distinguish paid vs unpaid absence.
**Data quality caveats**: Leave types are numeric codes (2,951 distinct values) — will need grouping into categories (sick, vacation, unpaid, etc.) or used as-is for total absence. Raw table requires custom aggregation. Some future-dated leaves (max 2029) need filtering.

---

### Pillar 6: Performance Distribution
**Core concept**: Rating curve health — are ratings normally distributed, or clustered?
**Required data**: Individual performance ratings per employee, company grouping

**Coverage assessment**:
| Requirement | Table found | Companies covered | Completeness | Notes |
|---|---|---|---|---|
| Performance ratings | `raw_hr.salaries` | 1,689 companies (93.4%) | 41.5% of employees rated | hrEmployeeSalaryPerformanceRating |
| Rating scale | Numeric (0–100 range observed) | Varies by company | — | Not standardized across companies |
| Time series | `raw_hr.salaries` via dateUtc | Daily snapshots since 2024-06 | — | |

**Per-company depth**:
- 776 companies (42.9%) have >50% of employees rated — **usable**
- 911 companies (50.4%) have 1–50% of employees rated — **marginal**
- 121 companies (6.7%) have zero ratings — **not usable**

**Verdict**: **Partially Supported**
**Recommended action**: Keep but flag as lower-confidence pillar. Only 776 companies have deep enough rating data (>50% of employees rated) for meaningful distribution analysis. For the remaining companies, this pillar will be scored as "insufficient data" rather than computed with sparse ratings. Ratings are numeric (appears to be 0–100 scale) but may not be standardized across companies — a company using 1–5 scale would show differently than one using 0–100.
**Data quality caveats**: ~50% of salary rows are missing performance ratings entirely (likely schema evolution — older snapshots didn't capture this field). Rating values appear continuous (e.g., 14.97, 55.97, 85.29) which is unusual — may be a computed score rather than a manager-assigned rating. Cross-company comparison is risky without normalization.

---

## Dropped / Merged Pillars

| Original Pillar | Reason | Disposition |
|---|---|---|
| Engagement & Absence | No engagement survey data; leave data covers absence only | **Renamed** to "Absence Rate" — scoped to absence metrics only |

---

## New Pillars Discovered

| Pillar Name | Source Tables | Rationale |
|---|---|---|
| Internal Mobility (candidate) | `dim_hr_employee_movements` | 4.3M movement records covering position changes (351K), department transfers (757K), employment type changes (118K). Rich data available. However, **recommend merging into Workforce Stability** rather than creating a standalone pillar, to keep the score structure clean (6 pillars max). |
| Workforce Demographics (candidate) | `periods_monthly_employees_agg` | Age distribution (6 buckets) and gender split available at 100% completeness for all 1,477 clients. Could measure demographic diversity. However, **recommend NOT making this a standalone pillar** — demographic composition is contextual, not inherently "healthy" or "unhealthy". Use as enrichment data in the dashboard, not as a scored pillar. |
| Overtime Patterns (candidate) | `raw_hr.overtime` | 15.5M records across 1,378 companies (62.2% coverage). Detailed OT breakdown by type. However, **recommend NOT including** — coverage too low for reliable benchmarking (<60% threshold) and OT norms vary heavily by industry. |

---

## Critical Gaps (Unrecoverable Without New Data)

| Gap | Impact | Data Request Generated |
|---|---|---|
| No engagement survey data | Medium — "Engagement" removed from pillar name; absence is a weak proxy | No — absence rate is a viable standalone metric |
| No time-to-fill / recruiting pipeline data | Low — Hiring Momentum uses hire counts instead of speed | No — hire velocity is sufficient |
| No org chart / span of control data | Low — Workforce Stability uses tenure + management data instead | No — existing data compensates |
| Performance ratings only 41.5% populated | Medium — limits benchmarking to ~776 companies with deep data | See below |

---

## Data Enrichment Requests

### Data Request: Performance Ratings
**Why it matters**: Performance distribution is a key signal for C-suite leaders — rating inflation, forced curves, and high-performer concentration directly impact talent strategy. Without reliable ratings, this pillar produces lower-confidence scores.
**What's needed**:
- Clarification on what `hrEmployeeSalaryPerformanceRating` actually represents (manager rating? computed score? scale?)
- Confirmation of whether the ~50% null rate is due to schema evolution or genuinely missing data
- If available: standardized rating scale documentation per company
**Minimum history**: At least 2 annual review cycles
**Impact if not provided**: Performance Distribution pillar will be scored for ~776 companies only (those with >50% employee coverage). Remaining companies get "insufficient data" for this pillar, and their overall Health Score weights will be redistributed across the other 5 pillars.

---

## Recommended Action

**Proceed with 5 confirmed pillars + 1 partial pillar.** The dataset strongly supports Retention Health, Compensation Equity, Hiring Momentum, Workforce Stability, and Absence Rate — these 5 pillars have 88%+ company coverage and high data completeness. Performance Distribution should be included as a 6th pillar but scored only for companies with sufficient rating data (~776 companies); for others, its weight redistributes to the remaining 5. Internal mobility data should be folded into Workforce Stability as an enrichment metric, not a standalone pillar.

**Minimum viable company filter**: Recommend restricting Health Score computation to companies with ≥10 active employees to avoid micro-company instability (this excludes ~33.6% of clients by count but retains the vast majority of employees).

---

## Approval

- [ ] **APPROVED — proceed to Session 2 with the recommended pillar set**
- [ ] **APPROVED WITH CHANGES — see notes below**
- [ ] **HOLD — request missing data before proceeding**

Notes: _______________
