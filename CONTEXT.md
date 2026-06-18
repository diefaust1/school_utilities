# Domain Context

## Glossary

### School Utilities

The overall product and repository. It is intended to contain multiple school-related tools over time, not only the Auto Grader.

### Tool

A bounded feature area inside School Utilities. Each tool should own its domain behavior instead of mixing unrelated behavior into a shared app.

### Auto Grader

The first tool in School Utilities. It handles tests, questions, student submissions, teacher review, and later LLM-assisted grading.

### Account

A signed-in user of School Utilities. Accounts can currently have the student or teacher role.
