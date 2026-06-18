# Test Object

## Current Implementation

Tests are stored in PostgreSQL using the `core.Test` model. Questions, submissions, and answers are also persisted.

The application seeds two example tests through Django migrations:

- `Mathematics - Basics`
- `Biology - Cell Structure`

Each seeded test has:

- Three questions
- Two multiple-choice questions
- One free-text question

For the current testing phase, every signed-in student and teacher can see every test.

## Test Fields

- Title
- Date
- Length in minutes
- Active status
  - Teachers can activate or deactivate a test from the Test Overview page.
  - Inactive tests remain visible but cannot be submitted.
- Instructions
- Created by
  - Optional teacher reference.
  - The seeded example test has no owner.

## Question Fields

Every question must include:

- Parent test
- Title
- Question description
- Answer type
  - `multiple_choice`
  - `free_text`
- Points

Multiple-choice questions can also include:

- Option A
- Option B
- Option C
- Option D
- Correct choice

The correct choice is stored for later grading work. It is not used for automatic grading yet.

## Test Overview Behavior

- Signed-in students and teachers can view all tests.
- Each test is displayed as a clickable card.
- Selecting a valid card opens the test-detail page.
- Requesting an unknown test ID returns a `404` response.
- Test visibility is not currently filtered by user, role, date, or active status.

## Test-Taking Behavior

- The test-detail page renders all questions belonging to the selected test.
- Students enter their first and last name on the test page.
- Multiple-choice questions render as radio-button choices.
- Free-text questions render as text areas.
- Every answer field is required.
- Submitting a test creates a `TestSubmission`.
- Each submitted answer creates a `StudentAnswer`.
- After submitting, the test is marked as submitted for that student.
- A student cannot submit the same test again while their submission status is `submitted`.
- Submitted answers remain visible on the test page in disabled/read-only fields.
- A teacher can reopen an individual student's submission. Reopening changes the previous submission status to `reopened` and allows that student to submit the same test again.
- Reopened tests prefill the previous submitted name and answers so the student can edit and resubmit.
- The test page has a Save as PDF button that opens the browser print dialog.

## Submission Fields

Each submission stores:

- Test
- Student account
- Student first name entered on the test form
- Student last name entered on the test form
- Submission date and time
- Status
  - `submitted`
  - `reopened`
- Reopened date and teacher, if the submission was reopened
- Answers

The test page displays `Remaining time at submission: Not tracked yet` because the countdown timer and remaining-time storage are not implemented.

## Student Answer Fields

Each student answer stores:

- Parent submission
- Question
- Submitted answer text

For multiple-choice questions, the answer text is currently the selected option key, such as `A`, `B`, `C`, or `D`.

## Teacher Review Behavior

- Teacher accounts can open the Submissions page.
- The Submissions page shows one expandable box per test.
- Teachers click a test box to view the submissions for that test.
- Teachers can see the student name, account e-mail, submission date, test title, and submitted answers.
- Teachers can reopen individual submitted attempts.
- Student accounts cannot access the Submissions page.

## Current Limitations And Later Work

- Test Creation is still only a frontend draft page and does not save new tests.
- Automatic grading is not implemented.
- Teacher approval of grades is not implemented.
- Points are stored on questions but are not awarded yet.
- Timers are not enforced.
- Remaining time is not tracked yet, so exported PDFs cannot include a real remaining-time value.
- Tests are visible to all signed-in users during the testing phase.
- A reopened submission remains stored as history; it is not deleted.
