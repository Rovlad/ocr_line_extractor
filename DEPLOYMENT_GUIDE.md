# 🚀 Quick Deployment Guide

## Prerequisites
- Docker Desktop installed and running
- Google Cloud Document AI service account credentials

## Step-by-Step Deployment

### 1. Setup Environment
```bash
# Copy environment template
cp env.example .env

# Edit with your Google Cloud credentials
nano .env
```

Add your actual values:
```env
GOOGLE_CLOUD_PROJECT_ID=your-actual-project-id
DOCUMENT_AI_PROCESSOR_ID=your-actual-processor-id
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account",...your-full-json...}
```

### 2. Build and Deploy
```bash
# Build the Docker image
./build.sh

# Deploy the service
./deploy.sh
```

### 3. Test the Service
- Open: http://localhost:8000/test_ui.html
- Upload a PDF file
- Extract piping lines
- View results

### 4. Management Commands

```bash
# View logs
docker-compose logs -f

# Stop service
docker-compose down

# Restart service
docker-compose restart

# View status
docker-compose ps
```

## Troubleshooting

### Common Issues

**Container won't start**
```bash
# Check logs
docker-compose logs piping-extractor

# Verify environment
docker exec piping-line-extractor env | grep GOOGLE
```

**API returns errors**
```bash
# Test Google Cloud connection
docker exec piping-line-extractor python -c "from google.cloud import documentai; print('✅ OK')"

# Check health
curl http://localhost:8000/health
```

**Port already in use**
```bash
# Find what's using port 8000
lsof -i :8000

# Or change port in docker-compose.yml
# ports:
#   - "8080:8000"  # Use port 8080 instead
```

## Next Steps

1. **Production**: Review security settings in `docker-compose.yml`
2. **Scaling**: Add load balancer for multiple instances
3. **Monitoring**: Set up logging and alerts
4. **SSL**: Configure HTTPS for production deployment

## File Structure
```
docker_deployment/
├── build.sh              # Build Docker image
├── deploy.sh             # Deploy service
├── docker-compose.yml    # Service configuration
├── Dockerfile            # Container definition
├── env.example           # Environment template
├── main.py               # FastAPI app
├── requirements.txt      # Dependencies
└── test_ui.html          # Test interface
```

## API Endpoints
- `GET /` - API info
- `GET /health` - Health check
- `POST /extract-piping-lines/` - Process PDF
- `GET /docs` - Interactive documentation
- `GET /test_ui.html` - Web test interface 