# Account Object

## Current Implementation

Accounts are stored in PostgreSQL using the custom Django `core.User` model. The model extends Django's `AbstractUser`.

The application supports two account roles:

- Student
- Teacher

## Stored Fields

- E-mail address
  - Required and unique.
  - Converted to lowercase.
  - Used as the login identifier instead of a username.
- Password
  - Stored as a secure Django password hash, never as plain text.
  - Registration currently requires at least four characters.
- Role
  - Must be either `student` or `teacher`.
  - New users select their role during registration.
- First name
  - Optional.
  - Maximum length of 150 characters.
  - Editable from the Account Info page.
- Last name
  - Optional.
  - Maximum length of 150 characters.
  - Editable from the Account Info page.
- Date joined
  - Automatically stored by Django when the account is created.
- Django permission fields
  - Includes active, staff, superuser, group, and permission information.

## Registration And Login

- Students and teachers can create accounts from the registration page.
- Registration requires an e-mail address, role, password, and password confirmation.
- Duplicate e-mail addresses and unknown roles are rejected.
- A successfully registered user is signed in automatically.
- Invalid login attempts return a generic error and do not reveal whether the e-mail exists.
- Superusers are automatically assigned the teacher role.

## Role Permissions

### Student

- Can view the Test Overview.
- Can open the currently available sample tests.
- Cannot access the Test Creation page.

### Teacher

- Has the same current test-viewing access as a student.
- Can access the Test Creation page.

## Account Info Page

- Signed-in users can view their e-mail address, role, and creation date.
- Signed-in users can change and save their own first and last name.
- E-mail address and account role are currently read-only after registration.

## Current Limitations And Later Work

- Public teacher registration allows users to grant themselves teacher permissions. Restrict this before production.
- The temporary four-character password minimum must be replaced with a stronger policy.
- Django password validators are currently disabled.
- E-mail addresses are not verified.
- Password reset and account deletion are not implemented.
