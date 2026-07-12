const printButtons = document.querySelectorAll("[data-print-test]");
const submissionPrintButtons = document.querySelectorAll("[data-print-submission]");

printButtons.forEach((button) => {
  button.addEventListener("click", () => {
    window.print();
  });
});

submissionPrintButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const submission = button.closest("[data-submission-print-section]");

    if (!submission) {
      window.print();
      return;
    }

    document.body.classList.add("printing-submission");
    submission.classList.add("is-print-target");
    window.print();
  });
});

window.addEventListener("afterprint", () => {
  document.body.classList.remove("printing-submission");
  document.querySelectorAll(".is-print-target").forEach((submission) => {
    submission.classList.remove("is-print-target");
  });
});
