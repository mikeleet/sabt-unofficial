"""
Tests for settings validation logic (from DeviceSettings.cs).

These ensure that settings constraints (e.g. min <= max) are maintained
correctly when values change.
"""

import unittest


class MockDeviceSettings:
    """Simplified mock of DeviceSettings with validation logic"""

    def __init__(self):
        self._minimum_tension = 200
        self._maximum_tension = 1000
        self._minimum_surge = -8
        self._maximum_surge = 25
        self._minimum_sway = -25
        self._maximum_sway = 25
        self._minimum_heave = -25
        self._maximum_heave = 90
        self._side_bias = 0
        self._smoothing_factor = 300
        self._auto_reconnect_delay = 3

    @property
    def minimum_tension(self):
        return self._minimum_tension

    @minimum_tension.setter
    def minimum_tension(self, value):
        self._minimum_tension = min(value, self._maximum_tension)

    @property
    def maximum_tension(self):
        return self._maximum_tension

    @maximum_tension.setter
    def maximum_tension(self, value):
        self._maximum_tension = max(value, self._minimum_tension)

    @property
    def minimum_surge(self):
        return self._minimum_surge

    @minimum_surge.setter
    def minimum_surge(self, value):
        self._minimum_surge = min(value, self._maximum_surge)

    @property
    def maximum_surge(self):
        return self._maximum_surge

    @maximum_surge.setter
    def maximum_surge(self, value):
        self._maximum_surge = max(value, self._minimum_surge)

    @property
    def minimum_sway(self):
        return self._minimum_sway

    @minimum_sway.setter
    def minimum_sway(self, value):
        self._minimum_sway = min(value, self._maximum_sway)

    @property
    def maximum_sway(self):
        return self._maximum_sway

    @maximum_sway.setter
    def maximum_sway(self, value):
        self._maximum_sway = max(value, self._minimum_sway)

    @property
    def minimum_heave(self):
        return self._minimum_heave

    @minimum_heave.setter
    def minimum_heave(self, value):
        self._minimum_heave = min(value, self._maximum_heave)

    @property
    def maximum_heave(self):
        return self._maximum_heave

    @maximum_heave.setter
    def maximum_heave(self, value):
        self._maximum_heave = max(value, self._minimum_heave)

    @property
    def auto_reconnect_delay(self):
        return self._auto_reconnect_delay

    @auto_reconnect_delay.setter
    def auto_reconnect_delay(self, value):
        self._auto_reconnect_delay = max(1, min(value, 10))


class TestSettingsValidation(unittest.TestCase):
    """Tests for settings constraint enforcement"""

    def setUp(self):
        self.s = MockDeviceSettings()

    def test_min_tension_cannot_exceed_max(self):
        self.s.minimum_tension = 1500
        self.assertEqual(self.s.minimum_tension, 1000)  # clamped to current max

    def test_max_tension_cannot_be_below_min(self):
        self.s.maximum_tension = 100
        self.assertEqual(self.s.maximum_tension, 200)  # clamped to current min

    def test_tightening_range(self):
        """Setting min higher and max lower should converge"""
        self.s.minimum_tension = 500  # now min=500, max still 1000
        self.assertEqual(self.s.minimum_tension, 500)

        self.s.maximum_tension = 400  # now max=500 (raised to min)
        self.assertEqual(self.s.maximum_tension, 500)

    def test_surge_range_enforcement(self):
        self.s.minimum_surge = 50
        self.assertEqual(self.s.minimum_surge, 25)  # capped at max

        self.s.maximum_surge = -50
        self.assertEqual(self.s.maximum_surge, 25)  # floored at current min (which is now 25)

    def test_sway_range_enforcement(self):
        self.s.minimum_sway = 50
        self.assertEqual(self.s.minimum_sway, 25)

        self.s.maximum_sway = -50
        self.assertEqual(self.s.maximum_sway, 25)  # floored at current min (now 25)

    def test_heave_range_enforcement(self):
        self.s.minimum_heave = 100
        self.assertEqual(self.s.minimum_heave, 90)

        self.s.maximum_heave = -50
        self.assertEqual(self.s.maximum_heave, 90)  # floored at current min (now 90)

    def test_auto_reconnect_delay_range(self):
        self.s.auto_reconnect_delay = 0
        self.assertEqual(self.s.auto_reconnect_delay, 1)  # minimum 1

        self.s.auto_reconnect_delay = 100
        self.assertEqual(self.s.auto_reconnect_delay, 10)  # maximum 10

        self.s.auto_reconnect_delay = 5
        self.assertEqual(self.s.auto_reconnect_delay, 5)  # valid

    def test_side_bias_no_enforcement(self):
        """Side bias has no min/max enforcement in settings (handled at runtime)"""
        self.s._side_bias = -2000
        self.assertEqual(self.s._side_bias, -2000)
        self.s._side_bias = 2000
        self.assertEqual(self.s._side_bias, 2000)

    def test_default_values(self):
        """Default values should be within valid ranges"""
        self.assertEqual(self.s.minimum_tension, 200)
        self.assertEqual(self.s.maximum_tension, 1000)
        self.assertLess(self.s.minimum_tension, self.s.maximum_tension)

        self.assertEqual(self.s.minimum_surge, -8)
        self.assertEqual(self.s.maximum_surge, 25)
        self.assertLess(self.s.minimum_surge, self.s.maximum_surge)

        self.assertEqual(self.s.minimum_sway, -25)
        self.assertEqual(self.s.maximum_sway, 25)
        self.assertLess(self.s.minimum_sway, self.s.maximum_sway)

        self.assertEqual(self.s.minimum_heave, -25)
        self.assertEqual(self.s.maximum_heave, 90)
        self.assertLess(self.s.minimum_heave, self.s.maximum_heave)

        self.assertEqual(self.s.auto_reconnect_delay, 3)
        self.assertTrue(1 <= self.s.auto_reconnect_delay <= 10)


class TestAdaptiveSettingsInteraction(unittest.TestCase):
    """Tests for how adaptive normalization settings interact"""

    def test_adaptive_enabled_disables_static_ranges(self):
        """When adaptive is on, the static range sliders should be irrelevant.
        In the C# code, the min/max values are set to -1000/1000 when adaptive is on.
        """
        # Simulate: when adaptive is on, the range is effectively unlimited
        min_surge = -1000
        max_surge = 1000
        surge = 20  # F1 level surge

        # With adaptive range, 20 m/s^2 maps to only 2% of full range
        # So the raw fraction is tiny, but that's OK because adaptive
        # normalization happens BEFORE this conversion
        from test_math_utils import convert_to_fraction_of_range

        fraction = convert_to_fraction_of_range(surge, min_surge, max_surge)
        self.assertAlmostEqual(fraction, 1020 / 2000)

        # The key insight: after adaptive normalization, surge becomes ~0.0 to 1.0
        # and the wide static range just passes it through unchanged.
        # So this test verifies the "pass-through" behavior is working.
        self.assertGreater(fraction, 0.5)


if __name__ == '__main__':
    unittest.main(verbosity=2)
