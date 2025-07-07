# Quick Start Guide - FastAPI Piping Line Extractor

## 🚀 Quick Setup

### 1. Start the Server
```bash
# From the fastapi_server directory
cd fastapi_server

# Option A: Production server (recommended)
./start_server.sh

# Option B: Development server with hot reload
./run_dev.sh

# Option C: Manual startup
cd .. && source setup_env.sh && cd fastapi_server
python main.py
```

### 2. Test the API
```bash
# Health check
curl http://localhost:8000/health

# Upload PDF and extract piping lines
curl -X POST -F "file=@../test_pid.pdf" http://localhost:8000/extract-piping-lines/
```

### 3. Interactive Documentation
Open your browser to: **http://localhost:8000/docs**

## 📁 File Structure
```
fastapi_server/
├── main.py              # FastAPI application
├── requirements.txt     # Dependencies
├── README.md           # Full documentation
├── start_server.sh     # Startup script
├── test_api.py         # Test script
└── QUICKSTART.md       # This file
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| POST | `/extract-piping-lines/` | Upload PDF, get piping lines |
| GET | `/docs` | Interactive API docs |

## 📋 Response Format

```json
{
  "metadata": {
    "source_file": "your_file.pdf",
    "extraction_timestamp": "2025-07-07T17:24:24.805515",
    "total_found": 23,
    "extraction_script": "fastapi_server/main.py",
    "pid_identifier": "13028-03-PID-003"
  },
  "piping_lines": [
    {
      "piping_line_number": "6\"-FH-A1-02",
      "text_line_number": 18,
      "context": "6\"-FH-A1-02",
      "coordinates": {
        "x": 490,
        "y": 212,
        "width": 7,
        "height": 10
      }
    }
  ]
}
```

## ⚡ Usage Examples

### Python
```python
import requests

with open('your_file.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/extract-piping-lines/', files=files)
    result = response.json()
    print(f"Found {result['metadata']['total_found']} piping lines")
```

### JavaScript
```javascript
const formData = new FormData();
formData.append('file', pdfFile);
fetch('http://localhost:8000/extract-piping-lines/', {
    method: 'POST',
    body: formData
}).then(response => response.json())
  .then(data => console.log(data));
```

### curl
```bash
curl -X POST -F "file=@document.pdf" http://localhost:8000/extract-piping-lines/
```

## 🔧 Environment Requirements

- Google Cloud credentials (loaded via `source setup_env.sh`)
- Virtual environment with dependencies installed
- PDF files for processing

## 🎯 Next Steps

1. **Test with your PDFs**: Upload your own PDF files via the `/docs` interface
2. **Integrate**: Use the API in your applications
3. **Deploy**: Consider Docker/cloud deployment for production use

For full documentation, see `README.md` 