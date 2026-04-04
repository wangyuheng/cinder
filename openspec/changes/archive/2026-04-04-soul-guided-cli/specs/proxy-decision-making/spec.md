## ADDED Requirements

### Requirement: Detect decision points
The system SHALL automatically detect when a decision requiring human input is needed during agent interactions.

#### Scenario: Agent encounters ambiguous user request
- **WHEN** agent receives a user request with multiple valid interpretations
- **THEN** system identifies this as a decision point
- **AND** system triggers the proxy decision mechanism

#### Scenario: Agent needs to choose between options
- **WHEN** agent needs to choose between multiple action options
- **THEN** system evaluates each option against soul preferences
- **AND** system makes a decision or requests human confirmation based on risk level

### Requirement: Apply soul rules to decisions
The system SHALL apply relevant soul rules when making proxy decisions.

#### Scenario: Apply risk tolerance rules
- **WHEN** making a decision involving risk
- **THEN** system checks the user's risk_tolerance trait
- **AND** system applies the appropriate risk rule (conservative, balanced, or aggressive)

#### Scenario: Apply communication preference rules
- **WHEN** formatting a response or recommendation
- **THEN** system checks the user's communication_preferences
- **AND** system formats the output accordingly (structured, exploratory, or conclusion-first)

#### Scenario: Apply decision boundary rules
- **WHEN** making a decision that crosses a boundary threshold
- **THEN** system checks the user's boundary_reminders
- **AND** system either makes the decision or escalates to human based on boundary rules

### Requirement: Decision confidence scoring
The system SHALL calculate a confidence score for each proxy decision.

#### Scenario: High confidence decision
- **WHEN** soul rules clearly indicate a preferred option
- **THEN** system assigns a high confidence score (> 0.8)
- **AND** system proceeds with the decision automatically

#### Scenario: Low confidence decision
- **WHEN** soul rules are ambiguous or conflicting
- **THEN** system assigns a low confidence score (< 0.5)
- **AND** system requests human confirmation before proceeding

#### Scenario: Medium confidence decision
- **WHEN** soul rules provide some guidance but not definitive
- **THEN** system assigns a medium confidence score (0.5-0.8)
- **AND** system makes the decision but logs it for review

### Requirement: Human escalation
The system SHALL escalate to human confirmation for high-stakes or uncertain decisions.

#### Scenario: High-stakes decision
- **WHEN** a decision involves significant financial, career, or relationship impact
- **THEN** system identifies it as high-stakes
- **AND** system requests human confirmation regardless of confidence score

#### Scenario: Decision outside soul scope
- **WHEN** a decision involves a domain not covered by soul rules
- **THEN** system identifies it as out-of-scope
- **AND** system requests human input

#### Scenario: User preference for manual confirmation
- **WHEN** user has configured a preference for manual confirmation on certain decision types
- **THEN** system respects the preference and requests confirmation

### Requirement: Explain decision rationale
The system SHALL provide clear explanations for proxy decisions.

#### Scenario: User requests decision explanation
- **WHEN** user asks why a decision was made
- **THEN** system displays the soul rules that were applied
- **AND** system shows the reasoning chain

#### Scenario: Display decision context
- **WHEN** displaying a proxy decision
- **THEN** system shows the decision context (what was being decided)
- **AND** system shows the options considered
- **AND** system shows the selected option and confidence score

### Requirement: Support multiple backends
The system SHALL support proxy decision-making with both Ollama and Claude backends.

#### Scenario: Proxy decision with Ollama
- **WHEN** using Ollama backend
- **THEN** system applies soul rules to the model's decision-making process
- **AND** system logs the decision

#### Scenario: Proxy decision with Claude
- **WHEN** using Claude backend
- **THEN** system applies soul rules to the model's decision-making process
- **AND** system logs the decision

### Requirement: Custom decision rules
The system SHALL allow users to define custom decision rules that override or supplement soul rules.

#### Scenario: User defines custom rule
- **WHEN** user adds a custom decision rule to soul.md
- **THEN** system applies the custom rule with higher priority than inferred rules

#### Scenario: Custom rule conflicts with soul rule
- **WHEN** a custom rule conflicts with an inferred soul rule
- **THEN** system follows the custom rule
- **AND** system logs the conflict

### Requirement: Decision mode toggle
The system SHALL allow users to toggle proxy decision mode on or off.

#### Scenario: Enable proxy mode
- **WHEN** user runs chat with --proxy flag
- **THEN** system enables proxy decision-making
- **AND** system makes decisions on behalf of the user when appropriate

#### Scenario: Disable proxy mode
- **WHEN** user runs chat without --proxy flag
- **THEN** system disables proxy decision-making
- **AND** system always asks for user input when decisions are needed

#### Scenario: Interactive mode switching
- **WHEN** user enters a command to toggle proxy mode during a session
- **THEN** system switches the mode
- **AND** system confirms the mode change
