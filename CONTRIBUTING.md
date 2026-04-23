# Contributing to System Prompts & Models of AI Tools

Thanks for your interest in contributing! This is the largest collection of real AI system prompts and tool definitions on GitHub. Here's how you can help grow it.

## How to Contribute

### 1. Add a New AI Tool's System Prompt

Found a system prompt that's not in the collection yet? Submit it!

**Steps:**
1. Fork this repo
2. Create a folder: `Tool Name/`
3. Add the prompt as `system-prompt.md` (or `.txt`)
4. If the tool has function/tool definitions, add them as `tools.json` or `tools.md`
5. Open a PR with title: `Add: [Tool Name] system prompt`

**Format your PR description:**
```
## Tool: [Name]
- **Source:** [How you obtained it — e.g., browser DevTools, API inspection, documentation]
- **Date captured:** [YYYY-MM-DD]
- **Model/Version:** [e.g., GPT-4o, Claude 3.5 Sonnet]
- **Includes tools:** [Yes/No]
```

### 2. Update an Existing Prompt

AI tools update their prompts frequently. If you notice a prompt has changed:

1. Update the file with the new version
2. In your PR, note what changed and when
3. If possible, keep the old version in a `previous-versions/` subfolder

### 3. Report a Missing Tool

Don't have the prompt yourself but know a tool is missing? Open an issue with:
- Tool name and URL
- Why it's notable (user count, unique features, etc.)

## What We're Looking For

**High-value additions:**
- Popular AI coding assistants (IDE plugins, CLI tools)
- AI chat products with unique system prompts
- AI agents with tool/function definitions
- Enterprise AI tools with complex prompt structures

**Quality standards:**
- Must be the actual system prompt (not a guess or recreation)
- Include the date it was captured
- No personal API keys or credentials in the content
- Organize files cleanly in a dedicated folder

## Directory Structure

```
Tool Name/
  system-prompt.md      # The main system prompt
  tools.json            # Tool/function definitions (if available)
  previous-versions/    # Older versions (optional)
    2025-01-system-prompt.md
```

## Code of Conduct

- Don't include credentials, API keys, or personal data
- Credit sources when possible
- Be respectful in issues and PRs
- This is for educational and research purposes

## Questions?

Open an issue or join the [Discord](https://discord.gg/NwzrWErdMU).
