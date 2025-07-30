#!/bin/bash
set -euo pipefail

# Configuration from environment variables
TODO_BACKEND_URL="${TODO_BACKEND_URL:-http://localhost:8000}"
WIKIPEDIA_RANDOM_URL="${WIKIPEDIA_RANDOM_URL:-https://en.wikipedia.org/wiki/Special:Random}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"

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

# Function to get random Wikipedia article URL
get_random_wikipedia_url() {
    log_debug "Fetching random Wikipedia article URL from: $WIKIPEDIA_RANDOM_URL"
    
    # Follow redirect and extract the final URL
    local final_url
    final_url=$(curl -s -L -w '%{url_effective}' -o /dev/null "$WIKIPEDIA_RANDOM_URL" 2>/dev/null)
    
    if [ -z "$final_url" ]; then
        log_error "Failed to get random Wikipedia URL"
        return 1
    fi
    
    log_debug "Random Wikipedia URL: $final_url"
    echo "$final_url"
}

# Function to create todo item
create_todo() {
    local wikipedia_url="$1"
    local todo_text="Read $wikipedia_url"
    local backend_endpoint="$TODO_BACKEND_URL/todos"
    
    log_info "Creating todo: $todo_text"
    log_debug "Backend endpoint: $backend_endpoint"
    
    # Create JSON payload
    local json_payload
    json_payload=$(cat <<EOF
{
    "text": "$todo_text"
}
EOF
)
    
    log_debug "JSON payload: $json_payload"
    
    # Send POST request to create todo
    local response
    local http_code
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d "$json_payload" \
        "$backend_endpoint" 2>/dev/null)
    
    http_code=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    response_body=$(echo "$response" | sed 's/HTTPSTATUS:[0-9]*$//')
    
    log_debug "HTTP response code: $http_code"
    log_debug "Response body: $response_body"
    
    if [ "$http_code" -eq 201 ]; then
        log_info "Successfully created todo item"
        log_debug "Todo response: $response_body"
        return 0
    else
        log_error "Failed to create todo. HTTP code: $http_code, Response: $response_body"
        return 1
    fi
}

# Main execution
main() {
    log_info "Starting Wikipedia todo creator"
    log_debug "Environment: TODO_BACKEND_URL=$TODO_BACKEND_URL"
    
    # Get random Wikipedia URL
    local wikipedia_url
    if ! wikipedia_url=$(get_random_wikipedia_url); then
        log_error "Failed to get random Wikipedia URL"
        exit 1
    fi
    
    # Create todo item
    if ! create_todo "$wikipedia_url"; then
        log_error "Failed to create todo item"
        exit 1
    fi
    
    log_info "Wikipedia todo creator completed successfully"
}

# Health check mode for testing
if [ "${1:-}" = "health" ]; then
    log_info "Health check: Testing connectivity to backend"
    
    health_endpoint="$TODO_BACKEND_URL/be-health"
    if curl -s -f "$health_endpoint" > /dev/null 2>&1; then
        log_info "Backend health check passed"
        exit 0
    else
        log_error "Backend health check failed"
        exit 1
    fi
fi

# Run main function
main "$@"
