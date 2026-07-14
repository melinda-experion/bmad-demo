const fs = require("fs");
const path = require("path");
const vm = require("vm");
const test = require("node:test");
const assert = require("node:assert/strict");
const { createServer } = require("../server");

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
  const { server, baseUrl } = await startServer();
  try {
    const response = await fetch(`${baseUrl}/api/ideas`, {
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
