const { execSync } = require("child_process");
const fs = require("fs");

const configPath = "_bmad/custom/project.json";
if (!fs.existsSync(configPath)) {
  console.error(
    "[bmad-hook] _bmad/custom/project.json not found — cannot resolve project name. Skipping status-revert check.",
  );
  process.exit(0); // don't block the commit over this
}
const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
const projectName = config.project_name;
if (!projectName) {
  console.error(
    "[bmad-hook] project_name missing from project.json — skipping status-revert check.",
  );
  process.exit(0);
}

const logPath = `_bmad-output/${projectName}-project-log.csv`;

function logAction(action) {
  const now = new Date();
  const date = now.toISOString().slice(0, 10);
  const time = now.toTimeString().slice(0, 8);
  const gitUser = execSync("git config user.name").toString().trim();

  if (!fs.existsSync(logPath)) {
    fs.writeFileSync(logPath, "date,time,bmad_user,action\n");
  }
  const escaped = action.includes(",") ? `"${action}"` : action;
  fs.appendFileSync(logPath, `${date},${time},${gitUser},${escaped}\n`);
}

const staged = execSync("git diff --cached --name-only").toString().split("\n");
const briefFiles = staged.filter((f) => /brief-.*\/brief\.md$/.test(f));

for (const file of briefFiles) {
  if (!fs.existsSync(file)) continue;

  const diff = execSync(`git diff --cached -- "${file}"`).toString();
  const nonStatusChange = diff
    .split("\n")
    .some(
      (line) =>
        (line.startsWith("+") || line.startsWith("-")) &&
        !line.match(/^[+-]status:/) &&
        !line.startsWith("+++") &&
        !line.startsWith("---"),
    );

  if (!nonStatusChange) continue;

  let content = fs.readFileSync(file, "utf8");
  if (/status:\s*approved/.test(content)) {
    content = content.replace(/status:\s*approved/, "status: draft");
    fs.writeFileSync(file, content);
    execSync(`git add "${file}"`);
    logAction(
      `Brief updated outside approval flow - status reverted to draft (${file})`,
    );
    console.log(
      `[bmad-hook] ${file}: reverted status to draft (content changed after approval).`,
    );
  }
}
