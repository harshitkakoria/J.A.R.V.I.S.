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
**Open Built-in Programs:**
- "open notepad" → Opens Notepad
- "launch calculator" → Opens Calculator
- "start paint" → Opens Paint
- "run cmd" → Opens Command Prompt
- "open powershell" → Opens PowerShell
- "open explorer" → Opens File Explorer
- "open task manager" → Opens Task Manager

**Open Apps from Desktop:**
- "open vlc" → Opens VLC (if on desktop)
- "launch google chrome" → Opens Chrome (if on desktop)
- "start photoshop" → Opens Photoshop (if on desktop)
- "run spotify" → Opens Spotify (if on desktop)
- ℹ️ Searches desktop for .lnk shortcuts and .exe files

**Window Management:**
- "close tab" → Closes current tab (Ctrl+W)
- "close all the tabs" → Closes all tabs
- "close this tab" → Closes current tab
- "close window" → Closes current window (Alt+F4)
- "close the window" → Closes current window
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
- "Take a screenshot" → Saves to OneDrive\Pictures\Screenshots
- "Capture screen" → Saves to OneDrive\Pictures\Screenshots
- ℹ️ Automatically creates folder if it doesn't exist
- ℹ️ Files saved with timestamp: screenshot_20260117_121545.png

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
"open vlc"
"close all the tabs"
"take a screenshot"
"who is iron man"
"what's the weather today"
```

### Operations Requiring Confirmation:
```
"delete file test.txt confirm"
"run command dir confirm"
"shutdown yes"
"restart confirm"
```

### What's Blocked:
```
"delete file System32" → ❌ Blocked (system file)
"run command format C:" → ❌ Blocked (dangerous keyword)
"delete file test.txt" → ❌ Requires "confirm"
```

### Natural Language Variations (All Work):
```
"close the tab"
"close this tab"
"close all the tabs"
"close my tabs"
"can you close these tabs"

"who is albert einstein"
"tell me about albert einstein"
"what is albert einstein"
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
- Check internet connection (Google Speech API requires internet)
- Speak louder or closer to microphone
- Reduce background noise
- Speak at normal pace
- Use text mode: `run_text_mode.bat` as alternative

**Speech Recognition Tips:**
- Full sentences are captured (up to 8 seconds of speech)
- Pauses up to 1.5 seconds between words are allowed
- System auto-retries 3 times if recognition fails
- "Jarvis" wake word detection (if enabled) uses 5-second timeout

**If confirmation is required:**
- Add "confirm" or "yes" to dangerous commands
- Example: "shutdown confirm" not just "shutdown"
- Example: "delete file test.txt confirm" not just "delete file test.txt"

**To cancel shutdown:**
- Open Command Prompt
- Type: `shutdown /a`
- Press Enter within 10 seconds

**Desktop apps not opening:**
- Make sure app is on Desktop (shortcut or executable)
- Check app name spelling
- Try opening from built-in programs list instead

---

🎉 **JARVIS is now fully empowered with advanced system control!**
Use responsibly and always double-check dangerous operations.
