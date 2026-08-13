import random
from profile_analysis import (
    calculate_profile_statistics as analyze_profile_statistics,
    calculate_temperature_gradient as analyze_temperature_gradient,
    detect_thermocline as analyze_thermocline,
    get_profile as load_profile,
    get_temperature_at_depth as analyze_temperature_at_depth,
)

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

def get_profile(profile_id: str) -> dict:
    """Return one complete synthetic/test ocean profile."""
    return load_profile(profile_id).to_dict()

def get_temperature_at_depth(profile_id: str, target_depth: float) -> dict:
    """Return deterministic profile temperature at depth using interpolation."""
    profile = load_profile(profile_id)
    return analyze_temperature_at_depth(profile, target_depth)

def calculate_temperature_gradient(profile_id: str) -> dict:
    """Return segment-by-segment deterministic temperature gradients."""
    profile = load_profile(profile_id)
    return analyze_temperature_gradient(profile)

def calculate_profile_statistics(profile_id: str) -> dict:
    """Return deterministic summary statistics for a synthetic/test profile."""
    profile = load_profile(profile_id)
    return analyze_profile_statistics(profile)

def detect_thermocline(profile_id: str) -> dict:
    """Detect strongest gradient zone with a simplified heuristic."""
    profile = load_profile(profile_id)
    return analyze_thermocline(profile)
