Example work flow

1. Students take a test on a web interface.
2. The system stores their answers.
3. A grading module compares the student answer with a teacher-provided solution/rubric.
4. For the free-text and calculation tasks an local LLM is grading and can suggest:
- how many points the answer deserves
- what is missing
- short feedback for the student
- where the teacher should review carefully
5. Afterwards the LLM is giving feedback and the system lists the points and resulting grades somewhere

The teacher can review the suggested grading and approve it

Tests for Code
- Build test-cases for the code

Roadmap
1. Build the frontend (webpages and login)
2. Create accounts for students and teachers
3. Create a test/exam (test if the functionality works)
4. Student submits a test (how should the data be saved?)
5. Automatically grading the students test (how should it be graded?)
