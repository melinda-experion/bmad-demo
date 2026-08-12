const http = require("http");
const fs = require("fs");
const path = require("path");
const { generateIdeas } = require("./lib/ideaService");

const publicDir = path.join(__dirname, "public");

const ERROR_CODE_STATUS = {
  TIMEOUT: 504,
  NETWORK: 502,
  MALFORMED: 500,
};

const MAX_PROMPT_LENGTH = 2000;

function sendFile(res, filePath, contentType) {
  fs.readFile(filePath, (error, content) => {
    if (error) {
      res.writeHead(404, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "Not found" }));
      return;
    }

    res.writeHead(200, { "Content-Type": contentType });
    res.end(content);
  });
}

function createServer() {
  const server = http.createServer((req, res) => {
    if (req.method === "POST" && req.url === "/api/ideas") {
      let body = "";
      req.on("data", (chunk) => {
        body += chunk;
      });
      req.on("end", async () => {
        let payload = {};
        try {
          payload = body ? JSON.parse(body) : {};
        } catch {
          res.writeHead(400, { "Content-Type": "application/json" });
          res.end(
            JSON.stringify({
              error: "Prompt is required and must not be empty",
            }),
          );
          return;
        }

        const prompt =
          typeof payload.prompt === "string" ? payload.prompt.trim() : "";
        if (!prompt) {
          res.writeHead(400, { "Content-Type": "application/json" });
          res.end(
            JSON.stringify({
              error: "Prompt is required and must not be empty",
            }),
          );
          return;
        }

        if (prompt.length > MAX_PROMPT_LENGTH) {
          res.writeHead(400, { "Content-Type": "application/json" });
          res.end(
            JSON.stringify({
              error: `Prompt must not exceed ${MAX_PROMPT_LENGTH} characters`,
            }),
          );
          return;
        }

        try {
          const ideas = await generateIdeas(prompt);
          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ ideas }));
        } catch (err) {
          const status = ERROR_CODE_STATUS[err.code] || 500;
          res.writeHead(status, { "Content-Type": "application/json" });
          res.end(
            JSON.stringify({ error: "Ideas couldn't generate. Try again." }),
          );
        }
      });
      return;
    }

    if (req.method === "GET") {
      if (req.url === "/") {
        sendFile(
          res,
          path.join(publicDir, "index.html"),
          "text/html; charset=utf-8",
        );
        return;
      }

      if (req.url === "/styles.css") {
        sendFile(
          res,
          path.join(publicDir, "styles.css"),
          "text/css; charset=utf-8",
        );
        return;
      }

      if (req.url === "/app.js") {
        sendFile(
          res,
          path.join(publicDir, "app.js"),
          "application/javascript; charset=utf-8",
        );
        return;
      }
    }

    res.writeHead(404, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "Not found" }));
  });

  return server;
}

if (require.main === module) {
  const port = process.env.PORT || 3000;
  const server = createServer();
  server.listen(port, () => {
    console.log(`Server listening on http://localhost:${port}`);
  });
}

module.exports = { createServer };
