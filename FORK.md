# Unofficial Fork

This is an **unofficial fork** of the [Simple Active Belt Tensioner](https://github.com/GeorgeWilkins/Simple-Active-Belt-Tensioner) by George Wilkins.

## What's Different

This branch contains bug fixes, quality-of-life improvements, and experimental features not yet merged upstream. These changes are **actively used** on a real rig and validated with hardware.

### Key Additions

- **Auto-Calibrate v2**: EMA peak-based telemetry normalization (works from frame 1, no dead zone)
- **Per-tab ScrollViewers**: Tab headers stay visible when switching between Connection/Tuning tabs
- **Test Motor improvements**: 50% torque, zero-torque release after test, serial port safety wrapper
- **Suppress Activation Warning** toggle (Connection tab, defaults ON)
- **Auto-reconnect retry**: 3 attempts before giving up, 0s minimum delay
- **Back-drive cable adapter warnings**: Connection tab + Tuning tab (all 5 languages)
- **Smoothing Factor guidance**: explains back-EMF and when to increase it
- Telemetry graph: 250px, Y-axis auto-scaling, 600-point history, pause toggle
- Slider units: m/s² for limits, (s) for auto-reconnect

### What Was Removed

- Massage chair (fun easter egg — removed, didn't fit the project scope)
- Window Size slider + Calibration Progress bar (over-engineering)
- Rolling window buffers (replaced with simpler EMA approach)

## Contributing Upstream

Bug fixes and features from this fork are offered back to the [upstream project](https://github.com/GeorgeWilkins/Simple-Active-Belt-Tensioner) as focused, single-purpose pull requests. See the [upstream issues](https://github.com/GeorgeWilkins/Simple-Active-Belt-Tensioner/issues) for active discussions.

## Licensing

This fork retains the original MIT license for software and CERN-OHL-P for hardware designs. All original copyright notices are preserved. See [LICENSE.md](LICENSE.md).

The "SABT" and "GW" brands and logos remain the property of George Wilkins and are used here only as part of the original software attribution.
