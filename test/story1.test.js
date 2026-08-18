const fs = require("fs");
const path = require("path");
const vm = require("vm");
const test = require("node:test");
const assert = require("node:assert/strict");
const { createServer } = require("../server");

const ORIGINAL_FETCH = global.fetch;
const ORIGINAL_API_KEY = process.env.IDEA_LLM_API_KEY;
const ORIGINAL_MODEL = process.env.ANTHROPIC_MODEL;

function mockProviderEnv() {
  process.env.IDEA_LLM_API_KEY = "test-api-key";
  process.env.ANTHROPIC_MODEL = "claude-sonnet-5";
}

function restoreProviderEnv() {
  global.fetch = ORIGINAL_FETCH;
  if (ORIGINAL_API_KEY === undefined) {
    delete process.env.IDEA_LLM_API_KEY;
  } else {
    process.env.IDEA_LLM_API_KEY = ORIGINAL_API_KEY;
  }
  if (ORIGINAL_MODEL === undefined) {
    delete process.env.ANTHROPIC_MODEL;
  } else {
    process.env.ANTHROPIC_MODEL = ORIGINAL_MODEL;
  }
}

function mockProviderSuccess(ideas) {
  global.fetch = async () => ({
    ok: true,
    json: async () => ({
      content: [{ type: "text", text: JSON.stringify(ideas) }],
    }),
  });
}

async function startServer() {
  const server = createServer();
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  return { server, baseUrl: `http://127.0.0.1:${address.port}` };
}

async function stopServer(server) {
  await new Promise((resolve, reject) => {
    server.close((error) => (error ? reject(error) : resolve()));
  });
}

test("POST /api/ideas returns exactly three ideas for a valid prompt", async () => {
  const nodeFetch = global.fetch;
  mockProviderEnv();
  mockProviderSuccess([
    { title: "Note Vault", description: "A tagging system for study notes." },
    { title: "Note Sync", description: "Cross-device sync for study notes." },
    { title: "Note Quiz", description: "Turns notes into quiz flashcards." },
  ]);
  const { server, baseUrl } = await startServer();
  try {
    const response = await nodeFetch(`${baseUrl}/api/ideas`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ prompt: "A tool for organizing study notes" }),
    });

    assert.equal(response.status, 200);
    const payload = await response.json();
    assert.ok(Array.isArray(payload.ideas));
    assert.equal(payload.ideas.length, 3);
    payload.ideas.forEach((idea) => {
      assert.ok(typeof idea.title === "string" && idea.title.length > 0);
      assert.ok(
        typeof idea.description === "string" && idea.description.length > 0,
      );
    });
  } finally {
    await stopServer(server);
    restoreProviderEnv();
  }
});

test("GET / serves the browser UI assets", async () => {
  const { server, baseUrl } = await startServer();
  try {
    const homeResponse = await fetch(`${baseUrl}/`);
    assert.equal(homeResponse.status, 200);
    const html = await homeResponse.text();
    assert.match(html, /href="\/styles.css"/);
    assert.match(html, /src="\/app.js"/);

    const cssResponse = await fetch(`${baseUrl}/styles.css`);
    assert.equal(cssResponse.status, 200);
    assert.match(await cssResponse.text(), /\.panel/);

    const jsResponse = await fetch(`${baseUrl}/app.js`);
    assert.equal(jsResponse.status, 200);
    assert.match(await jsResponse.text(), /fetch\((['"])\/api\/ideas\1/);
  } finally {
    await stopServer(server);
  }
});

test("clicking Generate renders exactly three idea cards", async () => {
  const appScript = fs.readFileSync(
    path.join(__dirname, "..", "public", "app.js"),
    "utf8",
  );

  const elements = {
    prompt: { value: "A study planner", handlers: {}, addEventListener() {} },
    generate: { disabled: false, handlers: {}, addEventListener() {} },
    clear: { handlers: {}, addEventListener() {} },
    status: { textContent: "" },
    error: { textContent: "" },
    results: { innerHTML: "" },
  };

  Object.entries(elements).forEach(([key, element]) => {
    element.addEventListener = function addEventListener(type, handler) {
      this.handlers[type] = handler;
    };
    element.dispatch = function dispatch(type, ...args) {
      if (this.handlers[type]) {
        return this.handlers[type](...args);
      }
    };
  });

  const document = {
    getElementById(id) {
      return elements[id];
    },
  };

  const fetchCalls = [];
  const context = {
    document,
    console,
    fetch: async (url, options) => {
      fetchCalls.push({ url, options });
      return {
        ok: true,
        json: async () => ({
          ideas: [
            { title: "One", description: "First" },
            { title: "Two", description: "Second" },
            { title: "Three", description: "Third" },
          ],
        }),
      };
    },
  };

  vm.createContext(context);
  vm.runInContext(appScript, context);

  await elements.generate.dispatch("click");

  assert.equal(fetchCalls.length, 1);
  assert.equal(
    (elements.results.innerHTML.match(/<article class="card"/g) || []).length,
    3,
  );
});

test("submitting a meaningful prompt shows a busy state and disables the button until the request resolves", async () => {
  const appScript = fs.readFileSync(
    path.join(__dirname, "..", "public", "app.js"),
    "utf8",
  );

  const elements = {
    prompt: { value: "", handlers: {}, addEventListener() {} },
    generate: { disabled: false, handlers: {}, addEventListener() {} },
    clear: { handlers: {}, addEventListener() {} },
    status: { textContent: "" },
    error: { textContent: "" },
    results: { innerHTML: "" },
  };

  Object.entries(elements).forEach(([key, element]) => {
    element.addEventListener = function addEventListener(type, handler) {
      this.handlers[type] = handler;
    };
    element.dispatch = function dispatch(type, ...args) {
      if (this.handlers[type]) {
        return this.handlers[type](...args);
      }
    };
  });

  const document = {
    getElementById(id) {
      return elements[id];
    },
  };

  let resolveFetch;
  const pendingResponse = new Promise((resolve) => {
    resolveFetch = resolve;
  });
  const fetchCalls = [];
  const context = {
    document,
    console,
    fetch: async (url, options) => {
      fetchCalls.push({ url, options });
      return pendingResponse;
    },
  };

  vm.createContext(context);
  vm.runInContext(appScript, context);

  elements.prompt.value = "A study planner";

  const clickPromise = elements.generate.dispatch("click");

  assert.equal(fetchCalls.length, 1);
  assert.equal(elements.generate.disabled, true);
  assert.equal(elements.status.textContent, "Generating ideas...");
  assert.equal(elements.error.textContent, "");

  resolveFetch({
    ok: true,
    json: async () => ({
      ideas: [{ title: "One", description: "First" }],
    }),
  });

  await clickPromise;

  assert.equal(elements.generate.disabled, false);
  assert.equal(elements.status.textContent, "Here are three starter ideas.");
});

test("empty prompts are rejected without calling the API", async () => {
  const appScript = fs.readFileSync(
    path.join(__dirname, "..", "public", "app.js"),
    "utf8",
  );

  const elements = {
    prompt: { value: "   ", handlers: {}, addEventListener() {} },
    generate: { disabled: false, handlers: {}, addEventListener() {} },
    clear: { handlers: {}, addEventListener() {} },
    status: { textContent: "" },
    error: { textContent: "" },
    results: { innerHTML: "" },
  };

  Object.entries(elements).forEach(([key, element]) => {
    element.addEventListener = function addEventListener(type, handler) {
      this.handlers[type] = handler;
    };
    element.dispatch = function dispatch(type, ...args) {
      if (this.handlers[type]) {
        return this.handlers[type](...args);
      }
    };
  });

  const document = {
    getElementById(id) {
      return elements[id];
    },
  };

  const fetchCalls = [];
  const context = {
    document,
    console,
    fetch: async (url, options) => {
      fetchCalls.push({ url, options });
      return {
        ok: true,
        json: async () => ({ ideas: [] }),
      };
    },
  };

  vm.createContext(context);
  vm.runInContext(appScript, context);

  await elements.generate.dispatch("click");

  assert.equal(fetchCalls.length, 0);
  assert.equal(elements.generate.disabled, false);
  assert.equal(
    elements.error.textContent,
    "Prompt is required and must not be empty",
  );
});

test("POST /api/ideas rejects empty prompts", async () => {
  const { server, baseUrl } = await startServer();
  try {
    const response = await fetch(`${baseUrl}/api/ideas`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ prompt: "   " }),
    });

    assert.equal(response.status, 400);
    const payload = await response.json();
    assert.match(payload.error.toLowerCase(), /required/i);
  } finally {
    await stopServer(server);
  }
});

test("POST /api/ideas rejects invalid JSON bodies with 400", async () => {
  const { server, baseUrl } = await startServer();
  try {
    const response = await fetch(`${baseUrl}/api/ideas`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: "{not valid json",
    });

    assert.equal(response.status, 400);
  } finally {
    await stopServer(server);
  }
});

test("POST /api/ideas rejects prompts over 2000 characters with 400", async () => {
  const { server, baseUrl } = await startServer();
  try {
    const response = await fetch(`${baseUrl}/api/ideas`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ prompt: "a".repeat(2001) }),
    });

    assert.equal(response.status, 400);
    const payload = await response.json();
    assert.match(payload.error, /2000/);
  } finally {
    await stopServer(server);
  }
});

test("POST /api/ideas accepts a prompt at exactly 2000 characters", async () => {
  const nodeFetch = global.fetch;
  mockProviderEnv();
  mockProviderSuccess([
    { title: "One", description: "First" },
    { title: "Two", description: "Second" },
    { title: "Three", description: "Third" },
  ]);
  const { server, baseUrl } = await startServer();
  try {
    const response = await nodeFetch(`${baseUrl}/api/ideas`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ prompt: "a".repeat(2000) }),
    });

    assert.equal(response.status, 200);
  } finally {
    await stopServer(server);
    restoreProviderEnv();
  }
});

test("POST /api/ideas returns 504 when the provider call times out", async () => {
  const nodeFetch = global.fetch;
  mockProviderEnv();
  process.env.IDEA_LLM_TIMEOUT_MS = "10";
  global.fetch = async (url, options) =>
    new Promise((resolve, reject) => {
      options.signal.addEventListener("abort", () => {
        const abortError = new Error("aborted");
        abortError.name = "AbortError";
        reject(abortError);
      });
    });

  const { server, baseUrl } = await startServer();
  try {
    const response = await nodeFetch(`${baseUrl}/api/ideas`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ prompt: "A study planner" }),
    });

    assert.equal(response.status, 504);
    const payload = await response.json();
    assert.ok(payload.error);
  } finally {
    await stopServer(server);
    delete process.env.IDEA_LLM_TIMEOUT_MS;
    restoreProviderEnv();
  }
});

test("POST /api/ideas returns 502 when the provider call fails before responding", async () => {
  const nodeFetch = global.fetch;
  mockProviderEnv();
  global.fetch = async () => {
    throw new Error("connect ECONNREFUSED");
  };

  const { server, baseUrl } = await startServer();
  try {
    const response = await nodeFetch(`${baseUrl}/api/ideas`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ prompt: "A study planner" }),
    });

    assert.equal(response.status, 502);
    const payload = await response.json();
    assert.ok(payload.error);
  } finally {
    await stopServer(server);
    restoreProviderEnv();
  }
});

test("POST /api/ideas returns 500 when the provider output doesn't parse into exactly 3 ideas", async () => {
  const nodeFetch = global.fetch;
  mockProviderEnv();
  mockProviderSuccess([{ title: "Only one", description: "Solo idea" }]);

  const { server, baseUrl } = await startServer();
  try {
    const response = await nodeFetch(`${baseUrl}/api/ideas`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ prompt: "A study planner" }),
    });

    assert.equal(response.status, 500);
    const payload = await response.json();
    assert.ok(payload.error);
  } finally {
    await stopServer(server);
    restoreProviderEnv();
  }
});

test("POST /api/ideas never caches: two identical prompts each independently reach the provider", async () => {
  const nodeFetch = global.fetch;
  mockProviderEnv();
  let callCount = 0;
  global.fetch = async () => {
    callCount += 1;
    return {
      ok: true,
      json: async () => ({
        content: [
          {
            type: "text",
            text: JSON.stringify([
              { title: "One", description: "First" },
              { title: "Two", description: "Second" },
              { title: "Three", description: "Third" },
            ]),
          },
        ],
      }),
    };
  };

  const { server, baseUrl } = await startServer();
  try {
    const requestOptions = {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ prompt: "Repeat this exact prompt" }),
    };
    const first = await nodeFetch(`${baseUrl}/api/ideas`, requestOptions);
    const second = await nodeFetch(`${baseUrl}/api/ideas`, requestOptions);

    assert.equal(first.status, 200);
    assert.equal(second.status, 200);
    assert.equal(callCount, 2);
  } finally {
    await stopServer(server);
    restoreProviderEnv();
  }
});
