# Session Starter Prompts
Copy the relevant prompt into Claude Code at the start of each session.

---

## SESSION 1 — Schema Discovery

```
Read CLAUDE.md, then load .claude/skills/01-schema-discovery/SKILL.md.

Your task: Map the complete Databricks schema from scratch.

1. List all catalogs → schemas → tables
2. Score every table by HR relevance using the keyword tiers in the skill
3. Profile every Tier 1 and Tier 2 table: structure, row counts, date range,
   company dimension, column cardinality
4. Flag all PII columns (name only — no values)
5. Discover and validate cross-table relationships
6. Build the company index: distinct companies, record counts per table

Write every finding to output/schema_map.md in real time.
Save all queries to queries/discovery/ as you run them.
At session close, write the Session 1 Handoff to output/session_log.md.

SELECT only. No data modification. No PII values in any output.
```

---

## SESSION 1.5 — Gap Analysis & Pillar Confirmation

```
Read CLAUDE.md, then load .claude/skills/1.5-gap-analysis/SKILL.md.
Then read output/schema_map.md and output/session_log.md.

Print a one-paragraph status summary of what Session 1 found before proceeding.

Your task: Determine what the data can actually support — do not assume
the six default pillars are valid until the data confirms it.

1. For each of the six default pillars, assess coverage using the schema map:
   - Is there a table that measures this? Which one(s)?
   - What percentage of companies have this data?
   - Is there a time dimension (multiple periods)?
   - What's the data quality like based on Session 1 profiling?
   - Verdict: Fully Supported / Partially Supported / Not Supported

2. Scan for unanticipated pillars — tables that are HR-relevant but don't map
   to any default pillar. Propose any that are well-covered and C-suite relevant.

3. For every gap (Partially or Not Supported pillar):
   - Assess recoverability: proxy metric, merge, drop, or data request
   - If critical and unrecoverable, generate a structured data enrichment request

4. Run the cross-company coverage SQL for every candidate pillar table.
   Flag any pillar below 60% company coverage.

5. Write the complete recommendation to output/pillar_recommendations.md
   using the template in the skill. Include the approval checkbox section.

6. Write Session 1.5 Handoff to output/session_log.md.

STOP after writing the recommendation. Do not begin metric extraction.
This document requires human approval before Session 2 starts.
```

---

## ⚠️ HUMAN REVIEW REQUIRED BEFORE SESSION 2

Before running Session 2:
1. Open `output/pillar_recommendations.md`
2. Review Claude Code's assessment of each pillar
3. Check the appropriate approval box
4. Add any notes or adjustments
5. Only then run Session 2

---

## SESSION 2 — Metric Extraction

```
Read CLAUDE.md, then load .claude/skills/02-metric-extraction/SKILL.md.
Then read output/schema_map.md, output/session_log.md, AND
output/pillar_recommendations.md.

IMPORTANT: Check that output/pillar_recommendations.md shows APPROVED status.
If it does not show approval, stop and notify the user.

Print a one-paragraph status summary before proceeding. Include which pillars
were approved and any changes from the default six.

Print a one-paragraph status summary of what Session 1 found before proceeding.

Your task: Extract all metrics needed for the Workforce Health Score pillars.

Work through all six pillars in order:
1. Retention Health
2. Compensation Equity
3. Hiring Momentum
4. Performance Distribution
5. Workforce Stability
6. Engagement & Absence

For each pillar: identify the source tables, run the extraction queries, document
data quality issues, and write clean aggregated outputs to output/metrics.md.

Save all queries to queries/metrics/.
At session close, write the Session 2 Handoff to output/session_log.md.

SELECT only. No PII values in any output.
```

---

## SESSION 3 — Health Score Engine

```
Read CLAUDE.md, then load .claude/skills/03-health-score-engine/SKILL.md.
Then read output/metrics.md and output/session_log.md.

Print a one-paragraph status summary before proceeding.

Your task: Build the Workforce Health Score engine and produce the first scores.

1. Implement models/health_score_engine.py following the skill specification
2. Run percentile normalization on all available pillar metrics
3. Calibrate pillar weights using cross-company variance
4. Compute final Health Score (0-100) for every company
5. Compute all gamification metadata: rank, quartile, badges, peer benchmarks,
   weakest/strongest pillar, forecast delta placeholder
6. Write output/scores.csv (internal) and output/scores_anonymized.csv (company-facing)
7. Write output/score_weights.md explaining the calibrated weights in plain English
8. Write output/score_summary.md with leaderboard and badge assignments

At session close, write Session 3 Handoff to output/session_log.md.
```

---

## SESSION 4 — Prediction Models

```
Read CLAUDE.md, then load .claude/skills/04-prediction-models/SKILL.md.
Then read output/metrics.md, output/scores.csv, and output/session_log.md.

Print a one-paragraph status summary before proceeding.

Your task: Build predictive models that power the dashboard's forward-looking alerts.

Build models in priority order — stop and document if data is insufficient:
1. Attrition Risk Score (90-day forward risk per company)
2. Health Score Forecast (next quarter projected score)
3. Pillar Risk Flags (pillars in consecutive decline)
4. Headcount Forecast (if time-series data available)

For each model:
- Choose the simplest appropriate approach given data availability
- Prioritise interpretability — C-suite must understand why the model flagged them
- Document confidence level and limitations honestly
- Write model notes to output/model_notes.md

Save trained models and prediction functions to models/.
Write output/predictions.json (internal) and output/predictions_anonymized.json.
At session close, write Session 4 Handoff to output/session_log.md.
```

---

## SESSION 5 — Executive Dashboard

```
Read CLAUDE.md, then load .claude/skills/05-executive-dashboard/SKILL.md.
Then read output/scores_anonymized.csv, output/predictions_anonymized.json,
output/metrics.md, and output/session_log.md.

Print a one-paragraph status summary before proceeding.

Your task: Build the executive dashboard — the product C-suite will use.

Build dashboard/index.html as a complete self-contained single HTML file.
Include all CSS and JavaScript inline. Use Chart.js from CDN only.

Requirements:
- Animated Health Score hero (large number, delta, rank, badges)
- Six pillar cards with scores, sparklines, and peer benchmark bars
- Prediction & alerts panel (forecast, attrition risk gauge, pillar flags)
- Anonymous peer benchmark charts (histogram, box plots)
- Trend history section (score over time)
- Dark theme using the color system in the skill
- Mobile-responsive layout

Create dashboard/data/ directory with anonymized JSON data files per company.
Test that the dashboard renders correctly by reviewing the HTML structure.
At session close, write Session 5 Handoff to output/session_log.md.
```

---

## SESSION 6 — Polish & Final Delivery

```
Read CLAUDE.md and output/session_log.md.

Print a one-paragraph status summary before proceeding.

Your task: Final calibration, polish, and delivery preparation.

1. Review output/scores.csv — flag any anomalous scores and investigate root cause
2. Review dashboard/index.html — fix any display issues noted in Session 5 handoff
3. Verify anonymization: grep all company-facing output files for real company IDs
4. Check all badges are assigned correctly against the scoring data
5. Write output/executive_summary.md:
   - 3-paragraph overview of what the data shows across all companies
   - Top 3 cross-company insights
   - Key limitations and data quality caveats
   - How to interpret the Health Score
6. Final deliverable checklist from skill 05 — mark each item complete

Produce output/final_delivery_checklist.md confirming all items are complete.
```
