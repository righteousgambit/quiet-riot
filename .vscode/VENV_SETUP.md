# Virtual Environment Auto-Setup

VS Code is now configured to automatically set up and use the `.venv` virtual environment.

## How It Works

### Automatic Setup

- **Setup Script**: `.vscode/setup-venv.sh` automatically creates `.venv` if it doesn't exist
- **Pre-Launch Task**: All debug configurations run the setup task before launching
- **Task Dependencies**: All VS Code tasks depend on the setup task

### Automatic Detection

- **Python Interpreter**: VS Code automatically detects `.venv/bin/python`
- **Settings**: Configured to use `.venv` as the default Python environment
- **Terminal**: Automatically activates `.venv` when opening integrated terminal

## What Gets Set Up

When `.venv` doesn't exist, the setup script:

1. Creates virtual environment using `python3 -m venv .venv`
2. Upgrades pip, setuptools, and wheel
3. Installs project dependencies: `pip install -e ".[dev]"`
4. Installs pre-commit hooks (if available)

## Usage

### Debug Configurations

All debug configurations now:

- Use `${workspaceFolder}/.venv/bin/python` explicitly
- Run "Setup Virtual Environment" task before launching
- Automatically create venv if missing

### Tasks

All tasks now:

- Use `.venv/bin/python` or `.venv/bin/<command>` explicitly
- Depend on "Setup Virtual Environment" task
- Automatically create venv if missing

### Manual Setup

If you want to set up manually:

```bash
# Run the setup task
Cmd+Shift+P → "Tasks: Run Task" → "Setup Virtual Environment"

# Or run the script directly
.vscode/setup-venv.sh
```

## Verification

To verify VS Code is using `.venv`:

1. Open Command Palette (`Cmd+Shift+P`)
2. Run "Python: Select Interpreter"
3. You should see `.venv/bin/python` selected

## Troubleshooting

### VS Code Not Detecting .venv

1. Reload VS Code window: `Cmd+Shift+P` → "Developer: Reload Window"
2. Manually select interpreter: `Cmd+Shift+P` → "Python: Select Interpreter"
3. Choose `.venv/bin/python`

### Setup Script Fails

1. Check Python is available: `python3 --version`
2. Check permissions: `chmod +x .vscode/setup-venv.sh`
3. Run manually: `.vscode/setup-venv.sh`

### Tasks Not Using .venv

- All tasks now explicitly use `.venv/bin/` paths
- If issues persist, check task configuration in `.vscode/tasks.json`
