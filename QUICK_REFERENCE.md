# Quick Reference Card

## 🎯 YOUR WEBHOOK URL (Copy this to Vogent):
```
https://love-unblinking-tachygraphically.ngrok-free.dev/webhook/vogent
```

## 🚀 Quick Commands:

### Start Everything:
```powershell
.\start_services.ps1
```

### Get Current URL:
```powershell
.\get_webhook_url.ps1
```

### Watch Logs Live:
```powershell
Get-Content vogent_automation.log -Wait -Tail 20
```

### Check Recent Transcripts:
```powershell
Get-ChildItem transcripts\transcript_*.txt | Sort-Object LastWriteTime -Descending | Select-Object -First 5
```

### Test Webhook Locally:
```powershell
curl -Method POST -Uri "http://localhost:5000/webhook/vogent" -Headers @{"Content-Type"="application/json"} -Body '{"event":"test","payload":{"dial_id":"test123"}}'
```

## 📁 Important Files:
- `PROBLEM_FIXED.md` - Summary of what was fixed
- `WEBHOOK_DEBUG_REPORT.md` - Detailed analysis
- `WEBHOOK_SETUP_GUIDE.md` - Complete setup guide
- `vogent_automation.log` - All webhook activity logs
- `transcripts/` - Saved transcripts folder

## ✅ Status Checklist:
- [x] Flask running on port 5000
- [x] ngrok exposing Flask to internet
- [x] Webhook endpoint active at /webhook/vogent
- [ ] Webhook URL configured in Vogent dashboard
- [ ] Test call made to verify end-to-end

## 🔧 Troubleshooting:
- Flask not running? → `python vogent_transcript_automation.py`
- ngrok not running? → `.\ngrok http 5000`
- Need URL? → `.\get_webhook_url.ps1`
- Not receiving webhooks? → Check Vogent dashboard configuration
