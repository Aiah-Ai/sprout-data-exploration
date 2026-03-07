# Skill 1.5: Data Gap Analysis & Pillar Confirmation
### Session 1.5 — Validate what the data can actually support before building anything

---

## Objective
This is a **human-in-the-loop gate**. Do not proceed to Session 2 without
explicit sign-off on the confirmed pillar set. The output of this session is
a recommendation document that a human reviews and approves. Only then does
metric extraction begin.

---

## Context
The six default Health Score pillars were derived from standard HR benchmarking
frameworks — not from this specific dataset. This session determines:

1. Which default pillars the data can actually support
2. Whether the data reveals additional pillars we didn't anticipate
3. What's missing and whether it's recoverable
4. The final approved pillar set that Sessions 2–5 will be built on

### The Six Default Pillars

These are the starting assumptions to validate against the actual data:

| # | Pillar | What it measures |
|---|---|---|
| 1 | Retention Health | Attrition rate vs. peer benchmark |
| 2 | Compensation Equity | Pay distribution fairness and band utilization |
| 3 | Hiring Momentum | Hiring velocity and time-to-fill trends |
| 4 | Performance Distribution | Rating curve health, high performer concentration |
| 5 | Workforce Stability | Tenure distribution, org depth, span of control |
| 6 | Engagement & Absence | Absence rates, engagement scores if available |

Assess each of these against the schema map. Some may be dropped, merged, or
replaced based on what the data actually supports.

### How to Execute SQL

Any validation queries should be run via the Databricks CLI:

```bash
databricks sql --query "YOUR SQL HERE"
```

---

## Default Pillar Checklist

For each default pillar, assess coverage using the schema map from Session 1.

### How to assess a pillar

A pillar is **Fully Supported** if:
- At least one table directly measures the core concept
- Data exists for 80%+ of companies in the dataset
- Time dimension is present (at least 2 periods)
- No critical quality issues identified in profiling

A pillar is **Partially Supported** if:
- Data exists but covers fewer than 80% of companies, OR
- Only one time period available (limits trend and prediction), OR
- Proxy metric needed (e.g. using tenure as proxy for stability when org data absent)

A pillar is **Not Supported** if:
- No relevant table found, OR
- Table exists but is empty, restricted, or has >40% null rate on key columns

---

## Pillar Assessment Template

Run this analysis for each of the six default pillars:

```markdown
### Pillar: <name>

**Core concept**: <what this pillar measures>
**Required data**: <minimum data needed to score this pillar>

**Coverage assessment**:
| Requirement | Table found | Companies covered | Completeness | Notes |
|---|---|---|---|---|
| <e.g. Exit records> | <table name or NONE> | <n/N> | <pct non-null> | |
| <e.g. Headcount denominator> | | | | |

**Verdict**: Fully Supported / Partially Supported / Not Supported
**Recommended action**: Keep as-is / Rename / Merge with another pillar /
                        Replace with proxy / Drop
**Proxy metric (if applicable)**: <what to use instead>
**Data quality caveats**: <honest notes>
```

---

## Unanticipated Pillar Discovery

After assessing the six defaults, scan the schema map for tables that don't
map to any default pillar but appear rich and HR-relevant.

Ask for each such table:
- What workforce dimension does this measure?
- Is it available for most companies?
- Would a C-suite executive find this meaningful?
- Could this become a standalone pillar or enrich an existing one?

**Common unanticipated pillars found in HR datasets**:
- Learning & Development (training hours, certifications, L&D spend)
- Internal Mobility (transfers, promotions, cross-functional moves)
- Workforce Cost Efficiency (cost per hire, revenue per employee)
- Succession Planning (bench strength, critical role coverage)
- Contractor/Contingent Workforce (mix, cost, conversion rates)
- Geographic Distribution (location diversity, remote/hybrid split)

Document any discovered pillars in the recommendation output.

---

## Critical Data Gaps

For any pillar that is Partially Supported or Not Supported, assess recoverability:

```markdown
### Gap: <pillar name> — <specific missing data>

**Impact on Health Score**: High / Medium / Low
(High = this pillar was expected to carry significant weight)

**Recovery options**:
- [ ] Request additional data from the source (describe what's needed)
- [ ] Use proxy metric (describe proxy and its limitations)
- [ ] Merge into adjacent pillar (describe which one)
- [ ] Drop from Health Score (reduce to N pillars)

**Recommendation**: <single clear recommendation>
```

---

## Cross-Company Coverage Analysis

A pillar is only useful for benchmarking if most companies have data for it.
Assess the coverage matrix:

```sql
-- For each candidate pillar table, check company coverage
SELECT
  COUNT(DISTINCT company_id)                          AS companies_with_data,
  (SELECT COUNT(DISTINCT company_id)
   FROM <master_company_table>)                       AS total_companies,
  ROUND(COUNT(DISTINCT company_id) * 100.0 /
    (SELECT COUNT(DISTINCT company_id)
     FROM <master_company_table>), 1)                 AS coverage_pct
FROM <pillar_table>;
```

A pillar with less than 60% company coverage should be flagged — it cannot
produce reliable peer benchmarks and will skew the comparative scoring.

---

## Data Enrichment Requests

If a critical pillar has no data, generate a structured data request that
Kismet Labs can take back to the data source:

```markdown
### Data Request: <pillar name>

**Why it matters**: <business value of this pillar to C-suite>
**What's needed**:
- Table structure: <describe columns and grain needed>
- Minimum history: <how many periods needed for trend and prediction>
- Coverage: <which companies must have this data>
- Format: <any specific requirements>

**Impact if not provided**: <which Health Score feature will be absent or degraded>
```

---

## Output: Pillar Recommendation Document

Write the full recommendation to `output/pillar_recommendations.md`:

```markdown
# Pillar Recommendation — Awaiting Human Approval
**Status**: PENDING APPROVAL — do not start Session 2 until approved

---

## Recommended Pillar Set

| # | Pillar Name | Status | Source Tables | Companies | Confidence |
|---|---|---|---|---|---|
| 1 | | Confirmed | | | |
| 2 | | Confirmed | | | |
...

## Dropped / Merged Pillars
| Original Pillar | Reason | Disposition |
|---|---|---|
...

## New Pillars Discovered
| Pillar Name | Source Tables | Rationale |
|---|---|---|
...

## Critical Gaps (Unrecoverable Without New Data)
| Gap | Impact | Data Request Generated |
|---|---|---|
...

## Data Enrichment Requests
<Full requests for any critical missing data>

---

## Recommended Action
<2–3 sentences: Claude Code's clear recommendation on how to proceed.
Be specific — "Proceed with 4 confirmed pillars and 1 proxy" is better
than "We have some gaps to address.">

---

## Approval

- [ ] **APPROVED — proceed to Session 2 with the recommended pillar set**
- [ ] **APPROVED WITH CHANGES — see notes below**
- [ ] **HOLD — request missing data before proceeding**

Notes: _______________
```

---

## How to Use This Output

1. Claude Code produces `output/pillar_recommendations.md` and stops
2. A human at Kismet Labs reviews the document
3. The human checks the appropriate box and adds any notes
4. Session 2 is started only after the file shows APPROVED status
5. At the start of Session 2, Claude Code reads this file and uses only
   the approved pillar set — not the default six

---

## Session 1.5 Handoff

Write to `output/session_log.md`:
```markdown
## Session 1.5 Handoff

**Pillars assessed**: <n>
**Fully supported**: <list>
**Partially supported**: <list + proxy approach>
**Not supported**: <list>
**New pillars discovered**: <list or none>
**Data requests generated**: <n>
**Document location**: output/pillar_recommendations.md
**Status**: AWAITING HUMAN APPROVAL — do not start Session 2
```
