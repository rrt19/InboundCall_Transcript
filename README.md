# Vogent Inbound Call Transcript Automation

This Python application automatically retrieves and saves transcripts from Vogent inbound calls. It runs a Flask webhook server that receives notifications from Vogent when calls complete, then fetches and saves the transcripts without any manual intervention.

## Features

- ✅ **Fully Automated**: No manual steps required after setup
- ✅ **Real-time Processing**: Uses Vogent webhooks for immediate transcript retrieval
- ✅ **Readable Output**: Saves transcripts in human-readable format
- ✅ **Backup Data**: Also saves raw JSON data for debugging
- ✅ **Error Handling**: Comprehensive logging and error recovery
- ✅ **Manual Override**: API endpoint for manual transcript retrieval
- ✅ **Health Monitoring**: Built-in health check endpoint

## How It Works

1. **Inbound Call**: Someone calls your Vogent-linked phone number
2. **AI Agent Handles Call**: Your configured Vogent agent answers and conducts the conversation
3. **Webhook Notification**: Vogent sends a `dial.transcript` webhook when the transcript is ready
4. **Automatic Retrieval**: The script fetches the transcript via Vogent API
5. **File Saving**: Transcript is saved as a formatted text file in the `transcripts/` directory

## Quick Start

### 1. Install Dependencies

```powershell
# Install Python packages
pip install -r requirements.txt
```

### 2. Configure Environment

```powershell
# Copy the example environment file
copy .env.example .env
```

Edit `.env` and add your Vogent API key:
```
VOGENT_API_KEY=elto_YourActualAPIKeyHere
```

### 3. Configure Vogent Webhooks

In your Vogent dashboard:
1. Go to **API Settings**
2. Set **Webhook URL** to: `http://your-server:5000/webhook/vogent`
3. Enable the `dial.transcript` event

**Note**: For testing locally, use a tool like [ngrok](https://ngrok.com/) to expose your local server:
```powershell
# In another terminal
ngrok http 5000
# Use the ngrok URL as your webhook URL in Vogent
```

### 4. Run the Application

```powershell
python vogent_transcript_automation.py
```

The server will start on port 5000 and begin listening for webhooks.

## Usage

### Automatic Operation

Once running, the system operates completely automatically:

1. When someone calls your Vogent number, the AI agent handles the call
2. After the call ends and transcript is ready, Vogent sends a webhook
3. The script automatically fetches and saves the transcript
4. Files are saved in the `transcripts/` directory with timestamps

### Manual Transcript Retrieval

You can also manually fetch a transcript if needed:

```powershell
# Using curl or similar HTTP client
curl -X POST http://localhost:5000/manual-fetch/YOUR_DIAL_ID
```

### Monitoring

Check if the service is running:
```powershell
curl http://localhost:5000/health
```

## File Output

The system creates two files for each call:

### 1. Formatted Transcript (`transcript_[dial_id]_[timestamp].txt`)
```
============================================================
VOGENT CALL TRANSCRIPT
============================================================
Dial ID: 5a6c6190-db20-4d8e-86a9-79a6af292dea
Generated: 2025-10-05 14:30:22
Agent ID: 97512a3c-dd94-45fb-965c-e8d58e762fcb
Caller Number: +18001234567
Call Status: completed

------------------------------------------------------------
CONVERSATION TRANSCRIPT
------------------------------------------------------------

[001] AI: Hello, thank you for calling Dr. Smith's office. How can I help you today?

[002] HUMAN: Hi, I need to schedule an appointment for a check-up.

[003] AI: I'd be happy to help you schedule that appointment. Could you please provide me with your full name?

[004] HUMAN: Sure, it's John Doe.

------------------------------------------------------------
End of transcript - 4 total entries
```

### 2. Raw JSON Data (`raw_dial_[dial_id]_[timestamp].json`)
Contains the complete API response from Vogent for debugging purposes.

## Configuration Options

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VOGENT_API_KEY` | Yes | - | Your Vogent API key (starts with `elto_`) |
| `PORT` | No | 5000 | Port for the webhook server |
| `DEBUG` | No | False | Enable Flask debug mode |

### Directory Structure

```
Inbound_transcript/
├── vogent_transcript_automation.py  # Main application
├── requirements.txt                 # Python dependencies
├── .env                            # Your configuration (create from .env.example)
├── .env.example                    # Configuration template
├── transcripts/                    # Output directory (auto-created)
│   ├── transcript_[id]_[time].txt  # Formatted transcripts
│   └── raw_dial_[id]_[time].json   # Raw API responses
└── vogent_automation.log           # Application logs
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook/vogent` | POST | Receives Vogent webhooks |
| `/health` | GET | Health check |
| `/manual-fetch/<dial_id>` | POST | Manually fetch a transcript |

## Troubleshooting

### Common Issues

**1. "VOGENT_API_KEY environment variable not set!"**
- Solution: Make sure you've created a `.env` file with your API key

**2. Webhooks not being received**
- Check that your webhook URL is correctly configured in Vogent
- Ensure your server is accessible from the internet (use ngrok for local testing)
- Verify the webhook URL includes the correct path: `/webhook/vogent`

**3. Transcript not found**
- The transcript might not be ready immediately after the call
- The script includes automatic retry logic
- Check the logs for specific error messages

**4. Connection errors**
- Verify your internet connection
- Check if the Vogent API is accessible: `https://api.vogent.ai/api`
- Ensure your API key is valid and has the correct permissions

### Logging

The application logs to both:
- Console output (visible when running)
- `vogent_automation.log` file

Log levels:
- **INFO**: Normal operations (calls received, transcripts saved)
- **WARNING**: Non-critical issues (transcript not immediately ready)
- **ERROR**: Critical problems (API failures, file write errors)

### Testing

You can test the webhook endpoint manually:

```powershell
# Test dial.transcript webhook
curl -X POST http://localhost:5000/webhook/vogent \
  -H "Content-Type: application/json" \
  -d '{
    "event": "dial.transcript",
    "payload": {
      "dial_id": "test-dial-id-123"
    }
  }'
```

## Production Deployment

For production use:

1. **Use a proper WSGI server** (not Flask's dev server):
   ```powershell
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 vogent_transcript_automation:app
   ```

2. **Set up reverse proxy** (nginx/Apache) for HTTPS
3. **Configure proper logging** and log rotation
4. **Set up monitoring** and alerting
5. **Secure your server** and restrict access to webhook endpoints

## Security Considerations

- Keep your Vogent API key secure and never commit it to version control
- Use HTTPS for webhook URLs in production
- Consider implementing webhook signature verification
- Restrict server access and use firewalls appropriately
- Regularly rotate API keys and monitor for unauthorized access

## Support

For issues with:
- **This script**: Check the logs and troubleshooting section above
- **Vogent API**: Refer to [Vogent documentation](https://docs.vogent.ai)
- **Webhook configuration**: Check your Vogent dashboard settings

## License

This automation script is provided as-is for use with the Vogent platform.