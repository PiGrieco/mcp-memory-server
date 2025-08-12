#!/bin/bash

# Backup Script for MCP Memory Server
# Automated backup of data, configuration, and logs

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
BACKUP_DIR="$PROJECT_ROOT/backups"
LOG_FILE="$PROJECT_ROOT/logs/backup.log"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
BACKUP_NAME="mcp_memory_backup_$TIMESTAMP"

# Backup retention (days)
RETENTION_DAYS=30

# Function to log messages
log_message() {
    echo -e "$1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $2" >> "$LOG_FILE"
}

# Function to create backup directory
create_backup_dir() {
    local backup_path="$BACKUP_DIR/$BACKUP_NAME"
    mkdir -p "$backup_path"
    log_message "${BLUE}📁${NC} Created backup directory: $backup_path" "Created backup directory: $backup_path"
    echo "$backup_path"
}

# Function to backup MongoDB
backup_mongodb() {
    local backup_path=$1
    local mongo_backup_dir="$backup_path/mongodb"
    
    log_message "${BLUE}🗄️${NC} Starting MongoDB backup..." "Starting MongoDB backup"
    
    mkdir -p "$mongo_backup_dir"
    
    if command -v mongodump &> /dev/null; then
        if mongodump --out "$mongo_backup_dir" --quiet; then
            log_message "${GREEN}✓${NC} MongoDB backup completed successfully" "MongoDB backup completed successfully"
            
            # Create backup info
            {
                echo "MongoDB Backup Information"
                echo "========================="
                echo "Backup Date: $(date)"
                echo "Backup Location: $mongo_backup_dir"
                echo "Database: mcp_memory"
                echo "Collections:"
                ls -la "$mongo_backup_dir/mcp_memory/" 2>/dev/null || echo "  No collections found"
                echo ""
            } > "$mongo_backup_dir/backup_info.txt"
            
        else
            log_message "${RED}✗${NC} MongoDB backup failed" "MongoDB backup failed"
            return 1
        fi
    else
        log_message "${YELLOW}⚠${NC} mongodump not available, skipping MongoDB backup" "mongodump not available"
    fi
}

# Function to backup Redis
backup_redis() {
    local backup_path=$1
    local redis_backup_dir="$backup_path/redis"
    
    log_message "${BLUE}🗄️${NC} Starting Redis backup..." "Starting Redis backup"
    
    mkdir -p "$redis_backup_dir"
    
    if command -v redis-cli &> /dev/null; then
        # Save Redis data
        if redis-cli SAVE >/dev/null 2>&1; then
            # Copy dump.rdb
            local redis_dump="/var/lib/redis/dump.rdb"
            if [ -f "$redis_dump" ]; then
                cp "$redis_dump" "$redis_backup_dir/"
                log_message "${GREEN}✓${NC} Redis backup completed successfully" "Redis backup completed successfully"
            else
                log_message "${YELLOW}⚠${NC} Redis dump file not found" "Redis dump file not found"
            fi
        else
            log_message "${RED}✗${NC} Redis backup failed" "Redis backup failed"
            return 1
        fi
        
        # Create backup info
        {
            echo "Redis Backup Information"
            echo "======================="
            echo "Backup Date: $(date)"
            echo "Backup Location: $redis_backup_dir"
            echo "Redis Info:"
            redis-cli INFO 2>/dev/null | head -20 || echo "  Redis info not available"
            echo ""
        } > "$redis_backup_dir/backup_info.txt"
        
    else
        log_message "${YELLOW}⚠${NC} redis-cli not available, skipping Redis backup" "redis-cli not available"
    fi
}

# Function to backup configuration files
backup_config() {
    local backup_path=$1
    local config_backup_dir="$backup_path/config"
    
    log_message "${BLUE}⚙️${NC} Starting configuration backup..." "Starting configuration backup"
    
    mkdir -p "$config_backup_dir"
    
    # Copy configuration files
    local config_files=(
        "$PROJECT_ROOT/config/settings.yaml"
        "$PROJECT_ROOT/config/cursor_config.json"
        "$PROJECT_ROOT/config/claude_config.json"
        "$PROJECT_ROOT/env.example"
        "$PROJECT_ROOT/.env"
    )
    
    local copied_count=0
    for config_file in "${config_files[@]}"; do
        if [ -f "$config_file" ]; then
            cp "$config_file" "$config_backup_dir/"
            copied_count=$((copied_count + 1))
        fi
    done
    
    log_message "${GREEN}✓${NC} Configuration backup completed ($copied_count files)" "Configuration backup completed ($copied_count files)"
    
    # Create backup info
    {
        echo "Configuration Backup Information"
        echo "==============================="
        echo "Backup Date: $(date)"
        echo "Backup Location: $config_backup_dir"
        echo "Files backed up:"
        ls -la "$config_backup_dir/" 2>/dev/null || echo "  No files found"
        echo ""
    } > "$config_backup_dir/backup_info.txt"
}

# Function to backup logs
backup_logs() {
    local backup_path=$1
    local logs_backup_dir="$backup_path/logs"
    
    log_message "${BLUE}📋${NC} Starting logs backup..." "Starting logs backup"
    
    mkdir -p "$logs_backup_dir"
    
    # Copy log files
    local log_files=(
        "$PROJECT_ROOT/logs/mcp_memory.log"
        "$PROJECT_ROOT/logs/server.log"
        "$PROJECT_ROOT/logs/error.log"
        "$PROJECT_ROOT/logs/health_check.log"
        "$PROJECT_ROOT/logs/backup.log"
    )
    
    local copied_count=0
    for log_file in "${log_files[@]}"; do
        if [ -f "$log_file" ]; then
            cp "$log_file" "$logs_backup_dir/"
            copied_count=$((copied_count + 1))
        fi
    done
    
    log_message "${GREEN}✓${NC} Logs backup completed ($copied_count files)" "Logs backup completed ($copied_count files)"
    
    # Create backup info
    {
        echo "Logs Backup Information"
        echo "======================"
        echo "Backup Date: $(date)"
        echo "Backup Location: $logs_backup_dir"
        echo "Files backed up:"
        ls -la "$logs_backup_dir/" 2>/dev/null || echo "  No files found"
        echo ""
    } > "$logs_backup_dir/backup_info.txt"
}

# Function to backup data directory
backup_data() {
    local backup_path=$1
    local data_backup_dir="$backup_path/data"
    
    log_message "${BLUE}📊${NC} Starting data backup..." "Starting data backup"
    
    mkdir -p "$data_backup_dir"
    
    # Copy data directory
    if [ -d "$PROJECT_ROOT/data" ]; then
        cp -r "$PROJECT_ROOT/data/"* "$data_backup_dir/" 2>/dev/null || true
        log_message "${GREEN}✓${NC} Data backup completed" "Data backup completed"
    else
        log_message "${YELLOW}⚠${NC} Data directory not found" "Data directory not found"
    fi
    
    # Create backup info
    {
        echo "Data Backup Information"
        echo "======================"
        echo "Backup Date: $(date)"
        echo "Backup Location: $data_backup_dir"
        echo "Data size: $(du -sh "$data_backup_dir" 2>/dev/null || echo "Unknown")"
        echo "Files backed up:"
        find "$data_backup_dir" -type f | wc -l 2>/dev/null || echo "0"
        echo ""
    } > "$data_backup_dir/backup_info.txt"
}

# Function to backup exports
backup_exports() {
    local backup_path=$1
    local exports_backup_dir="$backup_path/exports"
    
    log_message "${BLUE}📤${NC} Starting exports backup..." "Starting exports backup"
    
    mkdir -p "$exports_backup_dir"
    
    # Copy exports directory
    if [ -d "$PROJECT_ROOT/exports" ]; then
        cp -r "$PROJECT_ROOT/exports/"* "$exports_backup_dir/" 2>/dev/null || true
        log_message "${GREEN}✓${NC} Exports backup completed" "Exports backup completed"
    else
        log_message "${YELLOW}⚠${NC} Exports directory not found" "Exports directory not found"
    fi
    
    # Create backup info
    {
        echo "Exports Backup Information"
        echo "========================="
        echo "Backup Date: $(date)"
        echo "Backup Location: $exports_backup_dir"
        echo "Exports size: $(du -sh "$exports_backup_dir" 2>/dev/null || echo "Unknown")"
        echo "Files backed up:"
        find "$exports_backup_dir" -type f | wc -l 2>/dev/null || echo "0"
        echo ""
    } > "$exports_backup_dir/backup_info.txt"
}

# Function to create backup archive
create_archive() {
    local backup_path=$1
    
    log_message "${BLUE}📦${NC} Creating backup archive..." "Creating backup archive"
    
    local archive_name="$BACKUP_NAME.tar.gz"
    local archive_path="$BACKUP_DIR/$archive_name"
    
    # Create tar archive
    if tar -czf "$archive_path" -C "$BACKUP_DIR" "$BACKUP_NAME"; then
        log_message "${GREEN}✓${NC} Backup archive created: $archive_path" "Backup archive created: $archive_path"
        
        # Calculate archive size
        local archive_size=$(du -h "$archive_path" | cut -f1)
        log_message "${BLUE}📏${NC} Archive size: $archive_size" "Archive size: $archive_size"
        
        # Remove temporary directory
        rm -rf "$backup_path"
        log_message "${BLUE}🧹${NC} Cleaned up temporary files" "Cleaned up temporary files"
        
        echo "$archive_path"
    else
        log_message "${RED}✗${NC} Failed to create backup archive" "Failed to create backup archive"
        return 1
    fi
}

# Function to clean old backups
cleanup_old_backups() {
    log_message "${BLUE}🧹${NC} Cleaning up old backups..." "Cleaning up old backups"
    
    local deleted_count=0
    
    # Find and delete old backup files
    while IFS= read -r -d '' file; do
        if [ -f "$file" ]; then
            rm "$file"
            deleted_count=$((deleted_count + 1))
            log_message "${BLUE}🗑️${NC} Deleted old backup: $(basename "$file")" "Deleted old backup: $(basename "$file")"
        fi
    done < <(find "$BACKUP_DIR" -name "mcp_memory_backup_*.tar.gz" -mtime +$RETENTION_DAYS -print0 2>/dev/null)
    
    log_message "${GREEN}✓${NC} Cleanup completed ($deleted_count files deleted)" "Cleanup completed ($deleted_count files deleted)"
}

# Function to list backups
list_backups() {
    log_message "${BLUE}📋${NC} Listing available backups..." "Listing available backups"
    
    echo ""
    echo "Available Backups:"
    echo "=================="
    
    if [ -d "$BACKUP_DIR" ]; then
        local backup_count=0
        while IFS= read -r -d '' file; do
            if [ -f "$file" ]; then
                local filename=$(basename "$file")
                local size=$(du -h "$file" | cut -f1)
                local date=$(stat -c %y "$file" 2>/dev/null || echo "Unknown")
                echo "  $filename ($size) - $date"
                backup_count=$((backup_count + 1))
            fi
        done < <(find "$BACKUP_DIR" -name "mcp_memory_backup_*.tar.gz" -print0 2>/dev/null | sort -z)
        
        if [ $backup_count -eq 0 ]; then
            echo "  No backups found"
        else
            echo ""
            echo "Total backups: $backup_count"
        fi
    else
        echo "  Backup directory not found"
    fi
}

# Function to restore backup
restore_backup() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        log_message "${RED}✗${NC} No backup file specified" "No backup file specified"
        return 1
    fi
    
    local backup_path="$BACKUP_DIR/$backup_file"
    
    if [ ! -f "$backup_path" ]; then
        log_message "${RED}✗${NC} Backup file not found: $backup_path" "Backup file not found: $backup_path"
        return 1
    fi
    
    log_message "${BLUE}🔄${NC} Starting backup restoration..." "Starting backup restoration"
    
    # Create temporary directory for extraction
    local temp_dir="$BACKUP_DIR/restore_temp_$TIMESTAMP"
    mkdir -p "$temp_dir"
    
    # Extract backup
    if tar -xzf "$backup_path" -C "$temp_dir"; then
        log_message "${GREEN}✓${NC} Backup extracted successfully" "Backup extracted successfully"
        
        # Find the extracted directory
        local extracted_dir=$(find "$temp_dir" -maxdepth 1 -type d -name "mcp_memory_backup_*" | head -1)
        
        if [ -n "$extracted_dir" ]; then
            log_message "${BLUE}📁${NC} Restoring from: $extracted_dir" "Restoring from: $extracted_dir"
            
            # Restore configuration
            if [ -d "$extracted_dir/config" ]; then
                cp -r "$extracted_dir/config/"* "$PROJECT_ROOT/config/" 2>/dev/null || true
                log_message "${GREEN}✓${NC} Configuration restored" "Configuration restored"
            fi
            
            # Restore data
            if [ -d "$extracted_dir/data" ]; then
                cp -r "$extracted_dir/data/"* "$PROJECT_ROOT/data/" 2>/dev/null || true
                log_message "${GREEN}✓${NC} Data restored" "Data restored"
            fi
            
            # Restore exports
            if [ -d "$extracted_dir/exports" ]; then
                cp -r "$extracted_dir/exports/"* "$PROJECT_ROOT/exports/" 2>/dev/null || true
                log_message "${GREEN}✓${NC} Exports restored" "Exports restored"
            fi
            
            log_message "${GREEN}✓${NC} Backup restoration completed" "Backup restoration completed"
        else
            log_message "${RED}✗${NC} Could not find extracted backup directory" "Could not find extracted backup directory"
            return 1
        fi
        
        # Clean up temporary directory
        rm -rf "$temp_dir"
        log_message "${BLUE}🧹${NC} Cleaned up temporary files" "Cleaned up temporary files"
        
    else
        log_message "${RED}✗${NC} Failed to extract backup" "Failed to extract backup"
        return 1
    fi
}

# Main backup function
main_backup() {
    log_message "${BLUE}💾${NC} Starting MCP Memory Server Backup..." "Starting backup"
    log_message "${BLUE}⏰${NC} Timestamp: $TIMESTAMP" "Timestamp: $TIMESTAMP"
    echo ""
    
    # Create backup directory
    local backup_path=$(create_backup_dir)
    
    # Perform backups
    backup_mongodb "$backup_path"
    echo ""
    
    backup_redis "$backup_path"
    echo ""
    
    backup_config "$backup_path"
    echo ""
    
    backup_logs "$backup_path"
    echo ""
    
    backup_data "$backup_path"
    echo ""
    
    backup_exports "$backup_path"
    echo ""
    
    # Create archive
    local archive_path=$(create_archive "$backup_path")
    echo ""
    
    # Cleanup old backups
    cleanup_old_backups
    echo ""
    
    # Create backup summary
    {
        echo "MCP Memory Server Backup Summary"
        echo "==============================="
        echo "Backup Date: $(date)"
        echo "Backup Name: $BACKUP_NAME"
        echo "Archive: $(basename "$archive_path")"
        echo "Size: $(du -h "$archive_path" | cut -f1)"
        echo "Location: $archive_path"
        echo ""
        echo "Components Backed Up:"
        echo "  - MongoDB database"
        echo "  - Redis data"
        echo "  - Configuration files"
        echo "  - Log files"
        echo "  - Data directory"
        echo "  - Exports directory"
        echo ""
        echo "Retention: $RETENTION_DAYS days"
        echo ""
    } > "$BACKUP_DIR/backup_summary_$TIMESTAMP.txt"
    
    log_message "${GREEN}🎉${NC} Backup completed successfully!" "Backup completed successfully"
    log_message "${BLUE}📁${NC} Backup location: $archive_path" "Backup location: $archive_path"
}

# Handle command line arguments
case "${1:-}" in
    "list")
        list_backups
        ;;
    "restore")
        restore_backup "$2"
        ;;
    "cleanup")
        cleanup_old_backups
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  (no args)  Run full backup"
        echo "  list       List available backups"
        echo "  restore <file>  Restore from backup file"
        echo "  cleanup    Clean up old backups"
        echo "  help       Show this help"
        echo ""
        echo "Examples:"
        echo "  $0                    # Run full backup"
        echo "  $0 list              # List backups"
        echo "  $0 restore backup.tar.gz  # Restore backup"
        echo "  $0 cleanup           # Clean old backups"
        ;;
    *)
        main_backup
        ;;
esac 