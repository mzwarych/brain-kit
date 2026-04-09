#!/usr/bin/env python3
"""
brain-kit dashboard generator

Usage:
  python3 scripts/bk-dashboard.py [--open] [--serve [PORT]] [path/to/brain-kit]

  --open          Launch in default browser immediately
  --serve [PORT]  Start a local HTTP server (default port 7821) that rescans
                  on every page refresh — no stale data. Implies --open.
  path            Path to brain-kit root (default: two levels up from script)
"""

import json
import os
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {".git", "__pycache__", ".DS_Store", "node_modules"}
SKIP_FILES = {".gitkeep", ".DS_Store"}
CATEGORY_DIRS = ["skills", "agents", "prompts", "configs", "references", "scripts"]
MAX_FILE_BYTES = 512 * 1024  # 512 KB — skip binary/huge files


def scan_tree(root: Path):
    """Return (tree, files, counts).
    tree: nested dict representing directory structure
    files: {rel_path: content_string}
    counts: {category: int}
    """
    files = {}
    counts = {cat: 0 for cat in CATEGORY_DIRS}

    def _walk(path: Path, rel: str):
        entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        node = {"_type": "dir", "_children": {}}
        for entry in entries:
            if entry.name in SKIP_DIRS or entry.name in SKIP_FILES:
                continue
            entry_rel = f"{rel}/{entry.name}" if rel else entry.name
            if entry.is_dir():
                node["_children"][entry.name] = _walk(entry, entry_rel)
                # count top-level category dirs
                if rel == "" and entry.name in counts:
                    # count direct children that are not .gitkeep
                    count = sum(
                        1 for c in entry.iterdir()
                        if c.name not in SKIP_FILES and c.name not in SKIP_DIRS
                    )
                    counts[entry.name] = count
            else:
                file_node = {"_type": "file"}
                try:
                    if entry.stat().st_size <= MAX_FILE_BYTES:
                        content = entry.read_text(encoding="utf-8", errors="replace")
                    else:
                        content = f"[File too large to preview: {entry.stat().st_size // 1024} KB]"
                    files[entry_rel] = content
                except Exception as e:
                    files[entry_rel] = f"[Could not read file: {e}]"
                node["_children"][entry.name] = file_node
        return node

    tree = _walk(root, "")
    return tree, files, counts


def generate_html(root: Path, tree: dict, files: dict, counts: dict) -> str:
    def js_safe(obj):
        return json.dumps(obj, ensure_ascii=False).replace('</', '<\\/')

    tree_json = js_safe(tree)
    files_json = js_safe(files)
    counts_json = js_safe(counts)
    kit_name = root.name

    return rf"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{kit_name} dashboard</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --bg: #0d1117;
    --surface: #161b22;
    --border: #30363d;
    --text: #e6edf3;
    --muted: #8b949e;
    --accent: #58a6ff;
    --accent-dim: #1f3d6e;
    --green: #3fb950;
    --yellow: #d29922;
    --purple: #bc8cff;
    --orange: #f0883e;
    --pink: #f778ba;
    --red: #ff7b72;
    --code-bg: #1f2937;
    --hover: #21262d;
    --selected: #1d3a6b;
    --selected-border: #58a6ff;
  }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
    font-size: 14px;
    line-height: 1.5;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }}

  /* ── Header ── */
  header {{
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 12px 20px;
    display: flex;
    align-items: center;
    gap: 20px;
    flex-shrink: 0;
  }}

  .kit-name {{
    font-size: 16px;
    font-weight: 600;
    color: var(--text);
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  .kit-name span {{ color: var(--accent); }}

  .stats {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-left: 8px;
  }}

  .stat {{
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 20px;
    border: 1px solid var(--border);
    background: var(--bg);
    font-size: 12px;
    color: var(--muted);
    white-space: nowrap;
  }}

  .stat.active {{
    border-color: var(--accent-dim);
    background: rgba(88, 166, 255, 0.07);
    color: var(--text);
  }}

  .stat .dot {{
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--muted);
    flex-shrink: 0;
  }}

  .stat.active .dot {{ background: var(--green); }}

  .stat-count {{
    font-weight: 600;
  }}

  .stat-label {{ color: var(--muted); }}

  .header-right {{
    margin-left: auto;
    font-size: 12px;
    color: var(--muted);
  }}

  /* ── Body layout ── */
  .body {{
    display: flex;
    flex: 1;
    overflow: hidden;
  }}

  /* ── File Tree ── */
  .tree-panel {{
    width: 260px;
    min-width: 180px;
    max-width: 400px;
    background: var(--surface);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    flex-shrink: 0;
    resize: horizontal;
  }}

  .panel-header {{
    padding: 10px 14px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }}

  .tree-scroll {{
    overflow-y: auto;
    flex: 1;
    padding: 6px 0;
  }}

  .tree-scroll::-webkit-scrollbar {{ width: 6px; }}
  .tree-scroll::-webkit-scrollbar-track {{ background: transparent; }}
  .tree-scroll::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}

  .tree-item {{
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 3px 8px;
    cursor: pointer;
    border-left: 2px solid transparent;
    user-select: none;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}

  .tree-item:hover {{ background: var(--hover); }}

  .tree-item.selected {{
    background: var(--selected);
    border-left-color: var(--selected-border);
    color: var(--accent);
  }}

  .tree-item .chevron {{
    font-size: 10px;
    width: 14px;
    text-align: center;
    color: var(--muted);
    flex-shrink: 0;
    transition: transform 0.15s;
  }}

  .tree-item.open .chevron {{ transform: rotate(90deg); }}

  .tree-item .icon {{ flex-shrink: 0; font-size: 13px; }}

  .tree-item .name {{
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: 13px;
  }}

  .tree-children {{ display: none; }}
  .tree-children.open {{ display: block; }}

  /* ── Preview Panel ── */
  .preview-panel {{
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }}

  .preview-header {{
    padding: 10px 16px;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
    min-height: 41px;
  }}

  .breadcrumb {{
    font-size: 13px;
    color: var(--muted);
    display: flex;
    align-items: center;
    gap: 4px;
    flex-wrap: wrap;
  }}

  .breadcrumb .sep {{ color: var(--border); }}
  .breadcrumb .crumb {{ color: var(--muted); }}
  .breadcrumb .crumb.last {{ color: var(--text); font-weight: 500; }}

  .preview-scroll {{
    flex: 1;
    overflow-y: auto;
    padding: 24px 32px;
  }}

  .preview-scroll::-webkit-scrollbar {{ width: 8px; }}
  .preview-scroll::-webkit-scrollbar-track {{ background: transparent; }}
  .preview-scroll::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 4px; }}

  .empty-state {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--muted);
    gap: 12px;
    text-align: center;
  }}

  .empty-state .big-icon {{ font-size: 48px; opacity: 0.4; }}
  .empty-state p {{ font-size: 14px; }}

  /* ── Markdown styles ── */
  .md-body {{
    max-width: 800px;
    line-height: 1.7;
  }}

  .md-body h1, .md-body h2, .md-body h3, .md-body h4 {{
    color: var(--text);
    margin: 1.2em 0 0.5em;
    font-weight: 600;
    line-height: 1.3;
  }}

  .md-body h1 {{ font-size: 1.8em; border-bottom: 1px solid var(--border); padding-bottom: 0.3em; }}
  .md-body h2 {{ font-size: 1.4em; border-bottom: 1px solid var(--border); padding-bottom: 0.2em; }}
  .md-body h3 {{ font-size: 1.15em; }}
  .md-body h4 {{ font-size: 1em; }}

  .md-body p {{ margin: 0.7em 0; color: var(--text); }}

  .md-body a {{ color: var(--accent); text-decoration: none; }}
  .md-body a:hover {{ text-decoration: underline; }}

  .md-body code {{
    background: var(--code-bg);
    color: #f0883e;
    padding: 0.15em 0.4em;
    border-radius: 4px;
    font-family: 'SF Mono', 'Cascadia Code', 'Fira Code', Consolas, monospace;
    font-size: 0.875em;
  }}

  .md-body pre {{
    background: var(--code-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    overflow-x: auto;
    margin: 1em 0;
  }}

  .md-body pre code {{
    background: none;
    color: #c9d1d9;
    padding: 0;
    font-size: 13px;
    line-height: 1.6;
  }}

  .md-body blockquote {{
    border-left: 4px solid var(--accent-dim);
    padding: 4px 16px;
    color: var(--muted);
    margin: 1em 0;
    background: rgba(88,166,255,0.05);
    border-radius: 0 4px 4px 0;
  }}

  .md-body ul, .md-body ol {{
    padding-left: 1.8em;
    margin: 0.5em 0;
  }}

  .md-body li {{ margin: 0.25em 0; }}

  .md-body hr {{
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5em 0;
  }}

  .md-body table {{
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
    font-size: 13px;
  }}

  .md-body th, .md-body td {{
    padding: 8px 12px;
    border: 1px solid var(--border);
    text-align: left;
  }}

  .md-body th {{
    background: var(--surface);
    font-weight: 600;
    color: var(--text);
  }}

  .md-body td {{ color: var(--muted); }}
  .md-body tr:nth-child(even) td {{ background: rgba(255,255,255,0.02); }}

  /* frontmatter badge */
  .frontmatter {{
    background: var(--code-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 20px;
    font-family: 'SF Mono', Consolas, monospace;
    font-size: 12px;
    color: var(--muted);
  }}

  .frontmatter .fm-label {{ color: var(--purple); }}
  .frontmatter .fm-value {{ color: var(--green); }}

  /* raw text */
  .raw-body {{
    background: var(--code-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
    font-family: 'SF Mono', 'Cascadia Code', Consolas, monospace;
    font-size: 13px;
    line-height: 1.6;
    color: #c9d1d9;
    white-space: pre-wrap;
    word-break: break-word;
    overflow-x: auto;
  }}

  /* ── Resizer ── */
  .resizer {{
    width: 4px;
    background: var(--border);
    cursor: col-resize;
    flex-shrink: 0;
    transition: background 0.15s;
  }}
  .resizer:hover, .resizer.dragging {{ background: var(--accent); }}
</style>
</head>
<body>

<header>
  <div class="kit-name">🧠 <span>{kit_name}</span></div>
  <div class="stats" id="stats"></div>
  <div class="header-right" id="file-count"></div>
</header>

<div class="body">
  <div class="tree-panel" id="tree-panel">
    <div class="panel-header">Explorer</div>
    <div class="tree-scroll" id="tree-root"></div>
  </div>

  <div class="resizer" id="resizer"></div>

  <div class="preview-panel">
    <div class="preview-header">
      <div class="breadcrumb" id="breadcrumb">
        <span class="crumb">Select a file to preview</span>
      </div>
    </div>
    <div class="preview-scroll" id="preview-content">
      <div class="empty-state">
        <div class="big-icon">📂</div>
        <p>Click any file in the explorer to preview it here.</p>
      </div>
    </div>
  </div>
</div>

<script>
const TREE = {tree_json};
const FILES = {files_json};
const COUNTS = {counts_json};

// ── Stats bar ──
const STAT_COLORS = {{
  skills: '#3fb950', agents: '#58a6ff', prompts: '#d29922',
  configs: '#bc8cff', references: '#f0883e', scripts: '#f778ba'
}};
const statsEl = document.getElementById('stats');
let totalFiles = Object.keys(FILES).length;
document.getElementById('file-count').textContent = totalFiles + ' file' + (totalFiles !== 1 ? 's' : '');

for (const [cat, count] of Object.entries(COUNTS)) {{
  const el = document.createElement('div');
  el.className = 'stat' + (count > 0 ? ' active' : '');
  const dot = document.createElement('span');
  dot.className = 'dot';
  if (count > 0) dot.style.background = STAT_COLORS[cat] || '#3fb950';
  el.appendChild(dot);
  el.innerHTML += `<span class="stat-count">${{count}}</span><span class="stat-label"> ${{cat}}</span>`;
  statsEl.appendChild(el);
}}

// ── Markdown renderer ──
function renderMarkdown(text) {{
  // strip frontmatter, render separately
  let frontmatterHtml = '';
  const fmMatch = text.match(/^---\n([\s\S]*?)\n---\n?/);
  if (fmMatch) {{
    const fmLines = fmMatch[1].split('\n');
    const fmRows = fmLines.map(l => {{
      const m = l.match(/^(\w[\w-]*):\s*(.*)/);
      if (!m) return `<div>${{esc(l)}}</div>`;
      return `<div><span class="fm-label">${{esc(m[1])}}</span>: <span class="fm-value">${{esc(m[2])}}</span></div>`;
    }}).join('');
    frontmatterHtml = `<div class="frontmatter">${{fmRows}}</div>`;
    text = text.slice(fmMatch[0].length);
  }}

  // code blocks first (protect from inline processing)
  const blocks = [];
  text = text.replace(/```([^\n]*)\n([\s\S]*?)```/g, (_, lang, code) => {{
    const i = blocks.length;
    blocks.push(`<pre><code class="lang-${{esc(lang.trim())}}">${{esc(code)}}</code></pre>`);
    return `\x00BLOCK${{i}}\x00`;
  }});

  // inline code
  text = text.replace(/`([^`]+)`/g, (_, c) => `<code>${{esc(c)}}</code>`);

  // headings
  text = text.replace(/^######\s+(.+)$/mg, '<h6>$1</h6>');
  text = text.replace(/^#####\s+(.+)$/mg, '<h5>$1</h5>');
  text = text.replace(/^####\s+(.+)$/mg, '<h4>$1</h4>');
  text = text.replace(/^###\s+(.+)$/mg, '<h3>$1</h3>');
  text = text.replace(/^##\s+(.+)$/mg, '<h2>$1</h2>');
  text = text.replace(/^#\s+(.+)$/mg, '<h1>$1</h1>');

  // hr
  text = text.replace(/^(-{{3,}}|\*{{3,}}|_{{3,}})$/mg, '<hr>');

  // blockquotes
  text = text.replace(/^>\s?(.*)$/mg, (_, l) => `<blockquote>${{l}}</blockquote>`);

  // bold / italic
  text = text.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
  text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  text = text.replace(/\*(.+?)\*/g, '<em>$1</em>');
  text = text.replace(/___(.+?)___/g, '<strong><em>$1</em></strong>');
  text = text.replace(/__(.+?)__/g, '<strong>$1</strong>');
  text = text.replace(/_([^_\n]+)_/g, '<em>$1</em>');

  // links
  text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');

  // tables
  text = text.replace(/((?:^[|].+[|]\n)+)/mg, tableBlock => {{
    const rows = tableBlock.trim().split('\n');
    if (rows.length < 2) return tableBlock;
    const parseRow = r => r.replace(/^\||\|$/g, '').split('|').map(c => c.trim());
    const headers = parseRow(rows[0]);
    // skip separator row (---|---)
    const bodyRows = rows.slice(2);
    const ths = headers.map(h => `<th>${{h}}</th>`).join('');
    const trs = bodyRows.map(r => {{
      const cells = parseRow(r);
      return '<tr>' + cells.map(c => `<td>${{c}}</td>`).join('') + '</tr>';
    }}).join('');
    return `<table><thead><tr>${{ths}}</tr></thead><tbody>${{trs}}</tbody></table>`;
  }});

  // unordered lists
  text = text.replace(/((?:^[ \t]*[-*+]\s.+\n?)+)/mg, block => {{
    const items = block.trim().split('\n').map(l => `<li>${{l.replace(/^[ \t]*[-*+]\s/, '')}}</li>`).join('');
    return `<ul>${{items}}</ul>`;
  }});

  // ordered lists
  text = text.replace(/((?:^[ \t]*\d+\.\s.+\n?)+)/mg, block => {{
    const items = block.trim().split('\n').map(l => `<li>${{l.replace(/^[ \t]*\d+\.\s/, '')}}</li>`).join('');
    return `<ol>${{items}}</ol>`;
  }});

  // paragraphs (blank-line separated blocks not already tagged)
  text = text.split(/\n\n+/).map(para => {{
    para = para.trim();
    if (!para) return '';
    if (/^<(h[1-6]|ul|ol|li|table|blockquote|hr|pre|\x00BLOCK)/.test(para)) return para;
    return `<p>${{para.replace(/\n/g, '<br>')}}</p>`;
  }}).join('\n');

  // restore code blocks
  text = text.replace(/\x00BLOCK(\d+)\x00/g, (_, i) => blocks[+i]);

  return frontmatterHtml + `<div class="md-body">${{text}}</div>`;
}}

function esc(s) {{
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}}

// ── File tree ──
let selectedPath = null;

function buildTree(node, prefix, container) {{
  const children = node._children || {{}};
  const entries = Object.entries(children);
  // dirs first, then files
  const dirs = entries.filter(([,v]) => v._type === 'dir');
  const filEntries = entries.filter(([,v]) => v._type === 'file');

  for (const [name, child] of [...dirs, ...filEntries]) {{
    const path = prefix ? prefix + '/' + name : name;
    if (child._type === 'dir') {{
      // folder row
      const row = document.createElement('div');
      row.className = 'tree-item';
      row.style.paddingLeft = (8 + countDepth(prefix) * 14) + 'px';
      row.innerHTML = `<span class="chevron">▶</span><span class="icon">📁</span><span class="name">${{esc(name)}}</span>`;

      const sub = document.createElement('div');
      sub.className = 'tree-children';
      buildTree(child, path, sub);

      row.addEventListener('click', e => {{
        e.stopPropagation();
        const open = sub.classList.toggle('open');
        row.classList.toggle('open', open);
      }});

      container.appendChild(row);
      container.appendChild(sub);
    }} else {{
      // file row
      const row = document.createElement('div');
      row.className = 'tree-item';
      row.dataset.path = path;
      row.style.paddingLeft = (22 + countDepth(prefix) * 14) + 'px';
      const icon = fileIcon(name);
      row.innerHTML = `<span class="icon">${{icon}}</span><span class="name">${{esc(name)}}</span>`;
      row.addEventListener('click', e => {{
        e.stopPropagation();
        selectFile(path, row);
      }});
      container.appendChild(row);
    }}
  }}
}}

function countDepth(prefix) {{
  if (!prefix) return 0;
  return prefix.split('/').length;
}}

function fileIcon(name) {{
  const ext = name.split('.').pop().toLowerCase();
  if (name === 'SKILL.md' || name.endsWith('.md')) return '📝';
  if (['py','sh','bash'].includes(ext)) return '⚙️';
  if (['json','yaml','yml','toml'].includes(ext)) return '📋';
  if (['js','ts','jsx','tsx'].includes(ext)) return '🟨';
  if (['html','css'].includes(ext)) return '🌐';
  if (name === 'LICENSE') return '⚖️';
  return '📄';
}}

function selectFile(path, rowEl) {{
  // deselect old
  if (selectedPath) {{
    const old = document.querySelector('.tree-item.selected');
    if (old) old.classList.remove('selected');
  }}
  selectedPath = path;
  rowEl.classList.add('selected');

  // expand parents
  let el = rowEl.parentElement;
  while (el && el.id !== 'tree-root') {{
    if (el.classList.contains('tree-children')) {{
      el.classList.add('open');
      const prev = el.previousElementSibling;
      if (prev && prev.classList.contains('tree-item')) prev.classList.add('open');
    }}
    el = el.parentElement;
  }}

  // breadcrumb
  const parts = path.split('/');
  const bc = document.getElementById('breadcrumb');
  bc.innerHTML = parts.map((p, i) =>
    `<span class="crumb ${{i === parts.length-1 ? 'last' : ''}}">${{esc(p)}}</span>`
  ).join('<span class="sep">/</span>');

  // render preview
  const content = FILES[path];
  const previewEl = document.getElementById('preview-content');
  if (content === undefined) {{
    previewEl.innerHTML = '<div class="empty-state"><div class="big-icon">❓</div><p>File content not available.</p></div>';
    return;
  }}

  const isMarkdown = path.endsWith('.md') || path.endsWith('.MD');
  if (isMarkdown) {{
    previewEl.innerHTML = renderMarkdown(content);
  }} else {{
    previewEl.innerHTML = `<pre class="raw-body">${{esc(content)}}</pre>`;
  }}
  previewEl.scrollTop = 0;
}}

// build tree
const treeRoot = document.getElementById('tree-root');
buildTree(TREE, '', treeRoot);

// auto-select README.md if present
const readmePath = Object.keys(FILES).find(p => p.match(/^readme\.md$/i));
if (readmePath) {{
  const readmeRow = document.querySelector(`[data-path="${{readmePath}}"]`);
  if (readmeRow) selectFile(readmePath, readmeRow);
}}

// ── Resizer ──
const resizer = document.getElementById('resizer');
const treePanel = document.getElementById('tree-panel');
let isResizing = false, startX = 0, startW = 0;

resizer.addEventListener('mousedown', e => {{
  isResizing = true;
  startX = e.clientX;
  startW = treePanel.offsetWidth;
  resizer.classList.add('dragging');
  document.body.style.cursor = 'col-resize';
  document.body.style.userSelect = 'none';
}});

document.addEventListener('mousemove', e => {{
  if (!isResizing) return;
  const w = Math.max(160, Math.min(600, startW + e.clientX - startX));
  treePanel.style.width = w + 'px';
}});

document.addEventListener('mouseup', () => {{
  if (!isResizing) return;
  isResizing = false;
  resizer.classList.remove('dragging');
  document.body.style.cursor = '';
  document.body.style.userSelect = '';
}});
</script>
</body>
</html>"""


def open_browser(path: str):
    """Open a file in the default browser, WSL-aware."""
    import shutil

    # Detect WSL via environment variable (set by WSL itself)
    if os.environ.get("WSL_DISTRO_NAME"):
        try:
            # URLs must not go through wslpath — pass them directly to start
            if path.startswith("http://") or path.startswith("https://"):
                win_path = path
            else:
                win_path = subprocess.check_output(
                    ["wslpath", "-w", path], stderr=subprocess.DEVNULL
                ).decode().strip()
            subprocess.Popen(["cmd.exe", "/c", "start", "", win_path])
            return
        except Exception:
            pass  # fall through to generic handlers

    if shutil.which("wslview"):
        subprocess.Popen(["wslview", path])
    elif shutil.which("xdg-open"):
        subprocess.Popen(["xdg-open", path])
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["cmd.exe", "/c", "start", path])


def serve(root: Path, port: int, do_open: bool):
    """Start a local HTTP server that regenerates the dashboard on every request."""
    import http.server
    import functools

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            tree, files, counts = scan_tree(root)
            html = generate_html(root, tree, files, counts)
            data = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, fmt, *args):
            pass  # suppress per-request noise

    url = f"http://localhost:{port}"
    with http.server.HTTPServer(("localhost", port), Handler) as httpd:
        print(f"Serving live dashboard at {url}  (Ctrl-C to stop)")
        if do_open:
            open_browser(url)
            print("Opening in browser...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


def main():
    args = sys.argv[1:]
    do_open = "--open" in args
    args = [a for a in args if a != "--open"]

    # --serve [PORT]
    do_serve = False
    port = 7821
    if "--serve" in args:
        do_serve = True
        idx = args.index("--serve")
        args.pop(idx)
        # optional port argument immediately after --serve
        if idx < len(args) and args[idx].isdigit():
            port = int(args.pop(idx))

    path_args = [a for a in args if not a.startswith("--")]
    if path_args:
        root = Path(path_args[0]).expanduser().resolve()
    else:
        # default: two levels up from this script (scripts/ → root)
        root = Path(__file__).resolve().parent.parent

    if not root.is_dir():
        print(f"Error: '{root}' is not a directory", file=sys.stderr)
        sys.exit(1)

    if do_serve:
        serve(root, port, do_open=True)
        return

    print(f"Scanning {root} ...")
    tree, files, counts = scan_tree(root)

    html = generate_html(root, tree, files, counts)
    out = Path("/tmp/bk-dashboard.html")
    out.write_text(html, encoding="utf-8")
    print(f"Dashboard written to: {out}")

    if do_open:
        open_browser(str(out))
        print("Opening in browser...")
    else:
        print(f"Run with --open to launch, or open manually: {out}")


if __name__ == "__main__":
    main()
