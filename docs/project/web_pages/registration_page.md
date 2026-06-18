# Registration Page

## Purpose

The registration page allows a new student or teacher to create an account.

## Layout

- Display a simple registration card centered on the page.
- Use the same style as the login page.
- Include a link back to the login page.
- Keep the layout usable on desktop and mobile screens.

## Form Fields

- E-mail address
- Account type: student or teacher
- Password
- Password confirmation
- Create account button

## Behavior

- All fields are required.
- The password must currently contain at least four characters.
- JavaScript immediately warns when the password confirmation does not match.
- Django validates all submitted data again on the server.
- An e-mail address can only belong to one account.
- The selected student or teacher role is saved with the account.
- After registration, the user is signed in and sent to the Test-Overview page.

## Errors

- Validation errors are displayed next to the relevant field.
- Existing accounts receive a clear duplicate e-mail error.
- Password values are cleared after unsuccessful server-side validation.

## Later Security Work

- Replace the temporary four-character minimum with a stronger password policy before production deployment.
- Enable appropriate Django password validators.
- Restrict teacher account creation before production so users cannot grant themselves teacher permissions.
