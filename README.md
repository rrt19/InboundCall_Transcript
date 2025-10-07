# 📞 Vogent Call Transcript System

A comprehensive automation system that captures, processes, and displays Vogent call transcripts in a beautiful web interface.

## 🌟 **What This System Does**

This system consists of **two main components** that work together:

1. **📥 Transcript Automation** (`vogent_transcript_automation.py`)
   - Automatically receives webhook notifications from Vogent when calls complete
   - Fetches and saves call transcripts to your local system
   - Runs continuously in the background to capture all calls

2. **🌐 Web Viewer** (`transcript_viewer.py`)  
   - Provides a beautiful, chat-style interface to view your transcripts
   - Shows conversations between Human (Customer) and AI (Agent) in separate bubbles
   - Includes search functionality and easy downloading of transcripts

## 🚀 **Quick Start Guide**

### **Step 1: Install Dependencies**

```powershell
# Install required Python packages
pip install -r requirements.txt
```

### **Step 2: Configure Your API Key**

Create a `.env` file in this directory with your Vogent API key:

```
VOGENT_API_KEY=your_api_key_here
```

### **Step 3: Run Both Applications**

**⚠️ IMPORTANT: You need to run BOTH scripts for full functionality!**

#### **Terminal 1 - Transcript Automation (REQUIRED)**
```powershell
python vogent_transcript_automation.py
```
- This runs your webhook server on **http://localhost:5000**
- Keeps running to automatically capture new call transcripts
- **Must stay running** to receive webhooks from Vogent

#### **Terminal 2 - Web Viewer (RECOMMENDED)**
```powershell
python transcript_viewer.py
```
- This runs your web interface on **http://localhost:5001**
- Provides the beautiful chat-style interface for viewing transcripts
- Can be stopped and restarted without losing functionality

### **Step 4: Configure Vogent Webhook**

In your Vogent dashboard, set your webhook URL to:
```
http://your-server-ip:5000/webhook/vogent
```

### **Step 5: View Your Transcripts**

Open your browser and go to:
- **📋 Monitor automation**: http://localhost:5000 (basic dashboard)
- **✨ View transcripts beautifully**: http://localhost:5001 (recommended interface)

## 🎯 **How It Works**

```
[Call Ends] → [Webhook] → [Automation Script] → [Saves Transcript] → [Web Viewer Shows Chat]
```

1. **Call Completes**: When a Vogent call ends, Vogent sends a webhook
2. **Automation Captures**: Your automation script receives the webhook and fetches the transcript
3. **File Saved**: Transcript is saved as a `.txt` file in the `transcripts/` folder
4. **Web Display**: The web viewer reads the file and displays it in a chat-style interface

## 📁 **Project Structure**

```
InboundCall_Transcript/
├── 📄 vogent_transcript_automation.py  # Main automation script
├── 🌐 transcript_viewer.py             # Web interface
├── 📋 requirements.txt                 # Python dependencies
├── 📝 README.md                        # This file
├── 🔧 .env                            # API configuration (create this)
├── 📁 transcripts/                     # Saved transcript files
├── 📁 templates/                       # Web interface templates
│   ├── base.html
│   ├── index.html
│   └── transcript.html
└── 📊 vogent_automation.log            # System logs
```

## 🖥️ **User Interface Features**

### **Main Dashboard (localhost:5001)**
- **📱 Responsive Design**: Works on desktop, tablet, and mobile
- **🔍 Search Functionality**: Search transcripts by content, date, or ID
- **📊 Call Overview**: See call duration, status, and participant count
- **💾 Easy Downloads**: Download original transcript files

### **Transcript Viewer**
- **💬 Chat-Style Display**: 
  - 🟢 **Human (Customer)**: Green bubbles on the left with "H" avatar
  - 🔵 **AI (Agent)**: Blue bubbles on the right with "AI" avatar
- **📋 Copy Functionality**: One-click copy of entire conversations
- **📈 Call Metadata**: Duration, status, timestamp, and message count
- **📝 Call Summaries**: Automatically extracted from transcripts

## ⚙️ **Configuration Options**

### **Environment Variables (.env file)**
```env
# Required
VOGENT_API_KEY=your_vogent_api_key_here

# Optional
TRANSCRIPTS_DIR=transcripts
LOG_LEVEL=INFO
```

### **Webhook Configuration**
Your webhook URL should be configured in Vogent to point to:
```
http://your-domain.com:5000/webhook/vogent
```

For local testing with ngrok:
```powershell
# Install ngrok and expose port 5000
ngrok http 5000
# Use the ngrok URL in your Vogent webhook settings
```

## 🔧 **Troubleshooting**

### **No Transcripts Appearing?**
1. ✅ Check that `vogent_transcript_automation.py` is running
2. ✅ Verify your API key in the `.env` file
3. ✅ Confirm webhook URL is correctly configured in Vogent
4. ✅ Check the logs in `vogent_automation.log`

### **Web Interface Not Loading?**
1. ✅ Ensure `transcript_viewer.py` is running
2. ✅ Check that port 5001 is not blocked
3. ✅ Verify Python dependencies are installed

### **Conversation Not Parsing?**
1. ✅ Check that transcript files are in the `transcripts/` folder
2. ✅ Verify transcript format matches expected patterns
3. ✅ Look for parsing errors in the console output

## 📊 **Monitoring and Logs**

### **Log Files**
- `vogent_automation.log`: Contains all automation activity, errors, and webhook events
- Console output: Real-time status updates and debug information

### **API Endpoints**
- `GET /health`: System health check
- `GET /notifications`: Recent system notifications  
- `GET /recent-dials`: List of recent dial attempts
- `POST /webhook/vogent`: Webhook endpoint for Vogent

## 🔒 **Security Considerations**

- **API Keys**: Never commit your `.env` file to version control
- **Webhook Security**: Consider implementing webhook signature validation
- **Network Access**: Ensure proper firewall configuration for webhook access
- **Data Privacy**: Transcript files contain sensitive call data - secure appropriately

## 🆘 **Support and Maintenance**

### **Regular Maintenance**
- Monitor log files for errors or warnings
- Periodically restart both scripts for optimal performance
- Keep Python dependencies updated

### **Common Commands**
```powershell
# Check system status
curl http://localhost:5000/health

# View recent notifications
curl http://localhost:5000/notifications

# Restart automation (if needed)
# Stop with Ctrl+C, then restart
python vogent_transcript_automation.py

# View all transcripts via API
curl http://localhost:5001/api/transcripts
```

## 📈 **Advanced Usage**

### **Multiple Environments**
You can run multiple instances for different environments:
```powershell
# Production
VOGENT_API_KEY=prod_key python vogent_transcript_automation.py

# Development  
VOGENT_API_KEY=dev_key python vogent_transcript_automation.py
```

### **Custom Transcript Processing**
The system automatically handles various transcript formats:
- Vogent numbered format: `[001] HUMAN:` / `[002] AI:`
- Simple format: `Agent:` / `Customer:`
- Custom speaker identification and message parsing

## 💡 **Quick Reference**

| Component | Purpose | Port | Status |
|-----------|---------|------|--------|
| Automation Script | Captures transcripts | 5000 | Must Run |
| Web Viewer | Display interface | 5001 | Recommended |

**🔥 Pro Tip**: Keep both terminals open and running for the best experience. The automation script captures calls automatically, while the web viewer gives you a beautiful interface to review them!

## 🎬 **Getting Started Walkthrough**

### **First Time Setup (5 minutes)**

1. **Open PowerShell** in this project directory

2. **Install everything**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Create your API configuration**:
   ```powershell
   # Create .env file with your API key
   echo "VOGENT_API_KEY=your_actual_api_key_here" > .env
   ```

4. **Start the automation** (Terminal 1):
   ```powershell
   python vogent_transcript_automation.py
   ```
   ✅ Should show: "Starting webhook server on port 5000"

5. **Start the web viewer** (Terminal 2):
   ```powershell
   python transcript_viewer.py
   ```
   ✅ Should show: "Web interface available at http://localhost:5001"

6. **Test it works**:
   - Open http://localhost:5001 in your browser
   - You should see the transcript viewer interface

7. **Configure Vogent** (one-time setup):
   - In Vogent dashboard, set webhook to: `http://your-server:5000/webhook/vogent`
   - For local testing, use ngrok: `ngrok http 5000`

**That's it!** Your system is now ready to automatically capture and display call transcripts! 🎉

---

**Built for efficient Vogent call transcript management** 🚀