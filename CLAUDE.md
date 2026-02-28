# Workforce Intelligence Platform
### Claude Code Project — Kismet Labs Inc.

---

## What We Are Building
A **Workforce Health Score dashboard** — a Whoop-style executive product that
gives C-suite leaders a single compelling score for their organization's workforce
health, backed by predictive analytics and peer benchmarking. The goal is habitual
engagement: leaders check their score regularly, understand what's driving it, and
have clear actions to improve it.

This is a product, not a report. Design every output with that in mind.

---

## Data Environment
- **Source**: Databricks data warehouse (connected via MCP server)
- **Content**: Multi-company HR benchmark dataset — exact schema unknown at start
- **Access**: SELECT only. No INSERT, UPDATE, DELETE, CREATE, or DROP — ever.
- **Compliance**: Isolated environment, ISO 42001 compliant, data access approved

---

## Visibility Rules — Critical
This governs everything Claude Code produces. Never violate this.

| Audience | What they see |
|---|---|
| Each company's C-suite | Their own score, metrics, trends, predictions |
| Each company's C-suite | Peer benchmarks — anonymized as "Top Quartile", "Median", "Bottom Quartile" |
| Each company's C-suite | Their rank position (e.g. "#4 of 12") but NOT which companies are above/below |
| Kismet Labs internal | Full dataset, all company names, all scores, all comparisons |

**In all company-facing outputs**: replace company names/IDs with `Company [A-Z]`
or `Your Organization`. Never expose a competitor's identity to another company.

---

## PII Policy
- **DO** note PII column names in `output/schema_map.md`
- **DO NOT** surface PII values in any file, terminal output, or dashboard
- **DO NOT** use PII columns in samples, GROUP BY, or visualizations
- All analysis uses aggregates only — COUNT, AVG, percentiles, ratios

---

## The Workforce Health Score
A single 0–100 score per company, composed of weighted pillar sub-scores.

**Pillars** (weights to be calibrated by data variance in Session 3):
| Pillar | What it measures |
|---|---|
| Retention Health | Attrition rate vs. peer benchmark |
| Compensation Equity | Pay distribution fairness and band utilization |
| Hiring Momentum | Hiring velocity and time-to-fill trends |
| Performance Distribution | Rating curve health, high performer concentration |
| Workforce Stability | Tenure distribution, org depth, span of control |
| Engagement & Absence | Absence rates, engagement scores if available |

**Scoring logic**: Each pillar is scored 0–100 based on benchmarked percentile
position across all companies in the dataset. Weight calibration uses variance
contribution — pillars with higher cross-company variance carry more weight
because they are more differentiating.

---

## Gamification Mechanics
These are the hooks that drive habitual engagement:

- **Score delta**: Month-over-month change with driver attribution
- **Peer rank**: "You rank #4 of 12 companies this quarter"
- **Rank movement**: "↑ Moved up 2 positions since last quarter"
- **Prediction alerts**: "Attrition risk elevated — model projects +3% in 90 days"
- **Achievement badges**: Unlock when metrics cross thresholds
  - 🏆 Retention Champion — bottom quartile attrition
  - ⚖️ Pay Equity Leader — compensation Gini < 0.25
  - 🚀 Hiring Velocity — time-to-hire in top quartile
  - 📈 Most Improved — largest score gain in the period
  - ⭐ Workforce Elite — overall score > 85
- **Risk flags**: "⚠️ Attrition Risk" if score drops 10+ points or model flags elevation
- **Drill-down**: Every score links to the pillar, which links to the metric, which links to the insight

---

## Deliverables by Session

| Session | Skill | Primary output | Gate |
|---|---|---|---|
| 1 | 01-schema-discovery | `output/schema_map.md` — complete data dictionary | Auto |
| 1.5 | 1.5-gap-analysis | `output/pillar_recommendations.md` — pillar validation | ⚠️ Human approval required |
| 2 | 02-metric-extraction | `output/metrics.md` + metric SQL queries | Auto |
| 3 | 03-health-score-engine | `models/health_score_engine.py` + scored results | Auto |
| 4 | 04-prediction-models | `models/` trained models + prediction outputs | Auto |
| 5 | 05-executive-dashboard | `dashboard/index.html` — the actual product | Auto |
| 6 | All skills | Final calibration, polish, executive summary | Auto |

---

## Session Startup Protocol
At the start of EVERY session, Claude Code must:
1. Read this file (`CLAUDE.md`) fully
2. Read the skill file for the current session
3. Read `output/schema_map.md` to understand current data knowledge
4. Read `output/session_log.md` for the previous session's handoff note
5. For Sessions 2 onwards: read `output/pillar_recommendations.md` and confirm it shows APPROVED status before proceeding
6. Print a one-paragraph status summary before doing any work

---

## Behavioral Rules
- SELECT only — no data modification, ever
- No PII values in any output
- Write all discoveries to output files in real time — don't batch at the end
- Save every SQL query that produces a result to the appropriate `queries/` subfolder
- When uncertain about data quality, flag it — never silently assume clean data
- Think like a product designer, not just an analyst
