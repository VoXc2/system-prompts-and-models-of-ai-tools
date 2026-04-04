/**
 * Dealix — تحقق شامل: backend (pytest كامل + سيناريوهات الإطلاق) + frontend (lint + vitest + build).
 * التشغيل من جذر salesflow-saas: node scripts/verify-stack.cjs
 */
const { spawnSync } = require("child_process");
const path = require("path");

const root = path.join(__dirname, "..");
const backend = path.join(root, "backend");
const frontend = path.join(root, "frontend");

const testEnv = {
  ...process.env,
  DATABASE_URL: process.env.DATABASE_URL || "sqlite+aiosqlite:///./.verify_dealix.db",
  DEALIX_INTERNAL_API_TOKEN: "",
};

function run(label, command, cwd, env) {
  console.log(`\n── ${label} ──\n`);
  const r = spawnSync(command, {
    cwd,
    env,
    stdio: "inherit",
    shell: true,
  });
  if (r.status !== 0) {
    process.exit(r.status ?? 1);
  }
}

const py =
  process.platform === "win32"
    ? "py -3 -m pytest tests -q --tb=line"
    : "python3 -m pytest tests -q --tb=line";
const launch =
  process.platform === "win32"
    ? "py -3 -m pytest -m launch -q --tb=line"
    : "python3 -m pytest -m launch -q --tb=line";

run("Backend: pytest (full)", py, backend, testEnv);
run("Backend: pytest (-m launch)", launch, backend, testEnv);
run("Frontend: npm run verify", "npm run verify", frontend, process.env);

console.log("\n✅ verify-stack: اكتمل التحقق بنجاح.\n");
