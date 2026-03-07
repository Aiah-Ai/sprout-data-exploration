# Skill 05: Executive Dashboard
### Session 5 — Build the C-suite product that drives habitual engagement

---

## Objective
Build a self-contained executive dashboard as a single HTML file. This is the
product — not a report, not a prototype. Design it so a CEO opens it, sees their
score, understands what's driving it, and wants to check back next quarter.

---

## Prerequisites

Before starting:
1. Read `output/scores_anonymized.csv` — scored company data
2. Read `output/predictions_anonymized.json` — forward-looking predictions
3. Read `output/metrics.md` — underlying metric details
4. Read `output/session_log.md` — Session 4 handoff
5. Read `output/score_weights.md` — weight explanations

### Prerequisite Validation

Check these before doing any work:
- `output/scores_anonymized.csv` exists and contains scored data
- `output/predictions_anonymized.json` exists and contains prediction data
- Session 4 handoff exists in `output/session_log.md`

If any check fails, print a clear error (e.g., "STOP: output/scores_anonymized.csv
not found — run Session 3 first.") and do not proceed.

---

## Technical Requirements

### Single HTML File
- `dashboard/index.html` — complete, self-contained
- All CSS inline in `<style>` tags
- All JavaScript inline in `<script>` tags
- **Only external dependency**: Chart.js from CDN
  ```html
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  ```
- Must work when opened directly in a browser (`file://` protocol)

### Data Loading
- Create `dashboard/data/` directory
- One JSON file per company: `dashboard/data/company_a.json`, etc.
- Dashboard loads data via `<script>` tag or inline JSON
- A company selector dropdown switches between company views

---

## Dashboard Sections

### 1. Health Score Hero
The dominant visual element — large, animated score display.

**Elements**:
- Large score number (0–100) with color coding
  - 85–100: Green (Excellent)
  - 70–84: Blue (Good)
  - 55–69: Yellow (Fair)
  - Below 55: Red (Needs Attention)
- Score delta from previous period (↑↓→) with driver attribution
- Rank display: "#4 of 12 companies"
- Rank movement: "↑ Moved up 2 positions"
- Earned badges displayed as icons

### 2. Pillar Cards (6 cards in a grid)
Each card shows:
- Pillar name and icon
- Pillar score (0–100) with color bar
- Mini sparkline showing trend over time (if multi-period)
- Peer benchmark bar: your score vs. Top Quartile / Median / Bottom Quartile
- Click/hover for metric breakdown detail

### 3. Prediction & Alerts Panel
- Health Score forecast with confidence band
- Attrition risk gauge (0–100, color-coded by tier)
- Pillar risk flags with decline indicators
- Each alert includes a plain-English explanation

### 4. Peer Benchmark Charts
All anonymized — no company names visible.

**Charts**:
- Score distribution histogram (highlight "You are here")
- Box plot per pillar showing spread and the company's position
- Rank table (anonymized: "Company A", "Company B", with "Your Organization" highlighted)

### 5. Trend History
- Line chart: Health Score over time (all available periods)
- Pillar score breakdown over time (stacked or multi-line)
- Key events or inflection points annotated if detectable

---

## Color System (Dark Theme)

```css
:root {
  /* Background */
  --bg-primary: #0f1117;
  --bg-secondary: #1a1d27;
  --bg-card: #232733;
  --bg-card-hover: #2a2e3d;

  /* Text */
  --text-primary: #e8eaed;
  --text-secondary: #9aa0a6;
  --text-muted: #5f6368;

  /* Score colors */
  --score-excellent: #34a853;
  --score-good: #4285f4;
  --score-fair: #fbbc04;
  --score-poor: #ea4335;

  /* Accent */
  --accent-primary: #8ab4f8;
  --accent-secondary: #81c995;

  /* Borders */
  --border-subtle: #303340;
  --border-active: #8ab4f8;
}
```

**Typography**:
- Headings: system sans-serif (SF Pro, Segoe UI, Roboto)
- Score numbers: tabular-nums for alignment
- Body: 14px base, 1.5 line-height

---

## Responsive Layout

```
Desktop (>1024px):
┌─────────────────────────────────────┐
│         Health Score Hero           │
├──────────┬──────────┬───────────────┤
│ Pillar 1 │ Pillar 2 │ Pillar 3      │
├──────────┼──────────┼───────────────┤
│ Pillar 4 │ Pillar 5 │ Pillar 6      │
├──────────┴──────────┴───────────────┤
│     Predictions & Alerts            │
├─────────────────────────────────────┤
│     Peer Benchmarks                 │
├─────────────────────────────────────┤
│     Trend History                   │
└─────────────────────────────────────┘

Tablet (768–1024px): 2-column pillar grid
Mobile (<768px): Single column, stacked layout
```

---

## Data File Format

Each company JSON file in `dashboard/data/`:

```json
{
  "company_label": "Your Organization",
  "health_score": 78,
  "previous_score": 74,
  "score_delta": 4,
  "rank": 4,
  "total_companies": 12,
  "rank_change": 2,
  "quartile": 2,
  "badges": ["retention_champion", "most_improved"],
  "pillars": {
    "retention_health": {
      "score": 82,
      "trend": [75, 78, 82],
      "peer_top_quartile": 85,
      "peer_median": 72,
      "peer_bottom_quartile": 58,
      "metrics": { ... }
    }
  },
  "predictions": {
    "attrition_risk": {
      "score": 35,
      "tier": "Low",
      "factors": ["..."]
    },
    "score_forecast": {
      "projected": 80,
      "confidence_low": 75,
      "confidence_high": 85,
      "direction": "up"
    },
    "pillar_flags": []
  },
  "peer_benchmarks": {
    "score_distribution": [45, 52, 58, 63, 67, 72, 74, 78, 81, 83, 87, 91],
    "your_position": 7
  }
}
```

---

## Interactivity

- **Company selector**: Dropdown to switch between company views
- **Pillar cards**: Click to expand metric detail
- **Charts**: Hover tooltips with exact values
- **Animations**: Score counter animation on load, smooth transitions on company switch
- **Print-friendly**: `@media print` styles for clean PDF export

---

## Accessibility

- Color is never the sole indicator — use icons and text labels alongside color
- Sufficient contrast ratios (WCAG AA minimum)
- Semantic HTML structure
- Keyboard navigable

---

## Quality Checklist

Before marking Session 5 complete:

- [ ] Dashboard opens in browser without errors (check console)
- [ ] All company data loads correctly
- [ ] Score hero displays correctly with delta, rank, badges
- [ ] All 6 pillar cards render with scores and benchmarks
- [ ] Prediction panel shows alerts and forecasts
- [ ] Peer benchmark charts render correctly
- [ ] Company selector works to switch views
- [ ] Mobile layout works (test with browser dev tools)
- [ ] No real company names visible in company-facing view
- [ ] No PII values anywhere in the dashboard
- [ ] Chart.js CDN loads (or graceful fallback message)

---

## Session 5 Handoff

Write to `output/session_log.md`:

```markdown
## Session 5 Handoff

**Dashboard file**: dashboard/index.html
**Data files**: dashboard/data/ (<n> company files)
**External dependencies**: Chart.js CDN only
**Sections implemented**: <list>
**Known issues**: <any display quirks or missing features>
**Browser tested**: <which browsers/modes checked>
**Anonymization verified**: Yes/No
**Ready for**: Session 6 (Polish & Final Delivery)
```
