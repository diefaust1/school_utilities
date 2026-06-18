# Test Pages

## Test Overview

- Display each test in a card containing its title, date, time limit, and status.
- Selecting a test card opens the individual test page.
- Display the signed-in user's name and account role.
- Tests are loaded from the database.
- For now, every signed-in student and teacher can see every test.
- If the signed-in student has already submitted a test, the test card shows `Submitted` and appears gray.
- Inactive tests also appear gray.
- Teacher accounts see an Activate/Deactivate button below each test card.

## Individual Test Page

- Display the test title, date, time limit, and total points.
- Students enter the first and last name that should be stored with the submission.
- Display each database question with its title, description, points, answer type, and answer field.
- Multiple-choice questions use radio buttons.
- Free-text questions use text areas.
- Submitting the test saves a submission and all answers.
- If the test is inactive, the form is disabled.
- If the student already has a submitted attempt, the form is disabled until a teacher reopens that submission.
- Submitted answers remain visible after submission, but the inputs cannot be changed.
- Reopened tests prefill the previous submitted name and answers so the student can edit them.
- The Save as PDF button opens the browser print dialog so the filled test can be saved as a PDF.
- The PDF/print view includes the student name, test length, questions, answers, points, and a remaining-time field.
- Remaining time currently displays `Not tracked yet` because no countdown timer exists.

## Test Creation

- Only teacher accounts can access this page.
- Include fields for the test title, date, time limit, status, and instructions.
- Question creation and saving are not implemented during this phase.

## Submissions Page

- Only teacher accounts can access this page.
- Every test is shown as its own expandable box.
- Teachers click a test box to see the saved submissions inside that test group.
- Each submission shows the submitted student name, account e-mail, submission date, status, and answers.
- Teachers can reopen an individual submitted attempt.
