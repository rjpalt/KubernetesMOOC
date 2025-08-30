# Todo Cron Service

A multi-purpose CronJob service that provides:
1. Wikipedia todo creation - creates todo items with random Wikipedia articles. This job runs once daily.
2. Database backup - backs up the todo database to Azure Blob Storage.

## Scripts

### create_wikipedia_todo.sh
Creates todo items with random Wikipedia articles to read.

**Environment Variables:**
| Variable | Default | Description |
|----------|---------|-------------|
| `TODO_BACKEND_URL` | `http://localhost:8000` | URL of the todo-backend service |
| `WIKIPEDIA_RANDOM_URL` | `https://en.wikipedia.org/wiki/Special:Random` | Wikipedia random article endpoint |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, ERROR) |

### backup_database.sh
Creates database backups and uploads them to Azure Blob Storage.

**Azure Authentication:**
- **Current (Temporary)**: Uses Azure Storage Account key authentication via Kubernetes Secret
- **⚠️ Security Compromise**: This is a temporary workaround for Azure Workload Identity webhook compatibility issues
- **Planned**: Revert to Azure Workload Identity during infrastructure revamp (see `REVAMP_ROADMAP.md`)

**Environment Variables:**
| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_HOST` | *See environment config* | PostgreSQL server hostname |
| `POSTGRES_PORT` | `5432` | PostgreSQL server port |
| `POSTGRES_DB` | `todoapp` | Database name |
| `POSTGRES_USER` | *From Key Vault/env* | Database username |
| `POSTGRES_PASSWORD` | *From Key Vault/env* | Database password |
| `AZURE_STORAGE_ACCOUNT` | `kubemoocbackups` | Azure storage account name (secured with Azure AD auth) |
| `AZURE_STORAGE_CONTAINER` | `database-backups` | Blob container name (production: database-backups, feature: feature-backups, local: local-backups) |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, ERROR) |

**Azure Resources:**
| Environment | Managed Identity | Client ID | Storage Container | Service Account |
|-------------|------------------|-----------|-------------------|-----------------|
| Production | `backup-production-identity` | `50f96678-064c-463a-a3e3-2297a3b557f1` | `database-backups` | `system:serviceaccount:default:backup-serviceaccount` |
| Feature branches | `backup-development-identity` | `640dd28d-3d3e-416d-aaf6-85c52a1f0db5` | `feature-backups` | `system:serviceaccount:backup-shared:backup-serviceaccount` |
| Local development | *Azure CLI* | *Your user* | `local-backups` | *N/A* |

## Local Development

### Prerequisites
- bash, curl (for Wikipedia script)
- PostgreSQL client tools, Azure CLI (for backup script)
- Running todo-backend service (for Wikipedia script)
- PostgreSQL database (for backup script)
- Azure storage account and container (for backup script)

### Testing the Wikipedia Script
```bash
# Make script executable
chmod +x create_wikipedia_todo.sh

# Test with todo-backend running
TODO_BACKEND_URL=http://localhost:8000 LOG_LEVEL=DEBUG ./create_wikipedia_todo.sh

# Health check
TODO_BACKEND_URL=http://localhost:8000 ./create_wikipedia_todo.sh health
```

### Testing the Backup Script

**Prerequisites:**
- PostgreSQL 17 client tools: `brew install postgresql@17`
- Azure CLI: `brew install azure-cli` 
- Azure authentication: `az login`
- Storage Blob Data Contributor role on kubemoocbackups storage account
- Running PostgreSQL database: `docker compose up postgres_prod -d`

**Setup:**
```bash
# Add PostgreSQL 17 tools to PATH (required for each session)
export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"

# Authenticate with Azure (if not already done)
az login

# Set environment variables for local testing
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=todoapp
export POSTGRES_USER=todouser
export POSTGRES_PASSWORD=todopass
export AZURE_STORAGE_ACCOUNT=kubemoocbackups
export AZURE_STORAGE_CONTAINER=local-backups
export LOG_LEVEL=DEBUG
```

**Testing:**
```bash
cd course_project/todo-cron

# Make script executable
chmod +x backup_database.sh

# Health check (tests all connectivity)
./backup_database.sh health

# Single backup test
./backup_database.sh
```

**Note:** Docker-based local testing is not recommended due to Azure CLI authentication complexity. Use direct local execution instead.

## Docker Image

The Docker image includes both scripts and their dependencies:
- Base image: Alpine Linux 3.19 (~7MB)
- With curl, bash, PostgreSQL client, Azure CLI: ~150MB total
- Non-root user for security
- Both executable scripts available

### Build
```bash
docker build -t todo-cron:latest .
```

### Run Wikipedia Script
```bash
docker run --rm \
  -e TODO_BACKEND_URL=http://host.docker.internal:8000 \
  -e LOG_LEVEL=DEBUG \
  todo-cron:latest /usr/local/bin/create_wikipedia_todo.sh
```

**Note:** For backup script testing, use local execution instead of Docker due to Azure authentication complexity.

## Error Handling

The service handles various error scenarios:
- Network connectivity issues
- Backend service unavailability
- Invalid Wikipedia responses
- HTTP errors from todo-backend

All errors are logged with appropriate detail for debugging.

## Security

### Container Security
- Runs as non-root user (UID 1001)
- Minimal attack surface (only bash, curl, PostgreSQL client, Azure CLI)
- No sensitive data in environment variables
- Secure defaults for logging

### Azure Authentication
- **Production**: Passwordless authentication via Azure Workload Identity
- **Feature environments**: Shared development identity with proper scoping
- **Local development**: Standard Azure CLI authentication
- **No stored credentials**: All authentication uses Azure AD tokens
- **Principle of least privilege**: Each identity has minimal required permissions

### Storage Access
- Azure AD authentication enforced (`allowSharedKeyAccess: false`)
- Container-level permissions (no account-wide access)
- Environment-specific containers prevent cross-environment data access
