# Claude Code — Token Optimization Tools & Ecosystem Repos

A curated list of community repositories that reduce token consumption, optimize context, and improve efficiency when working with **Claude Code** (Anthropic's CLI / IDE coding agent).

These tools work as CLI proxies, plugins, hooks, MCP servers, skills, or drop-in `CLAUDE.md` configurations. Most are installable in minutes.

---

## 1. RTK — Rust Token Killer  *(currently the most impactful)*

- **Repo:** https://github.com/rtk-ai/rtk
- **Type:** CLI proxy
- **What it does:** Filters and compresses the output of shell commands (`git status`, `cargo test`, `ls`, `npm run`, etc.) **before** they enter Claude Code's context window.
- **Reported savings:** 60–90% on tool-call tokens (some users report ~89% savings within weeks).
- **Install:**
  ```bash
  brew install rtk-ai/tap/rtk
  # or via curl script — see repo README
  ```
- **Integration:** Supports an automatic hook with Claude Code.
- **Best for:** Projects with frequent terminal tool calls (builds, tests, git operations).

---

## 2. token-optimizer  *(alexgreensh)*

- **Repo:** https://github.com/alexgreensh/token-optimizer
- **Type:** Claude Code plugin
- **What it does:**
  - Detects "ghost tokens" (hidden/unused tokens inflating context)
  - Optimizes context retention across `/compact`
  - Survives compaction events
  - Ships with a local dashboard for visibility
- **Focus:** Preserving context **quality** while reducing token count.

---

## 3. claude-token-saver  *(Supersynergy)*

- **Repo:** https://github.com/Supersynergy/claude-token-saver
- **Type:** All-in-one bundle
- **Bundles:** Vault + RTK + context-mode + shellfirm
- **Reported savings:** 4–5 million tokens per month according to user reports
- **Install:**
  ```bash
  /sm init
  ```
- **Best for:** Users who want a single opinionated setup that combines several optimization strategies.

---

## 4. claude-token-efficient

- **Repo:** https://github.com/drona23/claude-token-efficient
- **Type:** Drop-in `CLAUDE.md`
- **What it does:** A single `CLAUDE.md` file that instructs Claude to produce terser, more concise responses.
- **Install:** Copy `CLAUDE.md` to your project root. No code changes required.
- **Best for:** Quick wins without installing any tooling.

---

## 5. claude-token-optimizer  *(nadimtuhin)*

- **Repo:** https://github.com/nadimtuhin/claude-token-optimizer
- **Type:** Pre-built prompt templates
- **What it does:** Ready-to-use prompt configurations that can save up to ~90% of tokens on a project in under 5 minutes.
- **Best for:** Fast project onboarding with immediate token savings.

---

## 6. headroom

- **Repo:** https://github.com/chopratejas/headroom
- **Type:** Context Optimization Engine
- **What it does:**
  - Image compression for multimodal inputs
  - Memory persistence across sessions
  - Long-context optimization
- **Best for:** Long-running sessions and projects with heavy image / document context.

---

## Additional Ecosystem Projects

### claude-code-prompt-optimizer  *(johnpsasser)*
- **Repo:** https://github.com/johnpsasser/claude-code-prompt-optimizer
- **Type:** Claude Code hook
- **What it does:** Automatically rewrites / optimizes prompts before they are sent.

### prompt-optimizer  *(Hashaam101)*
- **Repo:** https://github.com/Hashaam101/prompt-optimizer
- **Type:** Claude Code skill
- **What it does:** Automatic in-session prompt optimization as a registered skill.

### token-optimizer-mcp  *(ooples)*
- **Repo:** https://github.com/ooples/token-optimizer-mcp
- **Type:** MCP server
- **What it does:** Intelligent optimization via the Model Context Protocol, with caching and compression.

---

## Quick Tips for Claude Code Users

1. **Start with RTK.** It has the biggest impact because it targets tool-call output, which is the single largest source of token bloat in agentic coding sessions.
2. **Add a `CLAUDE.md`** to your project root with clear instructions about brevity, response structure, and formatting expectations.
3. **Use `/compact` and `/clear` regularly** inside Claude Code to manage context proactively.
4. **Start a new session every 15–20 messages** when possible — fresh sessions are cheaper and more focused than long compacted ones.
5. **Combine RTK + token-optimizer** for the best results: RTK handles shell output, token-optimizer handles context preservation.

---

## Comparison at a Glance

| Tool | Type | Primary Target | Install Effort | Est. Savings |
|---|---|---|---|---|
| RTK | CLI proxy | Tool-call output | Low (brew/curl) | 60–90% |
| token-optimizer | Plugin | Context / ghost tokens | Medium | Variable |
| claude-token-saver | Bundle | All layers | Low (`/sm init`) | 4–5M tokens/mo |
| claude-token-efficient | `CLAUDE.md` | Response verbosity | Very low (copy file) | Moderate |
| claude-token-optimizer | Prompt templates | Project prompts | Very low | Up to 90% |
| headroom | Engine | Long context, images | Medium | Large on long sessions |
| claude-code-prompt-optimizer | Hook | Outgoing prompts | Low | Small–medium |
| prompt-optimizer | Skill | In-session prompts | Low | Small–medium |
| token-optimizer-mcp | MCP server | Cross-tool caching | Medium | Medium–large |

---

## Notes

- All repositories listed above are community-maintained and independent from Anthropic. Check each repo's README for the latest install instructions, license, and compatibility notes before using.
- Savings figures are self-reported by repo authors and users; real-world impact depends heavily on project size, workload type, and usage patterns.
- This list is part of the `system-prompts-and-models-of-ai-tools` archive and is intended as a **reference index**, not an endorsement.
