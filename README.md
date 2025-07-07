# 🐳 Piping Line Extractor - Docker Deployment

This directory contains everything needed to deploy the Piping Line Extractor API as a Docker container.

## 📋 Prerequisites

- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Google Cloud Document AI** service account credentials
- At least **2GB RAM** available for the container

## 🚀 Quick Start

### 1. **Environment Setup**

Create a `.env` file with your Google Cloud credentials:

```bash
# Copy the environment template
cp .env.example .env

# Edit with your actual values
nano .env
```

Required environment variables:
```env
GOOGLE_CLOUD_PROJECT_ID=your-project-id-here
DOCUMENT_AI_PROCESSOR_ID=your-processor-id-here
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account",...}
DOCUMENT_AI_LOCATION=us
```

### 2. **Build and Deploy**

```bash
# Make scripts executable
chmod +x build.sh deploy.sh

# Build the Docker image
./build.sh

# Deploy the service
./deploy.sh
```

### 3. **Access the Service**

- **API Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs  
- **Test Interface**: http://localhost:8000/test_ui.html
- **Health Check**: http://localhost:8000/health

## 📁 File Structure

```
docker_deployment/
├── Dockerfile              # Container definition
├── docker-compose.yml      # Service orchestration
├── .dockerignore           # Build exclusions
├── build.sh                # Build script
├── deploy.sh               # Deployment script
├── README.md               # This file
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── test_ui.html           # Web test interface
└── .env                    # Environment variables (create this)
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_CLOUD_PROJECT_ID` | ✅ | - | Your Google Cloud project ID |
| `DOCUMENT_AI_PROCESSOR_ID` | ✅ | - | Document AI processor ID |
| `GOOGLE_APPLICATION_CREDENTIALS_JSON` | ✅ | - | Service account JSON (as string) |
| `DOCUMENT_AI_LOCATION` | ❌ | `us` | Document AI processor location |

### Docker Compose Profiles

```bash
# Basic deployment (API only)
docker-compose up -d

# Production deployment (with nginx proxy)
docker-compose --profile production up -d
```

## 🛠️ Management Commands

### **Building**
```bash
# Build with specific tag
./build.sh v1.0.0

# Build for registry
REGISTRY=your-registry.com ./build.sh
```

### **Deployment**
```bash
# Deploy and start services
./deploy.sh

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart specific service
docker-compose restart piping-extractor
```

### **Monitoring**
```bash
# View container status
docker-compose ps

# Monitor resource usage
docker stats piping-line-extractor

# View health status
curl http://localhost:8000/health
```

### **Debugging**
```bash
# Access container shell
docker exec -it piping-line-extractor bash

# View application logs
docker-compose logs piping-extractor

# Test API manually
curl -X POST "http://localhost:8000/extract-piping-lines/" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@test.pdf"
```

## 🔒 Security Considerations

### **Production Deployment**

1. **Environment Variables**: Use Docker secrets instead of .env files
2. **SSL/TLS**: Enable HTTPS with proper certificates
3. **Firewall**: Restrict access to necessary ports only
4. **Updates**: Regular security updates for base images

### **Secure Environment Setup**
```bash
# Use Docker secrets (production)
echo "your-project-id" | docker secret create gcp_project_id -
echo "your-processor-id" | docker secret create processor_id -
echo '{"type":"service_account",...}' | docker secret create gcp_credentials -
```

## 🚀 Deployment Scenarios

### **Local Development**
```bash
# Quick local testing
docker-compose up -d
```

### **Production Server**
```bash
# With nginx proxy and SSL
docker-compose --profile production up -d
```

### **Cloud Deployment**
```bash
# Build for cloud registry
REGISTRY=gcr.io/your-project ./build.sh
docker push gcr.io/your-project/piping-line-extractor:latest
```

### **Kubernetes**
```yaml
# Example k8s deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: piping-extractor
spec:
  replicas: 3
  selector:
    matchLabels:
      app: piping-extractor
  template:
    metadata:
      labels:
        app: piping-extractor
    spec:
      containers:
      - name: api
        image: piping-line-extractor:latest
        ports:
        - containerPort: 8000
        env:
        - name: GOOGLE_CLOUD_PROJECT_ID
          valueFrom:
            secretKeyRef:
              name: gcp-secrets
              key: project-id
```

## 📊 Performance Tuning

### **Resource Limits**
```yaml
# In docker-compose.yml
services:
  piping-extractor:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### **Scaling**
```bash
# Scale horizontally
docker-compose up --scale piping-extractor=3 -d

# Use load balancer
docker-compose --profile production up -d
```

## 🐛 Troubleshooting

### **Common Issues**

| Issue | Solution |
|-------|----------|
| Container won't start | Check `.env` file and Docker logs |
| API returns 500 errors | Verify Google Cloud credentials |
| Out of memory | Increase Docker memory limits |
| Port already in use | Change port mapping or stop conflicting service |

### **Health Checks**
```bash
# Container health
docker inspect piping-line-extractor --format='{{.State.Health.Status}}'

# Service health
curl -f http://localhost:8000/health || echo "Service unhealthy"

# Dependencies
docker exec piping-line-extractor python -c "import google.cloud.documentai; print('✅ Google Cloud AI imported')"
```

## 📝 API Usage Examples

### **Upload PDF via cURL**
```bash
curl -X POST "http://localhost:8000/extract-piping-lines/" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your-document.pdf"
```

### **Python Client**
```python
import requests

url = "http://localhost:8000/extract-piping-lines/"
files = {"file": open("document.pdf", "rb")}
response = requests.post(url, files=files)
result = response.json()
print(f"Found {result['metadata']['total_found']} piping lines")
```

### **JavaScript/Web**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/extract-piping-lines/', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

## 📞 Support

For issues and questions:
1. Check the logs: `docker-compose logs`
2. Verify environment variables: `docker exec container env`
3. Test Google Cloud connectivity: `docker exec container python -c "from google.cloud import documentai"`
4. Review the [main documentation](../README.md)

---

**Built with** 🐳 Docker • ⚡ FastAPI • �� Google Document AI 