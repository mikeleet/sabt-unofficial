# Software — Unofficial Fork

This folder contains a pre-built plugin package for the **unofficial fork** of SABT, based on upstream [`acaa1ed`](https://github.com/GeorgeWilkins/Simple-Active-Belt-Tensioner/commit/acaa1ed8a63a3292b84fe2fddc7ce95b841bfaa1) (PR #26, "Extra Tall motor brackets").

## Download & Install

1. Close SimHub
2. Download [SABT Unofficial Plugin.zip](https://github.com/mikeleet/sabt-unofficial/releases/latest/download/SABT.Unofficial.Plugin.zip)
3. Unzip — contains `User.ActiveBeltTensioner.dll` and `Languages\` folder
4. Copy both into your SimHub installation directory (e.g. `C:\Program Files (x86)\SimHub`)
5. Launch SimHub — look for "Simple Active Belt Tensioner" in the left sidebar

## Release Notes

```
v0.1.0 — Unofficial Build
Based on upstream: acaa1ed (PR #26, Extra Tall motor brackets)

Changes:
- Auto-Calibrate v2: EMA peak tracking, works from frame 1
- Per-tab scroll fix: tab headers always visible
- Test Motor: 50% torque, zero-torque release, serial safety (RunTest)
- Auto-reconnect: 3 retries, 0s minimum delay
- Suppress Activation Warning toggle (default ON)
- Graph: 250px, Y-axis auto-scale, 600-point history, pause
- Back-drive cable adapter warnings (Connection + Tuning tabs, all 5 langs)
- Slider units: m/s² for limits, (s) for auto-reconnect
- Smoothing Factor: back-EMF guidance with auto-calibrate note
- 67/67 tests pass, zero build errors
```

For the full list, see [FORK.md](../FORK.md). For the official build, visit [George Wilkins' original project](https://github.com/GeorgeWilkins/Simple-Active-Belt-Tensioner).

## Build From Source

```bash
cd Sources\Plugin
build.bat
```

Requires Visual Studio 2022+ and .NET Framework 4.8.
