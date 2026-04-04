## ADDED Requirements

### Requirement: Display generated soul profile
The system SHALL display the generated soul profile in a clear and organized manner after generation.

#### Scenario: Display core traits
- **WHEN** soul generation completes
- **THEN** system displays the core traits section from soul.md

#### Scenario: Display decision profile
- **WHEN** soul generation completes
- **THEN** system displays the decision profile section showing how the user handles uncertainty, emotions, conflicts, risks, motivation, and energy

#### Scenario: Display agent behavior guidelines
- **WHEN** soul generation completes
- **THEN** system displays the agent behavior guidelines section

### Requirement: Explain soul dimensions
The system SHALL provide explanations for each soul dimension in plain language.

#### Scenario: User requests explanation for a dimension
- **WHEN** user selects a dimension for explanation
- **THEN** system displays a plain-language explanation of what the dimension means
- **AND** system shows how it affects agent behavior

#### Scenario: Display all dimension explanations
- **WHEN** user requests to see all explanations
- **THEN** system displays explanations for all 6 dimensions (未知应对, 情绪调节, 冲突处理, 风险偏好, 能量恢复, 长期动力)

### Requirement: Allow soul adjustment
The system SHALL allow users to adjust their soul profile if they feel it doesn't accurately reflect their preferences.

#### Scenario: User wants to reanswer a question
- **WHEN** user selects the option to reanswer a question
- **THEN** system displays the question again
- **AND** system regenerates the soul profile with the new answer

#### Scenario: User wants to adjust trait scores
- **WHEN** user selects the option to manually adjust trait scores
- **THEN** system displays current trait scores
- **AND** system allows user to modify individual scores
- **AND** system regenerates the soul profile with adjusted scores

#### Scenario: User wants to add custom rules
- **WHEN** user selects the option to add custom decision rules
- **THEN** system prompts user to input custom rules
- **AND** system adds the custom rules to soul.md

### Requirement: Confirmation workflow
The system SHALL require explicit user confirmation before finalizing the soul profile.

#### Scenario: User confirms soul profile
- **WHEN** user reviews the soul profile and confirms it's accurate
- **THEN** system saves the confirmed soul.md and soul.meta.yaml
- **AND** system displays a success message

#### Scenario: User rejects soul profile
- **WHEN** user indicates the soul profile is not accurate
- **THEN** system offers options to reanswer questions or adjust traits
- **AND** system does not save the files until confirmation

#### Scenario: Skip confirmation for quick mode
- **WHEN** user runs with --skip-confirmation flag
- **THEN** system saves the soul files without requiring explicit confirmation

### Requirement: Visual presentation
The system SHALL present the soul profile in a visually appealing and easy-to-read format.

#### Scenario: Use syntax highlighting
- **WHEN** displaying soul profile in terminal
- **THEN** system uses colors and formatting to highlight key sections

#### Scenario: Paginate long content
- **WHEN** soul profile content exceeds terminal height
- **THEN** system paginates the content for easy reading

### Requirement: Save confirmation state
The system SHALL track whether the soul profile has been confirmed by the user.

#### Scenario: Check confirmation status
- **WHEN** system loads an existing soul.md
- **THEN** system checks if it has been confirmed
- **AND** system prompts for confirmation if not confirmed

#### Scenario: Mark soul as confirmed
- **WHEN** user confirms the soul profile
- **THEN** system adds a confirmation timestamp to soul.meta.yaml
