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

---

## Not Bugs

### BUG-06: Torque negation is hardcoded ❌
- `GetRightMotor()` already swaps based on `Settings.IsFlipped`. When `IsFlipped=true`, `GetRightMotor()` returns the motor labeled "Left" (ID 0x01), and that motor gets negated. The negation correctly follows the flip. My initial analysis was wrong.

### BUG-11: DesignTimeResources condition is fragile ❌
- The condition is intentional — it ensures design-time resources only load in Visual Studio designer or Expression Blend. Harmless in all build scenarios.

---

## Completed Features

### Auto-Calibrate (#27)
- **Origin**: [#27](https://github.com/GeorgeWilkins/Simple-Active-Belt-Tensioner/issues/27) — F1 cars felt great but slower cars felt weak; telemetry normalization needed
- Toggle on the Tuning tab. When ON, tracks running peak values per telemetry axis (surge/sway/heave) with exponential decay, normalizing live data so every car gets the full tensioner range. Static Surge/Sway/Heave limit sliders are disabled when active.
- Settings: checkbox + **Adaptation Speed** slider (0 = slow/memory, 1000 = fast/adaptive). Default: OFF, speed 500.

### Auto-Reconnect After Motor Failure
- Motor failure disables motors without a blocking popup. After a configurable delay (1-10 seconds), attempts background reconnection. Auto-re-enables if successful. 10-second cooldown prevents reconnect loops.
- Toggle and delay slider on the Connection tab. Default: ON, 3 seconds.

### Korean Translation
- Complete `ko-KR.resx` with all UI strings translated.

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
