# Skill 02: Metric Extraction
### Session 2 — Extract all metrics needed for the Workforce Health Score pillars

---

## Objective
Extract, validate, and document every metric required by the approved pillar set.
Each metric must be reproducible (SQL saved), quality-checked, and written to
`output/metrics.md` in a format that Session 3 can consume directly.

---

## Prerequisites

Before starting, verify:
1. `output/pillar_recommendations.md` shows **APPROVED** status
2. Note which pillars were approved and any changes from the defaults
3. Read `output/schema_map.md` for table locations and quality notes
4. Read `output/session_log.md` for Session 1/1.5 handoff context

**If pillar_recommendations.md does not show APPROVED status, STOP and notify the user.**

### Prerequisite Validation

Run these checks before doing any extraction work:

```python
# Pseudocode — verify before proceeding
pillar_doc = read("output/pillar_recommendations.md")
assert "APPROVED" in pillar_doc, "STOP: Pillar recommendations not yet approved."

schema_map = read("output/schema_map.md")
assert len(schema_map) > 0, "STOP: Schema map is empty — run Session 1 first."
```

If either check fails, print a clear error message and stop. Do not attempt extraction
with missing or unapproved inputs.

---

## How to Execute SQL

All SQL queries should be executed via the Databricks CLI:

```bash
databricks sql --query "YOUR SQL HERE"
```

For multi-line queries, use a heredoc:

```bash
databricks sql --query "$(cat <<'SQL'
SELECT
  company_id,
  COUNT(*) AS total
FROM some_table
GROUP BY company_id
SQL
)"
```

Save every query that produces results to `queries/metrics/` with a descriptive filename.

---

## Pillar Processing Order

Work through each **approved** pillar from `output/pillar_recommendations.md`
sequentially. Do not assume the default six pillars are all present — the gap
analysis may have dropped, merged, or added pillars.

For each approved pillar:

1. Identify source tables from the schema map
2. Design the extraction query
3. Run the query and validate results
4. Document data quality issues
5. Write clean aggregated output to `output/metrics.md`
6. Save the query to `queries/metrics/`

---

## Metric Extraction Pattern

For every pillar, follow this general pattern. The specific metrics, tables, and
columns will vary based on what the schema map and pillar recommendations say
is available.

### Step 1: Identify what to extract

Read the pillar's entry in `pillar_recommendations.md` to find:
- Which tables supply this pillar's data
- Whether a proxy metric is in use (and what it is)
- Any data quality caveats from Session 1.5

### Step 2: Design the extraction query

Each metric query should produce results at the **company × period** grain:

```sql
SELECT
  <company_col>   AS company_id,
  <period_col>    AS period,
  <aggregation>   AS metric_value
FROM <source_table>
GROUP BY company_id, period
ORDER BY company_id, period;
```

Use only aggregates (COUNT, AVG, MEDIAN, PERCENTILE, STDDEV, etc.) — never
surface individual-level data or PII values.

### Step 3: Validate results

For every extracted metric, run these sanity checks:

- **Completeness**: How many companies have data? Flag if < 80% coverage.
- **Reasonableness**: Are values within expected ranges? (e.g., attrition rate
  0–50%, compensation > 0, absence rate 0–100%)
- **Duplicates**: Are there duplicate company × period rows?
- **Nulls**: What percentage of values are null?
- **Outliers**: Flag values more than 3 standard deviations from the mean.

Document any issues found in the metrics output.

---

## Reference: Common Pillar Metrics

These are examples of metrics commonly needed for the default pillars. Use these
as guidance — adapt based on what pillars were actually approved and what data
is actually available.

### Retention Health (if approved)
- Voluntary attrition rate (by company, by period)
- Involuntary attrition rate (by company, by period)
- Total attrition rate
- Headcount denominator (average or period-end)
- Attrition by tenure bucket (< 1yr, 1-3yr, 3-5yr, 5+yr)

Quality checks: Attrition rate should be 0–50% (flag outliers). Every company
should have a headcount denominator. Check for duplicate termination records.

### Compensation Equity (if approved)
- Median compensation by company
- Compensation Gini coefficient by company
- Pay band utilization (% of employees within defined bands)
- Compensation ratio: median company pay / market median (if available)
- Gender pay gap ratio (if demographic data available — use aggregates only)

Gini coefficient — compute in Python after extraction if SQL doesn't support it.

Quality checks: Compensation values should be positive and within reasonable
range. Flag companies with very low employee counts (< 10). Check for currency
consistency.

### Hiring Momentum (if approved)
- Hires per period (by company)
- Hiring rate (hires / headcount)
- Time-to-fill (median days from requisition to hire, if available)
- Hiring trend (period-over-period change)
- Net hiring (hires minus exits)

Quality checks: Hire dates should be within expected range. Flag companies with
zero hires in any period. Check for reasonable time-to-fill values (0–365 days).

### Performance Distribution (if approved)
- Rating distribution by company (count per rating level)
- High performer concentration (% in top rating)
- Low performer concentration (% in bottom rating)
- Rating distribution entropy (how spread vs. clustered)

Quality checks: All employees should have a rating (flag null rate). Check for
consistent rating scales across companies. Flag companies where >80% have the
same rating (no differentiation).

### Workforce Stability (if approved)
- Average tenure by company
- Tenure distribution (buckets: <1yr, 1-3yr, 3-5yr, 5-10yr, 10+yr)
- Organizational depth (levels in hierarchy, if available)
- Span of control (avg direct reports per manager, if available)
- New hire ratio (% of workforce with <1yr tenure)

Quality checks: Tenure should be non-negative. Flag companies with average
tenure > 20 years (data issue?). Check that hire dates produce reasonable tenure values.

### Engagement & Absence (if approved)
- Absence rate (days absent / working days) by company
- Absence frequency (episodes per employee)
- Engagement score (if survey data available)
- Sick leave rate vs. other leave types
- Trend in absence rates over time

Quality checks: Absence rates should be 0–100%. Flag companies with zero absence
(likely missing data, not perfect attendance). Check for seasonal patterns that
might skew single-period metrics.

---

## Handling Approved Proxy Metrics

If the pillar recommendations document specifies proxy metrics for any pillar,
use the proxy as documented. Note the proxy in the metrics output:

```markdown
**Note**: This pillar uses a proxy metric (<proxy description>) as approved
in pillar_recommendations.md. See Session 1.5 for rationale.
```

---

## Output Format

Write all metrics to `output/metrics.md`:

```markdown
# Extracted Metrics — Workforce Health Score
**Generated**: <timestamp>
**Pillar set**: <approved pillar list from pillar_recommendations.md>
**Companies**: <n>
**Periods covered**: <date range>

---

## Pillar: <name>
**Source tables**: <list>
**Extraction query**: `queries/metrics/<filename>.sql`

### Metric: <metric_name>
| Company | Period | Value | Quality Flag |
|---|---|---|---|
| ... | ... | ... | ... |

**Summary statistics**:
- Cross-company mean: <value>
- Cross-company median: <value>
- Cross-company std dev: <value>
- Min: <value> (Company X) / Max: <value> (Company Y)

**Data quality notes**: <any issues found>

---
```

---

## Query Storage

Save all extraction queries to `queries/metrics/` with descriptive names that
match the approved pillars:

- `queries/metrics/<pillar_name_snake_case>.sql`

For example, if the approved pillars are Retention Health, Compensation Equity,
and Workforce Stability:
- `queries/metrics/retention_health.sql`
- `queries/metrics/compensation_equity.sql`
- `queries/metrics/workforce_stability.sql`

---

## Session 2 Handoff

Write to `output/session_log.md`:

```markdown
## Session 2 Handoff

**Pillars extracted**: <n> of <n> approved
**Total metrics computed**: <n>
**Companies with complete data**: <n> of <n>
**Date range covered**: <earliest> to <latest>
**Data quality issues**:
- <list of issues and how they were handled>
**Metrics file**: output/metrics.md
**Query files**: queries/metrics/
**Ready for**: Session 3 (Health Score Engine)
```
