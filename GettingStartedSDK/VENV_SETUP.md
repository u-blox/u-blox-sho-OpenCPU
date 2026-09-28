# Virtual Environment (venv) Consolidation

**Status:** [OK] .venv now lives in GettingStartedSDK/ directory

## Why This Change?

- **Better organization:** The venv is specific to the GettingStartedSDK build infrastructure, so it should live within that folder
- **Cleaner repo root:** Reduces clutter at the repository root level
- **Logical structure:** Everything build-related is contained within GettingStartedSDK/

## New Structure

```
u-blox-sho-OpenCPU/
├── GettingStartedSDK/
│   ├── .venv/                    ← Virtual environment HERE
│   ├── scripts/
│   │   ├── iris_w10_build.py
│   │   ├── nora_w50_w51_build.py
│   │   ├── nora_w30_build.py
│   │   └── nora_w40_build.py
│   ├── docs/
│   ├── setup_venv.py             ← Run this from GettingStartedSDK/
│   ├── BUILD_ALL_EXAMPLES.md
│   └── [other docs]
│
├── NORA-W*-OutputPower/          ← Other unrelated folders
├── [other repo files]
└── migrate_venv.sh / migrate_venv.bat  ← Helper scripts
```

## How to Setup

### Option 1: Automatic (Recommended)

If you have an old .venv at the repo root, just run setup_venv.py and it will automatically move it:

```bash
cd GettingStartedSDK
python setup_venv.py
```

The script will:
1. [OK] Detect if you have an old .venv at the repo root
2. [OK] Automatically move it to GettingStartedSDK/.venv
3. [OK] Create a new one if needed
4. [OK] Install 'west' in the venv

### Option 2: Manual Migration

If automatic migration fails, use the helper scripts:

**Linux/macOS/WSL:**
```bash
./migrate_venv.sh
```

**Windows:**
```cmd
migrate_venv.bat
```

### Option 3: Manual Move

```bash
# From repo root
mv .venv GettingStartedSDK/.venv
```

## Activation Instructions

Once setup is complete, activate the venv from the GettingStartedSDK directory:

**Windows CMD:**
```cmd
cd GettingStartedSDK
.venv\Scripts\activate.bat
```

**Windows PowerShell:**
```powershell
cd GettingStartedSDK
.venv\Scripts\Activate.ps1
```

**Git Bash / MSYS2:**
```bash
cd GettingStartedSDK
source .venv/Scripts/activate
```

**Linux/macOS/WSL:**
```bash
cd GettingStartedSDK
source .venv/bin/activate
```

## Running Build Scripts

With venv activated, run scripts from GettingStartedSDK:

```bash
cd GettingStartedSDK
python scripts/iris_w10_build.py doctor
python scripts/nora_w50_w51_build.py build empty
```

Or run with full path:

```bash
cd e:/u-blox/u-blox-sho-OpenCPU
source GettingStartedSDK/.venv/bin/activate
python GettingStartedSDK/scripts/iris_w10_build.py doctor
```

## What Changed

### setup_venv.py
- [OK] Now explicitly creates .venv in GettingStartedSDK/
- [OK] Automatically detects and moves old .venv from repo root
- [OK] Updated documentation

### Build Scripts
- [OK] No changes needed - they work with venv in any location
- [OK] Scripts use relative paths for configuration, not venv paths

### Helper Scripts
- [OK] migrate_venv.sh - For Linux/macOS/WSL
- [OK] migrate_venv.bat - For Windows CMD

## Troubleshooting

### Old .venv still at repo root?
```bash
# Option 1: Run setup_venv.py again
cd GettingStartedSDK
python setup_venv.py

# Option 2: Use migration script
./migrate_venv.sh  # or migrate_venv.bat on Windows

# Option 3: Manual deletion
rm -rf .venv  # from repo root
```

### "pip not found in venv"?
This means the venv might be corrupted. Delete it and recreate:
```bash
cd GettingStartedSDK
rm -rf .venv
python setup_venv.py
```

### Scripts still looking for old location?
Make sure you're running scripts from within the activated venv:
```bash
cd GettingStartedSDK
source .venv/bin/activate  # or appropriate activation command
python scripts/iris_w10_build.py doctor
```

## Verification

To verify the setup is correct:

```bash
cd GettingStartedSDK
ls -la .venv  # Should show venv directory
source .venv/bin/activate  # or appropriate command
which python  # Should show path inside .venv
python scripts/iris_w10_build.py doctor  # Should work
```

---

**Note:** All build scripts automatically detect and use the venv when it's activated. No code changes needed - the move is purely organizational!
