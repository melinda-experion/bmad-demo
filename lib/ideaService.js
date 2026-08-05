const ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages";
const ANTHROPIC_VERSION = "2023-06-01";

let timeoutMs = 25000;

function buildPrompt(prompt) {
  return (
    "Generate exactly 3 distinct starter ideas for the following prompt. " +
    "Respond with ONLY a JSON array of exactly 3 objects, each with a " +
    '"title" and "description" string field, and nothing else (no ' +
    "markdown, no code fences, no commentary).\n\n" +
    `Prompt: ${prompt}`
  );
}

function isWellFormedIdea(idea) {
  return (
    idea !== null &&
    typeof idea === "object" &&
    typeof idea.title === "string" &&
    idea.title.length > 0 &&
    typeof idea.description === "string" &&
    idea.description.length > 0
  );
}

function parseIdeas(responseBody) {
  const text = responseBody?.content?.[0]?.text;
  if (typeof text !== "string") {
    const error = new Error("Provider response did not contain text content");
    error.code = "MALFORMED";
    throw error;
  }

  let parsed;
  try {
    parsed = JSON.parse(text);
  } catch {
    const error = new Error("Provider response was not valid JSON");
    error.code = "MALFORMED";
    throw error;
  }

  if (!Array.isArray(parsed) || parsed.length !== 3 || !parsed.every(isWellFormedIdea)) {
    const error = new Error(
      "Provider response did not contain exactly 3 well-formed ideas",
    );
    error.code = "MALFORMED";
    throw error;
  }

  return parsed.map((idea) => ({
    title: idea.title,
    description: idea.description,
  }));
}

async function generateIdeas(prompt) {
  const apiKey = process.env.IDEA_LLM_API_KEY;
  if (!apiKey) {
    throw new Error("IDEA_LLM_API_KEY is not configured");
  }

  const model = process.env.ANTHROPIC_MODEL;
  if (!model) {
    throw new Error("ANTHROPIC_MODEL is not configured");
  }

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  let response;
  try {
    response = await fetch(ANTHROPIC_MESSAGES_URL, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": ANTHROPIC_VERSION,
      },
      body: JSON.stringify({
        model,
        max_tokens: 1024,
        messages: [{ role: "user", content: buildPrompt(prompt) }],
      }),
      signal: controller.signal,
    });
  } catch (cause) {
    if (cause.name === "AbortError") {
      const error = new Error("Provider call timed out");
      error.code = "TIMEOUT";
      throw error;
    }
    const error = new Error("Provider call failed before responding");
    error.code = "NETWORK";
    throw error;
  } finally {
    clearTimeout(timer);
  }

  if (!response.ok) {
    const error = new Error(`Provider responded with status ${response.status}`);
    error.code = "NETWORK";
    throw error;
  }

  const body = await response.json();
  return parseIdeas(body);
}

function __setTimeoutMsForTest(ms) {
  timeoutMs = ms;
}

module.exports = { generateIdeas, __setTimeoutMsForTest };
