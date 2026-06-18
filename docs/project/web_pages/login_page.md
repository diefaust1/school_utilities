# Login Page

## Purpose

The login page is the entry point for students and teachers. It allows an existing user to sign in before accessing tests, test creation, or account information.

The page does not use the standard navigation sidebar because the user is not authenticated yet.

## Layout

- Display a simple login card centered on the page.
- Show the project name, `Auto Grader`, and a short explanation of what the user can access after signing in.
- Keep the layout usable on desktop and mobile screens.
- Use the same simple visual style and colors as the rest of the application.

## Form Fields

- E-mail address
- Password
- Sign-in button

The user does not select whether they are a student or teacher. Their account type determines which features are available after login.

## Behavior

- Both fields are required.
- Submitting valid credentials signs the user in.
- A link opens the registration page.
- Students are sent to the Test-Overview page.
- Teachers are sent to the Test-Overview page and can access Test-Creation from the navigation sidebar.
- Invalid credentials display a clear error message without revealing whether the e-mail address or password was incorrect.
- The entered e-mail address remains in the form after an unsuccessful login attempt.
- The password field is cleared after an unsuccessful login attempt.
- Pressing Enter while using the form submits it.

## Accessibility

- Every input has a visible label.
- Keyboard users can reach and use all form controls.
- Focus states are clearly visible.
- Error messages are associated with the relevant form and announced to screen readers.

## Current Phase

Authentication is implemented for student and teacher accounts. Both account types can be created from the registration page.
