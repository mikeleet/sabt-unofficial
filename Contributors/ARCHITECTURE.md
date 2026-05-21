# Software Architecture

## High-Level Overview

The SABT plugin is a **.NET Framework 4.8 Class Library (DLL)** loaded by SimHub at runtime. It implements three SimHub interfaces:

| Interface | Role |
|-----------|------|
| `IPlugin` | Lifecycle (`Init`, `End`), metadata (name, icon, author) |
| `IDataPlugin` | Receives telemetry callbacks (`DataUpdate` at up to 60 Hz) |
| `IWPFSettingsV2` | Provides a WPF `UserControl` that SimHub embeds in its settings panel |

The physical data flow is:

```
SimHub telemetry → DataUpdate() → TelemetrySnapshot (cached)
                                       ↓
                              AutoResetEvent signal
                                       ↓
ControlLoop thread → effect computation → torque fractions → MotorController
                                       ↓
                    Motor.SetTorque() → serial frame → USB-RS485 → DDSM115 motor
```

---

## File-by-File Walkthrough

### 1. `DevicePlugin.cs` (~564 lines) — The Orchestrator

`Sources/Plugin/DevicePlugin.cs` is the main plugin class. It:

- **`Init()`**: Loads persisted settings, creates `MotorController`, optionally auto-connects, initializes the OxyPlot telemetry graph, spawns the `ControlLoop` background thread.
- **`DataUpdate()`**: Called by SimHub at up to 60 Hz. Reads `AccelerationSurge`, `AccelerationSway`, `AccelerationHeave`, `SpeedKmh`, and gear change data from `GameData`. Caches these in a `TelemetrySnapshot` struct, signals `_hasTelemetryArrived` (an `AutoResetEvent`), and updates the telemetry graph.
- **`ControlLoop()`**: Background thread. Waits for `_hasTelemetryArrived`, then computes all effects in a single pass:
  1. Converts raw telemetry into normalized fractions (braking, acceleration, landing, jumping, cornering)
  2. Applies per-effect strength multipliers
  3. Combines modifiers into left/right torque targets
  4. Applies idle tension (when stationary), side bias, and range clamping
  5. Calls `MotorController.SetTorques()` to send commands to hardware
  6. Handles **upshift effect** via `Thread.Sleep()` (blocking — crude proof-of-concept)
- **`End()`**: Saves settings, stops the control loop, disconnects motors.

**Key threading model**: `DataUpdate` runs on SimHub's thread (UI or telemetry). `ControlLoop` runs on its own dedicated thread. They communicate via `_latestTelemetry` (synchronized with `_telemetryLock`) and `_hasTelemetryArrived` (AutoResetEvent).

### 2. `MotorController.cs` (~1035 lines) — Hardware Communication

`Sources/Plugin/MotorController.cs` is the largest and most critical file. It has:

#### `MotorController` (outer class)
- Manages a single `SerialPort` at 115200 baud, 8N1
- Contains two `Motor` instances (Left = ID 0x01, Right = ID 0x02)
- **Serial port lifecycle**: `Connect()` → opens port, `Disconnect()` → sends stop commands + closes port
- **Device detection**: Uses WMI (`Win32_PnPEntity`) to scan for USB devices matching `VID_1A86&PID_55D3` (the Waveshare serial bridge). Extracts COM port names via regex.
- **Action tracking** (`StartAction`/`EndAction`): Prevents overlapping serial operations. Any code can check `IsBusy` before sending commands.
- **Torque alternation**: `SetTorques()` sends to only one motor per call (alternating left/right), achieving 30 Hz per motor at the overall 60 Hz loop rate.
- **Right motor torque inversion**: The right motor's torque is negated (`right * -1`) in `SetTorques()` at line 712, because the motors are physically mirrored.

#### `Motor` (inner class)
Each `Motor` instance:
- Has an `Identifier` byte (0x01 or 0x02) and a `Label` string ("Left" or "Right")
- Tracks `IsConnected`, `Status`, `Graphic` (image path) for UI binding
- Tracks consecutive `_commandFailures` (max 10 before giving up)
- Maintains `_smoothedTorque` for exponential smoothing
- Methods:
  - **`Check()`**: Full status check — query, verify torque mode, set torque mode if needed
  - **`Stop()`**: Sends zero-torque command (5 retries)
  - **`Query()`**: Sends status-request command (0x74), validates response (ID, mode, temperature < 60°C, error = 0)
  - **`Test()`**: Oscillates torque on/off to verify the motor physically moves
  - **`SetIdentifier()`**: Sends 5 ID-assignment frames (0x55 to address 0xAA). Motors accept a new ID only once per power cycle.
  - **`SetMode()`**: Sends mode-change (0xA0) to enable torque mode (0x01)
  - **`SetTorque()`**: Sends torque command (0x64), applies smoothing, increments failure counter on error

#### Serial Protocol
- **10-byte frames**: `[ID] [CMD] [B0...B6] [CRC8]`
- **CRC8**: XOR-based with polynomial 0x8C, computed over first 9 bytes
- **Response validation**: Checks CRC8, motor ID, mode byte, temperature, error byte

### 3. `DeviceSettings.cs` (~326 lines) — Settings Model

`Sources/Plugin/DeviceSettings.cs` is a flat `INotifyPropertyChanged` class. All settings are integers (0–1000 scale) that get converted to floating-point fractions (0.0–1.0) at runtime by `ConvertToFraction()`.

Settings include:
- **Connection**: `SerialPort`, `IsEnabled`, `StartAutomatically`, `IsFlipped`
- **Tension**: `IdleTension` (0–250), `MinimumTension`/`MaximumTension` (0–1000), `SideBias` (-1000–1000)
- **Effects**: Per-effect strengths — `CorneringStrength`, `BrakingStrength`, `AccelerationStrength`, `JumpingStrength`, `LandingStrength`, `ShiftingStrength`
- **Tuning**: `MinimumSurge`/`MaximumSurge`, `MinimumSway`/`MaximumSway`, `MinimumHeave`/`MaximumHeave`, `SmoothingFactor` (0–750)

Range validation enforces `min ≤ max` in property setters.

### 4. `DeviceControl.xaml` + `DeviceControl.xaml.cs` — WPF UI

The UI is a 5-tab WPF `UserControl`:
1. **Connection**: Motor graphics, enable/auto-start/flip toggles, serial port dropdown, test and setup buttons
2. **Tension**: Idle tension, driving tension range, left/right bias sliders
3. **Effects**: Six individual effect strength sliders
4. **Tuning**: OxyPlot live graph (surge/sway/heave lines + threshold annotations), range limit sliders, smoothing slider
5. **Credits**: Author links, license link, SimHub SDK link, tester credit

The code-behind:
- Starts a 5-second `DispatcherTimer` to poll for serial port availability (`UpdateSerialPorts()`)
- Button handlers: `TestLeftMotor()`, `TestRightMotor()`, `SetupMotors()` — all fire-and-forget via `DoWithoutWaiting()`

### 5. `DeviceViewModel.cs` (~27 lines) — MVVM Bridge

A simple pass-through ViewModel that exposes `Settings`, `MotorController`, and `TelemetryGraphModel` to XAML bindings. No logic.

---

## Threading Model

```
┌─────────────────────────────────────────────────────────┐
│  SimHub Main Thread (UI)                                │
│  ├── Init() called once at startup                     │
│  ├── DataUpdate() called at up to 60 Hz                  │
│  ├── End() called once at shutdown                      │
│  └── WPF UI binding updates                             │
├─────────────────────────────────────────────────────────┤
│  ControlLoop Thread (Background)                         │
│  └── Waits on AutoResetEvent, computes effects,         │
│      sends motor commands                                │
├─────────────────────────────────────────────────────────┤
│  Task Pool Threads (via DoWithoutWaiting)                │
│  └── Serial port open/close, motor check/test/setup     │
└─────────────────────────────────────────────────────────┘
```

Locks:
- `_motorControllerLock` (in DevicePlugin): Guards `MotorController` reference assignment
- `_telemetryLock` (in DevicePlugin): Guards `_latestTelemetry` reads/writes
- `_actionLock` (in MotorController): Guards the action tracking list (`_actionsIdentifiers`)
- `_serialLock` (in MotorController): Guards all serial port read/write operations

---

## Dependency Graph

```
SABT Plugin DLL
│
├── SimHub.Plugins.dll        (IPlugin, IDataPlugin, IWPFSettingsV2, UI controls)
├── SimHub.Logging.dll        (Logging.Current)
├── GameReaderCommon.dll      (GameData, telemetry types)
├── WoteverCommon.dll         (ToIcon extension, ReadCommonSettings, SaveCommonSettings)
├── WoteverLocalization.dll   (SLoc.GetValue, .resx-based i18n)
├── OxyPlot.dll + OxyPlot.Wpf.dll  (Telemetry graph)
├── MahApps.Metro.dll + IconPacks  (WPF theming)
├── log4net.dll               (Logging backend)
├── System.Management.dll     (WMI device detection)
└── System.IO.Ports.dll       (SerialPort)
```

All non-GAC references are resolved from `%SIMHUB_INSTALL_PATH%` via `<HintPath>` in the `.csproj`.

---

## Effect Computation Engine Detail

The `ControlLoop()` in `DevicePlugin.cs` (lines 190–377) computes torque targets as follows:

### Step 1: Convert telemetry to normalized fractions
```
braking      = clamp(surge, 0, maxSurge)       / (maxSurge - 0)
acceleration = 1 - clamp(surge, minSurge, 0)   / (0 - minSurge)
landing      = clamp(heave, 0, maxHeave)       / (maxHeave - 0)
jumping      = 1 - clamp(heave, minHeave, 0)   / (0 - minHeave)
sway         = (clamp(sway, minSway, maxSway)  / (maxSway - minSway)) * 2 - 1
```

### Step 2: Apply effect strengths
```
leftModifierIncrease  = max(braking * brakingStrength, landing * landingStrength,
                            (sway <= 0) ? |sway * corneringStrength| : 0)
rightModifierIncrease = max(braking * brakingStrength, landing * landingStrength,
                            (sway > 0) ? |sway * corneringStrength| : 0)
leftModifierDecrease  = max(acceleration * accelerationStrength,
                            jumping * jumpingStrength)
rightModifierDecrease = max(acceleration * accelerationStrength,
                            jumping * jumpingStrength)
```

### Step 3: Compute total modifier and target torque
```
totalModifier = increaseModifier - decreaseModifier

if totalModifier < 0:
    target = minTension + (totalModifier * minTension)
else:
    target = minTension + (totalModifier * (maxTension - minTension))
```

### Step 4: Post-processing
```
Clamp target to [0, maxTension]
If not moving: target = idleTension
Apply side bias: reduce opposite-side target
```
