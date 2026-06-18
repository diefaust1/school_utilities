const printButtons = document.querySelectorAll("[data-print-test]");

printButtons.forEach((button) => {
  button.addEventListener("click", () => {
    window.print();
  });
});
