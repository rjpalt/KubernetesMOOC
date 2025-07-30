# Implementation Plan: Request Logging & Todo Character Limits

## Goal
Add comprehensive request logging and enforce 140-character limit for todos in the backend service, following TDD approach.

## Features to Implement

### 1. Request Logging
- Log every incoming request to todo-backend
- Include request details: method, path, headers, body, timestamp
- Log response details: status code, response time
- Use structured logging format for Grafana integration
- Log validation failures for monitoring

### 2. Todo Character Limit
- Enforce 140-character limit on todo text
- Return proper HTTP error for oversized todos
- Include validation in both model and API layers
- Ensure error messages are descriptive

## Current State Assessment

### Architecture Overview
- **todo-backend**: FastAPI service with async PostgreSQL
- **todo-app**: Frontend application
- **Testing**: 58/58 tests passing (unit + integration)
- **Test Structure**: Unit tests (models, service) + Integration tests (API endpoints)

### Existing Features ✅
- **Character Limit**: Already implemented! 140-char limit in TodoCreate, TodoUpdate, and Todo models
- **Model Validation**: Pydantic validation with proper error messages
- **API Validation**: FastAPI automatic validation returning HTTP 422 for invalid data
- **Basic Logging**: Structured logging in place, logs to stdout

### Existing Tests ✅
- **Unit Tests**: Character limit validation (tests/unit/test_models.py)
- **Integration Tests**: API validation errors (tests/integration/test_todo_endpoints.py)
- **Test Coverage**: 141+ character todos properly rejected with HTTP 422

### Missing Features ✅ COMPLETED
- [x] **Request Logging Middleware**: Comprehensive request/response logging implemented
- [x] **Structured Request Logs**: JSON format for Grafana monitoring 
- [x] **Error Classification**: All HTTP error types (422, 404, 4xx, 5xx) logged with categories

## Implementation Approach (TDD) ✅ COMPLETED

### Phase 1: Assessment & Test Planning ✅
- [x] Analyze current todo-backend code structure
- [x] Review existing validation and logging  
- [x] **DISCOVERY**: Character limit already implemented and tested!
- [x] **DISCOVERY**: Need request logging middleware, not validation

### Phase 2: Test Implementation ✅
- [x] Write tests for request logging middleware functionality
- [x] Write tests for structured log format (JSON for Grafana)
- [x] Write tests for comprehensive error classification (422, 404, 4xx, 5xx)
- [x] All tests initially failed (red phase achieved)

### Phase 3: Feature Implementation ✅
- [x] Implement request/response logging middleware in proper module structure
- [x] Add structured JSON logging configuration
- [x] Implement comprehensive error classification for monitoring
- [x] All tests now pass (green phase achieved)

### Phase 4: Verification ✅
- [x] Run full test suite (66/66 tests passing - added 8 new tests)
- [x] Test with curl for validation errors and successful requests
- [x] Verify JSON log format for Grafana parsing
- [x] Ensure clean module structure (middleware/request_logging.py)

### Phase 5: Integration Ready 🔄
- [ ] Test with Postman for complete validation documentation
- [ ] Update docker-compose configuration for log forwarding
- [ ] Prepare for Kubernetes deployment with log aggregation
- [ ] Document logging format for Grafana dashboard creation
- [x] **DISCOVERY**: Need request logging middleware, not validation

### Phase 2: Test Implementation ✅
- [x] Write tests for request logging middleware functionality
- [x] Write tests for structured log format (JSON for Grafana)
- [x] Write tests for validation failure logging
- [x] All tests fail initially (red phase) ✅

### Phase 3: Feature Implementation ✅  
- [x] Implement request/response logging middleware
- [x] Add structured JSON logging configuration
- [x] Enhance validation error logging
- [x] Make tests pass (green phase) ✅

### Phase 4: Verification ✅
- [x] Run full test suite (64/64 tests passing!)
- [x] Test with curl for log verification ✅
- [x] Verify JSON log format for Grafana parsing ✅
- [x] Manual testing shows perfect structured logging

### Phase 5: Integration Ready
- [ ] Update docker-compose configuration for log forwarding
- [ ] Prepare for Kubernetes deployment
- [ ] Document logging format for Grafana

## Testing Strategy

### New Unit Tests Needed
- Todo character limit validation in models
- Service-level validation behavior
- Logging configuration and output format

### New Integration Tests Needed
- API rejection of 140+ character todos
- HTTP 422 response for validation errors
- Request logging middleware behavior
- Log message format verification

### Manual Testing
- Postman/curl tests with various todo lengths
- Log output verification in local environment
- Error message clarity for end users

## Technical Considerations

### Logging Implementation
- Use FastAPI middleware for request/response logging
- Structured JSON logging for Grafana parsing
- Include correlation IDs for request tracing
- Log levels: INFO for normal requests, WARN for validation failures

### Validation Strategy
- Pydantic model validation (first line of defense)
- FastAPI automatic validation (HTTP 422 responses)
- Clear error messages for client applications
- Maintain backward compatibility

### Performance Impact
- Minimal logging overhead
- Avoid logging sensitive data
- Consider log rotation for production

## Next Steps
1. Assess current todo-backend implementation
2. Identify existing test coverage gaps
3. Write failing tests for new features
4. Implement features to make tests pass

**Status**: Phase 1 - Assessment started
