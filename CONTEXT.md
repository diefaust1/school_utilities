# Domain Context

## Glossary

### School Utilities

The overall product and repository. It is intended to contain multiple school-related tools over time, not only the Auto Grader.

### Tool

A bounded feature area inside School Utilities. Each tool should own its domain behavior instead of mixing unrelated behavior into a shared app.

### Auto Grader

The first tool in School Utilities. It handles tests, questions, student submissions, teacher review, and later LLM-assisted grading.

### Student Submission

A student's completed attempt for a test. It includes the submitted status, submission time, and the student's answers in the context of the full test.

### Test Attempt

A student's started test session. It begins when the student starts a test, counts down even if the browser closes, and becomes a Student Submission when submitted or when time expires.

### Reopen Allowance

The extra time a teacher grants for the next Test Attempt after reopening a Student Submission. It applies only to that student's next attempt for that reopened submission.

### Account

A signed-in user of School Utilities. Accounts can currently have the student or teacher role.
