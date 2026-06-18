# Account Info Page

## Purpose

The Account Info page allows a signed-in student or teacher to review their account and update their first and last name.

## Fields

- First name, editable
- Last name, editable
- E-mail address, read-only
- Account creation date, read-only
- Account type, displayed in the profile heading

## Behavior

- Selecting `Save changes` submits the first and last name to Django.
- Django validates both names against the user model before saving.
- After a successful save, the page reloads and displays a confirmation message.
- Validation errors are displayed beside the relevant field.
- Both name fields can be left empty.
- E-mail address and account type cannot currently be changed.

## Access

- The page requires login.
- Users can only edit their own account.
