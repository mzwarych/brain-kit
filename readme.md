# brain-kit

A starter kit for managing Claude Code skills, agents, and configs across devices.

Clone once, make it yours.

*NOTE*: this kit is built for Claude Code. It can be ported over to other providers, but is not supported out of the box.

---

## What it does

I was tired of maintaining skill-bases across work and personal devices and their respective Claude Code instances.
The natural solution was a git-based source of truth, but that comes with managing the repo, and keeping it up to date with any local changes, on any device you might be working on at the time.

brain-kit is a skill-based framework centered around personal AI infrastructure for extensible development of a knowledge base you can pull into any environment you happen to be working in. It handles the heavy lifting of pushing, pulling, copying, overwriting and diffing for you, so you can spend less time syncing, writing and importing skills and more time on whatever it is you do. 

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
# Edit claude.md to fill in your device-specific paths — it's gitignored. this is a one-time per-device setup. all you need to is tell brain-kit where its local repo lives, and where your local AI resources live. 
```

Run `git pull` in `~/brain-kit` to stay in sync as your repo evolves.

---

## Syncing with `/sync`

Once the included skills are deployed, Claude manages the repo for you.

| Command | What it does |
|---------|-------------|
| `/sync pull` | `git pull` from remote, then deploy all assets to `~/.claude` |
| `/sync push <path> [message]` | Copy a locally-edited file back to brain-kit, commit, and push |
| `/sync deploy <asset>` | Deploy one specific skill, agent, or config to `~/.claude` |
| `/sync status` | Show what differs between brain-kit and `~/.claude` |
| `/sync help` | Print the command reference |

---

## Getting more skills

brain-kit ships with `/install-skill` to get you started. There are tons of great resources available publicly (see below) but most of the time you don't want the entire collection. `/install-skill` lets you pull down specific resources from git or the local plugin marketplace, so you get exactly what you need.

*NOTE:* `/install-skill` will pull the specified resource into your local AI resources (`.claude/skills`). Use `/sync push skills/skill-name` to copy it back to brain-kit and commit it.


#### To fetch a new skill from github:
`/install-skill git https://github.com/user/repo skills/skill-name skills/skill-name-2`

#### To fetch a new skill from the local marketplace:
`/install-skill local [keyword]`

As your collection starts to grow, it can become difficult to keep track of what version you have of a given skill, where it came from in the first place, and so on. `/install-skill` manages this for you by creating and updating a `sources.json` file that lives in your local AI skill resource (eg `.claude/skills/sources.json`).

Run `/sync push skills/sources.json` to copy it back to brain-kit and keep your registry in sync.

Some community collections that you can use `/install-skill`  to pull from:

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

If you improve a skill mid-session (edited inside `~/.claude/skills/`), push it back with:

```
/sync push skills/my-skill
```

This copies the entire skill folder back to brain-kit, commits, and pushes. You can also pass multiple paths or individual files:

```
/sync push skills/my-skill agents/my-agent.md
```

Or push everything that's changed at once — Claude will show you the diff and ask for confirmation first:

```
/sync push
```

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
