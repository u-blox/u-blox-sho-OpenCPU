# VS Code Workspace Setup Guide

## Overview

Two workspace configurations are available to optimize your development experience:

1. **u-blox-build-workspace.code-workspace** - PRIMARY (Active, for building)
2. **u-blox-debug-workspace.code-workspace** - Optional (For debugging, when ready)

## Primary Workspace: Build & Development

**File:** `u-blox-build-workspace.code-workspace`

### Features

✅ **Dual Folder Structure**
- Root folder: Full repository context
- GettingStartedSDK folder: Build-specific focus
- Switch between views as needed

✅ **Python Integration**
- Auto-configured interpreter at `.venv/bin/python`
- Virtual environment automatically detected
- Linting and formatting enabled

✅ **Pre-configured Launch Configurations**
- IRIS-W10 doctor/clone/build
- NORA-W50/W51 build examples
- NORA-W40 ESP-IDF clone
- venv setup automation
- Debug and run directly from VS Code

✅ **Smart File Exclusions**
- Large SDKs hidden (mcuxpresso-sdk, esp-idf)
- Search excludes these automatically
- Faster UI, better search performance
- .venv visible for inspection if needed

✅ **Extension Recommendations**
- Python development tools (Pylance, debugger)
- CMake tools (for some module builds)
- GitLens for history tracking
- Remote development (WSL, SSH)
- Cortex-Debug for future debugger support

### How to Use

#### Step 1: Open the Workspace

**Option A: From command line**
```bash
cd e:/u-blox/u-blox-sho-OpenCPU
code u-blox-build-workspace.code-workspace
```

**Option B: From VS Code**
1. File → Open Workspace from File
2. Select `u-blox-build-workspace.code-workspace`
3. Click "Open"

#### Step 2: Verify Python Environment

1. View → Command Palette (Ctrl+Shift+P)
2. Type: "Python: Select Interpreter"
3. Should show: `./.venv/bin/python` or similar
4. If not, run setup_venv.py first

#### Step 3: Use Launch Configurations

1. View → Run and Debug (Ctrl+Shift+D)
2. Select configuration from dropdown
3. Click "Run" (▶) or "Debug" (with breakpoint)

**Available configurations:**
- IRIS-W10 doctor - Verify tools
- IRIS-W10 clone - Download SDK
- NORA-W50/W51 build - Build WiFi provisioning example
- NORA-W40 clone - Setup ESP-IDF
- Setup venv - Initialize virtual environment

#### Step 4: Use Copilot with Context

With `.copilot-instructions.md` in scope:

1. Open Command Palette (Ctrl+Shift+P)
2. Type: "Copilot"
3. Ask questions like:
   - "How do I build IRIS-W10 hello_world?"
   - "What should ARMGCC_DIR be?"
   - "Why is my build failing with [error]?"
   - "What NORA-W50 capabilities exist?"

Copilot will use:
- Workspace instructions (.copilot-instructions.md)
- u-blox MCP (for module specs/docs)
- Your workspace context

## Optional: Debug Workspace (Future)

**File:** `u-blox-debug-workspace.code-workspace` (not created yet)

When you want to focus on debugging firmware:

```bash
code u-blox-debug-workspace.code-workspace
```

This workspace would include:
- Debugger configurations (J-Link, MCU-Link, etc.)
- Hardware breakpoint setup
- Memory/register viewer
- Serial terminal configuration
- Cortex-Debug tools

**For now:** Use the build workspace - debugging support will be added later.

## File: .copilot-instructions.md

This file provides Copilot with context about:

### Architecture Understanding
- 4 module types and their SDKs
- Shared venv and configuration system
- Cross-platform build patterns
- Directory structure

### Common Workflows
- First-time setup
- Building each module
- Environment variables
- Output artifacts

### Issue Resolution
- Python/pip problems
- ARMGCC_DIR issues
- SDK clone timeouts
- WSL2 requirements for NORA-W30

### Integration with u-blox MCP
- When to use module documentation
- How to search for specifications
- Finding application notes

## Quick Start Checklist

- [ ] Clone repository
- [ ] `cd GettingStartedSDK && python setup_venv.py`
- [ ] Activate venv: `source .venv/bin/activate` (or platform equivalent)
- [ ] Open workspace: `code ../u-blox-build-workspace.code-workspace`
- [ ] Verify Python interpreter selected
- [ ] Use "Run and Debug" to launch configurations
- [ ] Ask Copilot questions (workspace instructions + MCP available)

## Settings Reference

### Python Interpreter
```json
"python.defaultInterpreterPath": "${workspaceFolder}/GettingStartedSDK/.venv/bin/python"
```
Auto-configured to use the shared venv.

### Excluded Folders
- `**/mcuxpresso-sdk` - NXP SDK (large, slow to search)
- `**/esp-idf` - Espressif SDK (large, slow to search)
- `**/.git` - Git objects
- `**/__pycache__` - Python cache
- `**/.venv` - Hidden by default but visible if needed

### Terminal Environment
PYTHONPATH automatically set to GettingStartedSDK for proper module imports.

## Launch Configurations

Each configuration:
1. Runs a specific build script with arguments
2. Executes in integrated terminal
3. Sets working directory to GettingStartedSDK
4. Uses Python interpreter from .venv

### Example: IRIS-W10 doctor
```json
{
  "name": "Python: IRIS-W10 doctor",
  "type": "python",
  "program": "${workspaceFolder}/GettingStartedSDK/scripts/iris_w10_build.py",
  "args": ["doctor"],
  "cwd": "${workspaceFolder}/GettingStartedSDK"
}
```

### How to Add New Launch Configuration

1. Run → Open Configurations (Ctrl+Shift+D)
2. Click "Create a launch.json file"
3. Or edit the workspace file JSON directly
4. Add new configuration object to `launch.configurations`

Example for IRIS-W10 build:
```json
{
  "name": "Python: IRIS-W10 build hello_world",
  "type": "python",
  "program": "${workspaceFolder:u-blox Getting Started SDK}/GettingStartedSDK/scripts/iris_w10_build.py",
  "args": ["build", "demo_apps/hello_world"],
  "console": "integratedTerminal",
  "cwd": "${workspaceFolder:u-blox Getting Started SDK}/GettingStartedSDK",
  "justMyCode": true,
  "env": {
    "ARMGCC_DIR": "/c/Program Files/Arm/GNU Toolchain mingw-w64-x86_64-arm-none-eabi"
  }
}
```

## Extension Recommendations

Auto-suggested when you open the workspace:

| Extension | Purpose |
|-----------|---------|
| ms-python.python | Python language support |
| ms-python.vscode-pylance | Advanced Python analysis |
| ms-vscode.makefile-tools | Makefile support (some modules use Make) |
| eamodio.gitlens | Git history and blame |
| ms-vscode.remote-explorer | SSH/WSL browsing |
| ms-vscode-remote.remote-wsl | WSL2 debugging (NORA-W30) |
| ms-vscode-remote.remote-ssh | Remote Linux development |
| marus25.cortex-debug | ARM debugger (future) |
| ms-vscode.cmake-tools | CMake support (IRIS-W10) |

Accept recommendations for best experience.

## Using u-blox MCP in This Workspace

### What MCP Provides

The u-blox MCP server provides:
- Product documentation (datasheets, specs)
- Hardware specifications (pinouts, memory)
- Application notes and examples
- Troubleshooting guides
- API documentation

### How to Access

**Via Copilot:**
1. Ask questions naturally: "What are IRIS-W10 capabilities?"
2. Copilot searches u-blox knowledge sources
3. Returns relevant specs and documentation

**Via MCP Tools:**
If MCP tools are exposed, directly query u-blox knowledge.

### Example Questions

- "What modules have Thread support?"
- "Does NORA-W50 support 802.11ax?"
- "What's the memory configuration for IRIS-W10?"
- "Which NORA variant has the most GPIO pins?"
- "Where can I find the IRIS-W10 datasheet?"

## Troubleshooting

### Python Interpreter Not Found
```
Error: "Python not found in .venv"
```
**Solution:**
1. Delete .venv: `rm -rf GettingStartedSDK/.venv`
2. Run setup: `python GettingStartedSDK/setup_venv.py`
3. Reload VS Code window: Ctrl+Shift+P → "Reload Window"

### Launch Configuration Fails
```
Error: "Could not execute python script"
```
**Check:**
1. Verify venv activated: `source .venv/bin/activate`
2. Verify Python can run: `python --version`
3. Check working directory is GettingStartedSDK
4. Try running command in terminal first (manual debugging)

### Copilot Not Using Workspace Instructions
```
Copilot seems unaware of build infrastructure
```
**Verify:**
1. Open `.copilot-instructions.md` file
2. Confirm it's in GettingStartedSDK/ folder
3. Restart VS Code: Ctrl+Shift+P → "Developer: Reload Window"
4. Try asking question again

### Large Folders Slowing Down Search
```
Search is slow in VS Code
```
**Solution:** Verify file exclusions are working
1. View → Command Palette → "Files: Open Excluded File"
2. Try: "mcuxpresso-sdk" or "esp-idf"
3. Should say "Excluded by settings"

## Advanced Configuration

### Adding Environment Variables to Launch
For IRIS-W10 ARMGCC_DIR:

Edit launch configuration:
```json
"env": {
  "ARMGCC_DIR": "/c/Program Files/Arm/GNU Toolchain mingw-w64-x86_64-arm-none-eabi"
}
```

### Custom Tasks

Add to workspace for build automation:
```json
"tasks": [
  {
    "label": "Build IRIS-W10 hello_world",
    "type": "shell",
    "command": "python",
    "args": ["${workspaceFolder}/GettingStartedSDK/scripts/iris_w10_build.py", "build", "demo_apps/hello_world"],
    "group": "build"
  }
]
```

Run via: View → Run Task

## Next Steps

1. ✅ Open workspace
2. ✅ Verify Python interpreter
3. ✅ Test launch configuration (IRIS-W10 doctor)
4. ✅ Ask Copilot a build question
5. ✅ Build an example using "Run and Debug"
6. ✅ When debugging is ready: Create debug-workspace.code-workspace

---

**Workspace File:** u-blox-build-workspace.code-workspace  
**Copilot Instructions:** GettingStartedSDK/.copilot-instructions.md  
**Created:** 2026-09-28  
**Status:** Ready for use
