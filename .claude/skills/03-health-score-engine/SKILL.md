# Skill 03: Health Score Engine
### Session 3 — Build the scoring engine and produce the first Workforce Health Scores

---

## Objective
Transform raw pillar metrics into a single 0–100 Workforce Health Score per
company, with calibrated weights, gamification metadata, and peer benchmarks.
The engine must be deterministic, explainable, and reproducible.

---

## Prerequisites

Before starting:
1. Read `output/metrics.md` — all pillar metrics must be available
2. Read `output/session_log.md` — Session 2 handoff
3. Read `output/pillar_recommendations.md` — confirmed pillar set

### Prerequisite Validation

Check these before doing any work:
- `output/metrics.md` exists and contains at least one pillar section
- `output/pillar_recommendations.md` shows APPROVED status
- Session 2 handoff exists in `output/session_log.md`

If any check fails, print a clear error (e.g., "STOP: output/metrics.md not found —
run Session 2 first.") and do not proceed.

### How to Execute SQL

If any SQL queries are needed (e.g., to pull supplementary data), use the
Databricks CLI:

```bash
databricks sql --query "YOUR SQL HERE"
```

---

## Bundled Scripts

This skill includes a reusable scoring library at `scripts/scoring.py` (relative
to this skill directory). It contains tested implementations of:

- `percentile_normalize()` — convert raw metrics to 0-100 percentile scores
- `compute_pillar_score()` — average normalized metrics within a pillar
- `calibrate_weights()` — variance-based weight calibration with floor/ceiling
- `compute_health_score()` — weighted sum of pillar scores
- `assign_ranks()` — rank, quartile, and peer benchmark calculation
- `assign_badges()` — badge criteria evaluation (template — adapt to actual metrics)

When building `models/health_score_engine.py`, copy and adapt these functions
rather than writing from scratch. The bundled code handles edge cases like ties
in percentile ranking, missing pillar data, and weight re-normalization.

---

## Step 1: Implement the Scoring Engine

Create `models/health_score_engine.py` with these components:

### 1a. Data Loading
- Parse `output/metrics.md` or load from structured data files
- Validate all expected metrics are present
- Handle missing values: flag, don't silently impute

### 1b. Percentile Normalization
Convert each raw metric to a 0–100 score based on percentile rank across all
companies:

```python
def percentile_normalize(values: list[float]) -> list[float]:
    """
    Convert raw metric values to 0-100 percentile scores.
    Higher raw value = higher score (invert for metrics where lower is better,
    e.g. attrition rate).
    """
    # Use scipy.stats.percentileofscore or equivalent
    # Handle ties with 'mean' method
    # Return scores rounded to 1 decimal place
```

**Inversion rules** — for these metrics, lower raw values = higher scores:
- Attrition rate (lower is better)
- Absence rate (lower is better)
- Time-to-fill (lower is better)
- Low performer concentration (lower is better)
- Gini coefficient (lower is better → more equitable)

### 1c. Pillar Score Calculation
Each pillar score is the weighted average of its component metrics (equal weight
within a pillar unless there's a strong reason otherwise):

```python
def compute_pillar_score(metric_scores: dict[str, float]) -> float:
    """Average of normalized metric scores within a pillar."""
    valid_scores = [s for s in metric_scores.values() if s is not None]
    if not valid_scores:
        return None  # Flag — don't default to 0
    return round(sum(valid_scores) / len(valid_scores), 1)
```

---

## Step 2: Weight Calibration

Pillar weights are calibrated by **cross-company variance contribution**.
Pillars with higher variance carry more weight because they are more
differentiating.

```python
def calibrate_weights(pillar_scores: dict[str, list[float]]) -> dict[str, float]:
    """
    Weights proportional to cross-company variance of each pillar.

    1. Compute variance of each pillar's scores across companies
    2. Normalize so weights sum to 1.0
    3. Apply a floor of 0.05 (no pillar weighs less than 5%)
    4. Apply a ceiling of 0.35 (no pillar dominates)
    5. Re-normalize after floor/ceiling adjustments
    """
```

Document the calibrated weights with plain-English explanations in
`output/score_weights.md`:

```markdown
# Health Score Weight Calibration

## Calibrated Weights
| Pillar | Weight | Variance | Explanation |
|---|---|---|---|
| Retention Health | 0.22 | 245.3 | High variance — companies differ significantly |
| ... | ... | ... | ... |

## Why These Weights?
<2-3 paragraphs explaining the calibration logic in C-suite language>

## Weight Sensitivity
<What happens if weights change by ±5%? Is the ranking stable?>
```

---

## Step 3: Final Health Score

```python
def compute_health_score(
    pillar_scores: dict[str, float],
    weights: dict[str, float]
) -> float:
    """
    Weighted sum of pillar scores → final 0-100 score.

    Only include pillars with non-None scores.
    Re-normalize weights if some pillars are missing for a company.
    Round to nearest integer.
    """
```

---

## Step 4: Gamification Metadata

For each company, compute:

### Rank and Quartile
```python
rank = sorted_position  # 1 = best
quartile = ceil(rank / (total_companies / 4))
```

### Badges
Apply badge rules from CLAUDE.md:
- 🏆 **Retention Champion** — attrition rate in bottom quartile (lowest 25%)
- ⚖️ **Pay Equity Leader** — compensation Gini < 0.25
- 🚀 **Hiring Velocity** — time-to-hire in top quartile (fastest 25%)
- 📈 **Most Improved** — largest score gain in the period (if multi-period)
- ⭐ **Workforce Elite** — overall Health Score > 85

### Peer Benchmarks (Anonymized)
```python
benchmarks = {
    "top_quartile": percentile_75_score,
    "median": median_score,
    "bottom_quartile": percentile_25_score,
    "your_rank": f"#{rank} of {total}",
}
```

### Weakest and Strongest Pillar
```python
weakest = min(pillar_scores, key=pillar_scores.get)
strongest = max(pillar_scores, key=pillar_scores.get)
```

### Forecast Delta Placeholder
Set to `null` — Session 4 will populate this with predictive model output.

---

## Step 5: Output Files

### `output/scores.csv` (Internal — Kismet Labs only)
```csv
company_id,company_name,health_score,rank,quartile,retention_score,compensation_score,...,badges,weakest_pillar,strongest_pillar
```

### `output/scores_anonymized.csv` (Company-facing)
```csv
company_label,health_score,rank_display,quartile,retention_score,...,badges,weakest_pillar,strongest_pillar,peer_top_quartile,peer_median,peer_bottom_quartile
```
- Replace company identifiers with `Company A`, `Company B`, etc.
- Include peer benchmark columns

### `output/score_weights.md`
Weight calibration explanation (see Step 2).

### `output/score_summary.md`
```markdown
# Workforce Health Score — Summary

## Leaderboard
| Rank | Company | Score | Quartile | Badges |
|---|---|---|---|---|
| 1 | <name> | 87 | Q1 | 🏆⭐ |
| ... | ... | ... | ... | ... |

## Score Distribution
- Mean: <value>
- Median: <value>
- Std Dev: <value>
- Range: <min> – <max>

## Badge Assignments
| Badge | Companies Earned | Criteria |
|---|---|---|
| 🏆 Retention Champion | <n> | Bottom quartile attrition |
| ... | ... | ... |

## Pillar Score Correlations
<Which pillars tend to move together? Any surprising patterns?>
```

---

## Session 3 Handoff

Write to `output/session_log.md`:

```markdown
## Session 3 Handoff

**Companies scored**: <n>
**Score range**: <min> – <max>
**Mean score**: <value>
**Median score**: <value>
**Weight calibration**: <summary of weights>
**Badges awarded**: <n> total across <n> companies
**Engine location**: models/health_score_engine.py
**Scores**: output/scores.csv (internal), output/scores_anonymized.csv (company-facing)
**Known issues**: <any anomalies or caveats>
**Ready for**: Session 4 (Prediction Models)
```
