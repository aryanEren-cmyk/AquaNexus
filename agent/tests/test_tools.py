import sys
from pathlib import Path
from unittest import TestCase


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import (  # noqa: E402
    calculate_anomaly,
    check_significance,
    get_current_data,
    get_historical_baseline,
    get_spatial_pattern,
)


class ToolTests(TestCase):
    def test_mock_tools_can_be_called_independently(self):
        current = get_current_data("Arabian Sea", "temperature", "recent")
        baseline = get_historical_baseline("Arabian Sea", "temperature", "5yr avg")
        spatial = get_spatial_pattern("Arabian Sea")

        self.assertEqual(current["region"], "Arabian Sea")
        self.assertEqual(current["parameter"], "temperature")
        self.assertIn("value", current)
        self.assertEqual(baseline["mean"], 27.8)
        self.assertEqual(baseline["std_dev"], 0.6)
        self.assertGreaterEqual(len(spatial["nearby_comparisons"]), 3)

    def test_calculate_anomaly_preserves_positive_sign(self):
        result = calculate_anomaly(current_value=29.0, baseline_mean=27.8)

        self.assertGreater(result["deviation"], 0)
        self.assertGreater(result["percentage"], 0)

    def test_calculate_anomaly_preserves_negative_sign(self):
        result = calculate_anomaly(current_value=26.0, baseline_mean=27.8)

        self.assertLess(result["deviation"], 0)
        self.assertLess(result["percentage"], 0)

    def test_check_significance_handles_positive_and_negative_deviations(self):
        positive = check_significance(anomaly_deviation=1.0, std_dev=0.6)
        negative = check_significance(anomaly_deviation=-1.0, std_dev=0.6)

        self.assertTrue(positive["significant"])
        self.assertTrue(negative["significant"])
        self.assertEqual(positive["threshold_used"], 1.5)
        self.assertEqual(negative["threshold_used"], 1.5)
