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

---

## Pillar Processing Order

Work through each approved pillar sequentially. For each pillar:

1. Identify source tables from the schema map
2. Design the extraction query
3. Run the query and validate results
4. Document data quality issues
5. Write clean aggregated output to `output/metrics.md`
6. Save the query to `queries/metrics/`

---

## Pillar 1: Retention Health

**Core metrics needed**:
- Voluntary attrition rate (by company, by period)
- Involuntary attrition rate (by company, by period)
- Total attrition rate
- Headcount denominator (average or period-end)
- Attrition by tenure bucket (< 1yr, 1-3yr, 3-5yr, 5+yr)

**Extraction pattern**:
```sql
SELECT
  company_id,
  period,
  COUNT(CASE WHEN termination_type = 'Voluntary' THEN 1 END) AS voluntary_exits,
  COUNT(CASE WHEN termination_type = 'Involuntary' THEN 1 END) AS involuntary_exits,
  COUNT(*) AS total_exits,
  -- Join to headcount for rate calculation
  ROUND(COUNT(*) * 100.0 / headcount, 2) AS attrition_rate_pct
FROM <termination_table>
JOIN <headcount_table> USING (company_id, period)
GROUP BY company_id, period;
```

**Quality checks**:
- Attrition rate should be 0–50% (flag outliers)
- Every company should have a headcount denominator
- Check for duplicate termination records

---

## Pillar 2: Compensation Equity

**Core metrics needed**:
- Median compensation by company
- Compensation Gini coefficient by company
- Pay band utilization (% of employees within defined bands)
- Compensation ratio: median company pay / market median (if available)
- Gender pay gap ratio (if demographic data available — use aggregates only)

**Extraction pattern**:
```sql
SELECT
  company_id,
  period,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY compensation) AS median_comp,
  PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY compensation) AS p25_comp,
  PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY compensation) AS p75_comp,
  AVG(compensation) AS mean_comp,
  STDDEV(compensation) AS stddev_comp,
  COUNT(*) AS employee_count
FROM <compensation_table>
GROUP BY company_id, period;
```

**Gini coefficient** — compute in Python after extraction if SQL doesn't support it.

**Quality checks**:
- Compensation values should be positive and within reasonable range
- Flag companies with very low employee counts (< 10)
- Check for currency consistency

---

## Pillar 3: Hiring Momentum

**Core metrics needed**:
- Hires per period (by company)
- Hiring rate (hires / headcount)
- Time-to-fill (median days from requisition to hire, if available)
- Hiring trend (period-over-period change)
- Net hiring (hires minus exits)

**Quality checks**:
- Hire dates should be within expected range
- Flag companies with zero hires in any period
- Check for reasonable time-to-fill values (0–365 days)

---

## Pillar 4: Performance Distribution

**Core metrics needed**:
- Rating distribution by company (count per rating level)
- High performer concentration (% in top rating)
- Low performer concentration (% in bottom rating)
- Rating distribution entropy (how spread vs. clustered)
- Forced curve adherence (if a target distribution exists)

**Quality checks**:
- All employees should have a rating (flag null rate)
- Check for consistent rating scales across companies
- Flag companies where >80% have the same rating (no differentiation)

---

## Pillar 5: Workforce Stability

**Core metrics needed**:
- Average tenure by company
- Tenure distribution (buckets: <1yr, 1-3yr, 3-5yr, 5-10yr, 10+yr)
- Organizational depth (levels in hierarchy, if available)
- Span of control (avg direct reports per manager, if available)
- New hire ratio (% of workforce with <1yr tenure)

**Quality checks**:
- Tenure should be non-negative
- Flag companies with average tenure > 20 years (data issue?)
- Check that hire dates produce reasonable tenure values

---

## Pillar 6: Engagement & Absence

**Core metrics needed**:
- Absence rate (days absent / working days) by company
- Absence frequency (episodes per employee)
- Engagement score (if survey data available)
- Sick leave rate vs. other leave types
- Trend in absence rates over time

**Quality checks**:
- Absence rates should be 0–100%
- Flag companies with zero absence (likely missing data, not perfect attendance)
- Check for seasonal patterns that might skew single-period metrics

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
**Pillar set**: <approved pillar list>
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

Save all extraction queries to `queries/metrics/`:

- `queries/metrics/01_retention_health.sql`
- `queries/metrics/02_compensation_equity.sql`
- `queries/metrics/03_hiring_momentum.sql`
- `queries/metrics/04_performance_distribution.sql`
- `queries/metrics/05_workforce_stability.sql`
- `queries/metrics/06_engagement_absence.sql`

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
