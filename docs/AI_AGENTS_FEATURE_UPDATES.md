# AI Coding Agents: Recent Feature Releases & What to Leverage

**Last Updated:** February 27, 2026  
**Sources:** GitHub Releases (official)

---

## 🎯 **Executive Summary: Key Features to Leverage**

| Agent | Killer Feature | Best For | Maturity |
|-------|---------------|----------|----------|
| **Claude Code** | Auto-memory, `/copy`, worktree isolation | Daily coding, safe edits | ⭐⭐⭐ Stable |
| **Gemini CLI** | 5-phase planning, policy engine, tool masking | Complex tasks, security | ⭐⭐⭐ Stable |
| **OpenAI Codex** | JS REPL, diff-based memory, voice transcription | Multi-agent, JavaScript | ⭐⭐ Evolving |

---

## 1️⃣ **Claude Code** (Anthropic)

**Repository:** `anthropics/claude-code`  
**Latest:** v2.1.62 (Feb 27, 2026)

### 🚀 **Major Features (Last 5 Releases)**

#### **v2.1.59 - Feb 26, 2026** ⭐ **Biggest Update**

| Feature | Description | How to Leverage |
|---------|-------------|-----------------|
| **Auto-Memory** | Claude automatically saves useful context to memory | Use `/memory` command to manage. No manual saving needed! |
| **`/copy` Command** | Interactive picker for code blocks | Select individual code blocks or full response instantly |
| **Smart "Always Allow"** | Better prefix suggestions for compound bash commands | `cd /tmp && git fetch && git push` → per-subcommand prefixes |
| **Improved Task Ordering** | Better short task list organization | More coherent multi-step workflows |
| **Multi-Agent Memory GC** | Releases completed subagent task state | Lower memory usage in long sessions |

**Example:**
```bash
# Auto-memory in action
Claude automatically remembers:
- Project structure decisions
- Key file paths
- Previous solutions

# Manage memory
/memory show
/memory clear
/memory export
```

---

#### **v2.1.50 - Feb 20, 2026** ⭐ **Feature-Rich**

| Feature | Description | How to Leverage |
|---------|-------------|-----------------|
| **Worktree Isolation** | `isolation: worktree` in agent definitions | Agents run in isolated git worktrees automatically |
| **`/mcp reconnect`** | Reconnect MCP servers without restart | Fix broken MCP connections on the fly |
| **`CLAUDE_CODE_SIMPLE`** | Fully minimal mode (strips skills, memory, hooks) | Maximum speed, minimal overhead |
| **`claude agents` CLI** | List all configured agents | `claude agents` shows available agents |
| **1M Context Window** | Opus 4.6 fast mode includes full 1M context | Process entire codebases in one session |
| **`CLAUDE_CODE_DISABLE_1M_CONTEXT`** | Env var to disable 1M window | Save tokens when not needed |
| **Startup Timeout Config** | `startupTimeout` for LSP servers | Prevent hangs on slow LSP initialization |
| **Worktree Hooks** | `WorktreeCreate`/`WorktreeRemove` events | Custom VCS setup/teardown automation |

**Example:**
```bash
# Simple mode for speed
CLAUDE_CODE_SIMPLE=1 claude

# Disable 1M context to save tokens
CLAUDE_CODE_DISABLE_1M_CONTEXT=1 claude

# List agents
claude agents

# Agent with worktree isolation
{
  "name": "reviewer",
  "isolation": "worktree"
}
```

---

### 📊 **Feature Evolution Timeline**

| Version | Date | Key Features |
|---------|------|--------------|
| v2.1.62 | Feb 27 | Prompt cache fix (performance) |
| v2.1.61 | Feb 26 | Minor fixes |
| **v2.1.59** | **Feb 26** | **Auto-memory, `/copy`, smart allow prefixes** |
| v2.1.58 | Feb 25 | VS Code fixes |
| v2.1.56 | Feb 25 | VS Code crash fixes |
| v2.1.53 | Feb 25 | Multi-agent kill, shutdown improvements |
| **v2.1.50** | **Feb 20** | **Worktree isolation, 1M context, CLAUDE_CODE_SIMPLE** |

---

### 💡 **Top 5 Features to Use Today**

1. **Auto-Memory** - Let Claude remember context automatically
2. **`/copy` Command** - Instantly copy code blocks
3. **Worktree Isolation** - Safe parallel agent execution
4. **1M Context Window** - Full codebase analysis
5. **`CLAUDE_CODE_SIMPLE`** - Minimal mode for speed

---

### ⚠️ **Known Limitations**

| Limitation | Status |
|------------|--------|
| No long-term memory across sessions | Partially solved by auto-memory |
| CLI only (no GUI) | Use VS Code extension |
| Session resets on exit | Auto-memory helps, but not perfect |

---

## 2️⃣ **Gemini CLI** (Google)

**Repository:** `google-gemini/gemini-cli`  
**Latest:** v0.30.0 (Feb 25, 2026)

### 🚀 **Major Features (Last 5 Releases)**

#### **v0.30.0 - Feb 25, 2026** ⭐ **Massive Update**

| Feature | Description | How to Leverage |
|---------|-------------|-----------------|
| **5-Phase Sequential Planning** | Formalized workflow for complex tasks | Automatic for complex prompts, better task breakdown |
| **Tool Output Masking (Default)** | Hide sensitive tool outputs automatically | Enabled by default, no config needed |
| **Multi-line Text Answers** | Better `ask_user` tool support | Users can write long responses naturally |
| **Policy Engine** | Replace `--allowed-tools` with `--policy` | `--policy my-policy.yaml` for fine-grained control |
| **Ctrl-Z Suspension** | Background task support | `Ctrl-Z` to suspend, `fg` to resume |
| **Table Text Wrapping** | Markdown tables wrap properly | Better readability in terminal |
| **Hide Shortcuts Hint** | Setting to hide UI shortcuts | Cleaner interface |
| **Autoconfigure Memory** | Dialog-based memory usage setting | Easier memory management |
| **Search Result Limits** | Prevent overwhelming results | Better signal-to-noise ratio |
| **Debug Log Truncation** | Limit message history size | Better performance in long sessions |
| **Skills in Plan Mode** | Enable skills during planning | More powerful planning workflows |
| **Gemini 3 Internal Models** | Updated utility models | Better internal reasoning |

**Example:**
```bash
# Use policy engine
gemini --policy my-policy.yaml

# Policy file example
# my-policy.yaml
rules:
  - tool: shell
    pattern: "rm -rf"
    action: deny
  - tool: shell
    pattern: "git.*"
    action: auto_approve

# Suspend and resume
Ctrl-Z  # Suspend
fg      # Resume

# Multi-line answers
/ask_user "Describe your requirements in detail"
# User can now write multiple lines
```

---

#### **v0.29.6 - Feb 24, 2026**

| Feature | Description | How to Leverage |
|---------|-------------|-----------------|
| **Policy Persistence Fix** | Race condition in policy storage resolved | Reliable policy saves |
| **Memory Eval Improvements** | Better testing for memory features | More stable memory behavior |

---

#### **v0.28.0 - Jan 28, 2026** ⭐ **Major Features**

| Feature | Description | How to Leverage |
|---------|-------------|-----------------|
| **`/prompt-suggest` Command** | Get AI-suggested prompts | Overcome writer's block |
| **Hooks Enable/Disable** | Align with skills system | Better hook management |
| **Positron IDE Support** | New IDE integration | Use with Positron |
| **Custom Deny Messages** | Policy rules with custom messages | Better UX for denied actions |
| **Extension Themes** | Custom themes for extensions | Personalize UI |
| **Workspace Persistence** | Restore workspace on session resume | Continue where you left off |
| **Undo/Redo Keybindings** | Cmd+Z / Alt+Z support | Standard editing shortcuts |
| **User Identity Display** | Show auth/email/tier on startup | Know which account is active |
| **Background Shell Commands** | Run commands in background | Non-blocking execution |
| **Dynamic Policy for Subagents** | Subagents get their own policies | Fine-grained multi-agent control |
| **OAuth Interactive Consent** | Better OAuth flow | Easier authentication |
| **EOL Preservation** | Preserve line endings in files | Better Windows compatibility |

**Example:**
```bash
# Get prompt suggestions
/prompt-suggest

# Custom policy with deny messages
rules:
  - tool: shell
    pattern: "rm -rf /"
    action: deny
    message: "⚠️ Cannot delete root directory!"

# Background command
gemini "run this long task in background"

# Resume workspace
gemini --resume
```

---

### 📊 **Feature Evolution Timeline**

| Version | Date | Key Features |
|---------|------|--------------|
| **v0.30.0** | **Feb 25** | **5-phase planning, policy engine, masking, Ctrl-Z** |
| v0.29.7 | Feb 24 | Patch release |
| v0.29.6 | Feb 24 | Policy persistence fix |
| v0.29.5 | Feb 23 | Minor fixes |
| **v0.28.0** | **Jan 28** | **Prompt-suggest, themes, background shells, OAuth** |

---

### 💡 **Top 5 Features to Use Today**

1. **5-Phase Sequential Planning** - Best for complex multi-step tasks
2. **Policy Engine** - Fine-grained security control
3. **Tool Output Masking** - Automatic security (enabled by default)
4. **Ctrl-Z Suspension** - Background task management
5. **Background Shell Commands** - Non-blocking execution

---

### ⚠️ **Known Limitations**

| Limitation | Status |
|------------|--------|
| Nightly builds can be unstable | Use v0.30.0 stable |
| Policy syntax can be complex | Docs improving |
| Memory features still evolving | Autoconfigure helps |

---

## 3️⃣ **OpenAI Codex** (OpenAI)

**Repository:** `openai/codex`  
**Latest:** v0.106.0 (Feb 26, 2026)

### 🚀 **Major Features (Last 5 Releases)**

#### **v0.106.0 - Feb 26, 2026** ⭐ **Major Update**

| Feature | Description | How to Leverage |
|---------|-------------|-----------------|
| **Direct Install Script** | macOS/Linux one-line install | `curl ... | bash` - no build needed |
| **App-Server v2 Thread API** | Thread-scoped realtime endpoints | Realtime collaborative features |
| **`thread/unsubscribe` Flow** | Unload live threads without archiving | Clean up without losing history |
| **JS REPL (Experimental)** | Native JavaScript REPL in `/experimental` | Interactive JS development |
| **`request_user_input` in Default Mode** | Collaboration in all modes | Not just Plan mode anymore |
| **`5.3-codex` Model Visibility** | Available in CLI model list | Access to latest model |
| **Diff-Based Forgetting** | Smart memory management | Usage-aware memory selection |
| **WebSocket v2** | Prefer WS v2 when supported | Better realtime reliability |
| **~1M Character Input Cap** | Prevent hangs on oversized pastes | Safety limit with clear errors |
| **Hidden Absolute Paths** | TUI hides full paths in file links | Cleaner UI, better privacy |

**Example:**
```bash
# Direct install (macOS/Linux)
curl -fsSL https://github.com/openai/codex/releases/download/rust-v0.106.0/install.sh | bash

# Enable JS REPL
/experimental js_repl

# Use 5.3-codex model
codex --model 5.3-codex

# Realtime thread API
# POST /threads/{id}/realtime
# Subscribe to live updates

# User input in any mode
codex "Help me with this" --mode default
# Can now ask for clarification anytime
```

---

#### **v0.105.0 - Feb 2026** ⭐ **Feature-Rich**

| Feature | Description | How to Leverage |
|---------|-------------|-----------------|
| **Syntax Highlighting** | Fenced code blocks & diffs highlighted | Better readability |
| **`/theme` Picker** | Live preview theme selection | Personalize UI |
| **Voice Transcription** | Hold spacebar to record voice prompts | Hands-free coding (experimental) |
| **`spawn_agents_on_csv`** | Fan-out work from CSV with progress/ETA | Parallel agent workflows |
| **Sub-Agent Nicknames** | Easier to track multiple agents | Better multi-agent UX |
| **`/copy` Command** | Copy latest assistant reply | Quick code extraction |
| **`/clear` & `Ctrl-L`** | Clear screen without losing context | Clean workspace |
| **Extra Sandbox Permissions** | Ask for additional permissions per command | Flexible security |
| **Auto-Reject Approval Types** | Reject specific prompt types without disabling all | Granular control |
| **`thread/list` Search** | Search threads by title | Find past work |
| **`thread/resume` Inline** | Returns latest turn inline on reconnect | Lossless reconnection |

**Example:**
```bash
# Change theme
/theme  # Interactive picker

# Voice input (enable in config)
# features.voice_transcription = true
# Hold spacebar to record

# Spawn agents from CSV
codex "Process this CSV" --spawn-agents data.csv

# Copy last response
/copy

# Search threads
codex threads --search "authentication fix"

# Clear screen
/clear  # or Ctrl-L
```

---

#### **v0.104.0 - Feb 2026**

| Feature | Description | How to Leverage |
|---------|-------------|-----------------|
| **WS_PROXY Support** | WebSocket proxying via env vars | Corporate proxy support |
| **Thread Archive Notifications** | Clients react without polling | Better event-driven UX |
| **Distinct Approval IDs** | Multiple approvals per shell command | Complex command workflows |

---

### 📊 **Feature Evolution Timeline**

| Version | Date | Key Features |
|---------|------|--------------|
| **v0.106.0** | **Feb 26** | **Direct install, JS REPL, diff-based memory, realtime API** |
| v0.106.0-alpha.11 | Feb 26 | Bug fixes |
| v0.106.0-alpha.9 | Feb 26 | Performance improvements |
| **v0.105.0** | **Feb 2026** | **Voice transcription, themes, /copy, spawn_agents_on_csv** |
| v0.104.0 | Feb 2026 | WebSocket proxy, archive notifications |

---

### 💡 **Top 5 Features to Use Today**

1. **JS REPL** - Interactive JavaScript development (experimental but powerful)
2. **Diff-Based Memory** - Smart forgetting, usage-aware selection
3. **Direct Install Script** - No build required, instant setup
4. **Voice Transcription** - Hands-free prompting (experimental)
5. **`spawn_agents_on_csv`** - Parallel agent workflows with progress tracking

---

### ⚠️ **Known Limitations**

| Limitation | Status |
|------------|--------|
| JS REPL still experimental | Node 22.22.0+ required |
| Voice transcription under development | Enable via config flag |
| Frequent alpha releases | Use stable v0.106.0 for production |

---

## 🆚 **Head-to-Head: Feature Comparison**

| Feature | Claude Code | Gemini CLI | OpenAI Codex |
|---------|-------------|------------|--------------|
| **Auto-Memory** | ✅ Auto-memory (v2.1.59) | ⚠️ Manual config | ✅ Diff-based (v0.106.0) |
| **Copy Code** | ✅ `/copy` (v2.1.59) | ❌ | ✅ `/copy` (v0.105.0) |
| **Policy Engine** | ⚠️ Basic | ✅ Advanced (v0.30.0) | ✅ Approval types |
| **Multi-Agent** | ✅ Worktree isolation | ✅ Sub-agents | ✅ `spawn_agents_on_csv` |
| **Voice Input** | ❌ | ❌ | ✅ Experimental (v0.105.0) |
| **JS REPL** | ❌ | ❌ | ✅ Experimental (v0.106.0) |
| **1M Context** | ✅ Opus 4.6 | ✅ Gemini 3 | ⚠️ ~1M cap (safety) |
| **Background Tasks** | ⚠️ Sub-agents | ✅ Ctrl-Z (v0.30.0) | ✅ Background shells |
| **Theme Picker** | ❌ | ❌ | ✅ `/theme` (v0.105.0) |
| **Direct Install** | ❌ | ❌ | ✅ Script (v0.106.0) |
| **Realtime API** | ❌ | ❌ | ✅ Thread API (v0.106.0) |

---

## 🎯 **Recommendations by Use Case**

### **Daily Coding & File Editing**
🏆 **Winner: Claude Code**
- Auto-memory reduces context management
- `/copy` for quick code extraction
- Safest file edits
- Worktree isolation for parallel work

**Setup:**
```bash
claude
# Auto-memory handles context
# Use /copy to extract code
```

---

### **Complex Multi-Step Projects**
🏆 **Winner: Gemini CLI**
- 5-phase planning breaks down complex tasks
- Policy engine for fine-grained control
- Background shell commands
- Ctrl-Z for task suspension

**Setup:**
```bash
gemini --policy my-policy.yaml
# 5-phase planning automatic for complex prompts
# Ctrl-Z to suspend, fg to resume
```

---

### **JavaScript/Node.js Development**
🏆 **Winner: OpenAI Codex**
- JS REPL for interactive development
- Direct install (no build)
- Voice transcription for hands-free coding
- Realtime API for collaborative features

**Setup:**
```bash
# Install
curl -fsSL https://github.com/openai/codex/releases/download/rust-v0.106.0/install.sh | bash

# Enable JS REPL
/experimental js_repl
```

---

### **Multi-Agent Workflows**
🏆 **Winner: Tie (depends on need)**

| Need | Best Tool |
|------|-----------|
| **Safe isolation** | Claude Code (worktree) |
| **CSV fan-out** | OpenAI Codex (`spawn_agents_on_csv`) |
| **Dynamic policies** | Gemini CLI (sub-agent policies) |

---

### **Security-Conscious Environments**
🏆 **Winner: Gemini CLI**
- Policy engine with custom deny messages
- Tool output masking (default)
- Auto-reject specific approval types
- Fine-grained control

**Setup:**
```yaml
# my-policy.yaml
rules:
  - tool: shell
    pattern: "rm -rf"
    action: deny
    message: "⚠️ Dangerous command!"
  - tool: shell
    pattern: "git.*"
    action: auto_approve
```

---

## 📈 **Trend Analysis: What's Coming Next?**

### **Common Themes Across All Agents**

1. **Auto-Memory** → All moving toward automatic context management
2. **Multi-Agent** → Better orchestration and isolation
3. **Security** → Fine-grained policies, masking, approvals
4. **Realtime** → WebSocket-based collaborative features
5. **Voice/Multi-modal** → Beyond text input

### **Predicted Next Features**

| Agent | Likely Next Features |
|-------|---------------------|
| **Claude Code** | Voice input, better GUI, plugin system |
| **Gemini CLI** | Stable release cycle, more IDE integrations |
| **OpenAI Codex** | JS REPL stable, Python REPL, more languages |

---

## 🛠️ **Quick Start Guides**

### **Claude Code**
```bash
# Install (if not already)
npm install -g @anthropic-ai/claude-code

# Use auto-memory (automatic)
claude

# Copy code blocks
/copy

# Simple mode for speed
CLAUDE_CODE_SIMPLE=1 claude
```

---

### **Gemini CLI**
```bash
# Install
npm install -g @google/gemini-cli

# Use policy engine
gemini --policy my-policy.yaml

# Suspend/resume
Ctrl-Z  # Suspend
fg      # Resume

# Enable voice (if available)
# settings.voice_enabled = true
```

---

### **OpenAI Codex**
```bash
# Direct install (macOS/Linux)
curl -fsSL https://github.com/openai/codex/releases/download/rust-v0.106.0/install.sh | bash

# Enable JS REPL
codex
/experimental js_repl

# Use voice (experimental)
# config.toml: features.voice_transcription = true
# Hold spacebar to record

# Spawn agents from CSV
codex "Process this" --spawn-agents tasks.csv
```

---

## 📚 **Resources**

### **Official Documentation**
- **Claude Code:** https://docs.anthropic.com/claude-code
- **Gemini CLI:** https://github.com/google-gemini/gemini-cli
- **OpenAI Codex:** https://github.com/openai/codex

### **Release Notes**
- **Claude Code:** https://github.com/anthropics/claude-code/releases
- **Gemini CLI:** https://github.com/google-gemini/gemini-cli/releases
- **OpenAI Codex:** https://github.com/openai/codex/releases

### **Community**
- **Reddit:** r/claude, r/ChatGPTCoding, r/LocalLLaMA
- **Hacker News:** Search "claude code", "gemini cli", "codex"
- **Discord:** Official servers for each tool

---

## ✅ **Action Items: What to Try Today**

### **If Using Claude Code:**
- [ ] Test auto-memory (it's automatic!)
- [ ] Use `/copy` to extract code blocks
- [ ] Try `CLAUDE_CODE_SIMPLE=1` for speed
- [ ] Set up worktree isolation for agents

### **If Using Gemini CLI:**
- [ ] Create a policy file (`--policy`)
- [ ] Test Ctrl-Z suspension
- [ ] Try 5-phase planning with complex prompts
- [ ] Enable background shell commands

### **If Using OpenAI Codex:**
- [ ] Install via direct script (no build)
- [ ] Enable JS REPL (`/experimental js_repl`)
- [ ] Test voice transcription (experimental)
- [ ] Try `spawn_agents_on_csv` for parallel work

---

## 🎯 **Final Verdict**

| Category | Winner | Runner-Up |
|----------|--------|-----------|
| **Daily Coding** | Claude Code | OpenAI Codex |
| **Complex Projects** | Gemini CLI | Claude Code |
| **JavaScript Dev** | OpenAI Codex | Claude Code |
| **Security** | Gemini CLI | Claude Code |
| **Multi-Agent** | Tie (all good) | - |
| **Ease of Use** | Claude Code | Gemini CLI |
| **Features** | OpenAI Codex | Gemini CLI |
| **Stability** | Claude Code | Gemini CLI |

**Overall Recommendation:** Use **Claude Code** for daily work, **Gemini CLI** for complex/secure projects, and **OpenAI Codex** for JavaScript/ experimentation.

---

**Last Updated:** February 27, 2026  
**Next Review:** March 6, 2026 (weekly updates recommended)
