## ADDED Requirements

### Requirement: System provides initial time estimate
The system SHALL estimate total execution time before execution begins.

#### Scenario: Estimate based on task count
- **WHEN** task decomposition completes
- **THEN** the system provides an initial time estimate based on the number and type of tasks

#### Scenario: Estimate includes confidence interval
- **WHEN** providing a time estimate
- **THEN** the estimate includes a confidence interval (e.g., "5±2 minutes")

#### Scenario: Estimate uses historical data when available
- **WHEN** historical execution data exists for similar tasks
- **THEN** the estimate incorporates historical averages to improve accuracy

### Requirement: System provides phase-level estimates
The system SHALL estimate duration for each execution phase.

#### Scenario: Phase estimates are provided
- **WHEN** execution starts
- **THEN** the system provides estimated duration for each phase (PLAN, GENERATION, EVALUATION, DECISION)

#### Scenario: Phase estimates are updated
- **WHEN** a phase completes
- **THEN** estimates for remaining phases are recalculated based on actual performance

#### Scenario: Phase estimates reflect complexity
- **WHEN** tasks have varying complexity
- **THEN** phase estimates account for task complexity, not just count

### Requirement: System dynamically adjusts estimates
The system SHALL continuously refine time estimates during execution.

#### Scenario: Estimates update based on actual progress
- **WHEN** execution is 25% complete
- **THEN** the remaining time estimate is recalculated using actual speed data

#### Scenario: Confidence increases with progress
- **WHEN** execution progresses
- **THEN** the confidence of the estimate increases (narrower interval)

#### Scenario: Estimates adapt to slowdowns
- **WHEN** execution speed decreases significantly
- **THEN** the remaining time estimate is adjusted upward within 10 seconds

### Requirement: System calculates estimation accuracy
The system SHALL track and report the accuracy of time estimates.

#### Scenario: Accuracy is recorded
- **WHEN** an execution completes
- **THEN** the system calculates the accuracy of the initial and final estimates

#### Scenario: Accuracy statistics are maintained
- **WHEN** multiple executions have completed
- **THEN** the system maintains statistics on estimation accuracy

#### Scenario: Accuracy feedback improves future estimates
- **WHEN** historical accuracy data is available
- **THEN** the estimation algorithm is tuned to improve future predictions

### Requirement: System handles estimation edge cases
The system SHALL gracefully handle scenarios where estimation is difficult.

#### Scenario: No estimate when insufficient data
- **WHEN** execution just started (< 10% complete) and no historical data exists
- **THEN** the system displays "calculating..." instead of a potentially misleading estimate

#### Scenario: Wide confidence interval for uncertain estimates
- **WHEN** execution behavior is highly variable
- **THEN** the system provides a wide confidence interval to reflect uncertainty

#### Scenario: Estimate degrades gracefully on errors
- **WHEN** estimation algorithm encounters an error
- **THEN** the system falls back to a simple estimate or displays no estimate rather than crashing

### Requirement: System exposes estimation via API
The system SHALL provide APIs for accessing estimation data.

#### Scenario: API returns current estimate
- **WHEN** requesting progress for an active execution
- **THEN** the API includes current time estimate with confidence interval

#### Scenario: API provides estimation history
- **WHEN** requesting execution details
- **THEN** the API includes how estimates changed over time

#### Scenario: API supports estimation configuration
- **WHEN** configuring the estimation algorithm
- **THEN** the API allows adjusting parameters like update frequency and confidence thresholds

### Requirement: System provides transparent estimation
The system SHALL make estimation logic understandable to users.

#### Scenario: Estimation method is explained
- **WHEN** user requests details about an estimate
- **THEN** the system explains the estimation method used (historical average, current speed, etc.)

#### Scenario: Factors affecting estimate are shown
- **WHEN** displaying an estimate
- **THEN** the system indicates key factors (e.g., "based on 3 similar past executions")

#### Scenario: Estimate changes are explained
- **WHEN** an estimate changes significantly
- **THEN** the system indicates the reason (e.g., "task taking longer than expected")

### Requirement: System supports estimation customization
The system SHALL allow users to influence estimation behavior.

#### Scenario: Estimation algorithm can be configured
- **WHEN** user adjusts estimation settings
- **THEN** the system uses the configured parameters for future estimates

#### Scenario: Historical data weight can be adjusted
- **WHEN** user prefers recent performance over historical averages
- **THEN** the estimation algorithm weights recent data more heavily

#### Scenario: Estimation can be disabled
- **WHEN** user disables time estimation
- **THEN** the system does not display time estimates (only elapsed time)
