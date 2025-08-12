#!/bin/bash
set -euo pipefail

# Configuration from environment variables
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_DB="${POSTGRES_DB:-todoapp}"
POSTGRES_USER="${POSTGRES_USER:-todouser}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-todopass}"
AZURE_STORAGE_ACCOUNT="${AZURE_STORAGE_ACCOUNT:-}"
AZURE_STORAGE_CONTAINER="${AZURE_STORAGE_CONTAINER:-database-backups}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"
BACKUP_INTERVAL="${BACKUP_INTERVAL:-60}"  # Interval in seconds for local testing

# Normalize log level to uppercase
LOG_LEVEL=$(echo "$LOG_LEVEL" | tr '[:lower:]' '[:upper:]')

# Logging function
log() {
    local level="$1"
    shift
    echo "$(date '+%Y-%m-%d %H:%M:%S') [$level] $*" >&2
}

log_info() {
    case "$LOG_LEVEL" in
        DEBUG|INFO) log "INFO" "$@" ;;
    esac
}

log_error() {
    log "ERROR" "$@"
}

log_debug() {
    case "$LOG_LEVEL" in
        DEBUG) log "DEBUG" "$@" ;;
    esac
}

# Function to validate required environment variables
validate_config() {
    log_debug "Validating configuration"
    
    if [ -z "$AZURE_STORAGE_ACCOUNT" ]; then
        log_error "AZURE_STORAGE_ACCOUNT environment variable is required"
        return 1
    fi
    
    # Check if required tools are available
    if ! command -v pg_dump >/dev/null 2>&1; then
        log_error "pg_dump is not available. Please install PostgreSQL client tools."
        return 1
    fi
    
    if ! command -v az >/dev/null 2>&1; then
        log_error "Azure CLI is not available. Please install Azure CLI."
        return 1
    fi
    
    log_debug "Configuration validation passed"
    return 0
}

# Function to create database backup
create_backup() {
    log_info "Starting database backup"
    
    # Generate backup filename with timestamp
    local timestamp
    timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_filename="todoapp_backup_${timestamp}.sql"
    local backup_path="/tmp/${backup_filename}"
    
    log_debug "Backup file: $backup_path"
    log_debug "Database: $POSTGRES_USER@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB"
    
    # Set PGPASSWORD for non-interactive authentication
    export PGPASSWORD="$POSTGRES_PASSWORD"
    
    # Create database backup using pg_dump
    if pg_dump \
        --host="$POSTGRES_HOST" \
        --port="$POSTGRES_PORT" \
        --username="$POSTGRES_USER" \
        --dbname="$POSTGRES_DB" \
        --no-password \
        --verbose \
        --clean \
        --if-exists \
        --create \
        --format=plain \
        --file="$backup_path" 2>/dev/null; then
        
        log_info "Database backup created successfully: $backup_filename"
        log_debug "Backup size: $(du -h "$backup_path" | cut -f1)"
        echo "$backup_path"
        return 0
    else
        log_error "Failed to create database backup"
        # Clean up partial backup file
        [ -f "$backup_path" ] && rm -f "$backup_path"
        return 1
    fi
}

# Function to upload backup to Azure Blob Storage
upload_to_azure() {
    local backup_file="$1"
    local filename
    filename=$(basename "$backup_file")
    
    log_info "Uploading backup to Azure Blob Storage"
    log_debug "Storage account: $AZURE_STORAGE_ACCOUNT"
    log_debug "Container: $AZURE_STORAGE_CONTAINER"
    log_debug "Blob name: $filename"
    
    # Upload backup to Azure Blob Storage
    if az storage blob upload \
        --account-name "$AZURE_STORAGE_ACCOUNT" \
        --container-name "$AZURE_STORAGE_CONTAINER" \
        --name "$filename" \
        --file "$backup_file" \
        --overwrite \
        --output none 2>/dev/null; then
        
        log_info "Backup uploaded successfully to Azure Blob Storage"
        log_debug "Blob URL: https://${AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/${AZURE_STORAGE_CONTAINER}/${filename}"
        return 0
    else
        log_error "Failed to upload backup to Azure Blob Storage"
        return 1
    fi
}

# Function to clean up local backup file
cleanup_local_backup() {
    local backup_file="$1"
    
    log_debug "Cleaning up local backup file: $backup_file"
    
    if [ -f "$backup_file" ]; then
        rm -f "$backup_file"
        log_debug "Local backup file removed"
    fi
}

# Function to test database connectivity
test_db_connection() {
    log_info "Testing database connectivity"
    
    export PGPASSWORD="$POSTGRES_PASSWORD"
    
    if pg_isready \
        --host="$POSTGRES_HOST" \
        --port="$POSTGRES_PORT" \
        --username="$POSTGRES_USER" \
        --dbname="$POSTGRES_DB" >/dev/null 2>&1; then
        
        log_info "Database connection test passed"
        return 0
    else
        log_error "Database connection test failed"
        return 1
    fi
}

# Function to test Azure authentication and storage access
test_azure_access() {
    log_info "Testing Azure storage access"
    
    # Test Azure CLI authentication
    if ! az account show --output none 2>/dev/null; then
        log_error "Azure CLI authentication failed. Please run 'az login' or configure managed identity."
        return 1
    fi
    
    # Test storage account access
    if az storage container show \
        --account-name "$AZURE_STORAGE_ACCOUNT" \
        --name "$AZURE_STORAGE_CONTAINER" \
        --output none 2>/dev/null; then
        
        log_info "Azure storage access test passed"
        return 0
    else
        log_error "Cannot access storage container. Please check storage account name and container."
        return 1
    fi
}

# Main backup execution
main() {
    log_info "Starting database backup process"
    log_debug "Environment: $POSTGRES_USER@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB -> $AZURE_STORAGE_ACCOUNT/$AZURE_STORAGE_CONTAINER"
    
    # Validate configuration
    if ! validate_config; then
        log_error "Configuration validation failed"
        exit 1
    fi
    
    # Test database connectivity
    if ! test_db_connection; then
        log_error "Database connectivity test failed"
        exit 1
    fi
    
    # Test Azure access
    if ! test_azure_access; then
        log_error "Azure access test failed"
        exit 1
    fi
    
    # Create backup
    local backup_file
    if ! backup_file=$(create_backup); then
        log_error "Failed to create database backup"
        exit 1
    fi
    
    # Upload to Azure
    if ! upload_to_azure "$backup_file"; then
        log_error "Failed to upload backup to Azure"
        cleanup_local_backup "$backup_file"
        exit 1
    fi
    
    # Clean up local file
    cleanup_local_backup "$backup_file"
    
    log_info "Database backup process completed successfully"
}

# Health check mode for testing
if [ "${1:-}" = "health" ]; then
    log_info "Health check: Testing database and Azure connectivity"
    
    if ! validate_config; then
        log_error "Configuration validation failed"
        exit 1
    fi
    
    if ! test_db_connection; then
        log_error "Database connectivity test failed"
        exit 1
    fi
    
    if ! test_azure_access; then
        log_error "Azure access test failed"
        exit 1
    fi
    
    log_info "Health check passed"
    exit 0
fi

# Loop mode for local testing (Kubernetes uses CronJob scheduling instead)
if [ "${1:-}" = "loop" ]; then
    log_info "Starting backup loop mode (interval: ${BACKUP_INTERVAL}s)"
    log_info "Note: In Kubernetes, use CronJob scheduling instead of loop mode"
    
    while true; do
        log_info "Running scheduled backup"
        main
        log_info "Backup completed, sleeping for ${BACKUP_INTERVAL} seconds"
        sleep "$BACKUP_INTERVAL"
    done
fi

# Run main function (single execution - used by Kubernetes CronJob)
main "$@"
