#!/bin/bash

# Environment Management Script for MCP Memory Server
# Manages different environment configurations

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
CONFIG_DIR="$PROJECT_ROOT/config"
ENVIRONMENTS_DIR="$CONFIG_DIR/environments"
CURRENT_ENV_FILE="$CONFIG_DIR/current_environment.txt"

# Available environments
ENVIRONMENTS=("development" "testing" "staging" "production")

# Function to log messages
log_message() {
    echo -e "$1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [command] [environment]"
    echo ""
    echo "Commands:"
    echo "  list                    List available environments"
    echo "  current                 Show current environment"
    echo "  switch <environment>    Switch to specified environment"
    echo "  validate <environment>  Validate environment configuration"
    echo "  backup                  Backup current environment"
    echo "  restore <backup_file>   Restore environment from backup"
    echo "  diff <env1> <env2>      Show differences between environments"
    echo "  create <name>           Create new environment configuration"
    echo "  delete <name>           Delete environment configuration"
    echo "  help                    Show this help"
    echo ""
    echo "Environments:"
    for env in "${ENVIRONMENTS[@]}"; do
        echo "  $env"
    done
    echo ""
    echo "Examples:"
    echo "  $0 list"
    echo "  $0 switch development"
    echo "  $0 validate production"
    echo "  $0 diff development production"
}

# Function to list environments
list_environments() {
    log_message "${BLUE}📋${NC} Available environments:"
    echo ""
    
    for env in "${ENVIRONMENTS[@]}"; do
        local env_file="$ENVIRONMENTS_DIR/$env.yaml"
        if [ -f "$env_file" ]; then
            local current_env=$(cat "$CURRENT_ENV_FILE" 2>/dev/null || echo "none")
            if [ "$env" = "$current_env" ]; then
                log_message "${GREEN}  ✓ $env (current)${NC}"
            else
                log_message "  - $env"
            fi
        else
            log_message "${RED}  ✗ $env (missing)${NC}"
        fi
    done
    
    echo ""
    log_message "${BLUE}📁${NC} Environment files location: $ENVIRONMENTS_DIR"
}

# Function to show current environment
show_current_environment() {
    if [ -f "$CURRENT_ENV_FILE" ]; then
        local current_env=$(cat "$CURRENT_ENV_FILE")
        log_message "${BLUE}🎯${NC} Current environment: ${GREEN}$current_env${NC}"
        
        # Show environment details
        local env_file="$ENVIRONMENTS_DIR/$current_env.yaml"
        if [ -f "$env_file" ]; then
            echo ""
            log_message "${BLUE}📄${NC} Environment file: $env_file"
            
            # Extract key information
            local server_name=$(grep "name:" "$env_file" | head -1 | sed 's/.*name: *"\([^"]*\)".*/\1/')
            local debug_mode=$(grep "debug:" "$env_file" | head -1 | sed 's/.*debug: *\([^#]*\).*/\1/')
            local log_level=$(grep "log_level:" "$env_file" | head -1 | sed 's/.*log_level: *"\([^"]*\)".*/\1/')
            
            echo ""
            log_message "${BLUE}⚙️${NC} Configuration:"
            echo "  Server Name: $server_name"
            echo "  Debug Mode: $debug_mode"
            echo "  Log Level: $log_level"
        else
            log_message "${RED}❌${NC} Environment file not found: $env_file"
        fi
    else
        log_message "${YELLOW}⚠${NC} No environment currently set"
        log_message "${BLUE}💡${NC} Use '$0 switch <environment>' to set an environment"
    fi
}

# Function to switch environment
switch_environment() {
    local target_env=$1
    
    if [ -z "$target_env" ]; then
        log_message "${RED}❌${NC} No environment specified"
        show_usage
        exit 1
    fi
    
    # Check if environment exists
    local env_file="$ENVIRONMENTS_DIR/$target_env.yaml"
    if [ ! -f "$env_file" ]; then
        log_message "${RED}❌${NC} Environment '$target_env' not found"
        log_message "${BLUE}💡${NC} Available environments:"
        for env in "${ENVIRONMENTS[@]}"; do
            echo "  - $env"
        done
        exit 1
    fi
    
    # Validate environment configuration
    if ! validate_environment "$target_env"; then
        log_message "${RED}❌${NC} Environment validation failed"
        exit 1
    fi
    
    # Backup current environment if exists
    if [ -f "$CURRENT_ENV_FILE" ]; then
        local current_env=$(cat "$CURRENT_ENV_FILE")
        if [ "$current_env" != "$target_env" ]; then
            backup_environment "$current_env"
        fi
    fi
    
    # Switch to new environment
    echo "$target_env" > "$CURRENT_ENV_FILE"
    
    # Copy environment file to main settings
    cp "$env_file" "$CONFIG_DIR/settings.yaml"
    
    log_message "${GREEN}✅${NC} Switched to environment: ${GREEN}$target_env${NC}"
    log_message "${BLUE}📄${NC} Configuration copied to: $CONFIG_DIR/settings.yaml"
    
    # Show environment details
    echo ""
    show_current_environment
}

# Function to validate environment
validate_environment() {
    local env_name=$1
    local env_file="$ENVIRONMENTS_DIR/$env_name.yaml"
    
    log_message "${BLUE}🔍${NC} Validating environment: $env_name"
    
    if [ ! -f "$env_file" ]; then
        log_message "${RED}❌${NC} Environment file not found: $env_file"
        return 1
    fi
    
    # Basic YAML validation
    if ! python3 -c "import yaml; yaml.safe_load(open('$env_file'))" 2>/dev/null; then
        log_message "${RED}❌${NC} Invalid YAML syntax in $env_file"
        return 1
    fi
    
    # Check required sections
    local required_sections=("server" "environment" "database" "embedding" "memory")
    local missing_sections=()
    
    for section in "${required_sections[@]}"; do
        if ! grep -q "^$section:" "$env_file"; then
            missing_sections+=("$section")
        fi
    done
    
    if [ ${#missing_sections[@]} -gt 0 ]; then
        log_message "${RED}❌${NC} Missing required sections: ${missing_sections[*]}"
        return 1
    fi
    
    # Environment-specific validations
    case "$env_name" in
        "production")
            # Production validations
            if grep -q "debug: true" "$env_file"; then
                log_message "${YELLOW}⚠${NC} Warning: Debug mode enabled in production"
            fi
            if ! grep -q "api_key_required: true" "$env_file"; then
                log_message "${YELLOW}⚠${NC} Warning: API key not required in production"
            fi
            ;;
        "testing")
            # Testing validations
            if ! grep -q "testing: true" "$env_file"; then
                log_message "${YELLOW}⚠${NC} Warning: Testing flag not set"
            fi
            ;;
    esac
    
    log_message "${GREEN}✅${NC} Environment validation passed"
    return 0
}

# Function to backup environment
backup_environment() {
    local env_name=$1
    local backup_dir="$PROJECT_ROOT/backups/environments"
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_file="$backup_dir/${env_name}_${timestamp}.yaml"
    
    mkdir -p "$backup_dir"
    
    if [ -f "$ENVIRONMENTS_DIR/$env_name.yaml" ]; then
        cp "$ENVIRONMENTS_DIR/$env_name.yaml" "$backup_file"
        log_message "${GREEN}✅${NC} Environment backed up: $backup_file"
    else
        log_message "${YELLOW}⚠${NC} No environment file to backup"
    fi
}

# Function to restore environment
restore_environment() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        log_message "${RED}❌${NC} No backup file specified"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_message "${RED}❌${NC} Backup file not found: $backup_file"
        exit 1
    fi
    
    # Extract environment name from backup file
    local env_name=$(basename "$backup_file" | cut -d'_' -f1)
    local target_file="$ENVIRONMENTS_DIR/$env_name.yaml"
    
    # Restore environment
    cp "$backup_file" "$target_file"
    log_message "${GREEN}✅${NC} Environment restored: $env_name"
    
    # Validate restored environment
    if validate_environment "$env_name"; then
        log_message "${GREEN}✅${NC} Restored environment is valid"
    else
        log_message "${RED}❌${NC} Restored environment validation failed"
        exit 1
    fi
}

# Function to show differences between environments
show_environment_diff() {
    local env1=$1
    local env2=$2
    
    if [ -z "$env1" ] || [ -z "$env2" ]; then
        log_message "${RED}❌${NC} Two environments must be specified"
        exit 1
    fi
    
    local file1="$ENVIRONMENTS_DIR/$env1.yaml"
    local file2="$ENVIRONMENTS_DIR/$env2.yaml"
    
    if [ ! -f "$file1" ]; then
        log_message "${RED}❌${NC} Environment file not found: $file1"
        exit 1
    fi
    
    if [ ! -f "$file2" ]; then
        log_message "${RED}❌${NC} Environment file not found: $file2"
        exit 1
    fi
    
    log_message "${BLUE}🔍${NC} Comparing environments: $env1 vs $env2"
    echo ""
    
    if command -v diff &> /dev/null; then
        diff -u "$file1" "$file2" || true
    else
        log_message "${YELLOW}⚠${NC} 'diff' command not available"
        log_message "${BLUE}💡${NC} Install diffutils to see differences"
    fi
}

# Function to create new environment
create_environment() {
    local env_name=$1
    
    if [ -z "$env_name" ]; then
        log_message "${RED}❌${NC} No environment name specified"
        exit 1
    fi
    
    local env_file="$ENVIRONMENTS_DIR/$env_name.yaml"
    
    if [ -f "$env_file" ]; then
        log_message "${RED}❌${NC} Environment '$env_name' already exists"
        exit 1
    fi
    
    # Create new environment based on development template
    cp "$ENVIRONMENTS_DIR/development.yaml" "$env_file"
    
    # Update environment name in the file
    sed -i.bak "s/name: \"MCP Memory Server (Development)\"/name: \"MCP Memory Server ($env_name)\"/" "$env_file"
    sed -i.bak "s/name: \"development\"/name: \"$env_name\"/" "$env_file"
    
    # Remove backup file
    rm -f "${env_file}.bak"
    
    log_message "${GREEN}✅${NC} Created new environment: $env_name"
    log_message "${BLUE}📄${NC} Environment file: $env_file"
    log_message "${BLUE}💡${NC} Edit the file to customize the configuration"
}

# Function to delete environment
delete_environment() {
    local env_name=$1
    
    if [ -z "$env_name" ]; then
        log_message "${RED}❌${NC} No environment name specified"
        exit 1
    fi
    
    # Prevent deletion of built-in environments
    case "$env_name" in
        "development"|"testing"|"staging"|"production")
            log_message "${RED}❌${NC} Cannot delete built-in environment: $env_name"
            exit 1
            ;;
    esac
    
    local env_file="$ENVIRONMENTS_DIR/$env_name.yaml"
    
    if [ ! -f "$env_file" ]; then
        log_message "${RED}❌${NC} Environment '$env_name' not found"
        exit 1
    fi
    
    # Check if it's the current environment
    if [ -f "$CURRENT_ENV_FILE" ]; then
        local current_env=$(cat "$CURRENT_ENV_FILE")
        if [ "$current_env" = "$env_name" ]; then
            log_message "${RED}❌${NC} Cannot delete current environment: $env_name"
            log_message "${BLUE}💡${NC} Switch to another environment first"
            exit 1
        fi
    fi
    
    # Backup before deletion
    backup_environment "$env_name"
    
    # Delete environment file
    rm "$env_file"
    
    log_message "${GREEN}✅${NC} Deleted environment: $env_name"
}

# Main function
main() {
    case "${1:-}" in
        "list")
            list_environments
            ;;
        "current")
            show_current_environment
            ;;
        "switch")
            switch_environment "$2"
            ;;
        "validate")
            validate_environment "$2"
            ;;
        "backup")
            if [ -f "$CURRENT_ENV_FILE" ]; then
                local current_env=$(cat "$CURRENT_ENV_FILE")
                backup_environment "$current_env"
            else
                log_message "${YELLOW}⚠${NC} No current environment to backup"
            fi
            ;;
        "restore")
            restore_environment "$2"
            ;;
        "diff")
            show_environment_diff "$2" "$3"
            ;;
        "create")
            create_environment "$2"
            ;;
        "delete")
            delete_environment "$2"
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            log_message "${RED}❌${NC} Unknown command: $1"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 