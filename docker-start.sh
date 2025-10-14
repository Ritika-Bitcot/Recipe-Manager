#!/bin/bash

# Docker startup script for Recipe Manager API
# This script provides easy commands to manage the Docker environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to start production environment
start_production() {
    print_header "Starting Production Environment"
    check_docker
    
    print_status "Building and starting production services..."
    docker compose up -d --build
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    print_status "Checking service health..."
    if curl -f http://localhost:5000/api/health > /dev/null 2>&1; then
        print_status "✅ Application is running at http://localhost:5000"
    else
        print_warning "⚠️  Application may not be ready yet. Check logs with: docker compose logs app"
    fi
    
    print_status "Services started successfully!"
    echo "Available services:"
    echo "  - API: http://localhost:5000"
    echo "  - Database: localhost:5432"
    echo "  - Redis: localhost:6379"
    echo "  - App: http://localhost:5000"
}

# Function to start development environment
start_development() {
    print_header "Starting Development Environment"
    check_docker
    
    print_status "Building and starting development services..."
    docker compose -f docker-compose.dev.yml up -d --build
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    print_status "Running database migrations..."
    docker compose -f docker-compose.dev.yml exec app python -m flask db upgrade || print_warning "Database migrations not available (Flask-Migrate not configured)"
    
    print_status "Checking service health..."
    if curl -f http://localhost:5001/api/health > /dev/null 2>&1; then
        print_status "✅ Development application is running at http://localhost:5001"
    else
        print_warning "⚠️  Application may not be ready yet. Check logs with: docker compose -f docker-compose.dev.yml logs app"
    fi
    
    print_status "Development environment started successfully!"
    echo "Available services:"
    echo "  - API: http://localhost:5001 (with hot reload)"
    echo "  - Database: localhost:5433"
    echo "  - Redis: localhost:6380"
}

# Function to stop services
stop_services() {
    print_header "Stopping Services"
    
    print_status "Stopping production services..."
    docker compose down 2>/dev/null || true
    
    print_status "Stopping development services..."
    docker compose -f docker-compose.dev.yml down 2>/dev/null || true
    
    print_status "Services stopped successfully!"
}

# Function to show logs
show_logs() {
    local service=${1:-app}
    print_header "Showing Logs for $service"
    
    if docker compose ps | grep -q "$service"; then
        docker compose logs -f "$service"
    elif docker compose -f docker-compose.dev.yml ps | grep -q "$service"; then
        docker compose -f docker-compose.dev.yml logs -f "$service"
    else
        print_error "Service '$service' not found. Available services:"
        docker compose ps --services
    fi
}

# Function to run tests
run_tests() {
    print_header "Running Tests"
    
    if docker compose ps | grep -q "app"; then
        print_status "Running tests in production container..."
        docker compose exec app python -m pytest tests/ -v
    elif docker compose -f docker-compose.dev.yml ps | grep -q "app"; then
        print_status "Running tests in development container..."
        docker compose -f docker-compose.dev.yml exec app python -m pytest tests/ -v
    else
        print_error "No running application container found. Start the environment first."
        exit 1
    fi
}

# Function to clean up
cleanup() {
    print_header "Cleaning Up"
    
    print_status "Stopping all services..."
    docker compose down 2>/dev/null || true
    docker compose -f docker-compose.dev.yml down 2>/dev/null || true
    
    print_status "Removing volumes (WARNING: This will delete all data)..."
    read -p "Are you sure you want to delete all data? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker compose down -v 2>/dev/null || true
        docker compose -f docker-compose.dev.yml down -v 2>/dev/null || true
        print_status "All data deleted."
    else
        print_status "Cleanup cancelled."
    fi
}

# Function to show help
show_help() {
    print_header "Recipe Manager Docker Commands"
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start-prod     Start production environment"
    echo "  start-dev      Start development environment"
    echo "  stop           Stop all services"
    echo "  logs [service] Show logs for a service (default: app)"
    echo "  test           Run tests"
    echo "  cleanup        Clean up containers and volumes"
    echo "  help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start-dev          # Start development environment"
    echo "  $0 logs app           # Show application logs"
    echo "  $0 logs db            # Show database logs"
    echo "  $0 test               # Run tests"
}

# Main script logic
case "${1:-help}" in
    "start-prod")
        start_production
        ;;
    "start-dev")
        start_development
        ;;
    "stop")
        stop_services
        ;;
    "logs")
        show_logs "$2"
        ;;
    "test")
        run_tests
        ;;
    "cleanup")
        cleanup
        ;;
    "help"|*)
        show_help
        ;;
esac
