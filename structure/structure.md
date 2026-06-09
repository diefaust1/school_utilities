Techstack
- Web interface for the tests/exams = html, js, css
- Python with Django for the backend
- Database with Postgres
- Local LLM to check the answers against test solutions and giving points
- Docker to containerize it

Functionality

Accounts
- students and teachers

Student account (saved in the database)
- Firstname, lastname
- Date of creation
- E-Mail (will not be verified)
- Password

Teacher accounts
- Firstname, lastname
- Date of creation
- E-Mail (will not be verified)
- Password
- Are able to create tests in a different tab (functionality not implemented yet)

Webpages
All webpages are part of the from the navigation side bar and accessible through it

Standard layout for all pages
- Navigation side bar on the left

Navigation Tabs
- Test-Overview
- Test-Creation
- Account info

Test-Overview Page
- Students see info about a test in a Square window
- Every test is represented by a window
- When Students click on the window then land at the test page
- There account info in automatically inserted into the test 

Test (entity)
- Date
- Length (time limit)
- Active or not-active

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

Test for Code
Build test-cases for the code

Roadmap
1. Build the frontend (webpages and login)
2. Create accounts for students and teachers
3. Create a test/exam (test if the functionality works)
4. Student submits a test (how should the data be saved?)
5. Automatically grading the students test (how should it be graded?)
