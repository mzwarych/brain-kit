---
name: install-skill
description: Use this skill whenever the user wants to install, add, or pull in a new Claude Code skill — whether from GitHub, a curated list like VoltAgent/awesome-agent-skills, or the Anthropic skills repo. Trigger any time the user mentions installing a skill, adding a skill from a URL or repo, or asks how to get a specific skill without cloning an entire repo. Also use this when the user asks about skill sources, skill discovery, or how skills end up in ~/.claude/skills/.
---

# Installing Claude Code Skills

Claude Code loads skills from `~/.claude/skills/`. Each skill is a folder with a `SKILL.md` at its root. New skills are picked up automatically — no restart needed.

## Invocation

This skill supports two explicit modes via `$ARGUMENTS`:

- **`/install-skill git <github-url> <path/to/skill>`** — sparse-checkout a skill from a GitHub repo
- **`/install-skill local [keyword]`** — list or search available skills in the local plugin marketplace

If arguments are provided, jump straight to the relevant method below. If invoked without arguments (or contextually), infer the right method from the conversation.

---

## Method 1: From a GitHub repo (sparse checkout)

Use this when the skill lives inside a larger GitHub repo and you don't want to clone the whole thing. Git sparse-checkout lets you materialize only the subdirectories you need.

```bash
# 1. Clone metadata only — no file content yet
git clone --no-checkout --depth=1 --filter=blob:none \
  https://github.com/OWNER/REPO /tmp/skill-temp

# 2. Tell git which paths you want
cd /tmp/skill-temp
git sparse-checkout init --cone
git sparse-checkout set path/to/skill1 path/to/skill2

# 3. Pull down just those files
git checkout

# 4. Copy into your skills directory
cp -r path/to/skill1 ~/.claude/skills/
cp -r path/to/skill2 ~/.claude/skills/

# 5. Clean up
rm -rf /tmp/skill-temp
```

### Anthropic skills repo pattern

The Anthropic skills repo (`https://github.com/anthropics/skills`) keeps all skills under `skills/<skill-name>/`. So to install, say, `pdf` and `xlsx`:

```bash
git clone --no-checkout --depth=1 --filter=blob:none \
  https://github.com/anthropics/skills /tmp/anthropics-skills

cd /tmp/anthropics-skills
git sparse-checkout init --cone
git sparse-checkout set skills/pdf skills/xlsx
git checkout

cp -r skills/pdf ~/.claude/skills/
cp -r skills/xlsx ~/.claude/skills/
rm -rf /tmp/anthropics-skills
```

---

## Method 2: From the local plugin marketplace

Some skills ship bundled with Claude Code plugins. These are already on disk at:

```
~/.claude/plugins/marketplaces/claude-plugins-official/plugins/<plugin-name>/skills/<skill-name>/
```

To activate one, just copy it:

```bash
cp -r ~/.claude/plugins/marketplaces/claude-plugins-official/plugins/<plugin-name>/skills/<skill-name> \
  ~/.claude/skills/
```

To see what's available locally:

```bash
find ~/.claude/plugins/marketplaces -name "SKILL.md" | sed 's|/SKILL.md||' | sed 's|.*/skills/||'
```

---

## Discovering skills

- **Curated list**: https://github.com/VoltAgent/awesome-agent-skills — links out to skill repos from various providers
- **Anthropic skills repo**: https://github.com/anthropics/skills — official skills for PDF, XLSX, and more
- **Local marketplace**: already on disk (see Method 2 above)

---

## Recording the source

After every install, update `~/.claude/skills/sources.json` to log where each skill came from. Create the file if it doesn't exist.

**For a git install**, record the repo URL and the path within that repo:
```json
{
  "pdf": { "type": "git", "repo": "https://github.com/anthropics/skills", "path": "skills/pdf" },
  "xlsx": { "type": "git", "repo": "https://github.com/anthropics/skills", "path": "skills/xlsx" }
}
```

**For a local install**, record the full source path on disk:
```json
{
  "skill-creator": { "type": "local", "path": "~/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator" }
}
```

Merge new entries into the existing file — don't overwrite the whole thing. Use the skill's folder name (i.e. the name it lands in under `~/.claude/skills/`) as the key.

---

## Things to know

- A skill folder **must contain a `SKILL.md`** at its root — that's what Claude Code reads
- Skills activate on the **next message** after copying — no restart needed
- If a skill has a `scripts/` subdirectory, those get copied along automatically with `cp -r`
- To check what's currently installed: `ls ~/.claude/skills/`
