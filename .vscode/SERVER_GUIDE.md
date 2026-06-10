# Running the FastAPI Server in VS Code

## Quick Start

### Method 1: Debug Mode (Recommended)
1. Press **F5** or open Run and Debug panel (Cmd+Shift+D)
2. Select **"Python: FastAPI Server (Debug)"**
3. Server starts at http://localhost:8000
4. Open http://localhost:8000 in browser

### Method 2: Task (Quick)
1. Press **Cmd+Shift+P** (Mac) or **Ctrl+Shift+P** (Windows)
2. Type "Tasks: Run Task"
3. Select **"Start FastAPI Server"**
4. Server starts at http://localhost:8000

### Method 3: Terminal
```bash
uvicorn quiet_riot.api.server:app --host 0.0.0.0 --port 8000 --reload
```

## Debug Configurations

### Python: FastAPI Server (Debug)
- **Auto-reload**: Enabled
- **Debugging**: Full support (breakpoints, variables)
- **Best for**: Development and debugging

### Python: FastAPI Server (No Reload)
- **Auto-reload**: Disabled
- **Debugging**: Full support
- **Best for**: Performance testing, production-like debugging

## Tasks

### Start FastAPI Server
- Runs in background
- Auto-reload enabled
- Quick start without debugging

### Start FastAPI Server (Production)
- Runs in background
- No auto-reload
- Production-like environment

## Accessing the Server

Once running, access:
- **Dashboard**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Stopping the Server

- **Debug Mode**: Click stop button in debug toolbar
- **Task Mode**: Close the terminal or press Ctrl+C in terminal
- **Terminal**: Press Ctrl+C

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process (replace PID)
kill -9 <PID>
```

### Import Errors
```bash
# Install package
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"
```

### Server Won't Start
1. Check AWS credentials are configured
2. Verify dependencies: `pip list | grep uvicorn`
3. Check logs in VS Code terminal
