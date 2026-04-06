---
name: sync
description: Sync brain-kit with the local Claude config directory (~/.claude). Use this skill when the user wants to pull the latest skills/agents/configs from the brain-kit repo into their local Claude setup, push a locally-edited skill back to brain-kit, check what's out of sync, or deploy a specific asset. Trigger on phrases like "sync brain-kit", "deploy skills", "push this skill back", "pull latest", "update my skills", or "what's out of sync".
---

# brain-kit Sync

brain-kit (`~/brain-kit`) is the source of truth for all skills, agents, prompts, and configs. Local copies in `~/.claude` are disposable. The flow is always:

```
remote (GitHub) ←→ ~/brain-kit ←→ ~/.claude
```

---

## Reading device paths

Before running any commands, read `~/brain-kit/claude.md` to get the device-specific paths:
- `brain-kit repo:` → the local clone path (e.g. `~/brain-kit`) → referred to within this skill as `<BRAIN_KIT_PATH>`
- `Claude config dir:` → the local Claude dir (e.g. `~/.claude`) → referred to within this skill as `<CLAUDE_DIR>`

Use those values in all commands below. Never hardcode paths.

---

## Modes

This skill supports four modes, invoked as `/sync <mode>`:

| Mode | What it does |
|------|-------------|
| `/sync pull` | Pull latest from remote → brain-kit, then deploy all assets to `<CLAUDE_DIR>` |
| `/sync push [path...] [message]` | Copy locally-edited files or directories back to brain-kit, commit, and push. No path = sync all changes. |
| `/sync deploy <asset>` | Copy a specific skill/agent/config from brain-kit → `<CLAUDE_DIR>` |
| `/sync status` | Show what differs between brain-kit and `<CLAUDE_DIR>` |
| `/sync help` | Display this command reference |

If invoked without arguments or contextually, infer the right mode from the conversation.

---

## `/sync help`

Print the **Modes** table above as a quick reference. No other output.

---

## `/sync pull` — remote → brain-kit → <CLAUDE_DIR>

Pull the latest from remote, then deploy everything to the local Claude config.

```bash
# 1. Pull latest from remote
cd <BRAIN_KIT_PATH> && git pull origin main

# 2. Deploy skills
cp -r <BRAIN_KIT_PATH>/skills/. <CLAUDE_DIR>/skills/

# 3. Deploy agents (if agents/ exists and has content)
cp -r <BRAIN_KIT_PATH>/agents/. <CLAUDE_DIR>/agents/

# 4. Deploy configs (if configs/ exists and has content)
cp -r <BRAIN_KIT_PATH>/configs/. <CLAUDE_DIR>/

# 5. Deploy references (if references/ exists and has content)
cp -r <BRAIN_KIT_PATH>/references/. <CLAUDE_DIR>/references/

# 6. Deploy scripts (if scripts/ exists and has content)
cp -r <BRAIN_KIT_PATH>/scripts/. <CLAUDE_DIR>/scripts/
```

After pulling, report:
- How many commits were pulled (from git output)
- Which asset types were deployed
- Any directories that were skipped because they were empty

---

## `/sync push [path...] [message]` — local edit → brain-kit → remote

Use this when one or more skills or assets were edited inside `<CLAUDE_DIR>` and the improvements should be persisted to the repo.

`[path...]` is one or more paths relative to `<CLAUDE_DIR>`. Each path can be a file or a directory. Multiple paths are space-separated. If no path is provided, all differing assets are pushed (see no-argument mode below).

### With paths

```bash
# For each specified path:
SRC=<CLAUDE_DIR>/<path>
DEST=<BRAIN_KIT_PATH>/<path>

# 1. Show a diff for each path before touching anything
#    For a file:
diff "$DEST" "$SRC"
#    For a directory:
diff -r "$DEST" "$SRC"

# 2. Ask the user to confirm — the copy will overwrite brain-kit
# 3. Copy each path back (works for files and directories)
cp -r "$SRC" "$(dirname $DEST)/"

# 4. Stage, commit, and push all at once
cd <BRAIN_KIT_PATH>
git add <path1> <path2> ...
git commit -m "<message or auto-generated summary>"
git push origin main
```

If no `[message]` is provided, generate a concise commit message from the combined diff (e.g. `"improve pdf skill: add form annotation handling"`).

### No-argument mode — push all changes

When invoked as `/sync push` with no paths, find everything in `<CLAUDE_DIR>` that differs from brain-kit:

```bash
# Find all differing assets across each asset type
diff -rq --brief <CLAUDE_DIR>/skills <BRAIN_KIT_PATH>/skills
diff -rq --brief <CLAUDE_DIR>/agents <BRAIN_KIT_PATH>/agents
diff -rq --brief <CLAUDE_DIR>/configs <BRAIN_KIT_PATH>/configs
diff -rq --brief <CLAUDE_DIR>/references <BRAIN_KIT_PATH>/references
diff -rq --brief <CLAUDE_DIR>/scripts <BRAIN_KIT_PATH>/scripts
```

1. Show the full list of files that would be pushed
2. **Prompt the user to confirm before proceeding** — this is a bulk overwrite
3. Copy all differing paths back to brain-kit with `cp -r`
4. Stage all changes, commit with an auto-generated summary, and push

**Never commit `claude.md`** — it is gitignored and device-specific. Skip it even if it appears in the diff.

---

## `/sync deploy <asset>` — brain-kit → <CLAUDE_DIR> (single asset)

Use this to deploy one specific skill, agent, config, reference, or script without pulling from remote.

```bash
# Deploy a skill
cp -r <BRAIN_KIT_PATH>/skills/<skill-name> <CLAUDE_DIR>/skills/

# Deploy an agent
cp <BRAIN_KIT_PATH>/agents/<agent-name>.md <CLAUDE_DIR>/agents/

# Deploy a config file
cp <BRAIN_KIT_PATH>/configs/<file> <CLAUDE_DIR>/

# Deploy a reference directory
cp -r <BRAIN_KIT_PATH>/references/<name> <CLAUDE_DIR>/references/

# Deploy a script
cp <BRAIN_KIT_PATH>/scripts/<script-file> <CLAUDE_DIR>/scripts/
```

Confirm the asset exists in brain-kit before copying. If it doesn't exist, report clearly rather than erroring silently.

---

## `/sync status` — what's out of sync

Compare brain-kit against the local Claude config to show what would change on a pull or push.

```bash
# Check for remote commits not yet pulled
cd <BRAIN_KIT_PATH> && git fetch origin main --dry-run

# Show uncommitted local changes in brain-kit
git status --short

# Compare each asset type between brain-kit and <CLAUDE_DIR>
diff -rq --brief <BRAIN_KIT_PATH>/skills <CLAUDE_DIR>/skills
diff -rq --brief <BRAIN_KIT_PATH>/agents <CLAUDE_DIR>/agents
diff -rq --brief <BRAIN_KIT_PATH>/configs <CLAUDE_DIR>/configs
diff -rq --brief <BRAIN_KIT_PATH>/references <CLAUDE_DIR>/references
diff -rq --brief <BRAIN_KIT_PATH>/scripts <CLAUDE_DIR>/scripts
```

Skip any comparison where both sides don't exist or are empty.

Report in three sections:
1. **Remote** — commits available to pull (or "up to date")
2. **brain-kit working tree** — uncommitted edits in the repo itself
3. **Deploy delta** — files in brain-kit that differ from `<CLAUDE_DIR>` (pull would update these), and files in `<CLAUDE_DIR>` that differ from brain-kit (push candidates)

---

## Asset map

| Asset type | brain-kit location | <CLAUDE_DIR> location |
|------------|-------------------|-------------------|
| Skills | `skills/<name>/` | `skills/<name>/` |
| Agents | `agents/<name>.md` | `agents/<name>.md` |
| Configs | `configs/` | root |
| References | `references/<name>/` | `references/<name>/` |
| Scripts | `scripts/` | `scripts/` |
| Prompts | `prompts/` | (project dirs or root) |

---

## Rules

- **Never commit `claude.md`** — it is gitignored and device-specific
- **Never `git init` inside `<CLAUDE_DIR>`** — there is no git repo there
- **Local copies are disposable** — if unsure whether to push or pull, prefer pulling (brain-kit wins)
- **Improvements flow back**: edit in `~/.claude` → `/sync push` → brain-kit → git push → other devices pull
