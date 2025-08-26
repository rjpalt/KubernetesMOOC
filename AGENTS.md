# Project Instructions

## Overview
This is a Kubernetes MOOC course project featuring a microservices Todo application. The project demonstrates containerized application deployment, service communication, and cloud-native development practices using modern tooling and architectural patterns.

## Architecture Philosophy
- **Microservices**: Loosely coupled services with clear boundaries
- **Container-First**: All services designed for containerized deployment
- **Cloud-Native**: Kubernetes-ready with proper resource management
- **API-Driven**: RESTful services with clear interface contracts
- **Async-First**: Non-blocking operations throughout the stack

## Technology Stack
- **Language**: Python 3.13+ for all application services
- **Dependency Management**: UV (universal Python package manager)
- **Web Framework**: FastAPI for all HTTP services
- **Database**: PostgreSQL with async SQLAlchemy
- **Frontend**: Server-side rendering with HTMX for interactivity
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose (local) and Kubernetes (production)

## Development Standards

### Code Quality
- **Linting & Formatting**: Ruff for consistent code style
- **Line Length**: 120 characters maximum
- **String Style**: Double quotes throughout
- **Import Organization**: Combine imports, use trailing commas
- **Async Patterns**: Prefer async/await for I/O operations

### Project Organization
- **Service Isolation**: Each service in its own directory with independent dependencies
- **Shared Configuration**: Common settings in root-level configuration files
- **Test Co-location**: Tests alongside source code in each service
- **Documentation**: README files at service level, architectural docs at project level

### Container Standards
- **Networking**: Custom Docker networks for service communication
- **Health Checks**: All services must implement health endpoints
- **Volume Management**: Persistent data and artifacts properly mounted
- **Environment Configuration**: 12-factor app principles with environment variables

### Testing Philosophy
- **Test Pyramid**: Unit tests (fast), integration tests (realistic), E2E tests (comprehensive)
- **Async Testing**: Use pytest-asyncio for testing async code
- **Coverage**: Maintain high test coverage with meaningful assertions
- **Test Isolation**: Each test should be independent and repeatable
- **Multiple Environments**: Tests should work in both local and containerized environments

### Build & Deployment Patterns
- **Infrastructure as Code**: Kubernetes manifests with Kustomize overlays
- **Environment Separation**: Development, staging, and production configurations
- **Resource Management**: Proper CPU/memory requests and limits
- **Automation**: Makefile targets for common development tasks
- **Script Organization**: All automation scripts in dedicated `scripts/` directory

### Documentation Standards
- **Clarity**: Write for developers who are new to the project
- **Consistency**: Follow established patterns and conventions
- **Completeness**: Include setup, usage, and troubleshooting information
- **No Duplication**: Check existing documentation before adding new content
- **Professional Tone**: Avoid emojis and casual language in technical documentation

### Development Workflow
- **Feature Branches**: Isolate development work in dedicated branches
- **Error Handling**: Always implement proper error handling and cleanup
- **Exit Codes**: Scripts must propagate exit codes correctly
- **Resource Cleanup**: Always cleanup Docker containers and temporary resources
- **Incremental Development**: Build and test incrementally, not in large batches

### Common Patterns
- **Configuration**: Environment-based configuration with sensible defaults
- **Logging**: Structured logging with appropriate levels for debugging
- **Error Handling**: Use HTTP status codes and meaningful error messages
- **Service Communication**: RESTful APIs with proper timeout and retry logic
- **State Management**: Stateless services with externalized data persistence

## Implementation Guidelines

When working on this project:
1. **Follow the Architecture**: Respect service boundaries and communication patterns
2. **Use Standard Tools**: UV for Python dependencies, Ruff for code quality
3. **Test Thoroughly**: Unit, integration, and E2E tests as appropriate
4. **Document Changes**: Update relevant documentation when adding features
5. **Containerize Properly**: Ensure all components work in Docker environments
6. **Think Cloud-Native**: Design for scalability, observability, and resilience
