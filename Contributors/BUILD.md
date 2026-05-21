# Build Guide: Compile & Deploy to SimHub

This project is a **.NET Framework 4.8** class library. You must build on **Windows** — the plugin references SimHub DLLs that only exist on Windows.

---

## One-Time Setup

Do this once on your Windows machine:

### 1. Install Build Tools

Download **Build Tools for Visual Studio 2022** from:
https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022

During installation, select the **".NET desktop build tools"** workload.

(Or install full Visual Studio 2022 Community if you prefer an IDE.)

### 2. Set SimHub Path

Open Command Prompt as Administrator and run:

```cmd
setx SIMHUB_INSTALL_PATH "C:\Program Files (x86)\SimHub"
```

If SimHub is installed somewhere else, adjust the path.

### 3. Clone the Repo

```cmd
git clone https://github.com/YOUR_USERNAME/Simple-Active-Belt-Tensioner.git
cd Simple-Active-Belt-Tensioner
```

---

## Building (Every Time)

### Quick Way — Double-Click `build.bat`

Navigate to `Sources\Plugin\` and double-click **`build.bat`**. It will:

1. Verify SimHub is found
2. Restore NuGet packages
3. Build the plugin in Release mode
4. Copy the DLL and language files into your SimHub install
5. Warn you if SimHub is running (the DLL can't be replaced while SimHub is open)

If anything fails, the script stops and tells you exactly what went wrong.

### Manual Way

```cmd
cd Sources\Plugin
nuget restore User.ActiveBeltTensioner.sln
msbuild User.ActiveBeltTensioner.sln /p:Configuration=Release /p:Platform="Any CPU"
```

---

## After Building

1. Launch (or restart) **SimHub**
2. Look for **"Simple Active Belt Tensioner"** in the left sidebar menu
3. Click it — the settings panel with 5 tabs should appear
4. Check the SimHub log window for: `SABT: Initialising...`
5. If a motor controller is plugged in via USB, the serial port dropdown will auto-populate

---

## Build Output

| File | Where It Goes |
|------|---------------|
| `User.ActiveBeltTensioner.dll` | `C:\Program Files (x86)\SimHub\` |
| `User.ActiveBeltTensioner.pdb` | `C:\Program Files (x86)\SimHub\` |
| `Languages\*.resx` | `C:\Program Files (x86)\SimHub\Languages\` |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "SIMHUB_INSTALL_PATH not set" | Run `setx SIMHUB_INSTALL_PATH "C:\Program Files (x86)\SimHub"` and restart the command prompt |
| "MSBuild not found" | Install Build Tools for Visual Studio 2022 |
| "SimHub.Plugins.dll not found" | SimHub is not installed or the path is wrong |
| "DLL cannot be replaced" | Close SimHub before building |
| Build succeeds but plugin doesn't appear | Check SimHub log for errors; make sure DLL is in the right folder |
