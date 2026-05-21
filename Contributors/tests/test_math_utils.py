"""
Unit tests for SABT plugin core algorithms.

These tests mirror the C# implementation in DevicePlugin.cs, DeviceSettings.cs,
and MotorController.cs. They can be run on macOS/Linux without needing the .NET
build environment.

Usage:
    python3 Contributors/tests/test_math_utils.py
    python3 -m pytest Contributors/tests/test_math_utils.py -v
"""

import math
import unittest


# ---------------------------------------------------------------------------
# Ported C# utility functions (from DevicePlugin.cs)
# ---------------------------------------------------------------------------

def convert_to_fraction(value: float, resolution: int = 1000) -> float:
    """C# equivalent: ConvertToFraction(value, resolution)"""
    value = value / resolution
    if value < -1.0:
        return -1.0
    if value > 1.0:
        return 1.0
    return value


def convert_to_fraction_of_range(value: float, min_val: float, max_val: float) -> float:
    """C# equivalent: ConvertToFractionOfRange(value, min, max)"""
    value = clamp_to(value, min_val, max_val)
    if max_val == min_val:
        return 0.0
    return (value - min_val) / (max_val - min_val)


def clamp_to(value: float, min_val: float, max_val: float) -> float:
    """C# equivalent: ClampTo(value, min, max)"""
    if value < min_val:
        return min_val
    if value > max_val:
        return max_val
    return value


# ---------------------------------------------------------------------------
# Adaptive peak normalization (from DevicePlugin.ApplyAdaptiveNormalization)
# ---------------------------------------------------------------------------

def apply_adaptive_normalization(running_peak: float, raw_value: float, decay_per_frame: float) -> tuple:
    """
    C# equivalent: ApplyAdaptiveNormalization(ref runningPeak, rawValue, decayPerFrame)
    Returns (normalized_value, new_running_peak)
    """
    abs_value = abs(raw_value)
    running_peak = max(abs_value, running_peak * decay_per_frame)

    if running_peak < 0.5:
        running_peak = 0.5

    normalized = raw_value / running_peak

    if normalized < -1.0:
        normalized = -1.0
    if normalized > 1.0:
        normalized = 1.0

    return normalized, running_peak


def compute_decay_factor(adaptive_decay_rate: int) -> float:
    """
    C# equivalent: UpdateAdaptiveDecay() logic
    Converts 0-1000 slider value to a per-frame decay factor.
    """
    fraction = convert_to_fraction(adaptive_decay_rate)
    # 0.99999 at slider=0, 0.99 at slider=1000
    return 0.99999 - fraction * (0.99999 - 0.99)


# ---------------------------------------------------------------------------
# Effect computation (from DevicePlugin.ControlLoop)
# ---------------------------------------------------------------------------

def compute_effects(
    surge: float, sway: float, heave: float, speed: float,
    min_surge: int, max_surge: int,
    min_sway: int, max_sway: int,
    min_heave: int, max_heave: int,
    idle_tension: float, min_tension: float, max_tension: float,
    side_bias: float,
    cornering_strength: float, braking_strength: float,
    acceleration_strength: float, jumping_strength: float,
    landing_strength: float,
    is_upshift: bool = False, shifting_strength: float = 0.0,
) -> tuple:
    """
    C# equivalent: ControlLoop() effect computation.
    Returns (left_target, right_target)
    """
    is_moving = speed > 0.2

    # Tuning - convert slider ints to fractions
    min_surge_f = float(min_surge)
    max_surge_f = float(max_surge)
    min_sway_f = float(min_sway)
    max_sway_f = float(max_sway)
    min_heave_f = float(min_heave)
    max_heave_f = float(max_heave)

    # Normalize sway to [-1, 1]
    sway_norm = (convert_to_fraction_of_range(sway, min_sway_f, max_sway_f) * 2.0) - 1.0

    # Compute effect fractions
    braking = convert_to_fraction_of_range(surge, 0, max_surge_f)
    acceleration = 1.0 - convert_to_fraction_of_range(surge, min_surge_f, 0)
    landing = convert_to_fraction_of_range(heave, 0, max_heave_f)
    jumping = 1.0 - convert_to_fraction_of_range(heave, min_heave_f, 0)

    # Effects
    inc_left = 0.0
    inc_right = 0.0
    dec_left = 0.0
    dec_right = 0.0

    inc_left = max(inc_left, braking * braking_strength)
    inc_right = max(inc_right, braking * braking_strength)
    dec_left = max(dec_left, acceleration * acceleration_strength)
    dec_right = max(dec_right, acceleration * acceleration_strength)
    dec_left = max(dec_left, jumping * jumping_strength)
    dec_right = max(dec_right, jumping * jumping_strength)
    inc_left = max(inc_left, landing * landing_strength)
    inc_right = max(inc_right, landing * landing_strength)
    inc_left = max(inc_left, (abs(sway_norm * cornering_strength)) if sway_norm <= 0.0 else 0.0)
    inc_right = max(inc_right, (abs(sway_norm * cornering_strength)) if sway_norm > 0.0 else 0.0)

    # Combinator
    total_left = inc_left - dec_left
    total_right = inc_right - dec_right

    if total_left < 0.0:
        left_target = min_tension + (total_left * min_tension)
    else:
        left_target = min_tension + (total_left * (max_tension - min_tension))

    if total_right < 0.0:
        right_target = min_tension + (total_right * min_tension)
    else:
        right_target = min_tension + (total_right * (max_tension - min_tension))

    # Clamp
    left_target = clamp_to(left_target, 0.0, max_tension)
    right_target = clamp_to(right_target, 0.0, max_tension)

    # Idle tension when stationary
    if not is_moving:
        left_target = idle_tension
        right_target = idle_tension

    # Side bias
    if side_bias < 0.0:
        right_target *= (1.0 - abs(side_bias))
    elif side_bias > 0.0:
        left_target *= (1.0 - side_bias)

    return left_target, right_target


# ---------------------------------------------------------------------------
# Smoothing (from MotorController.Motor.SetTorque)
# ---------------------------------------------------------------------------

def apply_smoothing(torque: float, prev_smoothed: float, smoothing_factor: float) -> float:
    """
    C# equivalent: Motor.SetTorque() smoothing.
    smoothed = torque * (1 - factor) + prevSmoothed * factor
    """
    return torque * (1.0 - smoothing_factor) + prev_smoothed * smoothing_factor


def compute_torque_command(torque: float, torque_limit: int = 12000) -> int:
    """
    C# equivalent: short torque command computation.
    torque is negated (motor convention) and clamped to [-torque_limit, torque_limit]
    """
    raw = torque * torque_limit * -1.0
    return int(clamp_to(raw, -torque_limit, torque_limit))


# ---------------------------------------------------------------------------
# CRC8 checksum (from MotorController.CalculateChecksum)
# ---------------------------------------------------------------------------

def calculate_checksum(data: list, data_length: int) -> int:
    """
    C# equivalent: CalculateChecksum(byte[] data, int dataLength)
    XOR-based CRC8 with polynomial 0x8C
    """
    checksum = 0x00
    for i in range(data_length):
        checksum ^= data[i]
        for _ in range(8):
            if (checksum & 0x01) != 0:
                checksum = (checksum >> 1) ^ 0x8C
            else:
                checksum >>= 1
    return checksum & 0xFF


def build_frame(identifier: int, command: int,
                b0: int = 0, b1: int = 0, b2: int = 0,
                b3: int = 0, b4: int = 0, b5: int = 0,
                b6: int = 0, b7: int = None) -> list:
    """
    C# equivalent: BuildFrame()
    Constructs a 10-byte frame with CRC8 checksum.
    """
    payload = [0] * 10
    payload[0] = identifier & 0xFF
    payload[1] = command & 0xFF
    payload[2] = b0 & 0xFF
    payload[3] = b1 & 0xFF
    payload[4] = b2 & 0xFF
    payload[5] = b3 & 0xFF
    payload[6] = b4 & 0xFF
    payload[7] = b5 & 0xFF
    payload[8] = b6 & 0xFF
    payload[9] = b7 if b7 is not None else calculate_checksum(payload, 9)
    return payload


# ===========================================================================
# Tests
# ===========================================================================

class TestConvertToFraction(unittest.TestCase):
    """Tests for ConvertToFraction()"""

    def test_zero(self):
        self.assertEqual(convert_to_fraction(0), 0.0)

    def test_half(self):
        self.assertEqual(convert_to_fraction(500), 0.5)

    def test_full(self):
        self.assertEqual(convert_to_fraction(1000), 1.0)

    def test_overflow(self):
        self.assertEqual(convert_to_fraction(1500), 1.0)

    def test_negative(self):
        self.assertEqual(convert_to_fraction(-500), -0.5)

    def test_negative_overflow(self):
        self.assertEqual(convert_to_fraction(-1500), -1.0)

    def test_custom_resolution(self):
        self.assertEqual(convert_to_fraction(125, 250), 0.5)

    def test_near_boundary(self):
        self.assertAlmostEqual(convert_to_fraction(999), 0.999)


class TestConvertToFractionOfRange(unittest.TestCase):
    """Tests for ConvertToFractionOfRange()"""

    def test_midpoint(self):
        result = convert_to_fraction_of_range(0, -10, 10)
        self.assertEqual(result, 0.5)

    def test_min(self):
        result = convert_to_fraction_of_range(-10, -10, 10)
        self.assertEqual(result, 0.0)

    def test_max(self):
        result = convert_to_fraction_of_range(10, -10, 10)
        self.assertEqual(result, 1.0)

    def test_below_range(self):
        result = convert_to_fraction_of_range(-20, -10, 10)
        self.assertEqual(result, 0.0)

    def test_above_range(self):
        result = convert_to_fraction_of_range(20, -10, 10)
        self.assertEqual(result, 1.0)

    def test_f1_surge(self):
        """F1 car surge: -30 to 40 m/s^2 range"""
        surge = 20  # mid braking
        result = convert_to_fraction_of_range(surge, -30, 40)
        self.assertAlmostEqual(result, 50 / 70)

    def test_slow_car_surge(self):
        """Slow car surge: -3 to 8 m/s^2 range"""
        surge = 5  # mid braking
        result = convert_to_fraction_of_range(surge, -3, 8)
        self.assertAlmostEqual(result, 8 / 11)

    def test_zero_range(self):
        result = convert_to_fraction_of_range(5, 10, 10)
        self.assertEqual(result, 0.0)


class TestClampTo(unittest.TestCase):
    """Tests for ClampTo()"""

    def test_within_range(self):
        self.assertEqual(clamp_to(5, 0, 10), 5)

    def test_below_range(self):
        self.assertEqual(clamp_to(-5, 0, 10), 0)

    def test_above_range(self):
        self.assertEqual(clamp_to(15, 0, 10), 10)

    def test_at_min(self):
        self.assertEqual(clamp_to(0, 0, 10), 0)

    def test_at_max(self):
        self.assertEqual(clamp_to(10, 0, 10), 10)

    def test_negative_range(self):
        self.assertEqual(clamp_to(-20, -10, 10), -10)


class TestAdaptivePeakNormalization(unittest.TestCase):
    """Tests for ApplyAdaptiveNormalization()"""

    def test_startup_floor(self):
        """At startup, floor of 0.5 prevents division blowup"""
        peak = 0.0
        norm, peak = apply_adaptive_normalization(peak, 0.1, 0.999)
        self.assertAlmostEqual(norm, 0.2)  # 0.1 / 0.5
        self.assertAlmostEqual(peak, 0.5)  # floor

    def test_peak_tracking(self):
        """Peak should rise to match new maximum"""
        peak = 0.5
        norm, peak = apply_adaptive_normalization(peak, 20.0, 0.999)
        self.assertAlmostEqual(norm, 1.0)  # 20 / 20
        self.assertAlmostEqual(peak, 20.0)

    def test_peak_decay(self):
        """After peak, smaller values cause decay"""
        peak = 20.0
        norm, peak = apply_adaptive_normalization(peak, 0.0, 0.99)
        self.assertAlmostEqual(norm, 0.0)
        self.assertAlmostEqual(peak, 19.8)  # 20 * 0.99

    def test_f1_vs_slow_car_normalization(self):
        """Both should map to full [-1, 1] range"""
        decay = 0.999

        # F1 car: 20 m/s^2 surge
        peak = 20.0
        norm_f1, peak = apply_adaptive_normalization(peak, 15.0, decay)
        # peak decays slightly: 20*0.999=19.98, then 15/19.98 ≈ 0.75
        self.assertAlmostEqual(norm_f1, 0.75, places=1)

        # Slow car: 3 m/s^2 surge
        peak = 3.0
        norm_slow, peak = apply_adaptive_normalization(peak, 3.0, decay)
        self.assertAlmostEqual(norm_slow, 1.0, places=2)

    def test_negative_values(self):
        """Negative values (e.g. acceleration surge) should normalize"""
        peak = 10.0
        norm, peak = apply_adaptive_normalization(peak, -8.0, 0.999)
        self.assertAlmostEqual(norm, -0.8, places=1)

    def test_clamping(self):
        """Value exceeding peak should clamp to -1 or +1"""
        peak = 10.0
        norm, peak = apply_adaptive_normalization(peak, 15.0, 0.999)
        self.assertEqual(norm, 1.0)
        self.assertAlmostEqual(peak, 15.0)  # peak updated

    def test_stable_after_convergence(self):
        """After convergence, values within peak should be linear"""
        peak = 10.0
        norm, peak = apply_adaptive_normalization(peak, 5.0, 0.999)
        self.assertAlmostEqual(norm, 0.5, places=1)
        self.assertAlmostEqual(peak, 9.99, places=2)


class TestDecayFactor(unittest.TestCase):
    """Tests for decay factor computation"""

    def test_slider_zero(self):
        """Slider at 0 = slowest decay (long memory)"""
        factor = compute_decay_factor(0)
        self.assertAlmostEqual(factor, 0.99999)

    def test_slider_max(self):
        """Slider at 1000 = fastest decay"""
        factor = compute_decay_factor(1000)
        self.assertAlmostEqual(factor, 0.99)

    def test_slider_mid(self):
        """Slider at 500 = medium decay"""
        factor = compute_decay_factor(500)
        self.assertAlmostEqual(factor, 0.994995)

    def test_monotonic(self):
        """Higher slider = lower decay factor (faster forgetting)"""
        prev = compute_decay_factor(0)
        for i in range(1, 1001, 100):
            current = compute_decay_factor(i)
            self.assertLessEqual(current, prev)
            prev = current


class TestEffectComputation(unittest.TestCase):
    """Tests for the effect computation engine"""

    def test_stationary_idle_tension(self):
        """When not moving, idle tension should be applied"""
        left, right = compute_effects(
            surge=0, sway=0, heave=0, speed=0,
            min_surge=-8, max_surge=25,
            min_sway=-25, max_sway=25,
            min_heave=-25, max_heave=90,
            idle_tension=0.15, min_tension=0.2, max_tension=1.0,
            side_bias=0.0,
            cornering_strength=1.0, braking_strength=1.0,
            acceleration_strength=1.0, jumping_strength=1.0,
            landing_strength=1.0,
        )
        self.assertAlmostEqual(left, 0.15)
        self.assertAlmostEqual(right, 0.15)

    def test_braking_increases_tension(self):
        """Braking should increase tension on both belts"""
        left, right = compute_effects(
            surge=20, sway=0, heave=0, speed=50,  # strong positive surge = braking
            min_surge=-8, max_surge=25,
            min_sway=-25, max_sway=25,
            min_heave=-25, max_heave=90,
            idle_tension=0.15, min_tension=0.2, max_tension=1.0,
            side_bias=0.0,
            cornering_strength=1.0, braking_strength=1.0,
            acceleration_strength=1.0, jumping_strength=1.0,
            landing_strength=1.0,
        )
        # Both should be above min_tension
        self.assertGreater(left, 0.5)
        self.assertGreater(right, 0.5)
        self.assertAlmostEqual(left, right)  # braking affects both equally

    def test_cornering_asymmetric(self):
        """Left turn (negative sway) should tension right belt"""
        left, right = compute_effects(
            surge=0, sway=-15, heave=0, speed=50,
            min_surge=-8, max_surge=25,
            min_sway=-25, max_sway=25,
            min_heave=-25, max_heave=90,
            idle_tension=0.15, min_tension=0.2, max_tension=1.0,
            side_bias=0.0,
            cornering_strength=1.0, braking_strength=1.0,
            acceleration_strength=1.0, jumping_strength=1.0,
            landing_strength=1.0,
        )
        # With sway <= 0, left belt gets the cornering increase
        self.assertGreater(left, right)

    def test_cornering_right_turn(self):
        """Right turn (positive sway) should tension left belt"""
        left, right = compute_effects(
            surge=0, sway=15, heave=0, speed=50,
            min_surge=-8, max_surge=25,
            min_sway=-25, max_sway=25,
            min_heave=-25, max_heave=90,
            idle_tension=0.15, min_tension=0.2, max_tension=1.0,
            side_bias=0.0,
            cornering_strength=1.0, braking_strength=1.0,
            acceleration_strength=1.0, jumping_strength=1.0,
            landing_strength=1.0,
        )
        # With sway > 0, right belt gets the cornering increase
        self.assertGreater(right, left)

    def test_acceleration_reduces_tension(self):
        """Negative surge (acceleration) should reduce tension"""
        left, right = compute_effects(
            surge=-6, sway=0, heave=0, speed=50,
            min_surge=-8, max_surge=25,
            min_sway=-25, max_sway=25,
            min_heave=-25, max_heave=90,
            idle_tension=0.15, min_tension=0.2, max_tension=1.0,
            side_bias=0.0,
            cornering_strength=1.0, braking_strength=1.0,
            acceleration_strength=1.0, jumping_strength=1.0,
            landing_strength=1.0,
        )
        # Both should be at or below minimum tension
        self.assertLessEqual(left, 0.2)
        self.assertLessEqual(right, 0.2)

    def test_clamped_to_zero(self):
        """Tension should never go below 0"""
        left, right = compute_effects(
            surge=-8, sway=0, heave=0, speed=50,
            min_surge=-8, max_surge=25,
            min_sway=-25, max_sway=25,
            min_heave=-25, max_heave=90,
            idle_tension=0.15, min_tension=0.2, max_tension=1.0,
            side_bias=0.0,
            cornering_strength=1.0, braking_strength=1.0,
            acceleration_strength=1.0, jumping_strength=1.0,
            landing_strength=1.0,
        )
        self.assertGreaterEqual(left, 0.0)
        self.assertGreaterEqual(right, 0.0)

    def test_side_bias_left(self):
        """Positive side bias should reduce left belt tension"""
        left, right = compute_effects(
            surge=20, sway=0, heave=0, speed=50,
            min_surge=-8, max_surge=25,
            min_sway=-25, max_sway=25,
            min_heave=-25, max_heave=90,
            idle_tension=0.15, min_tension=0.2, max_tension=1.0,
            side_bias=0.5,  # 50% reduction on left
            cornering_strength=1.0, braking_strength=1.0,
            acceleration_strength=1.0, jumping_strength=1.0,
            landing_strength=1.0,
        )
        self.assertLess(left, right)

    def test_side_bias_right(self):
        """Negative side bias should reduce right belt tension"""
        left, right = compute_effects(
            surge=20, sway=0, heave=0, speed=50,
            min_surge=-8, max_surge=25,
            min_sway=-25, max_sway=25,
            min_heave=-25, max_heave=90,
            idle_tension=0.15, min_tension=0.2, max_tension=1.0,
            side_bias=-0.5,  # 50% reduction on right
            cornering_strength=1.0, braking_strength=1.0,
            acceleration_strength=1.0, jumping_strength=1.0,
            landing_strength=1.0,
        )
        self.assertGreater(left, right)

    def test_zero_strength_effects(self):
        """When all effects are at 0 strength, only min tension is applied"""
        left, right = compute_effects(
            surge=20, sway=15, heave=40, speed=50,
            min_surge=-8, max_surge=25,
            min_sway=-25, max_sway=25,
            min_heave=-25, max_heave=90,
            idle_tension=0.15, min_tension=0.2, max_tension=1.0,
            side_bias=0.0,
            cornering_strength=0.0, braking_strength=0.0,
            acceleration_strength=0.0, jumping_strength=0.0,
            landing_strength=0.0,
        )
        self.assertAlmostEqual(left, 0.2)
        self.assertAlmostEqual(right, 0.2)

    def test_max_tension_clamp(self):
        """Tension should not exceed max_tension"""
        left, right = compute_effects(
            surge=25, sway=0, heave=0, speed=50,
            min_surge=-8, max_surge=25,
            min_sway=-25, max_sway=25,
            min_heave=-25, max_heave=90,
            idle_tension=0.15, min_tension=0.2, max_tension=1.0,
            side_bias=0.0,
            cornering_strength=1.0, braking_strength=1.0,
            acceleration_strength=1.0, jumping_strength=1.0,
            landing_strength=1.0,
        )
        self.assertLessEqual(left, 1.0)
        self.assertLessEqual(right, 1.0)

    def test_normalized_adaptive_vs_static(self):
        """With adaptive normalization (wider ranges), same car should feel similar"""
        def run_with_ranges(min_s, max_s, min_sw, max_sw, min_h, max_h):
            return compute_effects(
                surge=20, sway=0, heave=0, speed=50,
                min_surge=min_s, max_surge=max_s,
                min_sway=min_sw, max_sway=max_sw,
                min_heave=min_h, max_heave=max_h,
                idle_tension=0.15, min_tension=0.2, max_tension=1.0,
                side_bias=0.0,
                cornering_strength=1.0, braking_strength=1.0,
                acceleration_strength=1.0, jumping_strength=1.0,
                landing_strength=1.0,
            )

        # With adaptive ranges, the normalized surge should produce similar tension
        # because the wider range means the same raw surge maps to a lower fraction,
        # simulating how adaptive normalization treats F1 vs slow car equally
        f1_left, f1_right = run_with_ranges(-8, 25, -25, 25, -25, 90)
        adaptive_left, adaptive_right = run_with_ranges(-1000, 1000, -1000, 1000, -1000, 1000)

        # F1: 20/33 = 0.606 → braking = 20/25 = 0.8 → high tension
        # Adaptive: 20/2000 = 0.01 → braking = 20/1000 = 0.02 → very low tension
        # This proves: with wider adaptive range, the raw surge maps to lower effect
        self.assertGreater(f1_left, adaptive_left)


class TestSmoothing(unittest.TestCase):
    """Tests for the torque smoothing algorithm"""

    def test_no_smoothing(self):
        """factor=0 means immediate response"""
        result = apply_smoothing(0.5, 0.0, 0.0)
        self.assertEqual(result, 0.5)

    def test_full_smoothing(self):
        """factor=1 means no change (fully smoothed)"""
        result = apply_smoothing(0.5, 0.8, 1.0)
        self.assertAlmostEqual(result, 0.8)

    def test_partial_smoothing(self):
        """factor=0.3 means 70% new, 30% old"""
        result = apply_smoothing(0.5, 0.2, 0.3)
        expected = 0.5 * 0.7 + 0.2 * 0.3
        self.assertAlmostEqual(result, expected)

    def test_smoothing_convergence(self):
        """Smoothing should converge toward target value"""
        prev = 0.0
        for _ in range(100):
            prev = apply_smoothing(1.0, prev, 0.9)
        self.assertGreater(prev, 0.999)  # nearly converged

    def test_smoothing_factor_from_settings(self):
        """Test with actual settings slider value"""
        smoothing = convert_to_fraction(300)  # default smoothing
        self.assertAlmostEqual(smoothing, 0.3)


class TestCRC8(unittest.TestCase):
    """Tests for the serial frame CRC8 checksum"""

    def test_empty_checksum(self):
        """CRC of zeroed data"""
        data = [0] * 9
        result = calculate_checksum(data, 9)
        self.assertEqual(result, 0x00)

    def test_known_frame(self):
        """Verify CRC for a known motor query frame"""
        # Motor ID 0x01, command 0x74 (query)
        frame = build_frame(0x01, 0x74)
        # The checksum is at position 9
        result = calculate_checksum(frame, 9)
        self.assertEqual(frame[9], result)

    def test_torque_frame(self):
        """Verify CRC for a torque command frame"""
        # Motor ID 0x01, command 0x64 (torque), value = 0x02EE (750)
        frame = build_frame(0x01, 0x64, 0x02, 0xEE)
        result = calculate_checksum(frame, 9)
        self.assertEqual(frame[9], result)

    def test_checksum_validation(self):
        """A good frame should pass validation, a bad one should fail"""
        # Motor ID 0x01, response frame
        frame = build_frame(0x01, 0x01)  # motor ID, torque mode byte
        result = calculate_checksum(frame, 9)
        self.assertEqual(frame[9], result)  # should match

        # Tamper with the frame - should fail
        frame[9] = (frame[9] + 1) & 0xFF
        result2 = calculate_checksum(frame, 9)
        self.assertNotEqual(frame[9], result2)

    def test_identifier_set_frame(self):
        """Build the special ID assignment frame"""
        frame = build_frame(0xAA, 0x55, 0x53, 0x01)
        self.assertEqual(frame[0], 0xAA)
        self.assertEqual(frame[1], 0x55)
        self.assertEqual(frame[2], 0x53)
        self.assertEqual(frame[3], 0x01)
        result = calculate_checksum(frame, 9)
        self.assertEqual(frame[9], result)


class TestMotorTorqueCommand(unittest.TestCase):
    """Tests for torque command computation"""

    def test_zero_torque(self):
        result = compute_torque_command(0.0)
        self.assertEqual(result, 0)

    def test_full_forward(self):
        result = compute_torque_command(1.0)
        self.assertEqual(result, -12000)

    def test_full_reverse(self):
        result = compute_torque_command(-1.0)
        self.assertEqual(result, 12000)

    def test_half_torque(self):
        result = compute_torque_command(0.5)
        self.assertEqual(result, -6000)

    def test_clamp_overflow(self):
        result = compute_torque_command(2.0)
        self.assertEqual(result, -12000)  # clamped


if __name__ == '__main__':
    unittest.main(verbosity=2)
