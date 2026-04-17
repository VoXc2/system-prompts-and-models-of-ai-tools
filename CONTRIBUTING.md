# Contributing to LeaksLab

Thank you for helping grow the most complete AI system prompt library on GitHub.

## What We Accept

### High Priority
- **New AI tool system prompts** not yet in the library
- **Updated versions** of existing prompts (tools update frequently)
- **Tool schemas** (JSON function/tool definitions used by AI agents)
- **Model configurations** (context window, temperature settings, model identifiers)

### Also Accepted
- Fixes to formatting or encoding issues
- Better organization within existing directories
- Additional analysis or documentation for existing tools

### Not Accepted
- Proprietary code, weights, or model binaries
- Content that violates a tool's Terms of Service in a harmful way
- Fabricated or AI-generated "fake" prompts
- Duplicate content without clear differentiation

---

## How to Contribute

### 1. Fork the Repository

```bash
git clone https://github.com/VoXc2/system-prompts-and-models-of-ai-tools.git
cd system-prompts-and-models-of-ai-tools
```

### 2. Add Your Files

**Directory structure:**
```
Tool Name/
  system_prompt.md          # The system prompt (required)
  tools.json                # Tool/function schemas if available (optional)
  model.md                  # Model info (optional)
  README.md                 # Brief notes about source/version (optional)
```

**Naming conventions:**
- Use the tool's official name for the directory
- `system_prompt.md` for the main system prompt
- `tools.json` for tool/function schemas
- `model.md` for model configuration info

### 3. Update the README Index

Add your tool to the appropriate table in `README.md`:

```markdown
| Tool Name | ✅ | ✅ | Category | `Tool Name/` |
```

Categories: `Coding Agent` | `Browser AI` | `General AI` | `Autonomous Agent` | `App Builder` | `Productivity AI` | `Terminal AI` | `UI Generator` | `Search AI`

### 4. Open a Pull Request

**PR title format:** `Add [Tool Name] system prompt` or `Update [Tool Name] to v[version]`

**PR description should include:**
- Where the prompt came from (public disclosure, your own extraction, community research)
- Version/date of the prompt if known
- Any interesting patterns or notable aspects worth highlighting

---

## Quality Standards

### For System Prompts
- Must be the actual system prompt, not a paraphrase
- Include the full prompt — partial prompts are less useful
- Preserve exact formatting (whitespace, line breaks matter in prompts)
- Mark clearly if it's a partial extraction

### For Tool Schemas
- Use valid JSON
- Include all available fields (name, description, parameters)
- If extracted programmatically, note the extraction method

### For README Updates
- Keep the table alphabetically sorted within each section
- Use the exact category labels listed above
- Link to the correct directory path

---

## Code of Conduct

- Be respectful to other contributors
- Don't claim credit for others' work
- If you're submitting content originally found/extracted by someone else, credit them in the PR description
- No spam PRs — quality over quantity

---

## Questions?

Open a [GitHub Discussion](https://github.com/VoXc2/system-prompts-and-models-of-ai-tools/discussions) and we'll help.

---

Thank you for contributing. Every prompt added helps engineers worldwide build better AI products.
