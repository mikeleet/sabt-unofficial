# Contributor Resources

This directory exists for **contributors** to the Simple Active Belt Tensioner (SABT) project. It contains technical documentation about the software side of the project — architecture, build instructions, debugging guides, and a catalog of known bugs and improvement opportunities.

If you're a user looking to install and use the plugin, see the main [`/Software/README.md`](../Software/README.md) and [`/INSTRUCTIONS.md`](../INSTRUCTIONS.md) instead.

---

## What's Here

| File | Purpose |
|------|---------|
| `ARCHITECTURE.md` | Full walkthrough of how the C# plugin is constructed, class-by-class and thread-by-thread |
| `BUILD.md` | Step-by-step: how to compile on macOS (Apple Silicon) and Windows, plus deployment to SimHub |
| `BUGS.md` | Catalog of known bugs, their severity, root causes, and fix approaches |

---

## Quick Start for Contributors

1. Read `ARCHITECTURE.md` to understand the codebase
2. Read `BUILD.md` to set up your compilation environment
3. Pick a bug from `BUGS.md` or bring your own
4. The plugin lives entirely in `Sources/Plugin/` — 7 C# files, ~2,100 lines total

---

## Project Overview (One Paragraph)

SABT is a **SimHub plugin** (C# .NET Framework 4.8, WPF UI) that controls two Waveshare DDSM115 BLDC servo motors via a USB-to-RS485 serial bridge. It reads telemetry from racing simulators through SimHub (surge, sway, heave), converts that into torque targets using configurable effect curves (braking, acceleration, cornering, jumping, landing, shifting), and sends torque commands to the motors at 60 Hz. The plugin also includes a full WPF settings UI with live telemetry graphing (OxyPlot), motor test/setup wizards, and multi-language localization (EN, DE, FR, IT).
