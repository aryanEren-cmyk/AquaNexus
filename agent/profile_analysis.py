from profiles import OceanProfile, SYNTHETIC_PROFILES


THERMOCLINE_GRADIENT_THRESHOLD_C_PER_M = 0.05


def get_profile(profile_id: str) -> OceanProfile:
    """Return a complete synthetic profile by ID."""
    if not profile_id:
        raise ValueError("profile_id is required")
    try:
        return SYNTHETIC_PROFILES[profile_id]
    except KeyError as exc:
        raise KeyError(f"Unknown synthetic profile_id: {profile_id}") from exc


def _valid_depth_temperature_pairs(profile: OceanProfile) -> list[tuple[float, float]]:
    _validate_profile(profile)
    pairs = [
        (float(depth), float(temp))
        for depth, temp in zip(profile.depths, profile.temperatures)
        if temp is not None
    ]
    if not pairs:
        raise ValueError("profile has no valid temperature measurements")
    return sorted(pairs, key=lambda item: item[0])


def _validate_profile(profile: OceanProfile) -> None:
    if not isinstance(profile, OceanProfile):
        raise TypeError("profile must be an OceanProfile")
    if not profile.depths or not profile.temperatures:
        raise ValueError("profile must include depth and temperature values")
    if len(profile.depths) != len(profile.temperatures):
        raise ValueError("depth and temperature values must have the same length")


def get_surface_temperature(profile: OceanProfile) -> dict:
    """Return the shallowest valid temperature measurement."""
    depth, temperature = _valid_depth_temperature_pairs(profile)[0]
    return {
        "profile_id": profile.profile_id,
        "depth": depth,
        "temperature": temperature,
        "unit": "degC",
    }


def get_temperature_at_depth(profile: OceanProfile, target_depth: float) -> dict:
    """
    Return temperature at a target depth using linear interpolation.

    If the exact depth exists, that value is returned. Otherwise, the function
    interpolates between the nearest valid shallower and deeper measurements.
    It does not extrapolate beyond the measured depth range.
    """
    if target_depth < 0:
        raise ValueError("target_depth must be non-negative")

    pairs = _valid_depth_temperature_pairs(profile)
    min_depth = pairs[0][0]
    max_depth = pairs[-1][0]
    if target_depth < min_depth or target_depth > max_depth:
        raise ValueError("target_depth is outside the profile depth range")

    for depth, temperature in pairs:
        if depth == target_depth:
            return {
                "profile_id": profile.profile_id,
                "depth": depth,
                "temperature": temperature,
                "method": "exact",
                "unit": "degC",
            }

    for index in range(len(pairs) - 1):
        upper_depth, upper_temp = pairs[index]
        lower_depth, lower_temp = pairs[index + 1]
        if upper_depth <= target_depth <= lower_depth:
            fraction = (target_depth - upper_depth) / (lower_depth - upper_depth)
            interpolated = upper_temp + fraction * (lower_temp - upper_temp)
            return {
                "profile_id": profile.profile_id,
                "depth": float(target_depth),
                "temperature": round(interpolated, 3),
                "method": "linear_interpolation",
                "bracketing_depths": [upper_depth, lower_depth],
                "unit": "degC",
            }

    raise ValueError("unable to calculate temperature at requested depth")


def calculate_temperature_gradient(profile: OceanProfile) -> dict:
    """Calculate segment-by-segment temperature change with depth."""
    pairs = _valid_depth_temperature_pairs(profile)
    if len(pairs) < 2:
        raise ValueError("at least two valid measurements are required")

    segments = []
    for index in range(len(pairs) - 1):
        start_depth, start_temp = pairs[index]
        end_depth, end_temp = pairs[index + 1]
        depth_change = end_depth - start_depth
        if depth_change <= 0:
            raise ValueError("depth values must increase monotonically")
        temp_change = end_temp - start_temp
        gradient = temp_change / depth_change
        segments.append(
            {
                "start_depth": start_depth,
                "end_depth": end_depth,
                "temperature_change": round(temp_change, 3),
                "gradient_c_per_m": round(gradient, 4),
            }
        )

    return {
        "profile_id": profile.profile_id,
        "segments": segments,
        "unit": "degC_per_meter",
    }


def calculate_profile_statistics(profile: OceanProfile) -> dict:
    """Return basic deterministic statistics for valid profile measurements."""
    pairs = _valid_depth_temperature_pairs(profile)
    temperatures = [temperature for _, temperature in pairs]
    surface = get_surface_temperature(profile)

    return {
        "profile_id": profile.profile_id,
        "min_temperature": min(temperatures),
        "max_temperature": max(temperatures),
        "mean_temperature": round(sum(temperatures) / len(temperatures), 3),
        "surface_temperature": surface["temperature"],
        "deepest_valid_depth": pairs[-1][0],
        "valid_measurement_count": len(pairs),
        "unit": "degC",
    }


def detect_thermocline(profile: OceanProfile) -> dict:
    """
    Identify the strongest temperature-gradient segment.

    This is a simplified engineering heuristic, not a formal oceanographic
    thermocline detection algorithm. A segment is flagged when the absolute
    cooling rate is at least 0.05 degC per meter.
    """
    gradient_result = calculate_temperature_gradient(profile)
    strongest = max(
        gradient_result["segments"],
        key=lambda segment: abs(segment["gradient_c_per_m"]),
    )
    is_detected = abs(strongest["gradient_c_per_m"]) >= THERMOCLINE_GRADIENT_THRESHOLD_C_PER_M

    return {
        "profile_id": profile.profile_id,
        "thermocline_detected": is_detected,
        "start_depth": strongest["start_depth"],
        "end_depth": strongest["end_depth"],
        "gradient_c_per_m": strongest["gradient_c_per_m"],
        "heuristic": "strongest absolute gradient >= 0.05 degC per meter",
        "note": "Simplified heuristic for synthetic profile analysis only.",
    }
