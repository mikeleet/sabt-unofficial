# Pull Request: Auto-Calibrate, Auto-Reconnect, Korean Translation, and Bug Fixes

Hi George,

I've been using the belt tensioner for a while now and wanted to contribute some improvements. Here's everything that's changed — I've tried to keep the existing code style and patterns consistent.

---

## What's New

### 1. Auto-Calibrate (addresses issue #27)

The biggest change. Currently the tensioner uses absolute telemetry values mapped against hardcoded Surge/Sway/Heave limits. This means an F1 car feels great but a slow road car barely moves the belts.

**Auto-Calibrate** tracks running peak values per telemetry axis and normalizes live data against those peaks. The result: every car gets the full tensioner range, from F1 to a Fiat 500.

**New settings (Tuning tab):**

| Setting | What it does |
|---------|-------------|
| **Auto-Calibrate** (checkbox) | Turn auto-ranging on/off. Default: off (keeps existing behavior) |
| **Adaptation Speed** (slider, 0-1000) | How fast the system forgets old peaks. Low = stable during a session (~2 min memory). High = quick to recalibrate when switching cars (~2 sec memory). Default: 500 |

**How it works technically:**

- Three running peak trackers (`_adaptivePeakSurge`, `_adaptivePeakSway`, `_adaptivePeakHeave`) update each telemetry frame as: `peak = max(|raw|, peak * decayFactor)`
- Decay factor ranges from 0.99999 (slider=0) to 0.99 (slider=1000), computed per-frame
- Values are normalized as `raw / runningPeak`, clamped to [-1, 1]
- A floor of 0.5 prevents division blowup at startup
- When Auto-Calibrate is ON, the static Surge/Sway/Heave limit sliders are disabled (grayed out) since they're irrelevant

**Files changed:** `DevicePlugin.cs` (ControlLoop and new helper methods), `DeviceSettings.cs` (2 new properties + `IsStaticRangeEnabled` computed property), `DeviceControl.xaml` (UI bindings)

---

### 2. Auto-Reconnect After Motor Failure

When the motors back-drive (e.g., pulling fast on the belts with no back-driving protection), the power supply can trip. Currently a blocking Message Box appears — you can't interact with SimHub until you dismiss it.

**Auto-Reconnect** handles this gracefully:

1. Motor failure detected → motors disabled (no popup, logged to SimHub console)
2. Waits a configurable delay (default 3 seconds)
3. Attempts to reconnect in the background
4. If successful → re-enables motors automatically
5. If it fails → leaves motors off (you can re-enable manually)

There's a 10-second cooldown between reconnect attempts to prevent loops.

**New settings (Connection tab):**

| Setting | What it does |
|---------|-------------|
| **Auto-Reconnect After Failure** (checkbox) | Default: ON |
| **Auto-Reconnect Delay** (slider, 1-10 seconds) | How long to wait before reconnecting. Default: 3 seconds |

**Files changed:** `DevicePlugin.cs` (new `HandleMotorFailure()` method, replaces the old MessageBox path), `MotorController.cs` (new `TryReconnect()` method), `DeviceSettings.cs` (2 new properties), `DeviceControl.xaml`

---

### 3. Korean Translation

Added `Languages/User.ActiveBeltTensioner.ko-KR.resx` with complete Korean translations for all UI strings. Also added it to the `.csproj` so it gets copied to SimHub on build.

---

## Bug Fixes

### Game-switching disconnect (issue #21)

When switching between games in SimHub, the USB-RS485 bridge can briefly disappear from WMI during USB re-enumeration. The old code would immediately disconnect and clear the serial port if 0 devices were found during a poll. Now it tracks consecutive "no device found" polls and only disconnects after 3 consecutive failures (15 seconds), giving the hardware time to settle.

**File changed:** `MotorController.cs` — `UpdateSerialPorts()` method

### Right motor setup error message

During motor setup, if the right motor failed to get its ID assigned, the error message said "Failed to set identifier for the LEFT MOTOR." Now it correctly says "RIGHT MOTOR." The key `SABT_Message_Setup_FailedToSetRightMotor` already existed in all `.resx` files — the code was just pointing to the wrong one.

**File changed:** `MotorController.cs` — `Setup()` method, line ~539

### Assembly name

`AssemblyInfo.cs` still said "User.PluginSdkDemo" (inherited from the SimHub plugin demo template). Changed to "User.ActiveBeltTensioner."

**File changed:** `Properties/AssemblyInfo.cs`

---

## Localization

All 5 language files (EN, DE, FR, IT, KO) have been updated with the new keys. I roughly translated the technical terms for FR/IT/KO — a native speaker should review them if possible. The English and German translations should be solid.

---

## How to Test

I've added Python tests in `Contributors/tests/` that verify all the math and algorithm logic. You can run them on your Windows machine (or any machine with Python 3) with:

```bash
python Contributors/tests/test_math_utils.py
python Contributors/tests/test_settings.py
```

There's also a manual testing guide at `Contributors/TESTING.md` covering things that need actual hardware:
- Auto-Calibrate with F1 vs road cars
- Auto-reconnect after unplugging USB
- Game-switching reliability
- Korean UI check
- Motor setup wizard error messages

---

## Build Notes

No new dependencies added. Everything compiles against the existing SimHub references in the `.csproj`. The build process is unchanged — still `msbuild User.ActiveBeltTensioner.sln /p:Configuration=Release`.

The `Contributors/` directory is documentation only and doesn't affect the build.

---

## Files Summary

```
Modified:
  Sources/Plugin/DeviceControl.xaml         (added new UI controls)
  Sources/Plugin/DevicePlugin.cs            (auto-calibrate + auto-reconnect)
  Sources/Plugin/DeviceSettings.cs          (4 new settings, 1 computed property)
  Sources/Plugin/MotorController.cs         (TryReconnect + game-switch fix)
  Sources/Plugin/Properties/AssemblyInfo.cs  (fixed assembly name)
  Sources/Plugin/User.ActiveBeltTensioner.csproj  (added Korean .resx)
  Sources/Plugin/Languages/User.ActiveBeltTensioner.resx        (new keys)
  Sources/Plugin/Languages/User.ActiveBeltTensioner.de-DE.resx  (new keys)
  Sources/Plugin/Languages/User.ActiveBeltTensioner.fr-FR.resx  (new keys)
  Sources/Plugin/Languages/User.ActiveBeltTensioner.it.resx     (new keys)

New:
  Sources/Plugin/Languages/User.ActiveBeltTensioner.ko-KR.resx  (Korean translation)
  Contributors/README.md
  Contributors/ARCHITECTURE.md
  Contributors/BUILD.md
  Contributors/BUGS.md
  Contributors/TESTING.md
  Contributors/tests/test_math_utils.py    (59 unit tests)
  Contributors/tests/test_settings.py      (10 unit tests)
  Contributors/tests/README.md
```

---

Let me know if anything needs adjusting. Happy to iterate on this.

— Mike
