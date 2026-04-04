## ADDED Requirements

### Requirement: Record decision metadata
The system SHALL record comprehensive metadata for each proxy decision.

#### Scenario: Record basic decision info
- **WHEN** a proxy decision is made
- **THEN** system records the decision timestamp, context, and outcome

#### Scenario: Record soul rules applied
- **WHEN** a proxy decision is made
- **THEN** system records which soul rules were referenced
- **AND** system records how each rule influenced the decision

#### Scenario: Record confidence score
- **WHEN** a proxy decision is made
- **THEN** system records the confidence score
- **AND** system records whether human confirmation was required

### Requirement: Store decision logs persistently
The system SHALL store decision logs in a persistent SQLite database.

#### Scenario: Create database on first use
- **WHEN** system makes the first proxy decision
- **THEN** system creates the SQLite database at ~/.cinder/decisions.db
- **AND** system creates the decisions table with proper schema

#### Scenario: Insert decision record
- **WHEN** a proxy decision is made
- **THEN** system inserts a new record into the decisions table
- **AND** system confirms the insertion was successful

#### Scenario: Handle database errors
- **WHEN** database operation fails
- **THEN** system logs the error
- **AND** system continues operation without crashing

### Requirement: Query decision history
The system SHALL allow users to query and view decision history.

#### Scenario: List recent decisions
- **WHEN** user runs the `decisions list` command
- **THEN** system displays the most recent decisions (default: last 10)
- **AND** system shows timestamp, context summary, and outcome for each

#### Scenario: Filter decisions by date range
- **WHEN** user runs `decisions list --from DATE --to DATE`
- **THEN** system displays decisions within the specified date range

#### Scenario: Filter decisions by confidence
- **WHEN** user runs `decisions list --min-confidence SCORE`
- **THEN** system displays decisions with confidence score >= specified value

#### Scenario: Search decisions by context
- **WHEN** user runs `decisions search "keyword"`
- **THEN** system displays decisions where context contains the keyword

### Requirement: Display decision details
The system SHALL allow users to view detailed information about a specific decision.

#### Scenario: Show decision details
- **WHEN** user runs `decisions show <decision-id>`
- **THEN** system displays full decision details including context, soul rules, reasoning, and outcome

#### Scenario: Display decision reasoning chain
- **WHEN** user views a decision with --reasoning flag
- **THEN** system displays the step-by-step reasoning chain

#### Scenario: Export decision as JSON
- **WHEN** user runs `decisions show <decision-id> --format json`
- **THEN** system outputs the decision details in JSON format

### Requirement: Decision statistics
The system SHALL provide statistics and insights about proxy decisions.

#### Scenario: Show decision summary
- **WHEN** user runs `decisions stats`
- **THEN** system displays total number of decisions
- **AND** system displays average confidence score
- **AND** system displays breakdown by decision type

#### Scenario: Show confidence distribution
- **WHEN** user runs `decisions stats --confidence-distribution`
- **THEN** system displays a histogram of confidence scores

#### Scenario: Show frequently applied rules
- **WHEN** user runs `decisions stats --top-rules`
- **THEN** system displays the most frequently applied soul rules

### Requirement: Export decision logs
The system SHALL allow users to export decision logs for external analysis.

#### Scenario: Export to CSV
- **WHEN** user runs `decisions export --format csv --output decisions.csv`
- **THEN** system exports all decision logs to a CSV file

#### Scenario: Export to JSON
- **WHEN** user runs `decisions export --format json --output decisions.json`
- **THEN** system exports all decision logs to a JSON file

#### Scenario: Export filtered decisions
- **WHEN** user runs `decisions export --from DATE --to DATE --output filtered.csv`
- **THEN** system exports only decisions within the specified date range

### Requirement: Clean up old logs
The system SHALL provide mechanisms to clean up old decision logs.

#### Scenario: Auto-archive old decisions
- **WHEN** decision logs exceed configured age limit (default: 90 days)
- **THEN** system automatically archives old logs to a separate file

#### Scenario: Manual cleanup
- **WHEN** user runs `decisions clean --older-than DAYS`
- **THEN** system deletes decisions older than specified days
- **AND** system displays count of deleted records

#### Scenario: Archive before cleanup
- **WHEN** user runs `decisions clean --archive`
- **THEN** system archives old decisions to a timestamped file before deletion

### Requirement: Privacy and security
The system SHALL protect sensitive information in decision logs.

#### Scenario: Redact sensitive data
- **WHEN** logging a decision containing sensitive information (passwords, keys, personal data)
- **THEN** system redacts or hashes the sensitive information

#### Scenario: Encrypt database
- **WHEN** user enables encryption with `config set encryption true`
- **THEN** system encrypts the SQLite database

#### Scenario: User consent for logging
- **WHEN** user runs chat with --no-logging flag
- **THEN** system disables decision logging for that session

### Requirement: Decision review workflow
The system SHALL allow users to review and provide feedback on proxy decisions.

#### Scenario: Mark decision as correct
- **WHEN** user runs `decisions review <decision-id> --correct`
- **THEN** system marks the decision as validated by user

#### Scenario: Mark decision as incorrect
- **WHEN** user runs `decisions review <decision-id> --incorrect --reason "reason"`
- **THEN** system marks the decision as incorrect
- **AND** system stores the user's reason for future learning

#### Scenario: View decisions needing review
- **WHEN** user runs `decisions review --pending`
- **THEN** system displays low-confidence decisions that haven't been reviewed
