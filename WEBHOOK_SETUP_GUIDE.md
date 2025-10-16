# 🚀 Vogent Webhook Setup Guide

## Complete Setup Instructions

### Step 1: Start the Flask Application

Open a PowerShell terminal and run:

```powershell
cd "c:\Users\reube\OneDrive\Documents\InboundCall_Transcript"
python vogent_transcript_automation.py
```

**You should see:**
```
Starting Vogent Transcript Automation Server
Transcripts will be saved to: transcripts
 * Running on http://127.0.0.1:5000
 * Running on http://172.20.10.6:5000
```

✅ **Leave this terminal running!** Do NOT close it.

---

### Step 2: Start ngrok Tunnel

Open a **SECOND** PowerShell terminal and run:

```powershell
cd "c:\Users\reube\OneDrive\Documents\InboundCall_Transcript\ngrok"
.\ngrok http 5000
```

**You should see something like:**
```
Session Status                online
Forwarding                    https://abc123-xyz.ngrok-free.app -> http://localhost:5000
```

✅ **Copy the HTTPS forwarding URL** (the one starting with `https://`)

✅ **Leave this terminal running!** Do NOT close it.

---

### Step 3: Get Your Exact Webhook URL

Take the ngrok HTTPS URL and add `/webhook/vogent` to the end.

**Example:**
- If ngrok shows: `https://love-unblinking-tachygraphically.ngrok.io`
- Your webhook URL is: `https://love-unblinking-tachygraphically.ngrok.io/webhook/vogent`

**OR:**
- If ngrok shows: `https://abc123-xyz.ngrok-free.app`
- Your webhook URL is: `https://abc123-xyz.ngrok-free.app/webhook/vogent`

---

### Step 4: Test Your Webhook (Optional but Recommended)

Open a **THIRD** PowerShell terminal and run:

```powershell
cd "c:\Users\reube\OneDrive\Documents\InboundCall_Transcript"
.\test_webhook.ps1
```

This will:
1. ✅ Check if Flask is running
2. ✅ Test the local endpoint
3. ✅ Find your ngrok URL
4. ✅ Show you the **exact URL to use in Vogent**
5. ✅ Test the public webhook

---

### Step 5: Configure Vogent Dashboard

1. **Log in to your Vogent dashboard**
2. **Go to Webhooks or Integration settings**
3. **Add a new webhook endpoint**
4. **Paste your webhook URL:**
   ```
   https://YOUR-NGROK-URL.ngrok.io/webhook/vogent
   ```
5. **Select these events** (if available):
   - `dial.completed`
   - `call.completed`
   - `transcript.ready`
   - `dial.transcript`
   - Or select "All events"

6. **Save the webhook configuration**

---

### Step 6: Verify It's Working

1. **Make a test call** through Vogent
2. **Watch the Flask terminal** - you should see:
   ```
   ============================================================
   🔔 WEBHOOK RECEIVED FROM VOGENT
   ============================================================
   ```
3. **Check the transcripts folder** - a new file should appear
4. **Check vogent_automation.log** for detailed logs

---

## 🎯 EXACT URL FORMAT FOR VOGENT

```
https://[YOUR-NGROK-SUBDOMAIN].ngrok.io/webhook/vogent
```

Or:

```
https://[YOUR-NGROK-SUBDOMAIN].ngrok-free.app/webhook/vogent
```

### ✅ Correct Examples:
- `https://love-unblinking-tachygraphically.ngrok.io/webhook/vogent`
- `https://abc123-xyz.ngrok-free.app/webhook/vogent`
- `https://my-unique-name.ngrok.io/webhook/vogent`

### ❌ Incorrect Examples:
- ~~`http://localhost:5000/webhook/vogent`~~ (not accessible from internet)
- ~~`https://ngrok.io/webhook/vogent`~~ (missing subdomain)
- ~~`https://abc123.ngrok.io/vogent`~~ (missing /webhook/ path)
- ~~`https://abc123.ngrok.io/webhook/vogent/`~~ (extra trailing slash)

---

## 🔍 Troubleshooting

### Problem: "Flask app is NOT running"
**Solution:** Start Flask in a terminal:
```powershell
python vogent_transcript_automation.py
```

### Problem: "ngrok is NOT running"
**Solution:** Start ngrok in a separate terminal:
```powershell
.\ngrok\ngrok http 5000
```
Or:
```powershell
.\ngrok http 5000
```

### Problem: "No webhooks received"
**Checklist:**
1. ✅ Flask app is running (check terminal)
2. ✅ ngrok is running (check terminal)
3. ✅ Webhook URL in Vogent is correct (with /webhook/vogent)
4. ✅ Webhook URL uses HTTPS (not HTTP)
5. ✅ No trailing slash in the URL
6. ✅ Events are selected in Vogent dashboard

### Problem: "Webhook receives but no transcript"
**Check the log file:**
```powershell
Get-Content vogent_automation.log -Tail 50
```

Look for:
- "Found dial_id: XXXXX" ✅
- "Successfully retrieved dial info" ✅
- "Transcript saved to:" ✅

---

## 📝 Quick Reference

| Item | Value |
|------|-------|
| Flask Port | 5000 |
| Flask Endpoint | `/webhook/vogent` |
| Method | POST |
| Content-Type | application/json |
| ngrok Dashboard | http://localhost:4040 |
| Logs | `vogent_automation.log` |
| Transcripts | `transcripts/` folder |

---

## 🎮 Testing Commands

### Test Local Endpoint:
```powershell
curl -Method POST -Uri "http://localhost:5000/webhook/vogent" `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"event":"test","payload":{"dial_id":"test123"}}'
```

### Test via ngrok:
```powershell
curl -Method POST -Uri "https://YOUR-NGROK-URL.ngrok.io/webhook/vogent" `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"event":"test","payload":{"dial_id":"test123"}}'
```

### Check Flask is Running:
```powershell
curl -Method GET -Uri "http://localhost:5000/health"
```

### View Live Logs:
```powershell
Get-Content vogent_automation.log -Wait -Tail 10
```

---

## ⚠️ Important Notes

1. **ngrok URLs change** every time you restart ngrok (on free plan)
   - You'll need to update the webhook URL in Vogent dashboard each time
   
2. **Both terminals must stay open** for webhooks to work
   - Terminal 1: Flask app
   - Terminal 2: ngrok tunnel

3. **Test locally first** before testing via ngrok

4. **Check logs frequently** - they show everything that's happening

---

## 🆘 Still Having Issues?

Run the automated test:
```powershell
.\test_webhook.ps1
```

This will diagnose your setup and show you the exact URL to use.
