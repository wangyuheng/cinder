#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
OLLAMA_HOST="${OLLAMA_HOST:-http://localhost:11434}"
PHOENIX_HOST="${PHOENIX_HOST:-localhost}"
PHOENIX_PORT="${PHOENIX_PORT:-6006}"
PHOENIX_DOCKER_IMAGE="${PHOENIX_DOCKER_IMAGE:-arizephoenix/phoenix:latest}"
PHOENIX_CONTAINER_NAME="${PHOENIX_CONTAINER_NAME:-cinder-phoenix}"

# Functions
check_ollama() {
    if curl -s --max-time 2 "${OLLAMA_HOST}/api/tags" > /dev/null 2>&1; then
        echo "running"
        return 0
    else
        echo "not_running"
        return 1
    fi
}

check_phoenix() {
    if curl -s --max-time 2 "http://${PHOENIX_HOST}:${PHOENIX_PORT}/healthz" > /dev/null 2>&1; then
        echo "running"
        return 0
    else
        echo "not_running"
        return 1
    fi
}

check_docker() {
    if command -v docker &> /dev/null && docker info &> /dev/null 2>&1; then
        echo "available"
        return 0
    else
        echo "not_available"
        return 1
    fi
}

start_phoenix() {
    echo "Starting Phoenix server..."
    
    # Check Docker
    if [ "$(check_docker)" != "available" ]; then
        echo -e "${RED}✗ Docker is not installed or not running${NC}"
        echo ""
        echo "Please ensure Docker is installed and running:"
        echo "  - Install: https://docs.docker.com/get-docker/"
        echo "  - Start: docker info"
        return 1
    fi
    
    # Check if already running
    if [ "$(check_phoenix)" = "running" ]; then
        echo -e "${GREEN}✓ Phoenix is already running${NC}"
        echo "  URL: http://${PHOENIX_HOST}:${PHOENIX_PORT}"
        return 0
    fi
    
    # Pull image
    echo "Pulling Phoenix Docker image: ${PHOENIX_DOCKER_IMAGE}"
    if ! docker pull "${PHOENIX_DOCKER_IMAGE}"; then
        echo -e "${RED}✗ Failed to pull Docker image${NC}"
        return 1
    fi
    
    # Stop existing container
    docker rm -f "${PHOENIX_CONTAINER_NAME}" &> /dev/null || true
    
    # Start container
    echo "Starting Phoenix container: ${PHOENIX_CONTAINER_NAME}"
    if ! docker run -d \
        --name "${PHOENIX_CONTAINER_NAME}" \
        -p "${PHOENIX_PORT}:6006" \
        -p "4317:4317" \
        -v phoenix-data:/root/.phoenix \
        "${PHOENIX_DOCKER_IMAGE}"; then
        echo -e "${RED}✗ Failed to start container${NC}"
        return 1
    fi
    
    # Wait for service to be ready
    echo "Waiting for Phoenix to be ready..."
    local max_attempts=30
    local attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if [ "$(check_phoenix)" = "running" ]; then
            echo -e "${GREEN}✓ Phoenix started successfully${NC}"
            echo "  URL: http://${PHOENIX_HOST}:${PHOENIX_PORT}"
            echo "  Container: ${PHOENIX_CONTAINER_NAME}"
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}✗ Phoenix container started but service not responding${NC}"
    echo "Check logs: docker logs ${PHOENIX_CONTAINER_NAME}"
    return 1
}

stop_phoenix() {
    echo "Stopping Phoenix server..."
    
    if [ "$(check_phoenix)" != "running" ]; then
        echo -e "${GREEN}✓ Phoenix is not running${NC}"
        return 0
    fi
    
    if docker stop "${PHOENIX_CONTAINER_NAME}" &> /dev/null; then
        docker rm "${PHOENIX_CONTAINER_NAME}" &> /dev/null || true
        echo -e "${GREEN}✓ Phoenix stopped successfully${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed to stop Phoenix${NC}"
        return 1
    fi
}

show_status() {
    echo ""
    echo "============================================================"
    echo "Service Status"
    echo "============================================================"
    
    # Ollama status
    echo ""
    echo "[Ollama]"
    if [ "$(check_ollama)" = "running" ]; then
        local models=$(curl -s "${OLLAMA_HOST}/api/tags" 2>/dev/null | grep -o '"models":\[.*\]' | grep -o '\[' | wc -l || echo "0")
        echo -e "  Status: ${GREEN}✓ Running${NC}"
        echo "  URL: ${OLLAMA_HOST}"
        echo "  Models: ${models}"
    else
        echo -e "  Status: ${RED}✗ Not Running${NC}"
        echo "  URL: ${OLLAMA_HOST}"
        echo "  Start: ollama serve"
    fi
    
    # Docker status
    echo ""
    echo "[Docker]"
    if [ "$(check_docker)" = "available" ]; then
        echo -e "  Status: ${GREEN}✓ Available${NC}"
    else
        echo -e "  Status: ${RED}✗ Not Available${NC}"
    fi
    
    # Phoenix status
    echo ""
    echo "[Phoenix]"
    if [ "$(check_phoenix)" = "running" ]; then
        echo -e "  Status: ${GREEN}✓ Running${NC}"
        echo "  URL: http://${PHOENIX_HOST}:${PHOENIX_PORT}"
        echo "  Container: ${PHOENIX_CONTAINER_NAME}"
    else
        echo -e "  Status: ${RED}✗ Not Running${NC}"
        echo "  URL: http://${PHOENIX_HOST}:${PHOENIX_PORT}"
        echo "  Start: cinder service start-phoenix"
    fi
    
    echo ""
    echo "============================================================"
}

check_all() {
    local ollama_status=$(check_ollama)
    local phoenix_status=$(check_phoenix)
    local docker_status=$(check_docker)
    
    echo "{"
    echo "  \"ollama\": {"
    echo "    \"running\": $([ "${ollama_status}" = "running" ] && echo "true" || echo "false"),"
    echo "    \"url\": \"${OLLAMA_HOST}\""
    echo "  },"
    echo "  \"phoenix\": {"
    echo "    \"running\": $([ "${phoenix_status}" = "running" ] && echo "true" || echo "false"),"
    echo "    \"url\": \"http://${PHOENIX_HOST}:${PHOENIX_PORT}\","
    echo "    \"container\": \"${PHOENIX_CONTAINER_NAME}\""
    echo "  },"
    echo "  \"docker\": $([ "${docker_status}" = "available" ] && echo "true" || echo "false")"
    echo "}"
    
    # Exit with error if Ollama not running
    [ "${ollama_status}" = "running" ]
}

# Main
case "${1:-}" in
    status)
        show_status
        ;;
    start-phoenix)
        start_phoenix
        ;;
    stop-phoenix)
        stop_phoenix
        ;;
    check)
        check_all
        ;;
    *)
        echo "Usage: $0 {status|start-phoenix|stop-phoenix|check}"
        echo ""
        echo "Commands:"
        echo "  status          Show status of all services"
        echo "  start-phoenix   Start Phoenix server via Docker"
        echo "  stop-phoenix    Stop Phoenix server"
        echo "  check           Check services (JSON output, exit 0 if all running)"
        exit 1
        ;;
esac
