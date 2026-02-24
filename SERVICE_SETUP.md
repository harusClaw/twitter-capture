# Twitter Capture Bot - Systemd Service Setup ✅

## 🎉 Status: **ENABLED & RUNNING**

Your Twitter capture bot is now configured to **auto-start on boot**!

---

## 📊 Current Status

```bash
$ systemctl --user status twitter-capture.service
● twitter-capture.service - Twitter URL to Image Telegram Bot
     Loaded: loaded (/home/openclaw/.config/systemd/user/twitter-capture.service; enabled)
     Active: active (running)
```

**Bot PID:** Running with `uv run python -m twitter_capture`

---

## 🔧 Service Management Commands

### **Check Status**
```bash
systemctl --user status twitter-capture.service
```

### **View Logs**
```bash
journalctl --user -u twitter-capture.service -f
```

### **Restart Bot**
```bash
systemctl --user restart twitter-capture.service
```

### **Stop Bot**
```bash
systemctl --user stop twitter-capture.service
```

### **Start Bot**
```bash
systemctl --user start twitter-capture.service
```

### **Disable Auto-start**
```bash
systemctl --user disable twitter-capture.service
```

### **Re-enable Auto-start**
```bash
systemctl --user enable twitter-capture.service
```

---

## 🚀 Auto-Start on Boot

✅ **Linger is enabled** for user `openclaw`
- Bot will start automatically when the system boots
- No need to log in first
- Service runs in the background

**Verify linger status:**
```bash
loginctl show-user openclaw | grep Linger
# Should show: Linger=yes
```

---

## 📝 Service Configuration

**Location:** `~/.config/systemd/user/twitter-capture.service`

**Key Settings:**
- **Working Directory:** `/home/openclaw/.nanobot/workspace/projects/twitter-capture`
- **Environment:** Loads `.env` file with bot token
- **Restart Policy:** Always restart on failure (10s delay)
- **Entry Point:** `uv run python -m twitter_capture`

---

## 🔍 Troubleshooting

### **Bot Not Starting?**
```bash
# Check if service is enabled
systemctl --user is-enabled twitter-capture.service

# Check for errors
systemctl --user status twitter-capture.service

# Try manual start
systemctl --user start twitter-capture.service
```

### **Check Process is Running**
```bash
ps aux | grep twitter_capture
```

### **Test Bot Manually**
```bash
cd /home/openclaw/.nanobot/workspace/projects/twitter-capture
~/.local/bin/uv run python -m twitter_capture
```
(Press Ctrl+C to stop)

### **Reload After Config Changes**
```bash
systemctl --user daemon-reload
systemctl --user restart twitter-capture.service
```

---

## 🎯 What Happens on Boot

1. System boots up
2. User session starts for `openclaw` (linger enabled)
3. systemd starts `twitter-capture.service`
4. Bot connects to Telegram API
5. Bot is ready to receive Twitter URLs!

---

## ✅ Verification Checklist

- [x] Service file installed: `~/.config/systemd/user/twitter-capture.service`
- [x] Service enabled: `systemctl --user is-enabled` returns `enabled`
- [x] Service running: `systemctl --user status` shows `active (running)`
- [x] Linger enabled: `loginctl show-user openclaw` shows `Linger=yes`
- [x] Bot token loaded from `.env` file
- [x] Auto-restart on failure configured

---

## 📞 Quick Test

After reboot, send a Twitter URL to your bot:
```
https://x.com/username/status/123456
```

You should get a response with the media! 🎉

---

**Setup completed:** 2026-02-20 18:40 JST
**Bot:** twitter-capture v1.0
**GitHub:** https://github.com/harusClaw/twitter-capture
