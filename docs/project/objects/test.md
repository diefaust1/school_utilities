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
- Each test is displayed as a card.
- Student accounts use Start test to create a Test Attempt.
- Student accounts use Continue test to return to an active Test Attempt.
- Student accounts cannot preview the test-detail page before starting a Test Attempt.
- Teacher accounts can open test-detail pages directly for preview without creating a Test Attempt.
- Requesting an unknown test ID returns a `404` response.
- Test visibility is not currently filtered by user, role, date, or active status.

## Test-Taking Behavior

- A Test Attempt is created when a student starts a test.
- A Test Attempt stores the start time, time allowance, draft student name, and draft answers.
- Normal Test Attempts use the Test length as their time allowance.
- Reopened Test Attempts use the Reopen Allowance from the reopened Student Submission.
- The test-detail page renders all questions belonging to the selected test after the student starts it.
- Students enter their first and last name on the test page.
- Multiple-choice questions render as radio-button choices.
- Free-text questions render as text areas.
- Answer fields are optional.
- Manual submit warns the student if not all answers are filled, but the student can confirm and submit anyway.
- Draft names and answers are autosaved every 5 seconds.
- Autosave returns server-authoritative remaining seconds so the browser timer can correct drift.
- Submitting a test creates a `TestSubmission`.
- Each submitted answer creates a `StudentAnswer`.
- Submitted answers include empty answer text for unanswered questions.
- After submitting, the test is marked as submitted for that student.
- A student cannot submit the same test again while their submission status is `submitted`.
- Submitted answers remain visible on the test page in disabled/read-only fields.
- A teacher can reopen an individual student's submission. Reopening changes the previous submission status to `reopened` and allows that student to start another Test Attempt.
- Reopened tests prefill the previous submitted name and answers so the student can edit and resubmit.
- Reopened tests use the teacher-provided Reopen Allowance for the next Test Attempt.
- If a Test Attempt expires, it is submitted with the last autosaved name and answers.
- Expired Test Attempts are finalized lazily on the next relevant request.
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
- Reopen Allowance, if the submission was reopened
- Remaining seconds at submission time
- Answers

Expired submissions store `0` remaining seconds.

## Student Answer Fields

Each student answer stores:

- Parent submission
- Question
- Submitted answer text

For multiple-choice questions, the answer text is currently the selected option key, such as `A`, `B`, `C`, or `D`.

## Teacher Review Behavior

- Teacher accounts can open the Submissions page.
- The Submissions page shows one expandable box per test.
- Teachers click a test box to view the Student Submissions for that test.
- Each Student Submission first shows the student name, submission status, and submission date and time.
- Teachers expand a Student Submission to view the full test with every question and the student's answer.
- Questions without a submitted answer are shown with an empty answer area.
- Multiple-choice answers are shown as the full selected option text.
- Teachers can save an expanded Student Submission as a PDF.
- Teachers can reopen individual submitted attempts and set the Reopen Allowance for the next Test Attempt.
- The Reopen Allowance defaults to 5 minutes.
- Teacher review shows remaining time in minutes and seconds.
- Reopened Student Submissions remain visible as review history.
- Student accounts cannot access the Submissions page.

## Current Limitations And Later Work

- Test Creation is still only a frontend draft page and does not save new tests.
- Automatic grading is not implemented.
- Teacher approval of grades is not implemented.
- Points are stored on questions but are not awarded yet.
- Timers are enforced lazily on the next relevant request rather than by a background worker.
- Tests are visible to all signed-in users during the testing phase.
- A reopened submission remains stored as history; it is not deleted.
