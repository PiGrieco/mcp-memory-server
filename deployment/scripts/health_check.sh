#!/bin/bash

# Health Check Script for MCP Memory Server
# Monitors all services and reports status

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_ROOT/logs/health_check.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Services to check
SERVICES=(
    "mcp-memory-server:8000"
    "mongodb:27017"
    "redis:6379"
    "nginx:80"
    "prometheus:9090"
    "grafana:3000"
)

# Health check endpoints
HEALTH_ENDPOINTS=(
    "http://localhost:8000/health"
    "http://localhost:8000/status"
    "http://localhost:8000/metrics"
)

# Function to log messages
log_message() {
    echo -e "$1"
    echo "[$TIMESTAMP] $2" >> "$LOG_FILE"
}

# Function to check if a service is running
check_service() {
    local service=$1
    local host=$(echo $service | cut -d: -f1)
    local port=$(echo $service | cut -d: -f2)
    
    if timeout 5 bash -c "</dev/tcp/$host/$port" 2>/dev/null; then
        log_message "${GREEN}✓${NC} Service $service is running" "Service $service is running"
        return 0
    else
        log_message "${RED}✗${NC} Service $service is not responding" "Service $service is not responding"
        return 1
    fi
}

# Function to check HTTP endpoint
check_http_endpoint() {
    local url=$1
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$response" = "200" ]; then
        log_message "${GREEN}✓${NC} HTTP endpoint $url is healthy (HTTP $response)" "HTTP endpoint $url is healthy (HTTP $response)"
        return 0
    else
        log_message "${RED}✗${NC} HTTP endpoint $url is unhealthy (HTTP $response)" "HTTP endpoint $url is unhealthy (HTTP $response)"
        return 1
    fi
}

# Function to check Docker containers
check_docker_containers() {
    log_message "${BLUE}🔍${NC} Checking Docker containers..." "Checking Docker containers"
    
    local containers=(
        "mcp-memory-server"
        "mongodb"
        "redis"
        "nginx"
        "prometheus"
        "grafana"
    )
    
    local all_healthy=true
    
    for container in "${containers[@]}"; do
        if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "$container.*Up"; then
            log_message "${GREEN}✓${NC} Container $container is running" "Container $container is running"
        else
            log_message "${RED}✗${NC} Container $container is not running" "Container $container is not running"
            all_healthy=false
        fi
    done
    
    return $([ "$all_healthy" = true ] && echo 0 || echo 1)
}

# Function to check system resources
check_system_resources() {
    log_message "${BLUE}🔍${NC} Checking system resources..." "Checking system resources"
    
    # CPU usage
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    if (( $(echo "$cpu_usage < 80" | bc -l) )); then
        log_message "${GREEN}✓${NC} CPU usage: ${cpu_usage}%" "CPU usage: ${cpu_usage}%"
    else
        log_message "${YELLOW}⚠${NC} CPU usage: ${cpu_usage}% (high)" "CPU usage: ${cpu_usage}% (high)"
    fi
    
    # Memory usage
    local mem_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    if (( $(echo "$mem_usage < 80" | bc -l) )); then
        log_message "${GREEN}✓${NC} Memory usage: ${mem_usage}%" "Memory usage: ${mem_usage}%"
    else
        log_message "${YELLOW}⚠${NC} Memory usage: ${mem_usage}% (high)" "Memory usage: ${mem_usage}% (high)"
    fi
    
    # Disk usage
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    if [ "$disk_usage" -lt 80 ]; then
        log_message "${GREEN}✓${NC} Disk usage: ${disk_usage}%" "Disk usage: ${disk_usage}%"
    else
        log_message "${YELLOW}⚠${NC} Disk usage: ${disk_usage}% (high)" "Disk usage: ${disk_usage}% (high)"
    fi
}

# Function to check logs for errors
check_logs() {
    log_message "${BLUE}🔍${NC} Checking recent logs for errors..." "Checking recent logs for errors"
    
    local log_files=(
        "$PROJECT_ROOT/logs/mcp_memory.log"
        "$PROJECT_ROOT/logs/server.log"
        "$PROJECT_ROOT/logs/error.log"
    )
    
    local error_count=0
    
    for log_file in "${log_files[@]}"; do
        if [ -f "$log_file" ]; then
            local recent_errors=$(tail -100 "$log_file" | grep -i "error\|exception\|failed" | wc -l)
            if [ "$recent_errors" -gt 0 ]; then
                log_message "${YELLOW}⚠${NC} Found $recent_errors errors in $log_file" "Found $recent_errors errors in $log_file"
                error_count=$((error_count + recent_errors))
            else
                log_message "${GREEN}✓${NC} No recent errors in $log_file" "No recent errors in $log_file"
            fi
        else
            log_message "${YELLOW}⚠${NC} Log file $log_file not found" "Log file $log_file not found"
        fi
    done
    
    return $([ "$error_count" -eq 0 ] && echo 0 || echo 1)
}

# Function to check database connectivity
check_database() {
    log_message "${BLUE}🔍${NC} Checking database connectivity..." "Checking database connectivity"
    
    # Check MongoDB
    if command -v mongo &> /dev/null; then
        if mongo --eval "db.runCommand('ping')" --quiet >/dev/null 2>&1; then
            log_message "${GREEN}✓${NC} MongoDB is accessible" "MongoDB is accessible"
        else
            log_message "${RED}✗${NC} MongoDB is not accessible" "MongoDB is not accessible"
            return 1
        fi
    else
        log_message "${YELLOW}⚠${NC} MongoDB client not available" "MongoDB client not available"
    fi
    
    # Check Redis
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping >/dev/null 2>&1; then
            log_message "${GREEN}✓${NC} Redis is accessible" "Redis is accessible"
        else
            log_message "${RED}✗${NC} Redis is not accessible" "Redis is not accessible"
            return 1
        fi
    else
        log_message "${YELLOW}⚠${NC} Redis client not available" "Redis client not available"
    fi
}

# Function to generate health report
generate_report() {
    local report_file="$PROJECT_ROOT/logs/health_report_$(date +%Y%m%d_%H%M%S).txt"
    
    log_message "${BLUE}📊${NC} Generating health report..." "Generating health report"
    
    {
        echo "MCP Memory Server Health Report"
        echo "Generated: $TIMESTAMP"
        echo "=================================="
        echo ""
        
        echo "System Information:"
        echo "  Hostname: $(hostname)"
        echo "  OS: $(uname -s) $(uname -r)"
        echo "  Uptime: $(uptime)"
        echo ""
        
        echo "Docker Status:"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "  Docker not available"
        echo ""
        
        echo "Service Status:"
        for service in "${SERVICES[@]}"; do
            if check_service "$service" >/dev/null 2>&1; then
                echo "  ✓ $service"
            else
                echo "  ✗ $service"
            fi
        done
        echo ""
        
        echo "HTTP Endpoints:"
        for endpoint in "${HEALTH_ENDPOINTS[@]}"; do
            local response=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint" 2>/dev/null || echo "000")
            echo "  $endpoint: HTTP $response"
        done
        echo ""
        
        echo "System Resources:"
        echo "  CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
        echo "  Memory: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')"
        echo "  Disk: $(df / | tail -1 | awk '{print $5}')"
        echo ""
        
    } > "$report_file"
    
    log_message "${GREEN}✓${NC} Health report saved to $report_file" "Health report saved to $report_file"
}

# Main health check function
main_health_check() {
    log_message "${BLUE}🏥${NC} Starting MCP Memory Server Health Check..." "Starting health check"
    log_message "${BLUE}⏰${NC} Timestamp: $TIMESTAMP" "Timestamp: $TIMESTAMP"
    echo ""
    
    local exit_code=0
    
    # Check Docker containers
    if ! check_docker_containers; then
        exit_code=1
    fi
    echo ""
    
    # Check services
    log_message "${BLUE}🔍${NC} Checking service connectivity..." "Checking service connectivity"
    for service in "${SERVICES[@]}"; do
        if ! check_service "$service"; then
            exit_code=1
        fi
    done
    echo ""
    
    # Check HTTP endpoints
    log_message "${BLUE}🔍${NC} Checking HTTP endpoints..." "Checking HTTP endpoints"
    for endpoint in "${HEALTH_ENDPOINTS[@]}"; do
        if ! check_http_endpoint "$endpoint"; then
            exit_code=1
        fi
    done
    echo ""
    
    # Check database connectivity
    if ! check_database; then
        exit_code=1
    fi
    echo ""
    
    # Check system resources
    check_system_resources
    echo ""
    
    # Check logs
    if ! check_logs; then
        exit_code=1
    fi
    echo ""
    
    # Generate report
    generate_report
    echo ""
    
    # Final status
    if [ $exit_code -eq 0 ]; then
        log_message "${GREEN}🎉${NC} All health checks passed!" "All health checks passed"
    else
        log_message "${RED}❌${NC} Some health checks failed!" "Some health checks failed"
    fi
    
    return $exit_code
}

# Handle command line arguments
case "${1:-}" in
    "report")
        generate_report
        ;;
    "services")
        for service in "${SERVICES[@]}"; do
            check_service "$service"
        done
        ;;
    "system")
        check_system_resources
        ;;
    "logs")
        check_logs
        ;;
    "docker")
        check_docker_containers
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  (no args)  Run full health check"
        echo "  report     Generate health report"
        echo "  services   Check service connectivity"
        echo "  system     Check system resources"
        echo "  logs       Check logs for errors"
        echo "  docker     Check Docker containers"
        echo "  help       Show this help"
        ;;
    *)
        main_health_check
        ;;
esac 