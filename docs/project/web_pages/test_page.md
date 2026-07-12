# Test Pages

## Test Overview

- Display each test in a card containing its title, date, time limit, and status.
- Student accounts start active tests with a Start test button.
- Starting a test creates a persistent Test Attempt.
- Student accounts with an active Test Attempt see Continue test.
- Student accounts cannot preview the test page before starting.
- Teacher accounts can select a test card to preview it without creating a Test Attempt.
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
- The timer starts when the student starts the Test Attempt.
- The browser autosaves the student name and all answers every 5 seconds.
- Autosave updates the browser countdown with server-authoritative remaining seconds.
- Submitting the test saves a submission, all answers, and remaining seconds.
- Answers are optional.
- Manual submit warns with a native confirmation if any answer is empty.
- If the test is inactive, the form is disabled.
- If the student already has a submitted attempt, the form is disabled until a teacher reopens that submission.
- Submitted answers remain visible after submission, but the inputs cannot be changed.
- Reopened tests prefill the previous submitted name and answers so the student can edit them.
- Reopened tests use the teacher-provided Reopen Allowance, defaulting to 5 minutes.
- If the timer expires, the Test Attempt is submitted with the last autosaved name and answers.
- The Save as PDF button opens the browser print dialog so the filled test can be saved as a PDF.
- The PDF/print view includes the student name, test length, questions, answers, points, and a remaining-time field.

## Test Creation

- Only teacher accounts can access this page.
- Include fields for the test title, date, time limit, status, and instructions.
- Question creation and saving are not implemented during this phase.

## Submissions Page

- Only teacher accounts can access this page.
- Every test is shown as its own expandable box.
- Teachers click a test box to see the Student Submissions inside that test group.
- Each Student Submission is shown as an expandable row with the submitted student name, submission date and time, and status.
- Expanding a Student Submission shows the full test with every question and the student's answer.
- Questions without a submitted answer show an empty answer area.
- Multiple-choice answers show the full selected option text.
- Teachers can reopen an individual submitted Student Submission and set the Reopen Allowance for the next Test Attempt.
- Reopened Student Submissions remain visible as review history.
- Remaining time is displayed as minutes and seconds.
- Teachers can save an expanded Student Submission as a PDF.
