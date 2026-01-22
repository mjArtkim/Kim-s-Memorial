#!/bin/bash
# automated deployment for Kim's Memorial

# --- Configuration ---
REMOTE_USER="vonhoon"
REMOTE_HOST="homeserver"
IMAGE_NAME="memorial-app"
PROJECT_DIR_LOCAL="/home/vonhoon/projects/Kim-s-Memorial"
PROJECT_DIR_REMOTE="kims_memorial"

# --- Script Logic ---
set -e
set -o pipefail

# --- Docker Management ---
DOCKER_STARTED_BY_SCRIPT=false

if ! systemctl is-active --quiet docker; then
    echo "🐳 Docker is not active. Starting..."
    sudo systemctl enable --now docker
    DOCKER_STARTED_BY_SCRIPT=true
    
    # Wait for socket (with timeout)
    count=0
    while ! sudo docker info > /dev/null 2>&1; do
        echo "⏳ Waiting for Docker to start... ($count/30)"
        sleep 1
        count=$((count+1))
        if [ $count -ge 30 ]; then
            echo "❌ Timeout waiting for Docker to start."
            echo "Debug: sudo docker info output:"
            sudo docker info
            exit 1
        fi
    done
    echo "✅ Docker is up."
fi


echo "🚀 Starting Kim's Memorial deployment script..."
cd "$PROJECT_DIR_LOCAL"

# --- NEW: Clean up old local images to save space/time ---
echo "🧹 Cleaning up old local image tags..."
sudo docker images --format "{{.Repository}}:{{.Tag}}" | grep "^${IMAGE_NAME}:" | grep -v ":latest$" | xargs --no-run-if-empty sudo docker rmi || true

# --- Versioning ---
VERSION_FILE=".version"
if [ ! -f "$VERSION_FILE" ]; then echo "1" > "$VERSION_FILE"; fi
BUILD_NUMBER=$(cat "$VERSION_FILE")
BASE_TAG="1.0"
VERSIONED_TAG="${IMAGE_NAME}:${BASE_TAG}.${BUILD_NUMBER}"
STATIC_TAG="${IMAGE_NAME}:latest"

IMAGE_FILE="${IMAGE_NAME}_${BASE_TAG}.${BUILD_NUMBER}.tar.gz"

echo "🔨 Building new image..."
sudo docker build -t "${VERSIONED_TAG}" -t "${STATIC_TAG}" .

echo "📦 Saving and compressing image to ${IMAGE_FILE}..."
sudo docker save "${STATIC_TAG}" | gzip > "${IMAGE_FILE}"

echo "📡 Copying image to ${REMOTE_HOST}..."
scp "${IMAGE_FILE}" "${REMOTE_USER}@${REMOTE_HOST}:~/"

# Copy docker-compose (if separate, but usually we just want to load the image and up)
# Note: We need to ensure docker-compose.yml is on the serving location too or we can just run it
# If the remote directory doesn't involve source code, we should at least copy the docker-compose.yml
scp "docker-compose.yml" "${REMOTE_USER}@${REMOTE_HOST}:~/${IMAGE_FILE}.yml"

echo "☁️  Deploying on remote server (${REMOTE_HOST})..."
ssh "${REMOTE_USER}@${REMOTE_HOST}" << EOF
    set -e
    
    # Create directory if it doesn't exist
    mkdir -p ~/${PROJECT_DIR_REMOTE}
    
    # Move uploaded compose file to project dir
    mv ~/${IMAGE_FILE}.yml ~/${PROJECT_DIR_REMOTE}/docker-compose.yml
    
    echo "    - Navigating to remote project directory..."
    cd ~/${PROJECT_DIR_REMOTE}

    echo "    - Stopping current services..."
    docker compose down || true

    echo "    - Loading new image from tarball..."
    gunzip -c ~/${IMAGE_FILE} | docker load

    echo "    - Starting new services in detached mode..."
    docker compose up -d

    echo "    - Cleaning up remote image file..."
    rm ~/${IMAGE_FILE}
EOF

# --- Cleanup and Version Bump ---
echo "🧹 Cleaning up local image file..."
rm "${IMAGE_FILE}"

NEW_BUILD_NUMBER=$((BUILD_NUMBER + 1))
echo "${NEW_BUILD_NUMBER}" > "$VERSION_FILE"

# --- Docker Cleanup ---
if [ "$DOCKER_STARTED_BY_SCRIPT" = true ]; then
    echo "🛑 Stopping Docker (restoring state)..."
    sudo systemctl disable --now docker
fi

echo "---"
echo "✅ Deployment of ${VERSIONED_TAG} successful!"
echo "---"
