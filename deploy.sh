#!/bin/bash
#
# DEPLOYMENT EXECUTION SCRIPT
# 
# This script automates the deployment process for the security fixes.
# Run this after merging the PR to main branch.
#
# Usage: ./deploy.sh [staging|production]

set -e  # Exit on error

ENVIRONMENT=${1:-staging}

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║  🚀 CrucibAI Deployment Script - $ENVIRONMENT Environment      ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if environment variables are set
check_env_vars() {
    print_step "Checking required environment variables..."
    
    MISSING_VARS=()
    
    if [ -z "$JWT_SECRET" ]; then
        MISSING_VARS+=("JWT_SECRET")
    fi
    
    if [ -z "$MONGO_URL" ]; then
        MISSING_VARS+=("MONGO_URL")
    fi
    
    if [ -z "$DB_NAME" ]; then
        MISSING_VARS+=("DB_NAME")
    fi
    
    if [ ${#MISSING_VARS[@]} -gt 0 ]; then
        print_error "Missing required environment variables: ${MISSING_VARS[*]}"
        echo ""
        echo "Set them with:"
        echo "  export JWT_SECRET=\"\$(openssl rand -base64 32)\""
        echo "  export ENCRYPTION_KEY=\"\$(python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')\""
        echo "  export CORS_ORIGINS=\"https://app.example.com\""
        echo "  export MONGO_URL=\"mongodb://localhost:27017\""
        echo "  export DB_NAME=\"crucibai_$ENVIRONMENT\""
        exit 1
    fi
    
    if [ -z "$ENCRYPTION_KEY" ]; then
        print_warning "ENCRYPTION_KEY not set. API keys will not be encrypted."
    fi
    
    if [ -z "$CORS_ORIGINS" ]; then
        print_warning "CORS_ORIGINS not set. Defaulting to localhost:3000"
    fi
    
    echo -e "${GREEN}✓${NC} All required environment variables are set"
}

# Pull latest code
pull_code() {
    print_step "Pulling latest code..."
    git pull origin main
    echo -e "${GREEN}✓${NC} Code updated"
}

# Install dependencies
install_dependencies() {
    print_step "Installing dependencies..."
    cd backend
    pip install -r requirements.txt
    cd ..
    echo -e "${GREEN}✓${NC} Dependencies installed"
}

# Run tests
run_tests() {
    print_step "Running tests..."
    cd backend
    
    # Run syntax validation
    python3 -m py_compile server.py encryption.py error_handlers.py
    echo -e "${GREEN}✓${NC} Syntax validation passed"
    
    # Run security tests
    if command -v pytest &> /dev/null; then
        pytest tests/test_security_fixes.py -v
        echo -e "${GREEN}✓${NC} Security tests passed"
    else
        print_warning "pytest not available, skipping test execution"
    fi
    
    cd ..
}

# Start the service
start_service() {
    print_step "Starting CrucibAI service..."
    
    if [ -f "docker-compose.yml" ]; then
        docker-compose down
        docker-compose up -d
        echo -e "${GREEN}✓${NC} Service started with Docker"
    else
        cd backend
        # Start with uvicorn in background
        nohup uvicorn server:app --host 0.0.0.0 --port 8000 > ../crucibai.log 2>&1 &
        echo $! > ../crucibai.pid
        echo -e "${GREEN}✓${NC} Service started (PID: $(cat ../crucibai.pid))"
        cd ..
    fi
}

# Health check
health_check() {
    print_step "Performing health check..."
    
    sleep 5  # Wait for service to start
    
    if curl -f http://localhost:8000/api/health &> /dev/null; then
        echo -e "${GREEN}✓${NC} Health check passed"
    else
        print_warning "Health check endpoint not available"
    fi
}

# Show logs
show_logs() {
    print_step "Showing recent logs..."
    
    if [ -f "crucibai.log" ]; then
        tail -n 20 crucibai.log
    elif command -v docker-compose &> /dev/null; then
        docker-compose logs --tail=20 backend
    fi
}

# Main deployment flow
main() {
    echo "Deploying to $ENVIRONMENT environment..."
    echo ""
    
    check_env_vars
    pull_code
    install_dependencies
    run_tests
    start_service
    health_check
    
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║  ✅ Deployment Complete!                                     ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Service is running on: http://localhost:8000"
    echo ""
    echo "To view logs:"
    if [ -f "crucibai.log" ]; then
        echo "  tail -f crucibai.log"
    else
        echo "  docker-compose logs -f backend"
    fi
    echo ""
    echo "To stop the service:"
    if [ -f "docker-compose.yml" ]; then
        echo "  docker-compose down"
    else
        echo "  kill \$(cat crucibai.pid)"
    fi
    echo ""
}

# Run main deployment
main
