import random

def get_current_data(region: str, parameter: str, time_range: str) -> dict:
    """Get recent measurements for a region/parameter. MOCK DATA for now."""
    return {
        "region": region,
        "parameter": parameter,
        "time_range": time_range,
        "value": round(random.uniform(27.0, 30.0), 2),
        "unit": "°C" if parameter == "temperature" else "unit",
    }

def get_historical_baseline(region: str, parameter: str, period: str) -> dict:
    """Get historical average for comparison. MOCK DATA for now."""
    return {
        "region": region,
        "parameter": parameter,
        "period": period,
        "mean": 27.8,
        "std_dev": 0.6,
    }

def calculate_anomaly(current_value: float, baseline_mean: float) -> dict:
    """Calculate deviation between current value and historical baseline."""
    deviation = current_value - baseline_mean
    percentage = (deviation / baseline_mean) * 100 if baseline_mean else 0
    return {
        "deviation": round(deviation, 2),
        "percentage": round(percentage, 2),
    }

def check_significance(anomaly_deviation: float, std_dev: float) -> dict:
    """
    Threshold heuristic — NOT a real statistical test.
    Significant if |deviation| > 1.5 standard deviations.
    """
    if std_dev == 0:
        return {"significant": False, "threshold_used": 1.5}
    ratio = abs(anomaly_deviation) / std_dev
    return {
        "significant": ratio > 1.5,
        "ratio": round(ratio, 2),
        "threshold_used": 1.5,
    }

def get_spatial_pattern(region: str, radius: str = "nearby") -> dict:
    """Compare anomaly across nearby regions. MOCK DATA for now."""
    nearby_regions = ["Northern Arabian Sea", "Southern Arabian Sea", "Gulf of Oman"]
    return {
        "region": region,
        "nearby_comparisons": [
            {"region": r, "deviation": round(random.uniform(-0.5, 1.2), 2)}
            for r in nearby_regions
        ],
    }