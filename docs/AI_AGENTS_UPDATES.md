# 🤖 AI Coding Agents: Latest Releases & Features

**Last Updated:** 2026-02-27  
**Source:** GitHub Releases API

---

## 📊 **Quick Summary**

| Agent | Latest Version | Release Date | Key Feature |
|-------|---------------|--------------|-------------|
| **Claude Code** | v2.1.62 | 2026-02-27 | Prompt cache optimization |
| **Gemini CLI** | v0.30.0 | 2026-02-25 | 5-phase planning, text masking |
| **OpenAI Codex** | v0.106.0 | 2026-02-26 | Memory diff, JS REPL, direct install |

---

## 1️⃣ **Claude Code** (Anthropic)

### 📦 Latest: **v2.1.62** (2026-02-27)

#### **What's New**
- ✅ **Fixed prompt suggestion cache regression** - Improved cache hit rates for faster responses

#### **Recent Changes** (v2.1.61 - v2.1.56)
- Continuous performance improvements
- Stability fixes

#### **Key Features to Leverage**
```bash
# File editing with @ syntax
@src/file.py Fix this function

# Multi-file operations
@file1 @file2 Update both files

# Safe shell commands
Run: pytest tests/

# Git integration
git diff HEAD~1
```

#### **Best For**
- Daily coding tasks
- Safe file editing
- CLI-native workflows

---

## 2️⃣ **Gemini CLI** (Google)

### 📦 Latest: **v0.30.0** (2026-02-25)

#### **🔥 Major New Features**

| Feature | Benefit | How to Use |
|---------|---------|------------|
| **5-Phase Sequential Planning** | Better complex task breakdown | Automatic for complex prompts |
| **Text Wrapping in Markdown Tables** | Better readability | Auto-applied in output |
| **Tool Output Masking (Default)** | Security & privacy | Enabled by default |
| **Hide Shortcuts Hint UI** | Cleaner interface | Settings → Hide shortcuts |
| **Multi-line Text Answers** | Better ask-user tool | `ask_user` tool enhanced |
| **Plan Mode Policy Overrides** | Flexible planning | Documented & validated |
| **Skills in Plan Mode** | Extended planning | Enable skills in plan mode |
| **Ctrl-Z Suspension** | Background tasks | Press `Ctrl-Z` |
| **Policy Engine** | Replace `--allowed-tools` | Use `--policy` flag |

#### **Performance Improvements**
- ⚡ Optimized table rendering (memoized styled characters)
- ⚡ Truncated large debug logs
- ⚡ Limited message history
- ⚡ Cached CLI version for consistency

#### **Security Enhancements**
- 🔒 Strict seatbelt profiles
- 🔒 Removed unusable closed profiles
- 🔒 Fixed credentials exposure

#### **Developer Experience**
- 📝 Multi-line text answers in `ask_user` tool
- 📝 Plan mode metrics for `AskUser` tool
- 📝 Admin controls documentation
- 📝 Extension management commands

#### **Key Features to Leverage**
```bash
# Use new policy engine
gemini --policy my-policy.yaml

# Enable plan mode with skills
gemini --plan-mode --enable-skills

# Hide shortcuts for clean UI
# Settings → UI → Hide shortcuts hint

# Use 5-phase planning (automatic)
"Implement a full authentication system"
```

#### **Best For**
- Large codebase analysis (1M token context)
- Complex multi-phase planning
- Google ecosystem integration
- Cost-sensitive users (free tier)

---

## 3️⃣ **OpenAI Codex**

### 📦 Latest: **v0.106.0** (2026-02-26)

#### **🔥 Major New Features**

| Feature | Benefit | How to Use |
|---------|---------|------------|
| **Direct Install Script** | Easy macOS/Linux install | Download from releases |
| **App-Server v2 Thread API** | Realtime endpoints, notifications | Experimental thread-scoped API |
| **JS REPL (Experimental)** | Run JavaScript interactively | `/experimental js_repl` |
| **request_user_input in Default Mode** | More collaboration | Now works outside Plan mode |
| **5.3-codex Model Visible** | Access to latest model | Available in CLI model list |
| **Memory Diff & Usage-Aware Selection** | Smarter memory management | Automatic diff-based forgetting |

#### **Bug Fixes & Reliability**
- ✅ WebSocket reliability (retry timeout, prefer v2)
- ✅ Fixed zsh-fork sandbox bypass
- ✅ 1M character input cap (prevent crashes)
- ✅ TUI file-link rendering (hide absolute paths)
- ✅ Ctrl-C handling for sub-agents

#### **Performance**
- ⚡ Reduced sub-agent startup overhead
- ⚡ Skip history metadata scan for sub-agents
- ⚡ OTEL audit logging for policy decisions

#### **Key Features to Leverage**
```bash
# Direct install (macOS/Linux)
curl -fsSL https://github.com/openai/codex/releases/download/rust-v0.106.0/install.sh | bash

# Use JS REPL (experimental)
/experimental js_repl

# Access 5.3-codex model
/model 5.3-codex

# Memory-aware sessions (automatic)
# Now uses diff-based forgetting
```

#### **Best For**
- Complex reasoning tasks
- JavaScript/Node.js development
- Realtime collaborative features
- Custom tool integrations

---

## 🎯 **Feature Comparison Matrix**

| Feature | Claude Code | Gemini CLI | OpenAI Codex |
|---------|-------------|------------|--------------|
| **Latest Version** | v2.1.62 | v0.30.0 | v0.106.0 |
| **Release Date** | 2026-02-27 | 2026-02-25 | 2026-02-26 |
| **Multi-File Editing** | ✅ Excellent | ✅ Good | ✅ Excellent |
| **Planning System** | ⚠️ Basic | ✅ 5-Phase | ✅ Advanced |
| **Memory Management** | ❌ Manual | ✅ Auto-config | ✅ Diff-based |
| **Real-time API** | ❌ No | ⚠️ Limited | ✅ Thread API |
| **JS/Node Support** | ⚠️ Via shell | ⚠️ Via shell | ✅ Native REPL |
| **Policy Engine** | ⚠️ Basic | ✅ Advanced | ✅ OTEL Audit |
| **Sub-agent Support** | ❌ No | ✅ Yes | ✅ Optimized |
| **Free Tier** | ❌ No | ✅ Yes | ⚠️ Limited |
| **Context Window** | ~200K | 1M+ | 128K-200K |

---

## 🚀 **Recommended Workflows**

### **For Daily Development**
```bash
# Primary: Claude Code
- Fast, safe file editing
- Reliable shell commands
- Git integration

# Backup: Gemini CLI
- Large file analysis
- Complex planning tasks
```

### **For Complex Projects**
```bash
# Planning: Gemini CLI (5-phase)
# Implementation: Claude Code
# Complex Logic: OpenAI Codex (o1)
# Project Memory: nanobot (MEMORY.md)
```

### **For Team Collaboration**
```bash
# Code Review: Claude Code
# Documentation: Gemini CLI
# Notifications: nanobot (Telegram)
# Memory: nanobot (shared MEMORY.md)
```

---

## 📈 **Trending Features to Watch**

### **1. Agentic Planning**
- Gemini's 5-phase planning
- Codex's thread-scoped agents
- **Action:** Use for complex multi-step tasks

### **2. Memory Optimization**
- Codex's diff-based forgetting
- Gemini's auto-config memory
- **Action:** Let agents manage memory automatically

### **3. Policy Engines**
- Gemini's `--policy` flag
- Codex's OTEL audit logging
- **Action:** Define custom policies for security

### **4. Real-time Collaboration**
- Codex's thread API
- request_user_input in Default mode
- **Action:** Build interactive workflows

### **5. Security Hardening**
- Seatbelt profiles (Gemini)
- Sandbox enforcement (Codex)
- Tool output masking (Gemini)
- **Action:** Enable security features by default

---

## 🛠️ **How to Update**

### **Claude Code**
```bash
# Auto-updates via pip/npm
pip install -U claude-code
# or
npm install -g @anthropic-ai/claude-code
```

### **Gemini CLI**
```bash
# npm update
npm install -g @google/gemini-cli@latest

# Or check releases
gh release list --repo google-gemini/gemini-cli
```

### **OpenAI Codex**
```bash
# Direct install (new in v0.106.0)
curl -fsSL https://github.com/openai/codex/releases/download/rust-v0.106.0/install.sh | bash

# Or via cargo
cargo install codex --version 0.106.0
```

---

## 📝 **Action Items for Your Projects**

### **twitter-capture Bot**
- [ ] Use **Claude Code** for Python code edits
- [ ] Use **Gemini CLI** for planning new features
- [ ] Use **nanobot** for project memory
- [ ] Enable **Gemini's 5-phase planning** for `/banners` feature expansion

### **nanobot Core**
- [ ] Consider **Codex's thread API** for sub-agent communication
- [ ] Implement **diff-based memory** (inspired by Codex)
- [ ] Add **policy engine** (inspired by Gemini)
- [ ] Enable **tool output masking** for security

---

## 🔗 **Resources**

| Project | GitHub | Releases | Docs |
|---------|--------|----------|------|
| **Claude Code** | github.com/anthropics/claude-code | [Releases](https://github.com/anthropics/claude-code/releases) | [Docs](https://docs.anthropic.com/claude-code) |
| **Gemini CLI** | github.com/google-gemini/gemini-cli | [Releases](https://github.com/google-gemini/gemini-cli/releases) | [Docs](https://ai.google.dev/gemini-cli) |
| **OpenAI Codex** | github.com/openai/codex | [Releases](https://github.com/openai/codex/releases) | [Docs](https://platform.openai.com/docs) |

---

## 📅 **Next Update**

This document will be updated when new releases are published.

**To fetch latest:**
```bash
# Claude Code
gh release view latest --repo anthropics/claude-code --json body

# Gemini CLI
gh release view latest --repo google-gemini/gemini-cli --json body

# OpenAI Codex
gh release view latest --repo openai/codex --json body
```

---

**Generated:** 2026-02-27T11:34:00+09:00  
**By:** nanobot with GitHub API
