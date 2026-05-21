# SABT Plugin Tests

Python test suite for the SABT SimHub plugin core algorithms.

## Why Python?

You edit C# on macOS but compile on Windows. These Python tests validate the
core math and logic **on macOS**, so you can iterate quickly without a Windows
build cycle.

## Running Tests

```bash
# Run all tests
python3 -m pytest Contributors/tests/ -v

# Or without pytest
python3 Contributors/tests/test_math_utils.py
python3 Contributors/tests/test_settings.py

# Run a specific test class
python3 -m pytest Contributors/tests/test_math_utils.py::TestEffectComputation -v
```

## What's Covered

| File | What It Tests |
|------|---------------|
| `test_math_utils.py` | `ConvertToFraction`, `ConvertToFractionOfRange`, `ClampTo`, adaptive normalization, effect computation, smoothing, CRC8 checksums, motor torque commands |
| `test_settings.py` | Settings validation (min ≤ max enforcement), range clamping, default values |

## What's NOT Covered (Manual Testing Required)

These tests cannot verify things that require a running SimHub instance:

- Serial port communication (WMI device detection, frame send/receive)
- WPF UI rendering and data binding
- Thread safety (ControlLoop vs DataUpdate race conditions)
- Motor physical behavior (torque, back-driving, power supply interaction)
- SimHub lifecycle integration (Init, End, DataUpdate callbacks)

See `Contributors/TESTING.md` for manual testing procedures.

## Adding New Tests

When you modify the C# code:

1. Port the algorithm to Python in the test file
2. Add test cases that exercise edge cases and expected behavior
3. Run the tests to verify correctness before compiling

## Porting Conventions

- C# `double` → Python `float`
- C# `int` → Python `int`
- C# `ref double` parameter → return tuple `(result, new_ref_value)`
- C# `Math.Max(a, b)` → Python `max(a, b)`
- C# `Math.Abs(x)` → Python `abs(x)`
- C# `ClampTo(value, min, max)` → Python `clamp_to(value, min, max)`
