# Skill 04: Prediction Models
### Session 4 — Build predictive models for forward-looking alerts and forecasts

---

## Objective
Build interpretable predictive models that power the dashboard's forward-looking
features. C-suite users must understand **why** the model flagged them — black-box
models are not acceptable. Prioritize honesty about confidence levels over
impressive-looking predictions.

---

## Prerequisites

Before starting:
1. Read `output/metrics.md` — pillar metrics with time dimension
2. Read `output/scores.csv` — current Health Scores
3. Read `output/session_log.md` — Session 3 handoff
4. Assess data availability: how many time periods exist? (< 3 periods = very limited)

### Prerequisite Validation

Check these before doing any work:
- `output/scores.csv` exists and contains scored company data
- `output/metrics.md` exists and contains pillar metrics
- Session 3 handoff exists in `output/session_log.md`

If any check fails, print a clear error (e.g., "STOP: output/scores.csv not found —
run Session 3 first.") and do not proceed.

### How to Execute SQL

If supplementary data queries are needed, use the Databricks CLI:

```bash
databricks sql --query "YOUR SQL HERE"
```

---

## Bundled Scripts

This skill includes a reusable prediction library at `scripts/prediction_utils.py`
(relative to this skill directory). It contains tested implementations of:

- `classify_attrition_risk()` — multi-factor risk scoring with explainable factors
- `forecast_health_score()` — linear trend extrapolation with confidence bands
- `flag_declining_pillar()` — consecutive decline and sharp drop detection
- `project_headcount()` — linear headcount projection with volatility bands

When building the model files in `models/`, copy and adapt these functions rather
than writing from scratch. They already handle data availability tiers (the
approach adapts based on how many time periods exist) and produce the
interpretable output format required for the dashboard.

---

## Model Priority Order

Build models in this order. **Stop and document honestly** if data is insufficient
for a model — a missing prediction is better than a misleading one.

### Model 1: Attrition Risk Score (90-day forward)

**Purpose**: Flag companies at elevated risk of attrition spikes in the next 90 days.

**Approach options** (choose simplest that fits data):

| Data Available | Approach |
|---|---|
| 3+ time periods | Logistic regression on lagged metric features |
| 2 time periods | Rule-based: flag if attrition trend is rising + below median retention |
| 1 time period | Static risk tiers based on current metrics only (document limitation) |

**Features to consider**:
- Current attrition rate vs. peer median
- Attrition trend (rising/falling/stable)
- Tenure distribution skew (high concentration of < 1yr = flight risk)
- Compensation equity score (low pay equity → higher attrition risk)
- Hiring momentum (high hiring + high attrition = churn problem)

**Reference implementation**: See the [Gian dela Rama Capstone](https://github.com/giandlr/Gian_dela_Rama_Capstone)
(cloned locally at `gian_attrition_prediction/`). This is an AI/ML capstone project
that built an employee attrition classifier on an IBM-style HR dataset. Key takeaways
to adapt for our multi-company Databricks context:

- **Feature engineering patterns worth adapting**:
  - `TenureRatio` = YearsAtCompany / (TotalWorkingYears + 1)
  - `PromotionRate` = YearsAtCompany / (YearsSinceLastPromotion + 1)
  - `IncomePerYearExp` = MonthlyIncome / (TotalWorkingYears + 1)
  - `YearsPerCompany` = TotalWorkingYears / (NumCompaniesWorked + 1)
  - `OverallSatisfaction` = mean(EnvironmentSatisfaction, JobSatisfaction, WorkLifeBalance)
  - Binary flags: `HighCommute`, `LowSatisfaction`, `FrequentTraveler`, `HasStockOption`
- **Model comparison approach**: Compared 6 classifiers (Random Forest, Gradient
  Boosting, SVM, Decision Tree, KNN, Logistic Regression) using stratified
  cross-validation. Random Forest won with 97.4% accuracy / 0.987 AUC-ROC.
- **Output format**: Per-employee attrition probability + risk category (Low/High)
  — maps well to our per-company risk tier output.

**What does NOT transfer** (build from scratch instead):
- The saved `.pkl` model — trained on different schema/features, single-company data
- Single-company design — our models must work cross-company with benchmarking
- No time dimension — the capstone used a static snapshot; we need temporal awareness

**Output**: Risk score 0–100, risk tier (Low / Moderate / Elevated / Critical),
top 3 contributing factors with plain-English explanations.

**Interpretability requirement**:
```
"Attrition Risk: ELEVATED (72/100)
 - Attrition rate 18% vs. peer median 12% (+6pp above benchmark)
 - Rising trend: +3pp over last 2 periods
 - 40% of workforce has <1yr tenure (flight risk concentration)"
```

---

### Model 2: Health Score Forecast (next quarter)

**Purpose**: Project where the Health Score is heading.

**Approach options**:

| Data Available | Approach |
|---|---|
| 4+ periods | Linear trend extrapolation per pillar |
| 2-3 periods | Simple directional forecast (up/down/stable) with confidence band |
| 1 period | No forecast possible — document and skip |

**Output**: Projected score, confidence interval, direction indicator (↑↓→),
projected rank change if applicable.

---

### Model 3: Pillar Risk Flags

**Purpose**: Flag pillars in consecutive decline — early warning before the
overall score drops.

**Logic**:
```python
def flag_declining_pillar(pillar_scores_over_time: list[float]) -> bool:
    """
    Flag if:
    - 2+ consecutive periods of decline, OR
    - Single-period drop of >10 points, OR
    - Currently in bottom quartile AND declining
    """
```

**Output**: List of flagged pillars per company with decline magnitude and
suggested action.

---

### Model 4: Headcount Forecast (conditional)

**Purpose**: Project headcount trajectory based on hiring and attrition trends.

**Only build if**: Time-series headcount data is available for 3+ periods.

**Approach**: Simple linear projection with confidence bands. Do NOT overfit
to small datasets.

**Output**: Projected headcount ± range, net growth/decline indicator.

---

## Model Documentation

For every model built, write to `output/model_notes.md`:

```markdown
## Model: <name>

**Type**: <regression / rule-based / trend extrapolation>
**Data used**: <tables and metrics>
**Time periods**: <n periods, date range>
**Companies modeled**: <n>

### Methodology
<Clear explanation of how the model works — assume the reader is a smart
non-technical executive>

### Confidence Assessment
| Aspect | Rating | Notes |
|---|---|---|
| Data sufficiency | High/Medium/Low | <n periods, n companies> |
| Model stability | High/Medium/Low | <sensitivity to input changes> |
| Prediction horizon | <timeframe> | <how far ahead is reliable> |

### Limitations
- <Honest list of what this model cannot do>
- <Edge cases where predictions may be unreliable>
- <What additional data would improve accuracy>

### Validation
<How was the model checked? Cross-validation, holdout test, sanity checks?>
```

---

## Output Files

### `output/predictions.json` (Internal — Kismet Labs only)
```json
{
  "generated": "<timestamp>",
  "models": {
    "attrition_risk": {
      "company_id": {
        "risk_score": 72,
        "risk_tier": "Elevated",
        "factors": ["..."],
        "confidence": "Medium"
      }
    },
    "health_score_forecast": { ... },
    "pillar_risk_flags": { ... },
    "headcount_forecast": { ... }
  }
}
```

### `output/predictions_anonymized.json` (Company-facing)
Same structure but with company IDs replaced by `Company A`, `Company B`, etc.

### Model code
Save all model implementations to `models/`:
- `models/attrition_risk.py`
- `models/health_score_forecast.py`
- `models/pillar_risk_flags.py`
- `models/headcount_forecast.py` (if built)

---

## Principles

1. **Simplest appropriate model** — don't use ML when a rule works
2. **Interpretability over accuracy** — C-suite must understand the "why"
3. **Honest confidence levels** — "Low confidence" is a valid and useful output
4. **Document what you can't do** — missing predictions are fine; wrong ones aren't
5. **No PII in any model input or output**

---

## Session 4 Handoff

Write to `output/session_log.md`:

```markdown
## Session 4 Handoff

**Models built**: <n> of 4
**Models skipped**: <list with reasons>
**Attrition risk**: <n> companies flagged Elevated/Critical
**Health Score forecast**: Available / Directional only / Not available
**Pillar risk flags**: <n> companies with declining pillars
**Headcount forecast**: Built / Skipped (reason)
**Model confidence**: <overall assessment>
**Prediction files**: output/predictions.json, output/predictions_anonymized.json
**Model code**: models/
**Model docs**: output/model_notes.md
**Ready for**: Session 5 (Executive Dashboard)
```
