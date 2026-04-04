## ADDED Requirements

### Requirement: API Server Startup
The system SHALL provide a FastAPI-based API server that can be started via CLI.

#### Scenario: Start server via CLI
- **WHEN** user runs `cinder server`
- **THEN** system starts the API server on the configured port (default 8000)

#### Scenario: Server with custom port
- **WHEN** user runs `cinder server --port 9000`
- **THEN** system starts the API server on port 9000

### Requirement: Executions API
The system SHALL provide REST API endpoints for execution management.

#### Scenario: List executions
- **WHEN** client requests GET /api/executions
- **THEN** system returns a paginated list of executions

#### Scenario: Get execution details
- **WHEN** client requests GET /api/executions/{id}
- **THEN** system returns detailed execution information

#### Scenario: Create execution
- **WHEN** client posts to POST /api/executions with goal and mode
- **THEN** system creates a new execution and returns execution ID

#### Scenario: Get execution statistics
- **WHEN** client requests GET /api/executions/stats
- **THEN** system returns aggregated statistics (total, success rate, etc.)

### Requirement: Soul Configuration API
The system SHALL provide REST API endpoints for Soul configuration management.

#### Scenario: Get Soul configuration
- **WHEN** client requests GET /api/soul
- **THEN** system returns current Soul profile and traits

#### Scenario: Update Soul configuration
- **WHEN** client sends PUT /api/soul with updated traits
- **THEN** system updates the Soul configuration file

### Requirement: Decisions API
The system SHALL provide REST API endpoints for decision history.

#### Scenario: List decisions
- **WHEN** client requests GET /api/decisions
- **THEN** system returns a paginated list of decisions

#### Scenario: Get decision details
- **WHEN** client requests GET /api/decisions/{id}
- **THEN** system returns detailed decision information

#### Scenario: Get decision statistics
- **WHEN** client requests GET /api/decisions/stats
- **THEN** system returns aggregated decision statistics

### Requirement: CORS Configuration
The system SHALL configure CORS to allow frontend access.

#### Scenario: CORS headers present
- **WHEN** frontend makes cross-origin request
- **THEN** system includes appropriate CORS headers in response

### Requirement: Error Handling
The system SHALL return appropriate HTTP error codes and messages.

#### Scenario: Resource not found
- **WHEN** client requests non-existent resource
- **THEN** system returns 404 status with error message

#### Scenario: Invalid request
- **WHEN** client sends malformed request
- **THEN** system returns 400 status with validation errors

#### Scenario: Server error
- **WHEN** unexpected error occurs
- **THEN** system returns 500 status with generic error message
