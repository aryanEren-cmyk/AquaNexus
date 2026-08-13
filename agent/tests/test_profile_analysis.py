import sys
from pathlib import Path
from unittest import TestCase


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from profile_analysis import (  # noqa: E402
    calculate_profile_statistics,
    calculate_temperature_gradient,
    detect_thermocline,
    get_profile,
    get_surface_temperature,
    get_temperature_at_depth,
)
from profiles import OceanProfile  # noqa: E402


WARM_PROFILE_ID = "SYN-ARABIAN-WARM-001"
NORMAL_PROFILE_ID = "SYN-ARABIAN-NORMAL-001"


class ProfileAnalysisTests(TestCase):
    def test_retrieving_known_profile(self):
        profile = get_profile(WARM_PROFILE_ID)

        self.assertEqual(profile.profile_id, WARM_PROFILE_ID)
        self.assertEqual(profile.source, "synthetic_test_data")
        self.assertEqual(profile.latitude, 15.2)
        self.assertEqual(len(profile.depths), len(profile.temperatures))

    def test_invalid_profile_id(self):
        with self.assertRaises(KeyError):
            get_profile("DOES-NOT-EXIST")

    def test_surface_temperature(self):
        profile = get_profile(WARM_PROFILE_ID)

        result = get_surface_temperature(profile)

        self.assertEqual(result["depth"], 0.0)
        self.assertEqual(result["temperature"], 30.6)

    def test_temperature_lookup_at_exact_depth(self):
        profile = get_profile(NORMAL_PROFILE_ID)

        result = get_temperature_at_depth(profile, 50)

        self.assertEqual(result["method"], "exact")
        self.assertEqual(result["temperature"], 25.9)

    def test_temperature_lookup_at_non_exact_depth_uses_linear_interpolation(self):
        profile = get_profile(NORMAL_PROFILE_ID)

        result = get_temperature_at_depth(profile, 30)

        self.assertEqual(result["method"], "linear_interpolation")
        self.assertEqual(result["bracketing_depths"], [25.0, 50.0])
        self.assertAlmostEqual(result["temperature"], 27.18)

    def test_gradient_calculation(self):
        profile = get_profile(WARM_PROFILE_ID)

        result = calculate_temperature_gradient(profile)

        self.assertEqual(result["profile_id"], WARM_PROFILE_ID)
        self.assertEqual(len(result["segments"]), 7)
        self.assertEqual(result["segments"][2]["start_depth"], 25.0)
        self.assertEqual(result["segments"][2]["end_depth"], 50.0)
        self.assertEqual(result["segments"][2]["gradient_c_per_m"], -0.152)

    def test_profile_statistics(self):
        profile = get_profile(NORMAL_PROFILE_ID)

        result = calculate_profile_statistics(profile)

        self.assertEqual(result["min_temperature"], 14.6)
        self.assertEqual(result["max_temperature"], 28.4)
        self.assertEqual(result["surface_temperature"], 28.4)
        self.assertEqual(result["deepest_valid_depth"], 200.0)
        self.assertEqual(result["valid_measurement_count"], 8)
        self.assertAlmostEqual(result["mean_temperature"], 23.438)

    def test_thermocline_detection(self):
        profile = get_profile(WARM_PROFILE_ID)

        result = detect_thermocline(profile)

        self.assertTrue(result["thermocline_detected"])
        self.assertEqual(result["start_depth"], 25.0)
        self.assertEqual(result["end_depth"], 50.0)
        self.assertEqual(result["gradient_c_per_m"], -0.152)

    def test_invalid_empty_profile_handling(self):
        empty = OceanProfile(
            profile_id="EMPTY",
            latitude=0.0,
            longitude=0.0,
            timestamp="2026-07-15T00:00:00Z",
            depths=(),
            temperatures=(),
        )

        with self.assertRaises(ValueError):
            get_surface_temperature(empty)
