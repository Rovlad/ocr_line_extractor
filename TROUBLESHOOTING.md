# FastAPI Server Troubleshooting Guide

## 🔧 Common Issues and Solutions

### 1. Pip Interpreter Error
**Error**: `bad interpreter: No such file or directory`

```bash
start_server.sh: /usr/local/bin/pip: /System/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/: bad interpreter: No such file or directory
```

**Solution**: Use the virtual environment's pip instead of system pip.

✅ **Fixed in `start_server.sh`**: Now uses `python -m pip` instead of `pip`

### 2. Uvicorn Reload Warning
**Error**: `WARNING: You must pass the application as an import string to enable 'reload' or 'workers'.`

**Solution**: Use uvicorn directly with module import string for reload mode.

✅ **Fixed**: 
- `python main.py` - Production mode (no reload)
- `./run_dev.sh` - Development mode with proper reload

### 3. Script Permission Issues
**Error**: `zsh: command not found: start_server.sh`

**Solution**: Make scripts executable or use `bash` explicitly.

```bash
# Make executable
chmod +x start_server.sh run_dev.sh

# Or run with bash
bash start_server.sh
```

## 📋 Startup Options

### Option 1: Production Server (Stable)
```bash
# Fixed pip issues, no reload warnings
./start_server.sh
```

### Option 2: Development Server (Hot Reload)
```bash
# Proper uvicorn reload support
./run_dev.sh
```

### Option 3: Manual Startup
```bash
# Load environment and start manually
cd .. && source setup_env.sh && cd fastapi_server
python main.py
```

### Option 4: Direct Uvicorn (Advanced)
```bash
# For development with full control
cd .. && source setup_env.sh && cd fastapi_server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🔍 Testing Server Status

### Check if Server is Running
```bash
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/

# Check processes
ps aux | grep uvicorn
```

### Environment Variables Check
```bash
# Verify environment is loaded
echo $GOOGLE_CLOUD_PROJECT_ID
echo $DOCUMENT_AI_PROCESSOR_ID

# Or check via API
curl http://localhost:8000/health | grep environment
```

## 🐞 Debug Steps

### 1. Environment Issues
```bash
# Reload environment
cd .. && source setup_env.sh && cd fastapi_server

# Check if variables are set
python -c "import os; print('Project ID:', os.getenv('GOOGLE_CLOUD_PROJECT_ID'))"
```

### 2. Dependency Issues
```bash
# Reinstall dependencies
python -m pip install fastapi uvicorn python-multipart

# Check imports
python -c "from main import app; print('Import successful')"
```

### 3. Port Issues
```bash
# Check if port 8000 is in use
lsof -i :8000

# Use different port
uvicorn main:app --host 0.0.0.0 --port 8001
```

### 4. Virtual Environment Issues
```bash
# Check virtual environment
which python
which pip
echo $VIRTUAL_ENV

# Reactivate if needed
source ../.venv/bin/activate
```

## 📝 Error Log Analysis

### Common Error Patterns

**Missing Environment Variables**:
```
ERROR: Missing required environment variables:
  - GOOGLE_CLOUD_PROJECT_ID
  - DOCUMENT_AI_PROCESSOR_ID
```
→ Solution: Run `source setup_env.sh`

**Import Error**:
```
Error importing PipingLineExtractor
```
→ Solution: Ensure parent directory has `process_pdf_to_piping_lines.py`

**Connection Refused**:
```
curl: (7) Failed to connect to localhost port 8000
```
→ Solution: Start the server first

## 🔄 Quick Recovery

If everything fails, try this complete reset:

```bash
# 1. Go to project root
cd ..

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Load environment
source setup_env.sh

# 4. Go to server directory
cd fastapi_server

# 5. Install dependencies
python -m pip install fastapi uvicorn python-multipart

# 6. Test import
python -c "from main import app; print('OK')"

# 7. Start server
python main.py
```

## 📞 Getting Help

If issues persist:

1. Check the terminal output for specific error messages
2. Verify all files exist: `ls -la main.py ../process_pdf_to_piping_lines.py`
3. Test the parent script first: `cd .. && python process_pdf_to_piping_lines.py test_pid.pdf`
4. Check network/firewall blocking port 8000

## ✅ Success Indicators

Server is working when you see:
- `Starting Piping Line Extractor API server...`
- `API Documentation available at: http://localhost:8000/docs`
- Health check returns: `{"status": "healthy"}`
- Interactive docs load at: http://localhost:8000/docs 