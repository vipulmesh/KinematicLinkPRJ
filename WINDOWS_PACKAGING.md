# Windows Packaging — Four-Bar Kinematic Chain Simulator v2.0

## Quick Start

```bat
pip install pyinstaller
pip install -r requirements.txt
build.bat
```

That single command produces the runnable application in `dist\FourBarSimulator\` and the distribution ZIP `FourBarSimulator_v2.0_Windows.zip`.

---

## Build Environment Requirements

| Component | Minimum Version | Notes |
|-----------|----------------|-------|
| Windows | 10 or 11 | Build machine only |
| Python | 3.11 or 3.12 | Must be on PATH |
| PyInstaller | 6.x | `pip install pyinstaller` |
| NumPy | ≥ 2.0.0 | Listed in requirements.txt |
| SciPy | ≥ 1.14.0 | Listed in requirements.txt |
| Matplotlib | ≥ 3.9.0 | Listed in requirements.txt |
| PySide6 | ≥ 6.8.0 | Listed in requirements.txt |
| Pandas | ≥ 2.2.0 | Listed in requirements.txt |

> **One-time setup:**
> ```bat
> pip install pyinstaller
> pip install -r requirements.txt
> ```

---

## Build Configuration

The build is controlled by two files:

| File | Purpose |
|------|---------|
| `FourBarSimulator.spec` | PyInstaller spec — packaging options, assets, hidden imports |
| `version_info.txt` | Windows PE metadata — company, copyright, version embedded in EXE |

Key settings in the spec file that reduce antivirus false positives:

| Setting | Value | Why |
|---------|-------|-----|
| Mode | `--onedir` | No self-extraction to `%TEMP%` — the #1 cause of false positives |
| UPX | `upx=False` | Uncompressed PE — no packer byte-patterns |
| Console | `console=False` | GUI application; no hidden console window |
| Debug | `debug=False` | No debug output |
| Strip | `strip=False` | Leaves symbols readable; less packer-like |

---

## Where the Application is Generated

After `build.bat` completes:

```
dist\
└── FourBarSimulator\           ← the complete runnable application
    ├── FourBarSimulator.exe    ← main executable
    ├── _internal\              ← Python runtime + all packages (PyInstaller ≥ 6)
    ├── assets\
    │   ├── app_icon.ico
    │   └── splash.png
    └── ... (PySide6, NumPy, SciPy DLLs etc.)
```

The build script also produces:

```
FourBarSimulator_v2.0_Windows.zip   ← ready to distribute
```

---

## Creating the ZIP

The build script creates the ZIP automatically. To recreate it manually:

```bat
powershell Compress-Archive -Path dist\FourBarSimulator -DestinationPath FourBarSimulator_v2.0_Windows.zip -Force
```

---

## Running on Another Windows PC (No Python Required)

1. Send `FourBarSimulator_v2.0_Windows.zip` to the recipient.
2. Recipient right-clicks the ZIP → **Extract All** → choose a folder.
3. Open the extracted `FourBarSimulator` folder.
4. Double-click `FourBarSimulator.exe`.

> **Important:** The recipient must keep all files in the `FourBarSimulator` folder together.  
> The EXE cannot be moved out of the folder and run in isolation — it depends on the DLLs and `_internal\` folder beside it.

No Python installation, no VS Code, no PyCharm, no additional setup is required on the recipient's machine.

---

## Antivirus / SmartScreen Troubleshooting

### Why might it be flagged?

PyInstaller-built executables can trigger antivirus heuristics because:

- The Python runtime is bundled into a non-standard PE structure.
- The application is unsigned (no code-signing certificate).
- Windows SmartScreen assigns low reputation to newly distributed executables that not many people have downloaded yet.

### What this build already does to minimize false positives

- Uses `--onedir` — nothing is extracted to `%TEMP%` at runtime.
- Disables UPX — no compressed PE patterns.
- Embeds full PE metadata (company, product, copyright).

### If Windows SmartScreen blocks the EXE

SmartScreen shows "Windows protected your PC" for unsigned applications with low download reputation.

The recipient can proceed safely:

1. Click **More info**.
2. Click **Run anyway**.

This is expected for any new unsigned application distributed outside the Microsoft Store.

### If Windows Defender flags the EXE as malware (false positive)

1. Right-click the flagged file → **Properties** → confirm it is the application you built.
2. In Windows Security → **Virus & threat protection** → **Protection history** → find the detection → note the exact detection name (e.g., `Trojan:Win32/...`).
3. Submit a false-positive report to Microsoft:

   ```
   https://www.microsoft.com/en-us/wdsi/filesubmission
   ```

   - Sign in with a Microsoft account.
   - Select **"Software developer"**.
   - Upload `FourBarSimulator.exe`.
   - Select **"I believe this file is incorrectly detected as malicious"**.
   - Add a brief description: *"Legitimate Python desktop four-bar linkage kinematic simulator. College project built with PyInstaller."*
   - Submit.

   Microsoft typically responds within 1–3 business days and pushes a signature update.

---

## Version History

| Version | Date | Notes |
|---------|------|-------|
| 2.0 | August 2026 | Non-Grashof strict validation, corrected velocity output, packaging improvements |
| 1.0 | — | Initial release |
