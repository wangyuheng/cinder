## ADDED Requirements

### Requirement: Evaluate execution results
The system SHALL evaluate execution results based on soul profile.

#### Scenario: Risk consistency evaluation
- **WHEN** code is generated
- **THEN** system checks if code matches user's risk tolerance
- **AND** system flags high-risk code for conservative users
- **AND** system suggests alternatives if mismatch

#### Scenario: Style consistency evaluation
- **WHEN** code style is evaluated
- **THEN** system checks if code matches user's communication preferences
- **AND** system adjusts code comments and documentation style
- **AND** system ensures code readability matches user preference

#### Scenario: Quality evaluation
- **WHEN** code quality is evaluated
- **THEN** system checks code complexity
- **AND** system checks code maintainability
- **AND** system assigns quality score

### Requirement: Provide improvement suggestions
The system SHALL provide suggestions for improving execution results.

#### Scenario: Code improvement suggestions
- **WHEN** reflection identifies improvement opportunities
- **THEN** system generates specific suggestions
- **AND** system explains rationale for each suggestion
- **AND** system offers to regenerate with improvements

#### Scenario: Architecture improvement suggestions
- **WHEN** reflection identifies architectural issues
- **THEN** system suggests architectural improvements
- **AND** system explains benefits of changes
- **AND** system offers to restructure code

#### Scenario: Performance improvement suggestions
- **WHEN** reflection identifies performance issues
- **THEN** system suggests optimizations
- **AND** system provides performance estimates
- **AND** system offers to optimize code

### Requirement: Support iterative refinement
The system SHALL support iterative refinement through reflection loops.

#### Scenario: Single reflection loop
- **WHEN** initial execution completes
- **THEN** system performs reflection
- **AND** system identifies improvements
- **AND** system regenerates code if needed

#### Scenario: Multiple reflection loops
- **WHEN** user enables multiple reflection loops
- **THEN** system iterates until quality threshold is met
- **AND** system limits iterations to configured maximum
- **AND** system reports progress after each iteration

#### Scenario: Reflection timeout
- **WHEN** reflection takes too long
- **THEN** system stops reflection
- **AND** system uses best result so far
- **AND** system notifies user of timeout

### Requirement: Track reflection history
The system SHALL track reflection history for each execution.

#### Scenario: Reflection log storage
- **WHEN** reflection is performed
- **THEN** system stores reflection results
- **AND** system stores suggestions made
- **AND** system stores actions taken

#### Scenario: Reflection history query
- **WHEN** user queries reflection history
- **THEN** system displays past reflections
- **AND** system shows improvements made
- **AND** system shows final decisions

#### Scenario: Reflection statistics
- **WHEN** user requests reflection statistics
- **THEN** system shows number of reflections performed
- **AND** system shows average improvement per reflection
- **AND** system shows most common issues identified

### Requirement: Apply soul-based decision rules
The system SHALL apply soul-based decision rules during reflection.

#### Scenario: Risk-based decisions
- **WHEN** evaluating risky code
- **THEN** system applies user's risk_tolerance trait
- **AND** system makes conservative choices for low risk tolerance
- **AND** system allows aggressive choices for high risk tolerance

#### Scenario: Communication-based decisions
- **WHEN** evaluating code documentation
- **THEN** system applies user's communication_preferences
- **AND** system adjusts documentation detail level
- **AND** system adjusts comment style

#### Scenario: Structure-based decisions
- **WHEN** evaluating code structure
- **THEN** system applies user's structure preference
- **AND** system creates more structure for high structure need
- **AND** system allows flexible structure for low structure need

### Requirement: Explain reflection decisions
The system SHALL provide explanations for reflection decisions.

#### Scenario: Decision explanation
- **WHEN** reflection makes a decision
- **THEN** system explains the rationale
- **AND** system cites relevant soul traits
- **AND** system shows alternative options considered

#### Scenario: Conflict explanation
- **WHEN** soul traits conflict
- **THEN** system explains the conflict
- **AND** system shows how conflict was resolved
- **AND** system allows user to override

#### Scenario: Learning from feedback
- **WHEN** user provides feedback on reflection
- **THEN** system learns from feedback
- **AND** system adjusts future reflections
- **AND** system stores feedback in soul profile
