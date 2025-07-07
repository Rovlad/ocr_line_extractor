#!/bin/bash

# Build script for Piping Line Extractor Docker image
set -e

# Configuration
IMAGE_NAME="piping-line-extractor"
IMAGE_TAG="${1:-latest}"
REGISTRY="${REGISTRY:-}"

echo "🔧 Building Piping Line Extractor Docker Image"
echo "================================================"
echo "Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "Registry: ${REGISTRY:-local}"
echo ""

# Build the Docker image
echo "📦 Building Docker image..."
docker build \
    --tag "${IMAGE_NAME}:${IMAGE_TAG}" \
    --tag "${IMAGE_NAME}:latest" \
    --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
    --build-arg VERSION="${IMAGE_TAG}" \
    .

echo "✅ Build completed successfully!"
echo ""

# Tag for registry if specified
if [ -n "$REGISTRY" ]; then
    echo "🏷️  Tagging for registry..."
    docker tag "${IMAGE_NAME}:${IMAGE_TAG}" "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    docker tag "${IMAGE_NAME}:latest" "${REGISTRY}/${IMAGE_NAME}:latest"
    echo "✅ Tagged for registry: ${REGISTRY}"
    echo ""
fi

# Show image info
echo "📋 Image Information:"
docker images "${IMAGE_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
echo ""

# Show next steps
echo "🚀 Next Steps:"
echo "1. Create your .env file with Google Cloud credentials"
echo "2. Run: docker-compose up -d"
echo "3. Access the API at: http://localhost:8000"
echo "4. View docs at: http://localhost:8000/docs"
echo "5. Test with UI at: http://localhost:8000/test_ui.html"
echo ""

if [ -n "$REGISTRY" ]; then
    echo "📤 To push to registry:"
    echo "   docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    echo "   docker push ${REGISTRY}/${IMAGE_NAME}:latest"
fi 