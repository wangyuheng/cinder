## ADDED Requirements

### Requirement: Interactive question guidance flow
The system SHALL provide an interactive command-line interface that guides users through 6 core questions to generate their soul profile.

#### Scenario: User starts question guidance
- **WHEN** user runs the `init` command
- **THEN** system displays a welcome message and starts the question guidance flow

#### Scenario: User answers all questions
- **WHEN** user completes all 6 questions with valid inputs
- **THEN** system generates soul.md and soul.meta.yaml files
- **AND** system displays a summary of the generated soul profile

#### Scenario: User skips optional reason field
- **WHEN** user presses Enter without typing a reason for a question
- **THEN** system accepts the empty reason and continues to the next question

#### Scenario: User provides invalid input
- **WHEN** user enters an invalid option (not A-D)
- **THEN** system displays an error message and prompts for input again

### Requirement: Question display and input handling
The system SHALL display each question with its title, prompt, and available options, and accept user input in a user-friendly manner.

#### Scenario: Question with multiple choice options
- **WHEN** system presents a question
- **THEN** system displays the question title, prompt text, and 4 options labeled A-D
- **AND** system prompts user to enter their choice

#### Scenario: Optional reason input
- **WHEN** user selects an option
- **THEN** system prompts for an optional reason
- **AND** system allows user to skip by pressing Enter

### Requirement: Progress indication
The system SHALL show progress indication during the question guidance flow.

#### Scenario: Display current question number
- **WHEN** system presents a question
- **THEN** system displays the current question number and total number of questions

#### Scenario: Display completion status
- **WHEN** user completes all questions
- **THEN** system displays a completion message before generating soul files

### Requirement: Soul file generation
The system SHALL generate both soul.md and soul.meta.yaml files based on user answers.

#### Scenario: Generate soul.md
- **WHEN** user completes all questions
- **THEN** system generates a soul.md file containing the human-readable soul profile

#### Scenario: Generate soul.meta.yaml
- **WHEN** user completes all questions
- **THEN** system generates a soul.meta.yaml file containing structured metadata

#### Scenario: Custom output path
- **WHEN** user specifies a custom output path with --output option
- **THEN** system generates soul files at the specified path

### Requirement: Quick mode for experienced users
The system SHALL provide a quick mode that uses default values to speed up the process.

#### Scenario: User runs in quick mode
- **WHEN** user runs the `init` command with --quick flag
- **THEN** system uses default values for optional fields
- **AND** system minimizes the number of prompts

### Requirement: Resume incomplete session
The system SHALL allow users to resume an incomplete question session.

#### Scenario: User interrupts session
- **WHEN** user presses Ctrl+C during question guidance
- **THEN** system saves current progress to a temporary file
- **AND** system displays a message indicating how to resume

#### Scenario: User resumes session
- **WHEN** user runs the `init` command with --resume flag
- **THEN** system loads previous progress from temporary file
- **AND** system continues from the last unanswered question
