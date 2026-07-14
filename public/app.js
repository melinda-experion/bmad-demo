const promptInput = document.getElementById("prompt");
const generateButton = document.getElementById("generate");
const clearButton = document.getElementById("clear");
const status = document.getElementById("status");
const error = document.getElementById("error");
const results = document.getElementById("results");

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

generateButton.addEventListener("click", async () => {
  const prompt = promptInput.value.trim();
  if (!prompt) {
    error.textContent = "Prompt is required and must not be empty";
    return;
  }

  error.textContent = "";
  status.textContent = "Generating ideas...";
  generateButton.disabled = true;

  try {
    const response = await fetch("/api/ideas", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ prompt }),
    });
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || "Ideas couldn't generate. Try again.");
    }

    results.innerHTML = payload.ideas
      .map(
        (idea) =>
          '<article class="card"><h3>' +
          escapeHtml(idea.title) +
          "</h3><p>" +
          escapeHtml(idea.description) +
          "</p></article>",
      )
      .join("");
    status.textContent = "Here are three starter ideas.";
  } catch (err) {
    status.textContent = "Ideas couldn't generate.";
    error.textContent = err.message;
  } finally {
    generateButton.disabled = false;
  }
});

clearButton.addEventListener("click", () => {
  promptInput.value = "";
  results.innerHTML = "";
  error.textContent = "";
  status.textContent = "Enter a prompt to begin.";
});
