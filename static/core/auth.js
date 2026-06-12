const authForms = document.querySelectorAll(".auth-form");

authForms.forEach((form) => {
  form.addEventListener("submit", (event) => {
    if (form.hasAttribute("data-password-check")) {
      const password = form.querySelector('[name="password"]');
      const confirmation = form.querySelector('[name="password_confirm"]');
      const error = form.querySelector("[data-password-error]");
      const passwordsMatch = password.value === confirmation.value;

      confirmation.setCustomValidity(passwordsMatch ? "" : "The passwords do not match.");
      error.hidden = passwordsMatch;

      if (!passwordsMatch) {
        event.preventDefault();
        confirmation.focus();
        return;
      }
    }

    const submitButton = form.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    submitButton.textContent = "Please wait...";
  });
});
