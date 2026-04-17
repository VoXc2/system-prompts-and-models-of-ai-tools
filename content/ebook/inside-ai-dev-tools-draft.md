# Inside AI Dev Tools: 40+ System Prompts Decoded
### A Practitioner's Guide to How the Best AI Coding Assistants Actually Work

**LeaksLab — 2026 Edition**
*Version 1.0*

---

## About This Book

This guide is for engineers, product builders, and technical founders who want to understand — not just use — AI coding tools.

Everything analyzed here comes from the LeaksLab open library: real system prompts, real tool schemas, real configurations from production AI tools. No speculation. No guessing.

By the end of this book, you will:
- Understand the architectural patterns behind the most successful AI coding tools
- Know exactly how to structure your own agents and system prompts
- Have concrete patterns you can implement immediately
- See the future of AI tooling based on where the industry is heading

---

## Table of Contents

### Part I: The Architecture of Modern AI Tools
1. [Why System Prompts Matter More Than Models](#ch1)
2. [The Anatomy of a Production System Prompt](#ch2)
3. [Tool Schemas: The Real Intelligence Layer](#ch3)

### Part II: The Tools, Decoded
4. [Cursor — The Benchmark](#ch4)
5. [Windsurf — Context-Aware Architecture](#ch5)
6. [Devin AI — Autonomous Agent Design](#ch6)
7. [Claude Code — Safety-First Engineering](#ch7)
8. [v0 by Vercel — Constraint-Driven Excellence](#ch8)
9. [Manus Agent — Multi-Agent Orchestration](#ch9)
10. [GitHub Copilot — The Integration Play](#ch10)
11. [Lovable & Emergent — App Builder Patterns](#ch11)

### Part III: Patterns Worth Stealing
12. [The 7 Universal Patterns Across All Tools](#ch12)
13. [Building Your Own Agent: A Template](#ch13)
14. [Common Mistakes and How to Fix Them](#ch14)

### Appendix
- Full tool list with category classifications
- Prompt engineering checklist
- Further reading and resources

---

## Chapter 1: Why System Prompts Matter More Than Models {#ch1}

There is a common misconception in the AI space: that model quality determines tool quality.

It does not. Not primarily.

Consider this: Cursor, Windsurf, and GitHub Copilot all run on similar underlying models (Claude, GPT-4 variants). Their output quality differs dramatically. The difference is not the model — it is the engineering layer around it.

That engineering layer is the system prompt.

A system prompt is not just a set of instructions. It is an architecture. It defines:

- **Who the AI is** — its identity and behavioral constraints
- **What tools it has** — its capabilities and their precise schemas
- **How it fails** — explicit fallback and recovery behavior
- **What it must not do** — constraint boundaries that define reliability

The companies that have built the best AI tools have treated their system prompts like production code: versioned, tested, iterated, and carefully engineered.

### The Evidence

After analyzing 40+ system prompts, one pattern is undeniable: the tools with the best user experience are the tools with the most thoughtfully engineered prompts.

This is not correlation. It is causation.

When the model receives precise, well-structured instructions, it produces precise, well-structured output. When it receives vague or contradictory instructions, it produces vague and unpredictable output.

The model is not the variable. The prompt is.

### What This Means for You

If you are building AI-powered products, your system prompt deserves the same engineering rigor as your production code.

- Write it with intention
- Test it systematically
- Version it
- Define failure modes explicitly
- Constrain it aggressively

The rest of this book shows you exactly how the best teams do this.

---

## Chapter 2: The Anatomy of a Production System Prompt {#ch2}

After analyzing 40+ production system prompts, a consistent structure emerges. The best prompts have five components, in this order:

### 1. Identity Declaration

The first thing every great system prompt does: establish who the AI is.

**From Cursor:**
> "You are an AI programming assistant..."

**From Devin:**
> "You are Devin, an autonomous AI software engineer..."

**From v0:**
> "You are v0, Vercel's AI-powered UI generator..."

This is not decoration. Identity shapes behavior at every subsequent step. A well-defined identity reduces ambiguity in edge cases — the AI asks "would someone with this identity do this?" and answers accordingly.

**What to steal**: Start every system prompt with a clear, specific identity. Not "You are a helpful assistant." Something precise: "You are a senior backend engineer specializing in distributed systems, working within [company name]'s engineering team."

### 2. Capability Definition

After identity: what can the AI do? This section defines the tools, integrations, and actions available.

The best prompts define capabilities as formal schemas, not prose descriptions.

**Poor (prose):**
> "You can search the codebase when needed."

**Good (schema):**
```json
{
  "name": "codebase_search",
  "description": "Semantic search over the codebase. Use when you need to find code by concept or intent.",
  "parameters": {
    "query": {"type": "string", "description": "Natural language search query"},
    "file_pattern": {"type": "string", "description": "Optional glob pattern to limit search scope"}
  }
}
```

The schema version forces the AI to use the tool correctly. The prose version leaves room for misinterpretation.

**What to steal**: Define every capability as a formal tool schema. Invest the time to write accurate descriptions and parameter constraints.

### 3. Behavioral Rules

With identity and capabilities established, the behavioral rules section answers: how should the AI act within those capabilities?

This is where most amateur prompts fail. They write rules like:
> "Try to be helpful and accurate."

Production prompts write rules like:
> "Do not make any changes beyond what was explicitly requested. If the user asks to fix a bug, fix only that bug. Do not refactor adjacent code. Do not improve naming. Do not add comments."

The difference: specific rules produce specific behavior. Vague rules produce variable behavior.

**What to steal**: Write behavioral rules as specific constraints, not aspirations. Replace "try to" with "always" or "never."

### 4. Failure Modes

This is the most neglected section in amateur prompts and the most carefully engineered section in production prompts.

Every production AI tool has explicit instructions for what to do when:
- A tool call fails
- The task is ambiguous
- The information is insufficient
- The requested action is outside the agent's scope

**Example from a production tool:**
> "If you are unable to complete the task with the available tools, explain specifically what information or capability is missing. Do not attempt the task with insufficient context."

**What to steal**: Write failure mode instructions before you write success path instructions. Ask: "What happens when this goes wrong?" and write that down explicitly.

### 5. Output Format

The final section: exactly how should the AI format its responses?

Production prompts specify:
- Whether to use markdown or plain text
- How to cite sources (file paths, line numbers)
- Response length constraints
- Required vs. optional sections in a response

**What to steal**: Always specify output format explicitly. "Use markdown headers for sections, include file path and line number for every code reference, keep explanations to 3 sentences or fewer unless asked for more."

---

## Chapter 3: Tool Schemas — The Real Intelligence Layer {#ch3}

If you only read one chapter of this book, read this one.

Most discussions of AI tools focus on the prompt text. The tool schemas are more important.

### What is a Tool Schema?

A tool schema is a formal definition of an action the AI can take. It specifies:
- The tool's name
- What it does (description)
- What parameters it accepts
- Which parameters are required vs. optional
- The type and format of each parameter

Here is a simplified example from Cursor's `edit_file` tool:

```json
{
  "name": "edit_file",
  "description": "Make targeted edits to an existing file. Use this for making changes to existing code. Provide the exact lines to change and what to change them to.",
  "parameters": {
    "target_file": {
      "type": "string",
      "description": "Path to the file to edit, relative to workspace root"
    },
    "instructions": {
      "type": "string",
      "description": "A clear description of the edit to make"
    },
    "code_edit": {
      "type": "string",
      "description": "The exact code change in unified diff format"
    }
  },
  "required": ["target_file", "instructions", "code_edit"]
}
```

Notice what this schema accomplishes:
1. It requires the file path (no ambiguity about which file)
2. It requires a human-readable description (forced documentation)
3. It requires diff format (not full file rewrites — smaller, more precise changes)

The schema does not just define what the AI can do. It shapes HOW the AI does it.

### The Cursor Lesson: Two Search Tools

Cursor's most revealing architectural decision: it has two separate search tools.

- `codebase_search` — semantic, vector-based, expensive, finds intent
- `grep_search` — text/regex, fast, cheap, finds exact strings

Why two? Because no single search tool is optimal for all cases.

"Find the authentication logic" → semantic search
"Find every call to `validateToken()`" → text search

Using one tool for both produces worse results and wastes computation. Using two tools, each optimized for its task, produces better results at lower cost.

**The principle**: Tool design is about matching tool capabilities to task characteristics. One generalist tool is almost always worse than two specialist tools.

### Manus Agent: 15 Tools and What It Reveals

Manus Agent has the most extensive tool schema in our library: 15 separate tools including browser control, file system access, code execution, and memory management.

What this reveals about autonomous agent design:

**Separation of concerns is non-negotiable.** With 15 tools, each has a narrow, well-defined purpose. There is no overlap. The AI always knows which tool is appropriate because each tool has a clear, distinct purpose.

**Memory is a first-class concern.** Manus has explicit memory tools — not just for reading context, but for writing and managing it. Long-running autonomous tasks require the agent to track its own state. This is not automatic — it has to be engineered.

**Browser control is structured, not freestyle.** Rather than "use a browser," Manus has discrete tools: `browser_navigate`, `browser_click`, `browser_type`, `browser_screenshot`. Each with precise parameter schemas. This prevents the AI from trying to do browser tasks via terminal or other inappropriate means.

### Building Your Tool Library

Based on the patterns across 40+ tools, here is a minimal but complete tool set for a coding agent:

| Tool | Purpose | Priority |
|------|---------|----------|
| `read_file` | Read file contents | Required |
| `edit_file` | Make targeted code changes | Required |
| `run_command` | Execute shell commands | Required |
| `semantic_search` | Find code by concept/intent | High |
| `text_search` | Find exact strings/patterns | High |
| `list_directory` | Explore project structure | Medium |
| `create_file` | Create new files | Medium |
| `web_fetch` | Read external documentation | Optional |

Start with the Required tier. Add High tier when you have the core working. Optional tier only when you have a clear use case.

---

## Chapter 4: Cursor — The Benchmark {#ch4}

Cursor is the tool every other AI editor is measured against. After analyzing its system prompt, the reasons are clear.

### The Key Design Decisions

**Decision 1: Separation of search modalities**

As covered in Chapter 3, Cursor's dual search (semantic + text) is its most important architectural choice. It costs more to implement. It produces significantly better results.

**Decision 2: The "minimal change" principle**

Cursor's prompt explicitly instructs the AI to make the smallest possible change that solves the problem. This runs counter to what many AI tools do (rewrite everything "for clarity").

The result: Cursor feels safe to use on production code. It does not introduce unexpected changes.

**Decision 3: Mandatory provenance**

Every code reference in a Cursor response includes a file path and line number. This is mandatory, not optional. The prompt enforces it at the instruction level.

This means every suggestion is auditable. Engineers can verify exactly what was changed, why, and where.

**Decision 4: No meta-instructions**

Cursor's prompt has almost no "be helpful, be safe" language. These concerns are delegated to the underlying model. The prompt focuses entirely on operational behavior.

This is efficient. Safety training at the model level is more reliable than prompt-level instructions. Cursor trusts the model for safety and uses the prompt for product behavior.

### What to Apply

From Cursor's architecture, these are the three most directly applicable principles:

1. **Smallest viable change**: Instruct your agent to change only what is asked. Define this explicitly.
2. **Mandatory structured output**: Require source citations in every response. File, line, timestamp — whatever applies to your domain.
3. **Separate safety from product behavior**: Use your system prompt for product-specific behavior. Trust the model for general safety. Do not duplicate concerns.

---

*[Chapters 5-14 continue in the full edition...]*

---

## Appendix A: Complete Tool Index

See the LeaksLab GitHub library for the full, current list:
[github.com/VoXc2/system-prompts-and-models-of-ai-tools](https://github.com/VoXc2/system-prompts-and-models-of-ai-tools)

## Appendix B: Prompt Engineering Checklist

Before shipping any system prompt, verify:

- [ ] Clear identity declaration at the start
- [ ] All capabilities defined as formal tool schemas (not prose)
- [ ] Behavioral rules use "always/never" not "try to/if possible"
- [ ] Failure modes explicitly defined for each tool
- [ ] Output format specified (markdown/plain, citation format, length)
- [ ] Constraints define what NOT to do as clearly as what to do
- [ ] The prompt has been read by someone unfamiliar with the product

---

*LeaksLab — Built for engineers who want to understand how AI tools actually work.*
*github.com/VoXc2/system-prompts-and-models-of-ai-tools*
