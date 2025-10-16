# 🏥 Kyron Medical Transcript Viewer - Quick Reference

## 🚀 Start the Viewer

```powershell
python transcript_viewer.py
```

Access at: **http://localhost:8080**

## 🎨 What You Get

✅ Beautiful homepage with transcript cards  
✅ Professional chat view with message bubbles  
✅ Patient messages (right, blue gradient)  
✅ Assistant messages (left, frost blue)  
✅ Kyron Medical branding throughout  
✅ Smooth animations and transitions  
✅ Responsive design (works on mobile)  

## 📊 Two Servers

| Server | Port | Purpose |
|--------|------|---------|
| Webhook Automation | 5000 | Receives webhooks, saves transcripts |
| Transcript Viewer | 8080 | Beautiful UI to view transcripts |

**Both run independently!**

## 🎨 Design Colors

- **Patient bubbles**: Blue gradient (#A6C8FF → #4C82E0)
- **Assistant bubbles**: Frost blue (#E7F0FA)
- **Accents**: Kyron blue (#4C82E0)
- **Background**: Clean white (#FFFFFF)

## 📁 Key Files

- `transcript_viewer.py` - Main app
- `templates/` - HTML templates
- `transcripts/` - Auto-saved transcript files
- `start_viewer.ps1` - Quick start script

## 🔧 Quick Commands

```powershell
# Start viewer
python transcript_viewer.py

# Or use script
.\start_viewer.ps1

# Check if running
curl http://localhost:8080

# Stop (Ctrl+C in the terminal)
```

## 🌐 Access URLs

- **Local**: http://localhost:8080
- **Network**: http://[YOUR-IP]:8080

## ✨ Features

- 🏠 **Homepage**: Grid of transcript cards
- 💬 **Chat View**: Beautiful message bubbles
- 📱 **Responsive**: Works on all devices
- 🎨 **Animated**: Smooth fade-in effects
- 🔄 **Auto-scroll**: Jumps to latest message
- 🎯 **Professional**: Healthcare-themed design

## 📖 Documentation

- `VIEWER_SETUP_COMPLETE.md` - Full setup guide
- `TRANSCRIPT_VIEWER_README.md` - User manual

---

**Your beautiful Kyron Medical transcript viewer is ready to use!** 🎉
