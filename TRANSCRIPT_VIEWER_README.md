# 🏥 Kyron Medical - Patient-Assistant Transcript Viewer

A beautiful, modern, healthcare-themed web interface for viewing patient-assistant transcripts with the Kyron Medical visual identity.

## 🎨 Design Features

- **Kyron Medical Branding**: Custom geometric logo and color palette
- **Clean Healthcare Theme**: Professional, minimal, and calm design
- **Responsive Layout**: Works beautifully on desktop and mobile
- **Animated UI**: Smooth transitions and fade-in effects
- **Chat Bubbles**: Patient (right, blue gradient) and Assistant (left, frost blue)
- **Auto-scroll**: Automatically scrolls to latest message

## 🎨 Color Palette

| Use | Hex | Description |
|-----|-----|-------------|
| Primary Background | `#FFFFFF` | Clean clinical white |
| Secondary Background | `#E7F0FA` | Light ice blue panel |
| Accent Blue (Primary) | `#4C82E0` | Kyron signature blue |
| Accent Navy | `#2E4C9E` | Deep navy |
| Light Gradient | `#A6C8FF` | Sky blue highlight |
| Frost Tint | `#DDEBFF` | Pale frost blue |
| Text Primary | `#1E2A36` | Charcoal navy |
| Text Secondary | `#4B5B67` | Muted gray-blue |

## 🚀 Quick Start

### Option 1: Run the viewer directly

```powershell
python transcript_viewer.py
```

Then open: http://localhost:8080

### Option 2: Use the startup script

```powershell
.\start_viewer.ps1
```

This will:
1. Check if the viewer is already running
2. Start the viewer if needed
3. Open it in your browser automatically

## 📁 File Structure

```
InboundCall_Transcript/
├── transcript_viewer.py          # Main Flask application
├── templates/
│   ├── base.html                 # Base template with Kyron branding
│   ├── index.html                # Homepage - transcript list
│   └── transcript.html           # Chat view - conversation display
├── transcripts/                  # Auto-saved transcript files
│   └── transcript_*.txt
└── start_viewer.ps1              # Startup script
```

## 🎯 Features

### Homepage (Transcript List)
- Clean card grid layout
- Displays all available transcripts
- Shows date, time, and file size
- Hover effects with blue glow
- Empty state when no transcripts

### Chat View (Conversation Display)
- Patient messages: right-aligned, blue gradient bubbles
- Assistant messages: left-aligned, frost blue bubbles
- Smooth fade-up animations
- Auto-scroll to latest message
- Back button to return to list
- Message counter

## 🔧 Technical Details

- **Frontend**: HTML5, CSS3 (no build process needed)
- **Backend**: Flask (Python)
- **Fonts**: Poppins & Inter (loaded from Google Fonts)
- **Port**: 8080
- **Auto-reload**: Yes (debug mode)

## 📝 Transcript Format

The viewer automatically parses transcript files with these formats:

```
[001] PATIENT: Hello, I need help
[002] ASSISTANT: How can I assist you today?
```

Or:

```
Patient: Hello, I need help
Assistant: How can I assist you today?
```

## 🌐 Access URLs

- **Local**: http://localhost:8080
- **Network**: http://[YOUR-IP]:8080

## 🎨 Visual Elements

### Geometric Background
- Animated floating shapes in corners
- Subtle opacity for professional look
- Based on Kyron's geometric design language

### Header
- Semi-transparent with blur effect
- Sticky positioning
- Kyron logo with geometric hexagon design
- Navigation with smooth underline transitions

### Footer
- Subtle border separator
- Copyright and "Powered by Kyron Medical"
- Small Kyron logo inline

## 🔄 Integration

The viewer automatically reads transcript files from the `transcripts/` folder.

When your webhook automation (`vogent_transcript_automation.py`) saves new transcripts, they will immediately appear in the viewer (just refresh the page).

## 💡 Usage Tips

1. **Start the viewer** on port 8080 (separate from the webhook server on port 5000)
2. **Keep both running**: Webhook server (5000) + Transcript viewer (8080)
3. **Access anytime**: Open http://localhost:8080 to view transcripts
4. **Auto-updates**: New transcripts appear automatically (refresh page)

## 🎉 That's It!

Your beautiful Kyron Medical transcript viewer is ready to use!

The design is professional, healthcare-appropriate, and matches the Kyron Medical brand identity perfectly.

---

**© 2025 Kyron Medical | All Rights Reserved**  
*Powered by Kyron Medical*
