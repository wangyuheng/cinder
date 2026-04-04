## ADDED Requirements

### Requirement: Dashboard Home Page
The system SHALL provide a dashboard home page that displays key metrics and recent activity.

#### Scenario: View dashboard metrics
- **WHEN** user opens the dashboard home page
- **THEN** system displays execution count, success rate, decision count, and file count

#### Scenario: View recent executions
- **WHEN** user views the dashboard
- **THEN** system displays a list of recent executions with status indicators

### Requirement: Executions Page
The system SHALL provide an executions page that lists all execution history.

#### Scenario: View execution list
- **WHEN** user navigates to the executions page
- **THEN** system displays a paginated list of all executions

#### Scenario: Filter executions by status
- **WHEN** user selects a status filter
- **THEN** system displays only executions matching the selected status

#### Scenario: View execution details
- **WHEN** user clicks on an execution
- **THEN** system displays detailed information including goal, status, created files, and timestamp

### Requirement: Soul Configuration Page
The system SHALL provide a page to view and edit Soul configuration.

#### Scenario: View Soul configuration
- **WHEN** user navigates to the Soul page
- **THEN** system displays the current Soul profile and trait scores

#### Scenario: Edit Soul configuration
- **WHEN** user modifies Soul traits and saves
- **THEN** system updates the Soul configuration file

### Requirement: Task Trigger Page
The system SHALL provide a page to manually trigger new execution tasks.

#### Scenario: Trigger new execution
- **WHEN** user enters a goal and clicks execute
- **THEN** system creates a new execution and displays progress

#### Scenario: Select execution mode
- **WHEN** user triggers a new execution
- **THEN** system allows selection of auto, interactive, or dry-run mode

### Requirement: Decisions Page
The system SHALL provide a page to view decision history.

#### Scenario: View decision list
- **WHEN** user navigates to the decisions page
- **THEN** system displays a paginated list of all decisions

#### Scenario: View decision details
- **WHEN** user clicks on a decision
- **THEN** system displays context, confidence score, and reasoning

### Requirement: Dark Theme Support
The system SHALL support dark theme as the default with light theme option.

#### Scenario: Default dark theme
- **WHEN** user first opens the dashboard
- **THEN** system displays in dark theme

#### Scenario: Toggle theme
- **WHEN** user clicks theme toggle
- **THEN** system switches between dark and light themes

### Requirement: Responsive Design
The system SHALL support both desktop and mobile viewports.

#### Scenario: Mobile viewport
- **WHEN** user accesses dashboard on mobile device
- **THEN** system displays responsive layout optimized for mobile
