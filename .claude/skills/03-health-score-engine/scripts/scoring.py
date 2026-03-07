"""
Reusable scoring utilities for the Workforce Health Score engine.

This module provides the core functions for:
- Percentile normalization of raw metrics
- Pillar score calculation
- Weight calibration via cross-company variance
- Final health score computation
- Gamification metadata (ranks, badges, benchmarks)

Usage:
    Import these functions into models/health_score_engine.py and adapt
    to the actual data structures produced by Session 2.
"""

import math
from typing import Optional


def percentile_normalize(
    values: list[float],
    invert: bool = False,
) -> list[float]:
    """
    Convert raw metric values to 0-100 percentile scores.

    Args:
        values: Raw metric values, one per company.
        invert: If True, lower raw values get higher scores.
                Use for metrics where lower is better (attrition, absence,
                time-to-fill, Gini coefficient, low performer concentration).

    Returns:
        List of 0-100 scores in the same order as input.
    """
    n = len(values)
    if n == 0:
        return []
    if n == 1:
        return [50.0]

    indexed = sorted(enumerate(values), key=lambda x: x[1])
    scores = [0.0] * n

    i = 0
    while i < n:
        # Find group of tied values
        j = i
        while j < n and indexed[j][1] == indexed[i][1]:
            j += 1
        # Mean rank for ties (0-indexed)
        mean_rank = (i + j - 1) / 2
        percentile = round(mean_rank / (n - 1) * 100, 1)
        for k in range(i, j):
            orig_idx = indexed[k][0]
            scores[orig_idx] = percentile
        i = j

    if invert:
        scores = [round(100 - s, 1) for s in scores]

    return scores


def compute_pillar_score(metric_scores: dict[str, Optional[float]]) -> Optional[float]:
    """
    Average of normalized metric scores within a pillar.

    Args:
        metric_scores: Dict of metric_name -> normalized score (0-100).
                       None values indicate missing data.

    Returns:
        Pillar score (0-100) or None if no valid scores exist.
    """
    valid_scores = [s for s in metric_scores.values() if s is not None]
    if not valid_scores:
        return None
    return round(sum(valid_scores) / len(valid_scores), 1)


def calibrate_weights(
    pillar_scores: dict[str, list[float]],
    floor: float = 0.05,
    ceiling: float = 0.35,
) -> dict[str, float]:
    """
    Weights proportional to cross-company variance of each pillar.

    Pillars with higher variance carry more weight because they are more
    differentiating across companies.

    Args:
        pillar_scores: Dict of pillar_name -> list of scores across companies.
        floor: Minimum weight for any pillar (default 5%).
        ceiling: Maximum weight for any pillar (default 35%).

    Returns:
        Dict of pillar_name -> weight, summing to 1.0.
    """
    variances = {}
    for name, scores in pillar_scores.items():
        valid = [s for s in scores if s is not None]
        if len(valid) < 2:
            variances[name] = 0.0
            continue
        mean = sum(valid) / len(valid)
        variances[name] = sum((x - mean) ** 2 for x in valid) / (len(valid) - 1)

    total_var = sum(variances.values())
    if total_var == 0:
        # Equal weights if no variance
        n = len(pillar_scores)
        return {name: round(1.0 / n, 4) for name in pillar_scores}

    # Initial proportional weights
    weights = {name: v / total_var for name, v in variances.items()}

    # Apply floor and ceiling, then re-normalize
    for _ in range(10):  # Iterate to converge after clamping
        clamped = {
            name: max(floor, min(ceiling, w)) for name, w in weights.items()
        }
        total = sum(clamped.values())
        weights = {name: round(w / total, 4) for name, w in clamped.items()}

    return weights


def compute_health_score(
    pillar_scores: dict[str, Optional[float]],
    weights: dict[str, float],
) -> Optional[int]:
    """
    Weighted sum of pillar scores -> final 0-100 score.

    Only includes pillars with non-None scores. Re-normalizes weights
    if some pillars are missing for a company.

    Returns:
        Integer health score (0-100), or None if no pillars have scores.
    """
    valid = {
        name: score
        for name, score in pillar_scores.items()
        if score is not None and name in weights
    }
    if not valid:
        return None

    # Re-normalize weights for available pillars
    available_weight = sum(weights[name] for name in valid)
    if available_weight == 0:
        return None

    score = sum(
        valid[name] * (weights[name] / available_weight) for name in valid
    )
    return round(score)


def assign_ranks(scores: dict[str, int]) -> dict[str, dict]:
    """
    Assign rank, quartile, and peer benchmarks from health scores.

    Args:
        scores: Dict of company_id -> health_score.

    Returns:
        Dict of company_id -> {rank, total, quartile, peer_top_quartile,
        peer_median, peer_bottom_quartile}.
    """
    sorted_companies = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    total = len(sorted_companies)
    all_scores = sorted(scores.values())

    # Peer benchmarks
    p75 = _percentile(all_scores, 75)
    p50 = _percentile(all_scores, 50)
    p25 = _percentile(all_scores, 25)

    result = {}
    for rank_idx, (company, score) in enumerate(sorted_companies):
        rank = rank_idx + 1
        quartile = math.ceil(rank / (total / 4)) if total >= 4 else 1
        quartile = min(quartile, 4)
        result[company] = {
            "rank": rank,
            "total": total,
            "quartile": quartile,
            "peer_top_quartile": p75,
            "peer_median": p50,
            "peer_bottom_quartile": p25,
        }
    return result


def assign_badges(
    company_id: str,
    pillar_scores: dict[str, Optional[float]],
    health_score: int,
    metrics: dict,
    rank_info: dict,
) -> list[str]:
    """
    Evaluate badge criteria for a company.

    Badge rules (from CLAUDE.md):
    - Retention Champion: attrition rate in bottom quartile (lowest 25%)
    - Pay Equity Leader: compensation Gini < 0.25
    - Hiring Velocity: time-to-hire in top quartile (fastest 25%)
    - Most Improved: largest score gain in the period (checked externally)
    - Workforce Elite: overall Health Score > 85

    Args:
        company_id: Company identifier.
        pillar_scores: This company's pillar scores.
        health_score: This company's overall health score.
        metrics: Raw metric values for badge threshold checks.
        rank_info: Rank and quartile data.

    Returns:
        List of badge names earned.
    """
    badges = []

    if health_score > 85:
        badges.append("workforce_elite")

    # Additional badge checks depend on available metrics.
    # The caller should pass relevant metric values and thresholds.
    # Example patterns:
    #
    # if metrics.get("attrition_rate_quartile") == 1:  # bottom quartile = lowest
    #     badges.append("retention_champion")
    #
    # if metrics.get("gini_coefficient", 1.0) < 0.25:
    #     badges.append("pay_equity_leader")
    #
    # if metrics.get("time_to_hire_quartile") == 1:  # top quartile = fastest
    #     badges.append("hiring_velocity")

    return badges


def _percentile(sorted_values: list[float], pct: float) -> float:
    """Simple percentile calculation on a sorted list."""
    if not sorted_values:
        return 0.0
    n = len(sorted_values)
    k = (pct / 100) * (n - 1)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_values[int(k)]
    return sorted_values[f] * (c - k) + sorted_values[c] * (k - f)
