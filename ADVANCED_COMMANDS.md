# JARVIS - Complete Command Reference

## 🎯 NEW ADVANCED FEATURES (With Safety Mechanisms)

### 📁 File Management
**Create Files/Folders:**
- "create file test.txt" → Creates a new file
- "create folder myfolder" → Creates a new folder

**Delete Files/Folders (REQUIRES CONFIRMATION):**
- "delete file test.txt confirm" → Deletes file
- "delete folder myfolder confirm" → Deletes folder
- ⚠️ Must include "confirm" keyword for safety

**Rename Files/Folders:**
- "rename file old.txt to new.txt" → Renames file
- "rename folder oldname to newname" → Renames folder

**List Files:**
- "list files" → Shows files in current directory
- "show files" → Lists folders and files

### 🪟 Application Control
**Open Programs:**
- "open notepad" → Opens Notepad
- "launch calculator" → Opens Calculator
- "start paint" → Opens Paint
- "run cmd" → Opens Command Prompt
- "open powershell" → Opens PowerShell
- "open explorer" → Opens File Explorer
- "open task manager" → Opens Task Manager

**Window Management:**
- "close tab" → Closes current tab (Ctrl+W)
- "close window" → Closes current window (Alt+F4)
- "switch window" → Switches to next window (Alt+Tab)
- "minimize" → Minimizes current window
- "maximize" → Maximizes current window

### 💻 System Commands (DANGEROUS - Use with Caution)
**Execute Commands (REQUIRES CONFIRMATION):**
- "run command dir confirm" → Lists directory contents
- "execute ipconfig confirm" → Shows network info
- "system command ping google.com confirm" → Pings Google
- ⚠️ Must include "confirm" keyword
- ⚠️ Dangerous commands are blocked automatically

### 🔌 Shutdown/Restart (RE-ENABLED with Safety)
**Power Commands (REQUIRES CONFIRMATION):**
- "shutdown confirm" → Shuts down in 10 seconds
- "shutdown yes" → Shuts down in 10 seconds
- "restart confirm" → Restarts in 10 seconds
- "reboot yes" → Restarts in 10 seconds
- ℹ️ You have 10 seconds to cancel with: `shutdown /a`

---

## 📚 EXISTING FEATURES

### ⏰ Time & Date
- "What time is it?"
- "What's today's date?"

### 😄 Entertainment
- "Tell me a joke"
- "Make me laugh"

### 🌤️ Weather
- "What's the weather?"
- "Weather in Chennai"
- "Temperature"

### 📸 Screenshots
- "Take a screenshot"
- "Capture screen"

### 🔊 Volume Control
- "Increase volume"
- "Decrease volume"
- "Mute"

### 🌐 Web Browsing
**Open Websites:**
- "Open Google"
- "Open YouTube"
- "Open GitHub"
- "Open Stack Overflow"

**Search:**
- "Google python tutorial"
- "Search for AI"
- "YouTube python programming"
- "Play music videos"

### 📖 Wikipedia
- "Who is Albert Einstein?"
- "What is machine learning?"
- "Tell me about quantum computing"

### 📰 Web Scraping
- "Latest news"
- "Gold price"
- "Stock market"

### 🤖 AI Conversations
- Ask any general question
- "How do I learn Python?"
- "Explain blockchain"
- Uses OpenRouter Llama 3 8B for intelligent responses

---

## ⚠️ SAFETY MECHANISMS

### 🔐 Confirmation Required For:
1. **File Deletion** - Must say "confirm" or "yes"
2. **System Commands** - Must say "confirm"
3. **Shutdown/Restart** - Must say "confirm" or "yes"

### 🚫 Automatic Blocks:
1. **System Files** - Cannot delete .exe, .dll, .sys files
2. **Dangerous Commands** - "format", "del /f", "rm -rf" blocked
3. **Fork Bombs** - Malicious commands blocked

### 📝 All Dangerous Actions Are Logged:
- File deletions logged with full path
- System commands logged with command text
- Shutdown/restart logged as CRITICAL

---

## 💡 USAGE EXAMPLES

### Safe Operations:
```
"create file notes.txt"
"list files"
"open notepad"
"close tab"
"take a screenshot"
```

### Operations Requiring Confirmation:
```
"delete file test.txt confirm"
"run command dir confirm"
"shutdown yes"
```

### What's Blocked:
```
"delete file System32" → ❌ Blocked (system file)
"run command format C:" → ❌ Blocked (dangerous keyword)
"delete file test.txt" → ❌ Requires "confirm"
```

---

## 🎤 How to Use

**Voice Mode:**
```batch
run.bat
```
- Speak commands naturally
- No wake word needed
- Say "goodbye" to exit

**Text Mode:**
```batch
run_text_mode.bat
```
- Type commands
- Press Enter
- Type "exit" to quit

---

## 📊 Command Priority

1. **Exact Keywords** → Direct skill execution (instant)
2. **No Match** → AI generates response (2-3 seconds)
3. **Confirmation Required** → Safety check first
4. **Blocked** → Dangerous operation rejected

---

## ⚙️ Technical Details

**Voice Recognition:** Google Speech API (requires internet)
**Text-to-Speech:** pyttsx3 (offline)
**AI Brain:** OpenRouter Llama 3 8B Instruct
**Safety:** Keyword blacklists, confirmation requirements, logging

**All operations are logged to:** `logs/jarvis.log`

---

## 🆘 Troubleshooting

**If voice recognition fails:**
- Check internet connection
- Speak louder/clearer
- Use text mode: `run_text_mode.bat`

**If confirmation is required:**
- Add "confirm" or "yes" to dangerous commands
- Example: "shutdown confirm" not just "shutdown"

**To cancel shutdown:**
- Open Command Prompt
- Type: `shutdown /a`
- Press Enter within 10 seconds

---

🎉 **JARVIS is now fully empowered with advanced system control!**
Use responsibly and always double-check dangerous operations.
