const test = require("node:test");
const assert = require("node:assert/strict");

const ORIGINAL_FETCH = global.fetch;
const ORIGINAL_API_KEY = process.env.IDEA_LLM_API_KEY;
const ORIGINAL_MODEL = process.env.ANTHROPIC_MODEL;

function setEnv() {
  process.env.IDEA_LLM_API_KEY = "test-api-key";
  process.env.ANTHROPIC_MODEL = "claude-sonnet-5";
}

function restoreEnv() {
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

function freshIdeaService() {
  delete require.cache[require.resolve("../lib/ideaService")];
  return require("../lib/ideaService");
}

function messagesResponse(ideas) {
  return {
    ok: true,
    json: async () => ({
      content: [{ type: "text", text: JSON.stringify(ideas) }],
    }),
  };
}

test("generateIdeas resolves exactly 3 ideas on a successful provider call", async () => {
  setEnv();
  try {
    const ideas = [
      { title: "One", description: "First idea" },
      { title: "Two", description: "Second idea" },
      { title: "Three", description: "Third idea" },
    ];
    global.fetch = async (url, options) => {
      assert.equal(url, "https://api.anthropic.com/v1/messages");
      assert.equal(options.headers["x-api-key"], "test-api-key");
      assert.ok(options.headers["anthropic-version"]);
      const body = JSON.parse(options.body);
      assert.equal(body.model, "claude-sonnet-5");
      return messagesResponse(ideas);
    };

    const { generateIdeas } = freshIdeaService();
    const result = await generateIdeas("A study planner");
    assert.deepEqual(result, ideas);
  } finally {
    restoreEnv();
  }
});

test("generateIdeas throws with .code = TIMEOUT when the provider call is aborted", async () => {
  setEnv();
  try {
    global.fetch = async (url, options) => {
      return new Promise((resolve, reject) => {
        options.signal.addEventListener("abort", () => {
          const abortError = new Error("The operation was aborted");
          abortError.name = "AbortError";
          reject(abortError);
        });
      });
    };

    const { generateIdeas } = freshIdeaService();

    await assert.rejects(
      () => generateIdeas("A study planner", { timeoutMs: 10 }),
      (error) => {
        assert.equal(error.code, "TIMEOUT");
        return true;
      },
    );
  } finally {
    restoreEnv();
  }
});

test("generateIdeas throws with .code = NETWORK on connection failure", async () => {
  setEnv();
  try {
    global.fetch = async () => {
      throw new Error("connect ECONNREFUSED");
    };

    const { generateIdeas } = freshIdeaService();
    await assert.rejects(
      () => generateIdeas("A study planner"),
      (error) => {
        assert.equal(error.code, "NETWORK");
        return true;
      },
    );
  } finally {
    restoreEnv();
  }
});

test("generateIdeas throws with .code = MALFORMED when fewer than 3 ideas are returned", async () => {
  setEnv();
  try {
    global.fetch = async () =>
      messagesResponse([{ title: "Only one", description: "Solo idea" }]);

    const { generateIdeas } = freshIdeaService();
    await assert.rejects(
      () => generateIdeas("A study planner"),
      (error) => {
        assert.equal(error.code, "MALFORMED");
        return true;
      },
    );
  } finally {
    restoreEnv();
  }
});

test("generateIdeas throws with .code = MALFORMED when more than 3 ideas are returned", async () => {
  setEnv();
  try {
    global.fetch = async () =>
      messagesResponse([
        { title: "One", description: "First" },
        { title: "Two", description: "Second" },
        { title: "Three", description: "Third" },
        { title: "Four", description: "Fourth" },
      ]);

    const { generateIdeas } = freshIdeaService();
    await assert.rejects(
      () => generateIdeas("A study planner"),
      (error) => {
        assert.equal(error.code, "MALFORMED");
        return true;
      },
    );
  } finally {
    restoreEnv();
  }
});

test("generateIdeas throws with .code = MALFORMED when entries are missing title/description", async () => {
  setEnv();
  try {
    global.fetch = async () =>
      messagesResponse([
        { title: "One", description: "First" },
        { title: "Two" },
        { title: "Three", description: "Third" },
      ]);

    const { generateIdeas } = freshIdeaService();
    await assert.rejects(
      () => generateIdeas("A study planner"),
      (error) => {
        assert.equal(error.code, "MALFORMED");
        return true;
      },
    );
  } finally {
    restoreEnv();
  }
});

test("generateIdeas throws with .code = MALFORMED when the provider output isn't valid JSON", async () => {
  setEnv();
  try {
    global.fetch = async () => ({
      ok: true,
      json: async () => ({
        content: [{ type: "text", text: "not json at all" }],
      }),
    });

    const { generateIdeas } = freshIdeaService();
    await assert.rejects(
      () => generateIdeas("A study planner"),
      (error) => {
        assert.equal(error.code, "MALFORMED");
        return true;
      },
    );
  } finally {
    restoreEnv();
  }
});

test("generateIdeas never memoizes: two calls with the identical prompt each hit the provider", async () => {
  setEnv();
  try {
    const ideas = [
      { title: "One", description: "First idea" },
      { title: "Two", description: "Second idea" },
      { title: "Three", description: "Third idea" },
    ];
    let callCount = 0;
    global.fetch = async () => {
      callCount += 1;
      return messagesResponse(ideas);
    };

    const { generateIdeas } = freshIdeaService();
    await generateIdeas("Repeat this exact prompt");
    await generateIdeas("Repeat this exact prompt");

    assert.equal(callCount, 2);
  } finally {
    restoreEnv();
  }
});

test("generateIdeas throws an uncoded error when ANTHROPIC_MODEL is not configured", async () => {
  setEnv();
  delete process.env.ANTHROPIC_MODEL;
  try {
    global.fetch = async () => {
      throw new Error("fetch should not be called");
    };

    const { generateIdeas } = freshIdeaService();
    await assert.rejects(
      () => generateIdeas("A study planner"),
      (error) => {
        assert.equal(error.code, undefined);
        return true;
      },
    );
  } finally {
    restoreEnv();
  }
});
