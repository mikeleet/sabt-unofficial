# SABT Unofficial

> ⚠️ **Unofficial fork** of the [Simple Active Belt Tensioner](https://github.com/GeorgeWilkins/Simple-Active-Belt-Tensioner) by George Wilkins. Based on upstream [`acaa1ed`](https://github.com/GeorgeWilkins/Simple-Active-Belt-Tensioner/commit/acaa1ed8a63a3292b84fe2fddc7ce95b841bfaa1) (PR #26). This build is **actively used on a real rig** and includes bug fixes, quality-of-life improvements, and experimental features not yet merged upstream. Hardware designs are unchanged. [See what's different](FORK.md).

---

## What Is SABT?

A haptic device for sim racing that dynamically tensions your racing harness in response to game telemetry — giving you the sensation of braking, cornering, acceleration, and jumping/landing forces.

- **No soldering or programming** required
- **~215 GBP** including the harness
- Works with any game supported by [SimHub](https://www.simhubdash.com/)
- 2× BLDC/FOC servo motors, direct-drive, silent operation

## What This Fork Adds

| Feature | Detail |
|---------|--------|
| **Auto-Calibrate v2** | EMA peak tracking — works from frame 1, no dead zone |
| **Per-tab scroll fix** | Tab headers always visible when switching tabs |
| **Test Motor fix** | 50% torque, releases after test, no serial race |
| **Auto-reconnect retry** | 3 attempts, 0s minimum delay, help popup on failure |
| **Suppress Activation Warning** | Toggle on Connection tab (defaults ON) |
| **Graph improvements** | 250px height, Y-axis auto-scale, 600-point history, pause |
| **Back-drive guidance** | Cable adapter warnings + smoothing factor notes |
| **Slider units** | m/s² on limits, (s) on auto-reconnect |

## Install

Same as the original — build with `build.bat` from `Sources/Plugin/`, deploy to SimHub.

```bash
cd Sources\Plugin
build.bat
```

Requires: Visual Studio 2022+ (Community is free), .NET Framework 4.8, SimHub installed.

## Hardware

This fork does **not** modify any hardware. All printable parts, motor brackets, and the controller case are identical to the [original](https://github.com/GeorgeWilkins/Simple-Active-Belt-Tensioner). See the upstream [build instructions](https://github.com/GeorgeWilkins/Simple-Active-Belt-Tensioner/blob/main/INSTRUCTIONS.md) for the full hardware guide.

## Contributing

Bug fixes from this fork are submitted back upstream as focused, single-purpose PRs referencing [upstream issues](https://github.com/GeorgeWilkins/Simple-Active-Belt-Tensioner/issues). If you find a bug, open an issue here or on the upstream repo.

## License

Software: **MIT** — [LICENSE.md](LICENSE.md)  
Hardware designs: **CERN-OHL-P** — unchanged from upstream  
Original copyright © 2026 George Wilkins. The "SABT" and "GW" brands and logos remain the property of George Wilkins.
