# Manual Testing Procedures

These tests require a Windows machine with SimHub installed and the SABT hardware connected.

## Pre-Flight Check

- [ ] Motors connected to controller, controller plugged into PC via USB
- [ ] Power supply connected and switched on
- [ ] SimHub running with a valid license (for 60 Hz telemetry)
- [ ] At least one racing game with telemetry output installed (e.g. Assetto Corsa, iRacing)

---

## Test 1: Adaptive Normalization — Basic Function

**Goal**: Verify adaptive normalization produces consistent feel across vehicle classes.

**Steps**:
1. Open SimHub → SABT plugin → Tuning tab
2. Enable **Adaptive Normalization** (checkbox)
3. Set **Adaptive Decay Rate** to 500 (default)
4. Set all effect strengths to 1000 on the Effects tab
5. Set Minimum Driving Tension to at least 200
6. Enable motors

**In an F1 car** (e.g. Assetto Corsa, Ferrari F2004):
- [ ] Drive for 5+ seconds — belt tension should feel strong during braking and cornering
- [ ] Check the telemetry graph — surge/sway/heave should show full-range activity
- [ ] The "Surge Limits" / "Sway Limits" / "Heave Limits" sliders should be grayed out or ignored

**In a slow road car** (e.g. Assetto Corsa, Abarth 500):
- [ ] Drive for 5+ seconds — belt tension should feel **just as strong** as in the F1 car
- [ ] Within 1-2 seconds of hard braking, the adaptive peak should rise and tension should feel full
- [ ] The system auto-calibrated — no manual slider adjustment needed

**Switch back** to F1 car:
- [ ] Within 10-20 seconds, the adaptive peak should adjust upward and tension should feel full again
- [ ] No "dead zone" or overly weak sensation

**Disable adaptive normalization**:
- [ ] Uncheck "Adaptive Normalization"
- [ ] Drive the slow car — tension should feel noticeably weaker than F1 (this is the old behavior)
- [ ] Re-enable adaptive normalization — tension should return to full strength

---

## Test 2: Adaptive Normalization — Decay Rate

**Goal**: Verify the decay rate slider changes how fast the system forgets peak values.

**Steps**:
1. Set **Adaptive Decay Rate** to 1000 (fastest)
2. Drive F1 car, brake hard, then stop and sit idle
3. [ ] Within ~1-2 seconds of idle, the adaptive peak should drop noticeably
4. Set **Adaptive Decay Rate** to 0 (slowest)
5. Drive F1 car, brake hard, then stop and sit idle
6. [ ] The adaptive peak should persist for minutes (effectively the whole session)
7. Set to 500 (default) — reasonable middle ground

---

## Test 3: Auto-Reconnect After Motor Failure

**Goal**: Verify that when motors fail, the plugin auto-reconnects without blocking UI.

**Steps**:
1. Enable **Auto-Reconnect After Failure** (checkbox, in Connection tab)
2. Set **Auto-Reconnect Delay** to 3 seconds
3. Enable motors — verify they are working
4. **Simulate a failure**: Unplug the controller USB cable briefly (or toggle power supply off and on)
5. [ ] Motors should disable (Enable Motors toggle turns off)
6. [ ] **No popup should block the UI** — this is the key fix
7. [ ] Check SimHub log: should see "SABT: Exceeded motor communication failure limit"
8. [ ] Check SimHub log: should see "SABT: Scheduling auto-reconnect in 3 seconds"
9. [ ] After 3 seconds, check log: "SABT: Attempting auto-reconnect now..."
10. [ ] If USB/power is restored: "SABT: Auto-reconnect succeeded — re-enabling motors"
11. [ ] Motors should be re-enabled automatically
12. [ ] Belt tension should resume

**Test with auto-reconnect disabled**:
1. Disable "Auto-Reconnect After Failure"
2. Cause a motor failure (unplug USB)
3. [ ] Motors should disable — but this time they stay off
4. [ ] Log should show "SABT: Auto-reconnect is disabled — motors will remain off"
5. [ ] User must manually re-enable

---

## Test 4: Game-Switching Reliability (#21)

**Goal**: Verify motors don't disconnect when switching between games.

**Steps**:
1. Enable motors in SimHub
2. Launch Game A (e.g. Assetto Corsa), drive for a few seconds
3. Exit Game A completely (back to Windows desktop or SimHub)
4. [ ] Motors should NOT disable on their own
5. [ ] The Enable Motors toggle should stay ON
6. [ ] Motor status should show "Connected" (idle tension applied)
7. Launch Game B (e.g. iRacing or ACC)
8. [ ] Motors should continue working without needing manual re-enable
9. [ ] Both motor status indicators should remain green/connected

**Repeat 3 times** — this tests the consecutive poll tracking fix:
- [ ] No disconnection across multiple game switches within a 15-second window

---

## Test 5: Korean Localization

**Goal**: Verify Korean language support works.

**Steps**:
1. Set SimHub language to Korean (if available in SimHub settings)
2. Open SABT plugin
3. [ ] Tab labels show Korean text (연결, 장력, 효과, 튜닝, 크레딧)
4. [ ] All buttons, sliders, descriptions show Korean text
5. [ ] Setup wizard messages show Korean text
6. [ ] Motor status indicators show Korean text

---

## Test 6: Motor Setup Wizard Fix

**Goal**: Verify the right-motor setup error message is correct.

**Steps**:
1. Disconnect one motor from the controller
2. Click "Setup Motors"
3. Follow the wizard — it will fail at some point
4. [ ] If the LEFT motor setup fails, the message should say "LEFT MOTOR" (not "RIGHT")
5. [ ] If the RIGHT motor setup fails, the message should say "RIGHT MOTOR" (not "LEFT")

---

## Test 7: UI Responsiveness

**Goal**: Verify no blocking popups during normal operation.

**Steps**:
1. Enable motors with auto-reconnect ON
2. Drive for several minutes
3. Cause a motor failure (unplug USB)
4. [ ] The SimHub UI remains responsive — can still click other tabs/plugins
5. [ ] No modal dialog blocks the interface
6. [ ] After auto-reconnect, the UI updates motor status indicators correctly

---

## Test 8: Assembly Metadata

**Goal**: Verify the plugin shows correct name in logs.

**Steps**:
1. Start SimHub
2. Check the log window for SABT initialization messages
3. [ ] Should see "SABT: Initialising..." (not "PluginSdkDemo")
4. Check Windows Event Viewer or SimHub plugin list
5. [ ] Plugin should be listed as "User.ActiveBeltTensioner" (not "User.PluginSdkDemo")
