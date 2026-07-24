const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

// --- Resolve BMAD user_name (not git identity) ---
function resolveBmadUser() {
  const candidates = ["_bmad/config.user.yaml", "_bmad/config.yaml"];
  for (const file of candidates) {
    if (!fs.existsSync(file)) continue;
    const text = fs.readFileSync(file, "utf8");
    const match = text.match(/^user_name:\s*(.+)$/m);
    if (match && match[1].trim()) {
      return match[1].trim();
    }
  }
  return "unknown-bmad-user";
}

// --- Resolve project_name (same source the skill uses) ---
function resolveProjectName() {
  const configPath = "_bmad/custom/project.json";
  if (!fs.existsSync(configPath)) return null;
  const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
  return config.project_name || null;
}

// --- Log via the canonical Python script, not duplicated JS logic ---
function logAction(action) {
  const projectName = resolveProjectName();
  const bmadUser = resolveBmadUser();
  if (!projectName) {
    console.error(
      "[bmad-hook] project_name not resolved — skipping log entry.",
    );
    return;
  }

  const scriptPath = "skills/agent-project-logger/scripts/log_action.py"; // adjust if the actual path differs
  const outputDir = "_bmad-output";

  try {
    execSync(
      `python "${scriptPath}" --project-name "${projectName}" --action "${action}" --user "${bmadUser}" --output-dir "${outputDir}"`,
      { stdio: "inherit" },
    );
  } catch (err) {
    console.error("[bmad-hook] Failed to write log entry:", err.message);
  }
}

// doc_type -> {pattern matching its staged path, human label for log messages}
const DOC_TYPES = [
  { pattern: /brief-.*\/brief\.md$/, label: "Brief" },
  { pattern: /prd-.*\/prd\.md$/, label: "PRD" },
  { pattern: /architecture-.*\/ARCHITECTURE-SPINE\.md$/, label: "Architecture" },
];

const projectName = resolveProjectName();
const staged = execSync("git diff --cached --name-only").toString().split("\n");

for (const { pattern, label } of DOC_TYPES) {
  const matchedFiles = staged.filter((f) => pattern.test(f));

  for (const file of matchedFiles) {
    if (!fs.existsSync(file)) continue;

    const diff = execSync(`git diff --cached -- "${file}"`).toString();
    const nonStatusChange = diff
      .split("\n")
      .some(
        (line) =>
          (line.startsWith("+") || line.startsWith("-")) &&
          !line.match(/^[+-]approval_status:/) &&
          !line.match(/^[+-]version:/) &&
          !line.startsWith("+++") &&
          !line.startsWith("---"),
      );

    if (!nonStatusChange) continue;

    let content = fs.readFileSync(file, "utf8");
    if (/approval_status:\s*approved/.test(content)) {
      content = content.replace(/approval_status:\s*approved/, "approval_status: draft");
      fs.writeFileSync(file, content);
      execSync(`git add "${file}"`);
      logAction(
        `${label} updated outside approval flow - status reverted to draft (${file})`,
      );
      console.log(
        `[bmad-hook] ${file}: reverted status to draft (content changed after approval).`,
      );
    }
  }
}
