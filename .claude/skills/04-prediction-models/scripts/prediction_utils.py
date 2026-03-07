"""
Reusable prediction utilities for Session 4 models.

This module provides building blocks for:
- Attrition risk scoring (rule-based and trend-based)
- Health score forecasting (linear trend extrapolation)
- Pillar decline detection
- Headcount projection

These are templates — adapt to the actual data structures from Sessions 2-3.
The functions prioritize interpretability over complexity, matching the
requirement that C-suite users must understand "why" behind every prediction.
"""

from typing import Optional


def classify_attrition_risk(
    current_attrition: float,
    peer_median_attrition: float,
    attrition_trend: Optional[list[float]] = None,
    short_tenure_pct: Optional[float] = None,
    compensation_equity_score: Optional[float] = None,
) -> dict:
    """
    Compute attrition risk score and tier with explainable factors.

    Approach adapts to data availability:
    - 3+ periods in trend: uses trend slope + current position
    - 2 periods: uses direction + current position
    - 1 period: static risk tiers from current metrics only

    Args:
        current_attrition: Company's current attrition rate (0-100).
        peer_median_attrition: Median attrition across all companies.
        attrition_trend: Attrition rates over time (oldest first). None if single period.
        short_tenure_pct: % of workforce with < 1yr tenure. None if unavailable.
        compensation_equity_score: Compensation pillar score (0-100). None if unavailable.

    Returns:
        Dict with risk_score (0-100), risk_tier, factors (list of strings),
        and confidence level.
    """
    risk_score = 0.0
    factors = []
    confidence = "Low"

    # Factor 1: Current attrition vs. peers (0-40 points)
    gap = current_attrition - peer_median_attrition
    if gap > 0:
        # Above median — risk increases proportionally
        attrition_risk = min(40, gap * 4)
        risk_score += attrition_risk
        factors.append(
            f"Attrition rate {current_attrition:.1f}% vs. peer median "
            f"{peer_median_attrition:.1f}% (+{gap:.1f}pp above benchmark)"
        )

    # Factor 2: Trend direction (0-30 points)
    if attrition_trend and len(attrition_trend) >= 2:
        confidence = "Medium" if len(attrition_trend) >= 3 else "Low"
        recent_change = attrition_trend[-1] - attrition_trend[-2]
        if recent_change > 0:
            trend_risk = min(30, recent_change * 5)
            risk_score += trend_risk
            factors.append(
                f"Rising trend: +{recent_change:.1f}pp over last period"
            )
        if len(attrition_trend) >= 3:
            # Check for sustained rise
            changes = [
                attrition_trend[i] - attrition_trend[i - 1]
                for i in range(1, len(attrition_trend))
            ]
            if all(c > 0 for c in changes):
                risk_score += 10
                factors.append(
                    f"Sustained increase across {len(changes)} consecutive periods"
                )
                confidence = "Medium"

    # Factor 3: Flight risk concentration (0-15 points)
    if short_tenure_pct is not None and short_tenure_pct > 30:
        flight_risk = min(15, (short_tenure_pct - 30) * 0.75)
        risk_score += flight_risk
        factors.append(
            f"{short_tenure_pct:.0f}% of workforce has <1yr tenure (flight risk concentration)"
        )

    # Factor 4: Compensation pressure (0-15 points)
    if compensation_equity_score is not None and compensation_equity_score < 40:
        comp_risk = min(15, (40 - compensation_equity_score) * 0.5)
        risk_score += comp_risk
        factors.append(
            f"Low compensation equity score ({compensation_equity_score:.0f}/100) "
            f"may drive voluntary exits"
        )

    # Clamp and classify
    risk_score = min(100, max(0, round(risk_score)))
    risk_tier = _score_to_tier(risk_score)

    if not factors:
        factors.append("No elevated risk indicators detected")

    return {
        "risk_score": risk_score,
        "risk_tier": risk_tier,
        "factors": factors[:3],  # Top 3 contributing factors
        "confidence": confidence,
    }


def forecast_health_score(
    scores_over_time: list[float],
) -> Optional[dict]:
    """
    Project health score direction and magnitude.

    Adapts to data availability:
    - 4+ periods: linear trend extrapolation with confidence band
    - 2-3 periods: directional forecast (up/down/stable)
    - 1 period: returns None (no forecast possible)

    Args:
        scores_over_time: Health scores ordered oldest to newest.

    Returns:
        Dict with projected score, confidence band, and direction.
        None if insufficient data.
    """
    n = len(scores_over_time)

    if n < 2:
        return None

    # Direction from recent movement
    recent_delta = scores_over_time[-1] - scores_over_time[-2]

    if n < 4:
        # Directional only
        if abs(recent_delta) < 2:
            direction = "stable"
        elif recent_delta > 0:
            direction = "up"
        else:
            direction = "down"

        projected = round(scores_over_time[-1] + recent_delta)
        projected = max(0, min(100, projected))

        return {
            "projected": projected,
            "confidence_low": max(0, projected - 10),
            "confidence_high": min(100, projected + 10),
            "direction": direction,
            "method": "directional",
            "confidence": "Low",
        }

    # Linear trend for 4+ periods
    x = list(range(n))
    x_mean = sum(x) / n
    y_mean = sum(scores_over_time) / n

    numerator = sum((x[i] - x_mean) * (scores_over_time[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

    if denominator == 0:
        slope = 0
    else:
        slope = numerator / denominator

    intercept = y_mean - slope * x_mean
    projected = round(intercept + slope * n)
    projected = max(0, min(100, projected))

    # Residual-based confidence band
    residuals = [scores_over_time[i] - (intercept + slope * i) for i in range(n)]
    residual_std = (sum(r ** 2 for r in residuals) / max(1, n - 2)) ** 0.5
    margin = round(1.5 * residual_std)

    if abs(slope) < 1:
        direction = "stable"
    elif slope > 0:
        direction = "up"
    else:
        direction = "down"

    return {
        "projected": projected,
        "confidence_low": max(0, projected - margin),
        "confidence_high": min(100, projected + margin),
        "direction": direction,
        "method": "linear_trend",
        "confidence": "Medium" if n >= 6 else "Low",
    }


def flag_declining_pillar(
    pillar_scores_over_time: list[float],
    current_quartile: Optional[int] = None,
) -> dict:
    """
    Flag a pillar if it shows concerning decline patterns.

    Flags if:
    - 2+ consecutive periods of decline, OR
    - Single-period drop of >10 points, OR
    - Currently in bottom quartile AND declining

    Args:
        pillar_scores_over_time: Scores ordered oldest to newest.
        current_quartile: 1-4 quartile position (4 = bottom). None if unknown.

    Returns:
        Dict with flagged (bool), reason (str), decline_magnitude (float).
    """
    if len(pillar_scores_over_time) < 2:
        return {"flagged": False, "reason": "Insufficient data", "decline_magnitude": 0}

    changes = [
        pillar_scores_over_time[i] - pillar_scores_over_time[i - 1]
        for i in range(1, len(pillar_scores_over_time))
    ]

    # Check single-period drop > 10
    latest_change = changes[-1]
    if latest_change < -10:
        return {
            "flagged": True,
            "reason": f"Sharp decline: {latest_change:+.1f} points in latest period",
            "decline_magnitude": abs(latest_change),
        }

    # Check 2+ consecutive declines
    consecutive_declines = 0
    for c in reversed(changes):
        if c < 0:
            consecutive_declines += 1
        else:
            break

    if consecutive_declines >= 2:
        total_decline = sum(changes[-consecutive_declines:])
        return {
            "flagged": True,
            "reason": (
                f"Sustained decline: {consecutive_declines} consecutive periods, "
                f"{total_decline:+.1f} points total"
            ),
            "decline_magnitude": abs(total_decline),
        }

    # Check bottom quartile + declining
    if current_quartile == 4 and latest_change < 0:
        return {
            "flagged": True,
            "reason": (
                f"Bottom quartile and still declining ({latest_change:+.1f} points)"
            ),
            "decline_magnitude": abs(latest_change),
        }

    return {"flagged": False, "reason": "No concerning patterns", "decline_magnitude": 0}


def project_headcount(
    headcounts: list[int],
    hires_per_period: Optional[list[int]] = None,
    exits_per_period: Optional[list[int]] = None,
) -> Optional[dict]:
    """
    Project headcount trajectory from historical data.

    Only meaningful with 3+ periods of data. Uses linear projection
    with confidence bands based on historical volatility.

    Args:
        headcounts: Headcount per period, oldest first.
        hires_per_period: Optional hire counts for decomposed projection.
        exits_per_period: Optional exit counts for decomposed projection.

    Returns:
        Dict with projected headcount, range, and growth indicator.
        None if insufficient data.
    """
    if len(headcounts) < 3:
        return None

    n = len(headcounts)
    x = list(range(n))
    x_mean = sum(x) / n
    y_mean = sum(headcounts) / n

    numerator = sum((x[i] - x_mean) * (headcounts[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

    slope = numerator / denominator if denominator != 0 else 0
    intercept = y_mean - slope * x_mean

    projected = round(intercept + slope * n)
    projected = max(0, projected)

    # Volatility-based confidence
    residuals = [headcounts[i] - (intercept + slope * i) for i in range(n)]
    residual_std = (sum(r ** 2 for r in residuals) / max(1, n - 2)) ** 0.5
    margin = round(1.5 * residual_std)

    if slope > 1:
        indicator = "growing"
    elif slope < -1:
        indicator = "shrinking"
    else:
        indicator = "stable"

    return {
        "projected_headcount": projected,
        "range_low": max(0, projected - margin),
        "range_high": projected + margin,
        "growth_indicator": indicator,
        "avg_period_change": round(slope, 1),
    }


def _score_to_tier(score: int) -> str:
    """Map 0-100 risk score to named tier."""
    if score >= 75:
        return "Critical"
    elif score >= 50:
        return "Elevated"
    elif score >= 25:
        return "Moderate"
    else:
        return "Low"
