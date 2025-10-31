#!/bin/bash

# ProTrace Deployment Script
# ==========================
#
# This script provides automated deployment for ProTrace components.
# Usage: ./deploy.sh [command]
#
# Commands:
#   build          - Build all Docker images
#   up             - Start all services
#   down           - Stop all services
#   restart        - Restart all services
#   logs           - Show logs from all services
#   clean          - Remove all containers and volumes
#   test           - Run tests in containers
#   deploy-dev     - Deploy development environment
#   deploy-prod    - Deploy production environment

set -e

PROJECT_NAME="protrace"
DOCKER_COMPOSE_FILE="docker-compose.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed and running
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker."
        exit 1
    fi

    log_info "Docker is available and running"
}

# Check if docker-compose is available
check_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker-compose"
    elif docker compose version &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker compose"
    else
        log_error "Neither 'docker-compose' nor 'docker compose' is available."
        exit 1
    fi

    log_info "Using Docker Compose: $DOCKER_COMPOSE_CMD"
}

# Build all Docker images
build_images() {
    log_info "Building Docker images..."
    $DOCKER_COMPOSE_CMD -f $DOCKER_COMPOSE_FILE build --no-cache
    log_success "Docker images built successfully"
}

# Start all services
start_services() {
    log_info "Starting ProTrace services..."
    $DOCKER_COMPOSE_CMD -f $DOCKER_COMPOSE_FILE up -d
    log_success "Services started successfully"

    # Show status
    show_status
}

# Stop all services
stop_services() {
    log_info "Stopping ProTrace services..."
    $DOCKER_COMPOSE_CMD -f $DOCKER_COMPOSE_FILE down
    log_success "Services stopped successfully"
}

# Show service status
show_status() {
    log_info "Service Status:"
    $DOCKER_COMPOSE_CMD -f $DOCKER_COMPOSE_FILE ps
}

# Show logs
show_logs() {
    log_info "Showing service logs (press Ctrl+C to exit)..."
    $DOCKER_COMPOSE_CMD -f $DOCKER_COMPOSE_FILE logs -f
}

# Clean up containers and volumes
cleanup() {
    log_warning "This will remove all containers and volumes. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        log_info "Cleaning up containers and volumes..."
        $DOCKER_COMPOSE_CMD -f $DOCKER_COMPOSE_FILE down -v --remove-orphans
        docker system prune -f
        log_success "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

# Run tests
run_tests() {
    log_info "Running tests..."

    # Run Python tests
    log_info "Running Python tests..."
    $DOCKER_COMPOSE_CMD -f $DOCKER_COMPOSE_FILE exec -T protrace python -m pytest tests/ -v

    # Run Rust tests (if available)
    log_info "Running Rust tests..."
    $DOCKER_COMPOSE_CMD -f $DOCKER_COMPOSE_FILE exec -T zk-system cargo test

    log_success "All tests completed"
}

# Deploy development environment
deploy_dev() {
    log_info "Deploying ProTrace development environment..."
    build_images
    start_services
    log_success "Development environment deployed"
    log_info "Access the application:"
    log_info "  - ProTrace CLI: docker-compose exec protrace bash"
    log_info "  - ZK System: docker-compose exec zk-system bash"
    log_info "  - IPFS API: http://localhost:5001"
    log_info "  - IPFS Gateway: http://localhost:8080"
}

# Deploy production environment
deploy_prod() {
    log_warning "Production deployment requires additional configuration:"
    log_warning "  - Set proper environment variables"
    log_warning "  - Configure SSL certificates"
    log_warning "  - Setup monitoring and logging"
    log_warning "  - Configure backup and recovery"
    log_warning "Continue with production deployment? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        log_info "Deploying ProTrace production environment..."
        build_images
        # In production, you might want to use a different compose file
        $DOCKER_COMPOSE_CMD -f $DOCKER_COMPOSE_FILE up -d
        log_success "Production environment deployed"
    else
        log_info "Production deployment cancelled"
    fi
}

# Health check
health_check() {
    log_info "Performing health checks..."

    # Check if services are running
    if $DOCKER_COMPOSE_CMD -f $DOCKER_COMPOSE_FILE ps | grep -q "Up"; then
        log_success "Services are running"

        # Check IPFS connectivity (if IPFS is running)
        if $DOCKER_COMPOSE_CMD -f $DOCKER_COMPOSE_FILE ps | grep -q "protrace-ipfs"; then
            if curl -s http://localhost:5001/api/v0/id &> /dev/null; then
                log_success "IPFS is accessible"
            else
                log_warning "IPFS is running but not accessible"
            fi
        fi
    else
        log_error "No services are running"
        return 1
    fi
}

# Main script logic
main() {
    local command="${1:-help}"

    check_docker
    check_docker_compose

    case $command in
        build)
            build_images
            ;;
        up)
            start_services
            ;;
        down)
            stop_services
            ;;
        restart)
            stop_services
            start_services
            ;;
        logs)
            show_logs
            ;;
        status)
            show_status
            ;;
        clean)
            cleanup
            ;;
        test)
            run_tests
            ;;
        deploy-dev)
            deploy_dev
            ;;
        deploy-prod)
            deploy_prod
            ;;
        health)
            health_check
            ;;
        help|*)
            echo "ProTrace Deployment Script"
            echo "=========================="
            echo ""
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  build          - Build all Docker images"
            echo "  up             - Start all services"
            echo "  down           - Stop all services"
            echo "  restart        - Restart all services"
            echo "  logs           - Show logs from all services"
            echo "  status         - Show service status"
            echo "  clean          - Remove all containers and volumes"
            echo "  test           - Run tests in containers"
            echo "  deploy-dev     - Deploy development environment"
            echo "  deploy-prod    - Deploy production environment"
            echo "  health         - Perform health checks"
            echo "  help           - Show this help message"
            ;;
    esac
}

# Run main function with all arguments
main "$@"
