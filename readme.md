# brain-kit

A starter kit for managing Claude Code skills, agents, and configs across devices.

Clone once, make it yours.

---

## What's included

| Skill | What it does |
|-------|-------------|
| `/sync` | Pull updates from your brain-kit repo into `~/.claude`, push local edits back, deploy individual assets, or check what's out of sync |
| `/install-skill` | Discover and install skills from GitHub repos, the Anthropic skills repo, or the local plugin marketplace |

Everything else — agents, references, prompts, scripts, configs — is yours to fill in.

---

## Getting started

brain-kit is a **template repository**. Click **"Use this template"** to create your own private copy, then:

```bash
# 1. Clone your copy to a stable location
git clone https://github.com/YOUR_USERNAME/brain-kit.git ~/brain-kit

# 2. Deploy the included skills
cp -r ~/brain-kit/skills/. ~/.claude/skills/

# 3. Set up your local Claude instructions
cp ~/brain-kit/claude.md.template ~/brain-kit/claude.md
# Edit claude.md to fill in your device-specific paths — it's gitignored
```

Run `git pull` in `~/brain-kit` to stay in sync as your repo evolves.

---

## Syncing with `/sync`

Once the skills are deployed, Claude manages the repo for you.

| Command | What it does |
|---------|-------------|
| `/sync pull` | `git pull` from remote, then deploy all assets to `~/.claude` |
| `/sync push <path> [message]` | Copy a locally-edited file back to brain-kit, commit, and push |
| `/sync deploy <asset>` | Deploy one specific skill, agent, or config to `~/.claude` |
| `/sync status` | Show what differs between brain-kit and `~/.claude` |
| `/sync help` | Print the command reference |

---

## Getting more skills

brain-kit ships with `/sync` and `/install-skill` to get you started. Use `/install-skill` to pull in more from the community:

- **[Anthropic skills](https://github.com/anthropics/skills)** — official skills for PDF, XLSX, and more
- **[everything-claude-code](https://github.com/affaan-m/everything-claude-code)** — frontend, backend, Python, API design patterns
- **[awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)** — curated list of community skills

---

## Adding your own content

```
brain-kit/
├── skills/       # Skill packs (each with a SKILL.md)
├── agents/       # Standalone agent instruction files
├── references/   # Schemas, reference docs, data files
├── prompts/      # Reusable prompt snippets
├── scripts/      # Utility scripts
└── configs/      # Claude Code settings and MCP configs
```

To add a new skill, create the folder and SKILL.md in `~/brain-kit`, then ask Claude to commit and push it:

> "commit and push the new my-skill skill"

Or manually:

```bash
mkdir skills/my-skill
# create skills/my-skill/SKILL.md
git add skills/my-skill/
git commit -m "add my-skill"
git push origin main
```

If you improve a skill mid-session (edited inside `~/.claude/skills/`), use `/sync push skills/my-skill/SKILL.md` to copy it back, commit, and push in one step.

---

## Multi-device setup

On each new device, clone your repo and do the initial deploy:

```bash
git clone https://github.com/YOUR_USERNAME/brain-kit.git ~/brain-kit
cp -r ~/brain-kit/skills/. ~/.claude/skills/
cp ~/brain-kit/claude.md.template ~/brain-kit/claude.md
# Fill in device-specific paths in claude.md
```

After that, `/sync pull` handles everything — pulling the latest from remote and deploying all assets to `~/.claude` in one step.
