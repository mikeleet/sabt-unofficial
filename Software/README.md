# Software — Unofficial Fork

This folder contains a pre-built plugin package for the **unofficial fork** of SABT.

## Download & Install

1. Close SimHub
2. Download [SABT Unofficial Plugin.zip](https://github.com/mikeleet/sabt-unofficial/releases/latest/download/SABT.Unofficial.Plugin.zip)
3. Unzip — contains `User.ActiveBeltTensioner.dll` and `Languages\` folder
4. Copy both into your SimHub installation directory (e.g. `C:\Program Files (x86)\SimHub`)
5. Launch SimHub — look for "Simple Active Belt Tensioner" in the left sidebar

## What's Different

This build includes bug fixes and improvements not in the upstream release. See [FORK.md](../FORK.md) for the full list.

For the official build, visit [George Wilkins' original project](https://github.com/GeorgeWilkins/Simple-Active-Belt-Tensioner).

## Build From Source

If you prefer to build yourself:

```bash
cd Sources\Plugin
build.bat
```

Requires Visual Studio 2022+ and .NET Framework 4.8.
