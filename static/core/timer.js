const attemptForm = document.querySelector("[data-test-attempt-form]");
const timer = document.querySelector("[data-test-timer]");
const timerDisplay = document.querySelector("[data-test-timer-display]");
let autosaveInFlight = false;

function formatSeconds(totalSeconds) {
  const safeSeconds = Math.max(0, Number(totalSeconds) || 0);
  const minutes = Math.floor(safeSeconds / 60);
  const seconds = safeSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

function hasEmptyAnswer() {
  if (!attemptForm) {
    return false;
  }

  const answerFields = attemptForm.querySelectorAll('[name^="question_"]');
  const fieldNames = new Set(Array.from(answerFields).map((field) => field.name));

  return Array.from(fieldNames).some((name) => {
    const fields = attemptForm.querySelectorAll(`[name="${name}"]`);
    if (fields.length === 0) {
      return true;
    }
    if (fields[0].type === "radio") {
      return !Array.from(fields).some((field) => field.checked);
    }
    return fields[0].value.trim() === "";
  });
}

function setRemainingSeconds(seconds) {
  if (!timer || !timerDisplay) {
    return;
  }

  timer.dataset.remainingSeconds = String(Math.max(0, Number(seconds) || 0));
  timerDisplay.textContent = formatSeconds(timer.dataset.remainingSeconds);
}

async function autosave() {
  if (!attemptForm || !attemptForm.dataset.autosaveUrl) {
    return;
  }
  if (autosaveInFlight) {
    return;
  }

  autosaveInFlight = true;

  try {
    const response = await fetch(attemptForm.dataset.autosaveUrl, {
      method: "POST",
      body: new FormData(attemptForm),
      credentials: "same-origin",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    });

    if (!response.ok) {
      return;
    }

    const payload = await response.json();
    setRemainingSeconds(payload.remaining_seconds);

    if (payload.finalized) {
      window.location.href = `${window.location.pathname}?submitted=1`;
      return;
    }

    if (payload.remaining_seconds <= 0) {
      attemptForm.dataset.skipIncompleteWarning = "true";
      attemptForm.submit();
    }
  } finally {
    autosaveInFlight = false;
  }
}

if (timer) {
  setRemainingSeconds(timer.dataset.remainingSeconds);

  window.setInterval(() => {
    const remaining = Math.max(0, Number(timer.dataset.remainingSeconds || 0) - 1);
    setRemainingSeconds(remaining);
    if (remaining === 0) {
      autosave();
    }
  }, 1000);

  window.setInterval(autosave, 5000);
}

if (attemptForm) {
  attemptForm.addEventListener("submit", (event) => {
    if (attemptForm.dataset.skipIncompleteWarning === "true") {
      return;
    }

    if (!hasEmptyAnswer()) {
      return;
    }

    const confirmed = window.confirm(
      "Are you sure you want to submit? Not all fields are filled with answers."
    );
    if (!confirmed) {
      event.preventDefault();
    }
  });
}
