---
name: bk-view
description: Open the brain-kit HTML dashboard — a visual file explorer with resource counts (skills, agents, prompts, etc.) and a GitHub-style file preview. Use when the user wants to browse their brain-kit, view skill contents, or get an overview of what's in the kit.
---

# brain-kit Visual Dashboard

Opens a live dashboard in the browser: resource stats at the top, a collapsible file tree on the left, and a file preview on the right. Rescans the directory on every page refresh — always up to date.

## Steps

1. Read `~/brain-kit/claude.md` to get `<BRAIN_KIT_PATH>` (the `brain-kit repo:` line).

2. Run the dashboard in serve mode (rescans on every refresh):
   ```
   python3 <BRAIN_KIT_PATH>/scripts/bk-dashboard.py --serve <BRAIN_KIT_PATH>
   ```
   This starts a local HTTP server at `http://localhost:7821` and opens the browser automatically.

3. Report the URL to the user and confirm the browser launched.

## Notes

- `--serve` starts a local HTTP server (port 7821 by default) — page refresh always reflects the latest files.
- Use a custom port if needed: `--serve 8080`
- The server runs until Ctrl-C. For a one-shot static file instead, use `--open` (no refresh support).
- On WSL: the script detects WSL automatically and opens the URL in the Windows default browser.
- If the browser doesn't open automatically (e.g. headless environment), tell the user to open `http://localhost:7821` manually.
- If `claude.md` doesn't exist yet, ask the user to set it up from `claude.md.template` first.
