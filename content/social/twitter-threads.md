# Twitter/X Thread Drafts — LeaksLab

---

## Thread 1: Cursor's System Prompt (Technical Breakdown)
**Best time to post**: Tuesday/Wednesday morning

---

🧵 I read Cursor's full system prompt so you don't have to.

Here are the 7 most important things it reveals about how to build a production AI coding agent:

1/8

---

Cursor gives its AI **8 specialized tools**. Not 1 catch-all tool. Not "search the internet". 8 specific, purpose-built tools.

This single architectural decision is why Cursor feels smarter than most AI editors.

2/8

---

The 8 tools are:
- `codebase_search` (semantic)
- `grep_search` (text/regex)
- `read_file`
- `edit_file`
- `run_terminal_cmd`
- `list_dir`
- `file_search`
- `web_fetch`

Notice the two search tools. Semantic AND text. Most builders use one. Cursor uses both. Here's why that matters 👇

3/8

---

Semantic search = expensive, slow, finds intent
Text search = cheap, fast, finds exact strings

Having both means the AI can say:
- "I need to find the login logic" → semantic
- "I need to find every `console.log`" → text

One decision. Massive performance difference.

4/8

---

The prompt has an entire section on what NOT to do.

"Do not be excessively helpful."
"Do not make changes beyond what was asked."
"Do not explain code unless asked."

This is counterintuitive. But it's why Cursor doesn't rewrite your entire codebase when you ask it to fix a typo.

5/8

---

Every code reference requires a file path + line number.

This sounds obvious but almost no one enforces it.

The result: every suggestion is auditable. You can always trace what changed, why, and where.

6/8

---

The safety layer (be helpful, be harmless) is almost completely absent.

Because that's handled at the model level — Claude/GPT training.

The prompt is purely operational. This is why Cursor feels fast and decisive. No wasted tokens on meta-instructions.

7/8

---

Three things to steal for your own agent builds:

1. Separate cheap tools from expensive ones
2. Require structured output with provenance (file + line)
3. Define what the agent should NOT do as clearly as what it should

Full breakdown + all 40+ tool prompts: [github.com/VoXc2/system-prompts-and-models-of-ai-tools]

8/8

---

## Thread 2: What 40 System Prompts Taught Me
**Best time to post**: Monday morning or Thursday

---

🧵 I read the system prompts of 40+ AI tools.

Cursor, Windsurf, Devin, Claude Code, v0, Manus, ChatGPT, Lovable...

Here are the 5 patterns that appear in every successful one:

1/7

---

**Pattern 1: Identity before instructions**

Every great system prompt starts with WHO the AI is, not WHAT it should do.

"You are a senior software engineer..."
"You are an autonomous coding agent..."

Identity shapes every downstream behavior. Start there.

2/7

---

**Pattern 2: Explicit failure modes**

The best prompts don't assume the AI will succeed. They define exactly what to do when it fails.

Most prompts I've seen from startups have zero failure instructions. The result: the AI improvises badly.

3/7

---

**Pattern 3: Tool schemas > prose instructions**

"You can search the codebase" vs a full JSON tool schema with parameter descriptions.

Every production system uses schemas. Every prototype uses prose.

Schemas force precision. Prose allows drift.

4/7

---

**Pattern 4: Scope constraints**

v0 by Vercel has explicit rules about React/Tailwind/shadcn. It will not generate raw CSS. It will not use other UI frameworks.

Constraints make AI more predictable. Unconstrained AI is unreliable AI.

5/7

---

**Pattern 5: The "no more than asked" rule**

Cursor, Devin, Claude Code — all have explicit instructions to do exactly what was asked. Nothing more.

This is the most underrated principle in prompt engineering.

6/7

---

All 40+ system prompts are free in our library.

We add new tools every week.

⭐ Star it and help us reach every AI engineer building in 2026:
[github.com/VoXc2/system-prompts-and-models-of-ai-tools]

7/7

---

## Thread 3: Devin AI Breakdown
**Best time to post**: Weekend or Friday

---

🧵 Devin AI bills itself as a "fully autonomous software engineer."

Its system prompt reveals exactly how that autonomy is engineered.

This is what $21M in VC funding looks like in text form:

1/6

---

Devin's prompt is structured around **tasks, not conversations**.

Most AI tools are built for back-and-forth dialogue. Devin assumes it will run for hours, autonomously, with minimal human input.

This changes everything about how the prompt is written.

2/6

---

The task decomposition section is explicit:

1. Understand the full requirement
2. Break into sub-tasks
3. Estimate dependencies
4. Execute in order
5. Verify each step before moving forward

This is just software engineering methodology. But written into a prompt, it becomes autonomous execution.

3/6

---

Failure recovery has three levels:

1. Retry the same approach
2. Try an alternative approach
3. Ask the human

Most AI tools jump to level 3 immediately. Devin tries levels 1 and 2 first.

This is why it feels more autonomous — it has been told to be.

4/6

---

Context management is a core part of the prompt.

Devin explicitly tracks:
- What has been completed
- What is in progress
- What is blocked and why
- What the human needs to review

This is state management. In a text prompt. It works because it's explicit.

5/6

---

The full Devin prompt + 39 other tools are in our free library.

If you are building autonomous agents, there is no better reference material.

[github.com/VoXc2/system-prompts-and-models-of-ai-tools]

6/6
