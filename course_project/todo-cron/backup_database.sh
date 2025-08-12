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
    
    # Debug: Show all environment variables for troubleshooting
    log_debug "=== All Environment Variables ==="
    env | sort | while read -r line; do
        log_debug "  $line"
    done
    
    # Debug: Show specifically Azure-related environment variables
    log_debug "=== Azure Environment Variables ==="
    log_debug "  AZURE_STORAGE_ACCOUNT_NAME=${AZURE_STORAGE_ACCOUNT_NAME:-<NOT_SET>}"
    log_debug "  AZURE_STORAGE_ACCOUNT_KEY=<HIDDEN>"
    log_debug "  AZURE_STORAGE_ACCOUNT=${AZURE_STORAGE_ACCOUNT:-<NOT_SET>}"
    log_debug "  AZURE_STORAGE_CONTAINER=${AZURE_STORAGE_CONTAINER:-<NOT_SET>}"
    
    # Debug: Show PostgreSQL-related environment variables
    log_debug "=== PostgreSQL Environment Variables ==="
    log_debug "  POSTGRES_HOST=${POSTGRES_HOST}"
    log_debug "  POSTGRES_PORT=${POSTGRES_PORT}"
    log_debug "  POSTGRES_DB=${POSTGRES_DB}"
    log_debug "  POSTGRES_USER=${POSTGRES_USER}"
    log_debug "  POSTGRES_PASSWORD=<HIDDEN>"
    
    # Debug: Show Kubernetes-related environment variables
    log_debug "=== Kubernetes Environment Variables ==="
    log_debug "  KUBERNETES_SERVICE_HOST=${KUBERNETES_SERVICE_HOST:-<NOT_SET>}"
    log_debug "  KUBERNETES_SERVICE_PORT=${KUBERNETES_SERVICE_PORT:-<NOT_SET>}"
    log_debug "  HOSTNAME=${HOSTNAME:-<NOT_SET>}"
    log_debug "  POD_NAME=${POD_NAME:-<NOT_SET>}"
    log_debug "  POD_NAMESPACE=${POD_NAMESPACE:-<NOT_SET>}"
    
    if [ -z "$AZURE_STORAGE_ACCOUNT" ]; then
        log_error "AZURE_STORAGE_ACCOUNT environment variable is required"
        return 1
    fi
    
    # Check if required tools are available
    log_debug "Checking for pg_dump availability..."
    if ! command -v pg_dump >/dev/null 2>&1; then
        log_error "pg_dump is not available. Please install PostgreSQL client tools."
        return 1
    else
        log_debug "pg_dump found: $(which pg_dump)"
        log_debug "pg_dump version: $(pg_dump --version)"
    fi
    
    if ! command -v az >/dev/null 2>&1; then
        log_error "Azure CLI is not available. Please install Azure CLI."
        return 1
    fi
    
    # Debug: Show Azure CLI version
    log_debug "Azure CLI version:"
    az version --output table 2>/dev/null | while read -r line; do
        log_debug "  $line"
    done
    
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
    log_debug "Executing pg_dump command..."
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
        --file="$backup_path" 2>&1; then
        
        log_info "Database backup created successfully: $backup_filename"
        log_debug "Backup size: $(du -h "$backup_path" | cut -f1)"
        log_debug "Backup file contents preview:"
        log_debug "$(head -10 "$backup_path" 2>/dev/null || echo 'Unable to preview backup file')"
        echo "$backup_path"
        return 0
    else
        local exit_code=$?
        log_error "Failed to create database backup (exit code: $exit_code)"
        log_debug "Checking if partial backup file exists..."
        if [ -f "$backup_path" ]; then
            log_debug "Partial backup file size: $(du -h "$backup_path" | cut -f1)"
            log_debug "Partial backup file preview:"
            log_debug "$(head -10 "$backup_path" 2>/dev/null || echo 'Unable to read partial backup file')"
            rm -f "$backup_path"
            log_debug "Cleaned up partial backup file"
        else
            log_debug "No backup file was created"
        fi
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
    log_debug "Local file: $backup_file"
    log_debug "Local file size: $(du -h "$backup_file" | cut -f1)"
    
    # Ensure we're authenticated before uploading
    if ! azure_login; then
        log_error "Failed to authenticate with Azure before upload"
        return 1
    fi
    
    # Debug: Test upload with verbose output first
    log_debug "Attempting blob upload with verbose logging..."
    
    # Upload backup to Azure Blob Storage using storage account key
    if az storage blob upload \
        --account-name "$AZURE_STORAGE_ACCOUNT" \
        --container-name "$AZURE_STORAGE_CONTAINER" \
        --name "$filename" \
        --file "$backup_file" \
        --overwrite \
        --output none 2>/dev/null; then
        
        log_info "Backup uploaded successfully to Azure Blob Storage"
        
        # Debug: Verify the upload by checking blob properties
        log_debug "Verifying uploaded blob properties:"
        az storage blob show \
            --account-name "$AZURE_STORAGE_ACCOUNT" \
            --container-name "$AZURE_STORAGE_CONTAINER" \
            --name "$filename" \
            --output table 2>/dev/null | while read -r line; do
            log_debug "  $line"
        done
        
        log_debug "Blob URL: https://${AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/${AZURE_STORAGE_CONTAINER}/${filename}"
        return 0
    else
        log_error "Failed to upload backup to Azure Blob Storage"
        
        # Debug: Show detailed upload error
        log_debug "Detailed upload error:"
        az storage blob upload \
            --account-name "$AZURE_STORAGE_ACCOUNT" \
            --container-name "$AZURE_STORAGE_CONTAINER" \
            --name "$filename" \
            --file "$backup_file" \
            --overwrite \
            --debug 2>&1 | while read -r line; do
            log_debug "  $line"
        done
        
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

# Function to authenticate with Azure using storage account key (simple approach)
azure_login() {
    log_info "Setting up Azure storage authentication using account key"
    
    # Check that required environment variables are set
    if [ -z "${AZURE_STORAGE_ACCOUNT_NAME:-}" ]; then
        log_error "AZURE_STORAGE_ACCOUNT_NAME environment variable not set"
        return 1
    fi
    
    if [ -z "${AZURE_STORAGE_ACCOUNT_KEY:-}" ]; then
        log_error "AZURE_STORAGE_ACCOUNT_KEY environment variable not set"
        return 1
    fi
    
    # Set Azure CLI environment variables for storage account key authentication
    export AZURE_STORAGE_ACCOUNT="$AZURE_STORAGE_ACCOUNT_NAME"
    export AZURE_STORAGE_KEY="$AZURE_STORAGE_ACCOUNT_KEY"
    
    log_info "Azure storage authentication configured using account key"
    log_debug "Storage account: $AZURE_STORAGE_ACCOUNT_NAME"
    log_debug "Using storage account key authentication (key length: ${#AZURE_STORAGE_ACCOUNT_KEY} characters)"
    
    return 0
}

# Function to test Azure storage access using account key
test_azure_access() {
    log_info "Testing Azure storage access"
    
    # First, set up authentication
    if ! azure_login; then
        log_error "Failed to set up Azure authentication"
        return 1
    fi
    
    # Test storage account access
    log_debug "Testing storage account access: $AZURE_STORAGE_ACCOUNT"
    log_debug "Testing container: $AZURE_STORAGE_CONTAINER"
    
    # Test container access with detailed error output
    if az storage container show \
        --account-name "$AZURE_STORAGE_ACCOUNT" \
        --name "$AZURE_STORAGE_CONTAINER" \
        --output none 2>/dev/null; then
        
        log_info "Azure storage access test passed"
        
        # Debug: Show container properties
        log_debug "Container properties:"
        az storage container show \
            --account-name "$AZURE_STORAGE_ACCOUNT" \
            --name "$AZURE_STORAGE_CONTAINER" \
            --output table 2>/dev/null | while read -r line; do
            log_debug "  $line"
        done
        
        return 0
    else
        log_error "Cannot access storage container. Please check storage account name and container."
        log_debug "Detailed storage access error:"
        az storage container show \
            --account-name "$AZURE_STORAGE_ACCOUNT" \
            --name "$AZURE_STORAGE_CONTAINER" \
            --output table 2>&1 | while read -r line; do
            log_debug "  $line"
        done
        
        # Debug: Try to list available containers
        log_debug "Attempting to list available containers in storage account:"
        az storage container list \
            --account-name "$AZURE_STORAGE_ACCOUNT" \
            --output table 2>/dev/null | while read -r line; do
            log_debug "  $line"
        done
        
        return 1
    fi
}

# Main backup execution
main() {
    log_info "Starting database backup process"
    log_debug "Environment: $POSTGRES_USER@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB -> $AZURE_STORAGE_ACCOUNT/$AZURE_STORAGE_CONTAINER"
    
    # Debug: Show execution context
    log_debug "=== Execution Context ==="
    log_debug "Script started at: $(date)"
    log_debug "Script arguments: $*"
    log_debug "Working directory: $(pwd)"
    log_debug "Script location: ${BASH_SOURCE[0]:-$0}"
    log_debug "Process ID: $$"
    log_debug "User ID: $(id -u)"
    log_debug "Group ID: $(id -g)"
    
    # Debug: Show filesystem information
    log_debug "=== Filesystem Information ==="
    log_debug "Available disk space in /tmp:"
    df -h /tmp 2>/dev/null | while read -r line; do
        log_debug "  $line"
    done
    
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
    log_debug "Script completed at: $(date)"
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
    
    # Run the backup loop immediately
    while true; do
        log_info "Running scheduled backup"
        main
        log_info "Backup completed, sleeping for ${BACKUP_INTERVAL} seconds"
        sleep "$BACKUP_INTERVAL"
    done
fi

# Run main function (single execution - used by Kubernetes CronJob)
main "$@"
