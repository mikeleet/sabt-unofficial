# Known Bugs & Improvement Opportunities

> **Legend**: ~~strikethrough~~ = fixed, ❌ = not a bug, ⚠️ = real but low-priority

---

## Quick Reference

| ID | Description | Origin | Status |
|----|-------------|--------|--------|
| BUG-01 | Thread.Sleep blocks upshift effect | Code review | ⚠️ Low — needs enhancement |
| BUG-02 | Race condition: ControlLoop vs Disconnect | Code review | ⚠️ Low — well-guarded by locks |
| BUG-03 | MessageBox blocks UI on motor failure | [#21](https://github.com/GeorgeWilkins/Simple-Active-Belt-Tensioner/issues/21) | ✅ Fixed (auto-reconnect) |
| BUG-04 | Wrong error key for right motor setup | Code review | ✅ Fixed |
| BUG-05 | Assembly name says "PluginSdkDemo" | Code review | ✅ Fixed |
| BUG-06 | Torque negation hardcoded | Code review | ❌ Not a bug |
| BUG-07 | Serial port null after failed Connect | Code review | ⚠️ Low — messy, not failing |
| BUG-08 | DataUpdate races with End() | Code review | ⚠️ Low — SimHub likely prevents |
| BUG-09 | Settings only saved on exit | Code review | ⚠️ Design tradeoff |
| BUG-10 | WaitOne has no timeout | Code review | ⚠️ Low — linked to BUG-01 |
| BUG-11 | DesignTimeResources condition | Code review | ❌ Not a bug |
| BUG-12 | Motor disconnect when switching games | [#21](https://github.com/GeorgeWilkins/Simple-Active-Belt-Tensioner/issues/21) | ✅ Fixed |
| BUG-13 | Activation warning blocks during auto-reconnect | Code review | ✅ Fixed |
| BUG-14 | Tab bar disappears when switching to Connection/Tuning | User report | ✅ Fixed |
| BUG-15 | Auto-calibrate "dead quiet" until data gathered | User report | ✅ Fixed |

---

## Fixed in This PR

### BUG-03: MessageBox blocks UI on motor failure ✅
- **Origin**: [#21](https://github.com/GeorgeWilkins/Simple-Active-Belt-Tensioner/issues/21) — users reported motors disconnecting unexpectedly, blocking popup made recovery frustrating
- **What**: When motors exceeded the 10-consecutive-failure limit, a blocking `MessageBox.Show()` appeared. You couldn't interact with SimHub until dismissing it.
- **Fix**: Replaced with `HandleMotorFailure()` — logs to SimHub console, disables motors, and optionally auto-reconnects after a configurable delay.
- **Files**: `DevicePlugin.cs`

### BUG-04: Wrong localization key for right motor setup failure ✅
- **What**: When the RIGHT motor failed `SetIdentifier()` during the setup wizard, the error message said "Failed to set identifier for the LEFT MOTOR."
- **Fix**: Changed from `SABT_Message_Setup_FailToSetLeftMotor` to `SABT_Message_Setup_FailedToSetRightMotor`. The correct key already existed in all `.resx` files.
- **Files**: `MotorController.cs`

### BUG-05: AssemblyInfo has wrong title ✅
- **What**: `AssemblyTitle` and `AssemblyProduct` said `"User.PluginSdkDemo"` (inherited from the SimHub plugin demo template).
- **Fix**: Changed to `"User.ActiveBeltTensioner"`.
- **Files**: `Properties/AssemblyInfo.cs`

### BUG-12: Motor disconnect when switching games (#21) ✅
- **Origin**: [#21](https://github.com/GeorgeWilkins/Simple-Active-Belt-Tensioner/issues/21) — reported by @Barley194: motors disabled themselves and took several retries to re-enable when switching between games
- **What**: When switching between games, the USB-RS485 bridge briefly disappears from WMI during USB re-enumeration. The old code immediately called `Disconnect()` and cleared the serial port if 0 devices were found during any poll.
- **Fix**: `UpdateSerialPorts()` now tracks `_consecutiveDeviceNotFoundCount`. It only disconnects after 3 consecutive polls (15 seconds) find no device.
- **Files**: `MotorController.cs`

---

## Real Bugs (Open)

### BUG-01: Thread.Sleep blocks ControlLoop during upshift
- `DevicePlugin.cs`, lines 328–336
- **Severity**: Medium — cornering/braking freeze for up to 1 second during upshift. Telemetry frames pile up behind the `WaitOne`.
- **Root cause**: `Thread.Sleep((int)(shiftingStrength * 1000))` called directly inside the ControlLoop thread.
- **Fix approach**: Replace with timestamp-based logic. Record `_upshiftEndTime` on upshift detection. On each loop iteration, if within the upshift window, force zero torque. No sleep needed.

### BUG-02: Potential race between ControlLoop and Disconnect
- `MotorController.cs`, `DevicePlugin.cs`
- **Severity**: Low — the `_serialLock` protects serial port operations. `IsBusy` guards the action tracker. `End()` joins the ControlLoop thread with a 500ms timeout. Hard to trigger in practice.
- **Note**: Fixing this without knowing SimHub's exact lifecycle guarantees could introduce new bugs. Leave unless users report shutdown crashes.

### BUG-07: Serial port null after failed Connect in Check
- `MotorController.cs`
- **Severity**: Low — `Check()` calls `Connect()` recursively, and if `Connect()` fails it nulls `_serialPort`. Both methods handle their own errors correctly via independent action tracking. The code is messy but not actually failing.
- **Fix approach**: Refactor `Check()` to not recursively call `Connect()`. Let callers handle reconnection logic.

### BUG-08: DataUpdate can race with End()
- `DevicePlugin.cs`
- **Severity**: Low — theoretically possible if SimHub calls `DataUpdate()` during or after `End()`. SimHub's plugin lifecycle likely guarantees `Init → DataUpdate* → End` ordering.
- **Fix approach**: Add a `_isEnding` flag checked at the top of `DataUpdate()` if crashes during shutdown are ever reported.

### BUG-09: Settings only saved on plugin unload
- `DevicePlugin.cs`, line 174
- **Severity**: Design tradeoff — settings are only persisted in `End()`. If SimHub crashes, in-session changes are lost. Saving on every change would cause unnecessary disk I/O.
- **Fix approach**: Add periodic auto-save (debounced, every 30 seconds if dirty). Enhancement territory.

### BUG-10: WaitOne has no timeout
- `DevicePlugin.cs`, line 209
- **Severity**: Low — `End()` calls `_hasTelemetryArrived.Set()` then `Join(500ms)`. The only operation that could outlast the 500ms join is the upshift `Thread.Sleep()` from BUG-01. Fix BUG-01 and this goes away.
- **Fix approach**: Add `WaitOne(500)` timeout as a safety net, or fix BUG-01 which is the root cause.

### BUG-13: Activation warning still blocks during auto-reconnect ✅
- **What**: When auto-reconnect succeeded and re-enabled the motors, the activation warning `MessageBox` still appeared, requiring manual dismissal before motors would start.
- **Fix**: Added `_suppressActivationWarning` flag. Set to `true` by `HandleMotorFailure()` before re-enabling. When set, the ControlLoop skips the activation warning and proceeds directly. Resets after use.
- **Files**: `DevicePlugin.cs`

### BUG-14: Tab bar disappears when switching to Connection or Tuning tab ✅
- **What**: The Connection and Tuning tabs had tall content (600px motor graphics, 600px telemetry graph) inside a shared outer ScrollViewer. Scrolling down on one tab, then switching to another, left the ScrollViewer scrolled down — hiding the SHTabControl tab headers at the top. The initial fix (SelectionChanged → ScrollToTop) failed because SimHub's SHTabControl doesn't expose SelectionChanged.
- **Fix**: Removed the outer ScrollViewer entirely and wrapped each tab's content in its own `<ScrollViewer>`. Tab headers now sit outside any scroll region and are always visible. Each tab independently maintains its own scroll position. Also reduced telemetry graph height from 600px to 250px to make the Tuning tab more compact.
- **Files**: `DeviceControl.xaml`, `DeviceControl.xaml.cs`

### BUG-15: Auto-calibrate dead quiet until data is gathered ✅
- **What**: The old `ApplyAdaptiveNormalization` normalized telemetry values to [-1,1] then set static limits to [-1000,1000], causing `ConvertToFractionOfRange` to divide every effect by 1000x — belt was effectively dead. Even without that bug, the single-peak-per-axis model couldn't handle directional asymmetry (e.g., braking stronger than acceleration on the same surge axis).
- **Fix**: Replaced with a **rolling window** approach (`ComputeWindowBounds`). Three circular buffers (surge, sway, heave, 600 samples each) track recent telemetry. Min/max of the filled window become the adaptive limits for `ConvertToFractionOfRange`. Raw telemetry flows directly into effect math — no separate normalization step. Window starts at 1s (60 samples), automatically grows up to 10s (600 samples) as data accumulates, then rotates oldest data out. Works from frame 1.
- **Removed**: "Window Size" slider (over-engineering — the difference between 1s and 10s windows is negligible for relative range detection). "Calibration Progress" bar (always fills to 100% within 1 second). `UpdateAdaptiveDecay`, `WindowSamplesFromSetting`, `UpdateWindowSize`, `AdaptiveCalibrationProgress` property.
- **Files**: `DevicePlugin.cs`, `DeviceSettings.cs`, `DeviceControl.xaml`, `test_math_utils.py`

---

## Not Bugs

### BUG-06: Torque negation is hardcoded ❌
- `GetRightMotor()` already swaps based on `Settings.IsFlipped`. When `IsFlipped=true`, `GetRightMotor()` returns the motor labeled "Left" (ID 0x01), and that motor gets negated. The negation correctly follows the flip. My initial analysis was wrong.

### BUG-11: DesignTimeResources condition is fragile ❌
- The condition is intentional — it ensures design-time resources only load in Visual Studio designer or Expression Blend. Harmless in all build scenarios.

---

## Completed Features

### Auto-Calibrate v2 (#27)
- **Origin**: [#27](https://github.com/GeorgeWilkins/Simple-Active-Belt-Tensioner/issues/27) — F1 cars felt great but slower cars felt weak; telemetry normalization needed
- Toggle on the Tuning tab. When ON, uses a rolling window of recent telemetry samples per axis (surge/sway/heave) to dynamically determine the range for normalization. Raw telemetry values are mapped to [0,1] within the observed min/max window. Static Surge/Sway/Heave limit sliders are disabled when active.
- **Fixed window**: starts at 1 second (60 samples), grows up to 10 seconds (600 samples) as telemetry accumulates. After 10 seconds, old data rotates out as a true rolling window. No user configuration needed — the window sizes itself automatically.

### Physics & Math References

The normalization math uses **min-max feature scaling** (aka min-max normalization):
- Formula: `x' = (x - min) / (max - min)`
- Reference: [Wikipedia: Feature Scaling § Rescaling (min-max normalization)](https://en.wikipedia.org/wiki/Feature_scaling#Rescaling_(min-max_normalization))
- The rolling-window variant is a standard technique in **sliding window time series analysis**: [Wikipedia: Moving Average](https://en.wikipedia.org/wiki/Moving_average)

The underlying force model follows **Newton's Second Law**: F = m·a, where `a` is the in-game accelerometer (surge/sway/heave in m/s²). The belt tension linearly counteracts the perceived acceleration force. No non-linear transforms are used — the mapping from telemetry to tension is a direct linear interpolation within the observed range.

### Motor Back-EMF & Back-Driving

The DDSM115 BLDC motors use FOC (Field Oriented Control) over RS-485. The plugin applies an **exponential moving average (EMA)** smoothing filter to torque commands: `smoothed = target*(1-α) + previous*α` where `α = smoothingFactor/1000`.

**Why smoothing matters**: When braking force is released suddenly (e.g., coming off the brake pedal), the belt — under tension from the user's body — snaps back against the motor. This external torque can briefly exceed the motor's holding current, causing:
- **Back-EMF**: The motor acts as a generator, producing a reverse voltage that the controller must absorb
- **Rotor slip**: The FOC controller's PID loop momentarily loses sync with the rotor position
- **Controller fault**: The DDSM115 may interpret the back-EMF as a fault condition and briefly cut power

The **Back-Driving Protection Case** (in Printables) mechanically limits how far the belt can pull the motor in reverse, reducing the peak back-EMF. Users without this hardware should use higher smoothing (450–750) to soften torque transitions and prevent the controller from faulting.

**References**:
- Back-EMF in BLDC motors: [Wikipedia: Counter-electromotive force](https://en.wikipedia.org/wiki/Counter-electromotive_force)
- FOC torque ripple during load transients: Krishnan, R. "Permanent Magnet Synchronous and Brushless DC Motor Drives" (CRC Press, 2010), Chapter 9
- EMA filter for motor control: standard digital signal processing technique; the smoothing uses the same formula as a first-order IIR low-pass filter

### Auto-Reconnect After Motor Failure
- Motor failure disables motors without a blocking popup. After a configurable delay (1-10 seconds), attempts background reconnection. Auto-re-enables if successful. 10-second cooldown prevents reconnect loops.
- Toggle and delay slider on the Connection tab. Default: ON, 3 seconds.

### Korean Translation
- Complete `ko-KR.resx` with all UI strings translated.

### UI Polish & Quality-of-Life
- **Suppress Activation Warning** toggle on Connection tab (defaults ON). Disables the "motors will be activated. Proceed?" popup every time you flick Enable. The internal `_suppressActivationWarning` flag still works for auto-reconnect suppression.
- **Slider units** added: Surge/Sway/Heave Limits now show `(m/s²)`. Auto-Reconnect Delay shows `(s)`.
- **Smoothing Factor description** rewritten with back-EMF/back-driving warning: explains that low smoothing + no protection case = motor jitter/reversal risk. References the Back-Driving Protection Case in Printables.
- **Test Motor always uses full torque** (1.0 = 100%). Previously hardcoded at 12% torque — invisible when idle tension was 0. Now pulses the motor image opacity to show torque level visually during the test.
- **Test Motor**: full 50% torque with ScaleY pulse animation synced to each test pull/release (8 cycles × 200ms). Uses `RunTest()` wrapper for serial port safety — prevents concurrent test calls on the shared bus.
- **Test Motor** shows live torque-level animation: motor image pulses in scale synced to each test pull/release (8 cycles × 200ms). Always uses 100% torque.

---

## Potential Enhancements

1. **Upshift effect redesign** — timestamp-based release instead of `Thread.Sleep` (see BUG-01)
2. **Downshift detection** — currently only upshifts trigger the shift effect
3. **Per-effect response curves** — non-linear mapping instead of linear interpolation
4. **Motor position feedback** — display motor position in UI using mode 0x03
5. **Log viewer tab** — show recent SABT log entries in the plugin UI
6. **Velocity limiting** — configurable max rate-of-change for torque commands
7. **Profile system** ([#19](https://github.com/GeorgeWilkins/Simple-Active-Belt-Tensioner/issues/19)) — save/load named setting profiles per car/game
8. **Settings auto-save** — periodic save to prevent loss if SimHub crashes (see BUG-09)
