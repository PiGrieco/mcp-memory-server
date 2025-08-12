#!/bin/bash

# Monitoring Script for MCP Memory Server
# Collects metrics and sends alerts

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
LOG_FILE="$PROJECT_ROOT/logs/monitoring.log"
METRICS_FILE="$PROJECT_ROOT/logs/metrics.json"
ALERTS_FILE="$PROJECT_ROOT/logs/alerts.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Thresholds for alerts
CPU_THRESHOLD=80
MEMORY_THRESHOLD=80
DISK_THRESHOLD=80
ERROR_RATE_THRESHOLD=5
RESPONSE_TIME_THRESHOLD=1000

# Function to log messages
log_message() {
    echo -e "$1"
    echo "[$TIMESTAMP] $2" >> "$LOG_FILE"
}

# Function to collect system metrics
collect_system_metrics() {
    log_message "${BLUE}📊${NC} Collecting system metrics..." "Collecting system metrics"
    
    # CPU usage
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    
    # Memory usage
    local mem_total=$(free | grep Mem | awk '{print $2}')
    local mem_used=$(free | grep Mem | awk '{print $3}')
    local mem_usage=$(echo "scale=2; $mem_used * 100 / $mem_total" | bc -l)
    
    # Disk usage
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    
    # Load average
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    
    # Network stats
    local network_rx=$(cat /proc/net/dev | grep eth0 | awk '{print $2}' 2>/dev/null || echo "0")
    local network_tx=$(cat /proc/net/dev | grep eth0 | awk '{print $10}' 2>/dev/null || echo "0")
    
    # Create metrics JSON
    cat > "$METRICS_FILE" << EOF
{
    "timestamp": "$TIMESTAMP",
    "system": {
        "cpu_usage": $cpu_usage,
        "memory_usage": $mem_usage,
        "disk_usage": $disk_usage,
        "load_average": $load_avg,
        "network_rx": $network_rx,
        "network_tx": $network_tx
    }
}
EOF
    
    log_message "${GREEN}✓${NC} System metrics collected" "System metrics collected"
}

# Function to collect application metrics
collect_app_metrics() {
    log_message "${BLUE}📊${NC} Collecting application metrics..." "Collecting application metrics"
    
    # Check if application is running
    local app_status="unknown"
    local app_response_time="0"
    local app_error_rate="0"
    
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/health" >/dev/null 2>&1; then
        app_status="healthy"
        
        # Measure response time
        app_response_time=$(curl -s -o /dev/null -w "%{time_total}" "http://localhost:8000/health" 2>/dev/null || echo "0")
        app_response_time=$(echo "$app_response_time * 1000" | bc -l 2>/dev/null || echo "0")
        
        # Get error rate from metrics endpoint
        local error_count=$(curl -s "http://localhost:8000/metrics" 2>/dev/null | grep "mcp_memory_errors_total" | awk '{print $2}' || echo "0")
        local total_requests=$(curl -s "http://localhost:8000/metrics" 2>/dev/null | grep "mcp_memory_requests_total" | awk '{print $2}' || echo "1")
        app_error_rate=$(echo "scale=2; $error_count * 100 / $total_requests" | bc -l 2>/dev/null || echo "0")
    else
        app_status="unhealthy"
    fi
    
    # Update metrics file
    local temp_metrics=$(mktemp)
    jq --arg status "$app_status" \
       --arg response_time "$app_response_time" \
       --arg error_rate "$app_error_rate" \
       '.application = {
           "status": $status,
           "response_time_ms": $response_time,
           "error_rate_percent": $error_rate
       }' "$METRICS_FILE" > "$temp_metrics"
    mv "$temp_metrics" "$METRICS_FILE"
    
    log_message "${GREEN}✓${NC} Application metrics collected" "Application metrics collected"
}

# Function to collect database metrics
collect_db_metrics() {
    log_message "${BLUE}📊${NC} Collecting database metrics..." "Collecting database metrics"
    
    local mongo_status="unknown"
    local redis_status="unknown"
    local mongo_connections="0"
    local redis_memory="0"
    
    # Check MongoDB
    if command -v mongo &> /dev/null; then
        if mongo --eval "db.runCommand('ping')" --quiet >/dev/null 2>&1; then
            mongo_status="healthy"
            mongo_connections=$(mongo --eval "db.serverStatus().connections.current" --quiet 2>/dev/null || echo "0")
        else
            mongo_status="unhealthy"
        fi
    fi
    
    # Check Redis
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping >/dev/null 2>&1; then
            redis_status="healthy"
            redis_memory=$(redis-cli info memory | grep "used_memory:" | cut -d: -f2 2>/dev/null || echo "0")
        else
            redis_status="unhealthy"
        fi
    fi
    
    # Update metrics file
    local temp_metrics=$(mktemp)
    jq --arg mongo_status "$mongo_status" \
       --arg redis_status "$redis_status" \
       --arg mongo_connections "$mongo_connections" \
       --arg redis_memory "$redis_memory" \
       '.databases = {
           "mongodb": {
               "status": $mongo_status,
               "connections": $mongo_connections
           },
           "redis": {
               "status": $redis_status,
               "memory_used": $redis_memory
           }
       }' "$METRICS_FILE" > "$temp_metrics"
    mv "$temp_metrics" "$METRICS_FILE"
    
    log_message "${GREEN}✓${NC} Database metrics collected" "Database metrics collected"
}

# Function to check thresholds and generate alerts
check_alerts() {
    log_message "${BLUE}🚨${NC} Checking for alerts..." "Checking for alerts"
    
    local alerts=()
    
    # Read metrics
    if [ -f "$METRICS_FILE" ]; then
        local cpu_usage=$(jq -r '.system.cpu_usage' "$METRICS_FILE" 2>/dev/null || echo "0")
        local memory_usage=$(jq -r '.system.memory_usage' "$METRICS_FILE" 2>/dev/null || echo "0")
        local disk_usage=$(jq -r '.system.disk_usage' "$METRICS_FILE" 2>/dev/null || echo "0")
        local app_status=$(jq -r '.application.status' "$METRICS_FILE" 2>/dev/null || echo "unknown")
        local response_time=$(jq -r '.application.response_time_ms' "$METRICS_FILE" 2>/dev/null || echo "0")
        local error_rate=$(jq -r '.application.error_rate_percent' "$METRICS_FILE" 2>/dev/null || echo "0")
        
        # Check CPU usage
        if (( $(echo "$cpu_usage > $CPU_THRESHOLD" | bc -l) )); then
            alerts+=("HIGH_CPU: CPU usage is ${cpu_usage}% (threshold: ${CPU_THRESHOLD}%)")
        fi
        
        # Check memory usage
        if (( $(echo "$memory_usage > $MEMORY_THRESHOLD" | bc -l) )); then
            alerts+=("HIGH_MEMORY: Memory usage is ${memory_usage}% (threshold: ${MEMORY_THRESHOLD}%)")
        fi
        
        # Check disk usage
        if [ "$disk_usage" -gt "$DISK_THRESHOLD" ]; then
            alerts+=("HIGH_DISK: Disk usage is ${disk_usage}% (threshold: ${DISK_THRESHOLD}%)")
        fi
        
        # Check application status
        if [ "$app_status" != "healthy" ]; then
            alerts+=("APP_UNHEALTHY: Application status is $app_status")
        fi
        
        # Check response time
        if (( $(echo "$response_time > $RESPONSE_TIME_THRESHOLD" | bc -l) )); then
            alerts+=("HIGH_RESPONSE_TIME: Response time is ${response_time}ms (threshold: ${RESPONSE_TIME_THRESHOLD}ms)")
        fi
        
        # Check error rate
        if (( $(echo "$error_rate > $ERROR_RATE_THRESHOLD" | bc -l) )); then
            alerts+=("HIGH_ERROR_RATE: Error rate is ${error_rate}% (threshold: ${ERROR_RATE_THRESHOLD}%)")
        fi
    fi
    
    # Log alerts
    if [ ${#alerts[@]} -gt 0 ]; then
        log_message "${RED}🚨${NC} Alerts detected:" "Alerts detected"
        for alert in "${alerts[@]}"; do
            log_message "${RED}  ⚠${NC} $alert" "Alert: $alert"
            echo "[$TIMESTAMP] ALERT: $alert" >> "$ALERTS_FILE"
        done
    else
        log_message "${GREEN}✓${NC} No alerts detected" "No alerts detected"
    fi
}

# Function to send notifications
send_notifications() {
    log_message "${BLUE}📧${NC} Sending notifications..." "Sending notifications"
    
    # Check if there are recent alerts
    local recent_alerts=$(tail -10 "$ALERTS_FILE" 2>/dev/null | grep "$(date '+%Y-%m-%d')" | wc -l)
    
    if [ "$recent_alerts" -gt 0 ]; then
        log_message "${YELLOW}⚠${NC} $recent_alerts recent alerts found" "$recent_alerts recent alerts found"
        
        # Send email notification (if configured)
        if [ -n "$SMTP_HOST" ] && [ -n "$SMTP_USER" ] && [ -n "$SMTP_PASS" ]; then
            send_email_notification
        fi
        
        # Send webhook notification (if configured)
        if [ -n "$WEBHOOK_URL" ]; then
            send_webhook_notification
        fi
    else
        log_message "${GREEN}✓${NC} No notifications needed" "No notifications needed"
    fi
}

# Function to send email notification
send_email_notification() {
    log_message "${BLUE}📧${NC} Sending email notification..." "Sending email notification"
    
    # Create email content
    local email_content=$(cat << EOF
Subject: MCP Memory Server Alert

MCP Memory Server Monitoring Alert

Timestamp: $TIMESTAMP
Recent Alerts: $recent_alerts

Please check the server status and logs for more details.

Best regards,
MCP Memory Server Monitoring
EOF
)
    
    # Send email (simplified - would need proper SMTP configuration)
    echo "$email_content" | mail -s "MCP Memory Server Alert" "$NOTIFICATION_EMAIL" 2>/dev/null || true
    
    log_message "${GREEN}✓${NC} Email notification sent" "Email notification sent"
}

# Function to send webhook notification
send_webhook_notification() {
    log_message "${BLUE}🌐${NC} Sending webhook notification..." "Sending webhook notification"
    
    # Create webhook payload
    local webhook_payload=$(cat << EOF
{
    "timestamp": "$TIMESTAMP",
    "service": "mcp-memory-server",
    "alerts": $recent_alerts,
    "status": "alert",
    "message": "MCP Memory Server monitoring detected $recent_alerts recent alerts"
}
EOF
)
    
    # Send webhook
    curl -s -X POST "$WEBHOOK_URL" \
         -H "Content-Type: application/json" \
         -d "$webhook_payload" >/dev/null 2>&1 || true
    
    log_message "${GREEN}✓${NC} Webhook notification sent" "Webhook notification sent"
}

# Function to generate monitoring report
generate_report() {
    log_message "${BLUE}📊${NC} Generating monitoring report..." "Generating monitoring report"
    
    local report_file="$PROJECT_ROOT/logs/monitoring_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "MCP Memory Server Monitoring Report"
        echo "==================================="
        echo "Generated: $TIMESTAMP"
        echo ""
        
        echo "System Metrics:"
        if [ -f "$METRICS_FILE" ]; then
            echo "  CPU Usage: $(jq -r '.system.cpu_usage' "$METRICS_FILE")%"
            echo "  Memory Usage: $(jq -r '.system.memory_usage' "$METRICS_FILE")%"
            echo "  Disk Usage: $(jq -r '.system.disk_usage' "$METRICS_FILE")%"
            echo "  Load Average: $(jq -r '.system.load_average' "$METRICS_FILE")"
        else
            echo "  Metrics not available"
        fi
        echo ""
        
        echo "Application Metrics:"
        if [ -f "$METRICS_FILE" ]; then
            echo "  Status: $(jq -r '.application.status' "$METRICS_FILE")"
            echo "  Response Time: $(jq -r '.application.response_time_ms' "$METRICS_FILE")ms"
            echo "  Error Rate: $(jq -r '.application.error_rate_percent' "$METRICS_FILE")%"
        else
            echo "  Metrics not available"
        fi
        echo ""
        
        echo "Database Metrics:"
        if [ -f "$METRICS_FILE" ]; then
            echo "  MongoDB Status: $(jq -r '.databases.mongodb.status' "$METRICS_FILE")"
            echo "  MongoDB Connections: $(jq -r '.databases.mongodb.connections' "$METRICS_FILE")"
            echo "  Redis Status: $(jq -r '.databases.redis.status' "$METRICS_FILE")"
            echo "  Redis Memory: $(jq -r '.databases.redis.memory_used' "$METRICS_FILE") bytes"
        else
            echo "  Metrics not available"
        fi
        echo ""
        
        echo "Recent Alerts:"
        if [ -f "$ALERTS_FILE" ]; then
            tail -10 "$ALERTS_FILE" | while read -r line; do
                echo "  $line"
            done
        else
            echo "  No alerts found"
        fi
        echo ""
        
    } > "$report_file"
    
    log_message "${GREEN}✓${NC} Monitoring report saved to $report_file" "Monitoring report saved to $report_file"
}

# Function to clean old logs
cleanup_logs() {
    log_message "${BLUE}🧹${NC} Cleaning up old logs..." "Cleaning up old logs"
    
    # Remove old metrics files (keep last 7 days)
    find "$PROJECT_ROOT/logs" -name "metrics_*.json" -mtime +7 -delete 2>/dev/null || true
    
    # Remove old monitoring reports (keep last 30 days)
    find "$PROJECT_ROOT/logs" -name "monitoring_report_*.txt" -mtime +30 -delete 2>/dev/null || true
    
    # Truncate alerts log if too large (keep last 1000 lines)
    if [ -f "$ALERTS_FILE" ] && [ $(wc -l < "$ALERTS_FILE") -gt 1000 ]; then
        tail -1000 "$ALERTS_FILE" > "${ALERTS_FILE}.tmp" && mv "${ALERTS_FILE}.tmp" "$ALERTS_FILE"
    fi
    
    log_message "${GREEN}✓${NC} Log cleanup completed" "Log cleanup completed"
}

# Main monitoring function
main_monitoring() {
    log_message "${BLUE}📊${NC} Starting MCP Memory Server Monitoring..." "Starting monitoring"
    log_message "${BLUE}⏰${NC} Timestamp: $TIMESTAMP" "Timestamp: $TIMESTAMP"
    echo ""
    
    # Collect metrics
    collect_system_metrics
    echo ""
    
    collect_app_metrics
    echo ""
    
    collect_db_metrics
    echo ""
    
    # Check for alerts
    check_alerts
    echo ""
    
    # Send notifications
    send_notifications
    echo ""
    
    # Generate report
    generate_report
    echo ""
    
    # Cleanup old logs
    cleanup_logs
    echo ""
    
    log_message "${GREEN}🎉${NC} Monitoring completed successfully!" "Monitoring completed successfully"
}

# Handle command line arguments
case "${1:-}" in
    "metrics")
        collect_system_metrics
        collect_app_metrics
        collect_db_metrics
        ;;
    "alerts")
        check_alerts
        ;;
    "notifications")
        send_notifications
        ;;
    "report")
        generate_report
        ;;
    "cleanup")
        cleanup_logs
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  (no args)  Run full monitoring"
        echo "  metrics     Collect metrics only"
        echo "  alerts      Check for alerts only"
        echo "  notifications  Send notifications only"
        echo "  report      Generate monitoring report"
        echo "  cleanup     Clean up old logs"
        echo "  help        Show this help"
        ;;
    *)
        main_monitoring
        ;;
esac 