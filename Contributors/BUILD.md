# Build Guide: Compile & Deploy to SimHub

This project is a **.NET Framework 4.8** class library. You must build on **Windows** — the plugin references SimHub DLLs that only exist on Windows.

---

## One-Time Setup

Do this once on your Windows machine:

### 1. Install Build Tools

This project requires **MSBuild** (the .NET SDK alone is not sufficient for .NET Framework 4.8).

Download **Build Tools for Visual Studio** from either:

- **[Build Tools direct installer](https://aka.ms/vs/17/release/vs_buildtools.exe)** (recommended, small download)
- Or go to the [Visual Studio downloads page](https://visualstudio.microsoft.com/downloads/), scroll to **"All Downloads"**, expand **"Tools for Visual Studio"**, and download **"Build Tools for Visual Studio"**

Run the installer, select the **".NET desktop build tools"** workload (under "Desktop & Mobile"), and click Install.

> **Note:** The .NET SDK (`dotnet`) can restore NuGet packages but cannot build .NET Framework projects. MSBuild is required for compilation.

(Or install full Visual Studio Community if you prefer an IDE — select the same workload during setup.)

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
2. Restore NuGet packages (auto-downloads `nuget.exe` if needed)
3. Build the plugin in Release mode
4. Back up the current DLL before overwriting
5. Copy the DLL and language files into your SimHub install
6. Warn you if SimHub is running (the DLL can't be replaced while SimHub is open)

If a previous backup exists, the script will offer to restore it instead of deploying the new build — useful for quickly rolling back a broken build.

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
| Window disappears instantly when double-clicking `build.bat` | Open Command Prompt manually, `cd` to `Sources\Plugin`, then run `build.bat` to see the error message. Most likely MSBuild is not installed — see step 1 above. |
| "SIMHUB_INSTALL_PATH not set" | Run `setx SIMHUB_INSTALL_PATH "C:\Program Files (x86)\SimHub"` and restart the command prompt |
| "MSBuild not found" | Install Build Tools for Visual Studio — the .NET SDK alone is not enough for .NET Framework projects |
| "\SimHub\ was unexpected at this time" | Your SimHub path contains parentheses (e.g. `Program Files (x86)`). Update to the latest `build.bat` from the repo — this bug is fixed. |
| "SimHub.Plugins.dll not found" | SimHub is not installed or the path is wrong |
| "DLL cannot be replaced" | Close SimHub before building |
| Build succeeds but plugin doesn't appear | Check SimHub log for errors; make sure DLL is in the right folder |
