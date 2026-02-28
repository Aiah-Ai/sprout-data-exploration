# Sprout Data Exploration

**Workforce Health Score** — a Whoop-style executive dashboard that gives C-suite leaders a single 0–100 score for their organization's workforce health, backed by predictive analytics and peer benchmarking.

Built by **Kismet Labs Inc.**

## What It Does

- Computes a composite **Workforce Health Score** from six pillars: Retention Health, Compensation Equity, Hiring Momentum, Performance Distribution, Workforce Stability, and Engagement & Absence
- Benchmarks each company against anonymized peers (quartile rankings, position tracking)
- Generates **predictive alerts** (attrition risk, score forecasts, pillar decline flags)
- Delivers an interactive **executive dashboard** with gamification mechanics (badges, rank movement, score deltas)

## Data Environment

- **Source**: Databricks data warehouse (read-only, SELECT only)
- **Content**: Multi-company HR benchmark dataset
- **Compliance**: ISO 42001 compliant, isolated environment

## Project Structure

| Directory | Purpose |
|---|---|
| `output/` | Schema maps, metrics, scores, and session logs |
| `models/` | Health score engine and prediction models |
| `dashboard/` | Self-contained executive dashboard (HTML + inline JS/CSS) |
| `queries/` | All SQL queries organized by session |

## Session Workflow

The project is built incrementally across six Claude Code sessions:

1. **Schema Discovery** — Map the Databricks schema and profile tables
2. **Gap Analysis** — Validate pillar coverage against actual data (requires human approval)
3. **Metric Extraction** — Extract all metrics needed for scoring
4. **Health Score Engine** — Build the scoring engine and produce scores
5. **Prediction Models** — Train forward-looking risk and forecast models
6. **Executive Dashboard** — Build the final product

## Visibility Rules

- Each company sees only their own data plus anonymized peer benchmarks
- Peer companies are never identified — only quartile positions and rank numbers
- Kismet Labs internal views have full access to all company data
