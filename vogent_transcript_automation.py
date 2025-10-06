#!/usr/bin/env python3
"""
Vogent Inbound Call Transcript Automation
==========================================

This script automatically retrieves transcripts from Vogent inbound calls.
It runs a Flask webhook server to receive dial events from Vogent, then
fetches and saves the call transcripts automatically.

Features:
- Receives webhook notifications from Vogent
- Automatically fetches transcripts when calls complete
- Saves transcripts in readable format
- Error handling and logging
- No manual intervention required

Setup:
1. Set your VOGENT_API_KEY environment variable
2. Configure Vogent webhook URL to point to this server
3. Run the script to start the webhook server

Author: Generated for Kyron Inbound Transcript Automation
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
import requests
from flask import Flask, request, jsonify

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded .env file successfully")
except ImportError:
    print("⚠️  python-dotenv not installed. Run: pip install python-dotenv")
except Exception as e:
    print(f"⚠️  Could not load .env file: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vogent_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VogentAPI:
    """Client for interacting with Vogent API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.vogent.ai/api"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_dial_info(self, dial_id: str) -> Optional[Dict]:
        """
        Retrieve dial information including transcript
        
        Args:
            dial_id: The unique identifier for the call
            
        Returns:
            Dict containing dial information or None if failed
        """
        url = f"{self.base_url}/dials/{dial_id}"
        
        try:
            logger.info(f"Fetching dial info for ID: {dial_id}")
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"Successfully retrieved dial info for {dial_id}")
                return response.json()
            elif response.status_code == 404:
                logger.warning(f"Dial {dial_id} not found")
                return None
            else:
                logger.error(f"Failed to get dial info: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching dial {dial_id}: {str(e)}")
            return None
    
    def wait_for_transcript(self, dial_id: str, max_attempts: int = 10, wait_seconds: int = 5) -> Optional[Dict]:
        """
        Wait for transcript to be available with polling
        
        Args:
            dial_id: The unique identifier for the call
            max_attempts: Maximum number of polling attempts
            wait_seconds: Seconds to wait between attempts
            
        Returns:
            Dict containing dial information with transcript or None if failed
        """
        for attempt in range(max_attempts):
            dial_info = self.get_dial_info(dial_id)
            
            if dial_info and dial_info.get('transcript'):
                logger.info(f"Transcript ready for dial {dial_id}")
                return dial_info
            
            if attempt < max_attempts - 1:
                logger.info(f"Transcript not ready for {dial_id}, attempt {attempt + 1}/{max_attempts}. Waiting {wait_seconds}s...")
                time.sleep(wait_seconds)
        
        logger.warning(f"Transcript not available for {dial_id} after {max_attempts} attempts")
        return dial_info  # Return whatever we have

class TranscriptProcessor:
    """Handles transcript processing and file saving"""
    
    def __init__(self, output_directory: str = "transcripts"):
        self.output_directory = output_directory
        self._ensure_output_directory()
    
    def _ensure_output_directory(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
            logger.info(f"Created output directory: {self.output_directory}")
    
    def save_transcript(self, dial_info: Dict) -> Optional[str]:
        """
        Save transcript to a formatted text file
        
        Args:
            dial_info: Complete dial information from Vogent API
            
        Returns:
            Path to saved file or None if failed
        """
        dial_id = dial_info.get('id', 'unknown')
        transcript_entries = dial_info.get('transcript', [])
        
        if not transcript_entries:
            logger.warning(f"No transcript entries found for dial {dial_id}")
            return None
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transcript_{dial_id}_{timestamp}.txt"
        filepath = os.path.join(self.output_directory, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # Write header information
                f.write("=" * 60 + "\n")
                f.write("VOGENT CALL TRANSCRIPT\n")
                f.write("=" * 60 + "\n")
                f.write(f"Dial ID: {dial_id}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                # Add additional metadata if available
                if 'agent_id' in dial_info:
                    f.write(f"Agent ID: {dial_info['agent_id']}\n")
                if 'source_number' in dial_info:
                    f.write(f"Caller Number: {dial_info['source_number']}\n")
                if 'status' in dial_info:
                    f.write(f"Call Status: {dial_info['status']}\n")
                
                f.write("\n" + "-" * 60 + "\n")
                f.write("CONVERSATION TRANSCRIPT\n")
                f.write("-" * 60 + "\n\n")
                
                # Write transcript entries
                for i, entry in enumerate(transcript_entries, 1):
                    speaker = entry.get('speaker', 'UNKNOWN')
                    text = entry.get('text', '')
                    timestamp_entry = entry.get('timestamp', '')
                    
                    # Format each entry
                    f.write(f"[{i:03d}] {speaker}")
                    if timestamp_entry:
                        f.write(f" ({timestamp_entry})")
                    f.write(f": {text}\n\n")
                
                f.write("-" * 60 + "\n")
                f.write(f"End of transcript - {len(transcript_entries)} total entries\n")
            
            logger.info(f"Transcript saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save transcript for {dial_id}: {str(e)}")
            return None
    
    def save_raw_json(self, dial_info: Dict) -> Optional[str]:
        """
        Save raw dial information as JSON for debugging/backup
        
        Args:
            dial_info: Complete dial information from Vogent API
            
        Returns:
            Path to saved JSON file or None if failed
        """
        dial_id = dial_info.get('id', 'unknown')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"raw_dial_{dial_id}_{timestamp}.json"
        filepath = os.path.join(self.output_directory, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(dial_info, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Raw dial data saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save raw dial data for {dial_id}: {str(e)}")
            return None

# Initialize Flask app
app = Flask(__name__)

# Initialize components
API_KEY = "elto_DfXARu0I6uEEENntZkWvoCIkQPodVvjA"  # Your Vogent API key

vogent_api = VogentAPI(API_KEY)
transcript_processor = TranscriptProcessor()

# Add a simple dashboard
@app.route('/', methods=['GET'])
def dashboard():
    """
    Simple dashboard showing server status
    """
    return f"""
    <html>
    <head><title>Vogent Transcript Automation</title></head>
    <body style="font-family: Arial, sans-serif; margin: 40px;">
        <h1>🎙️ Vogent Transcript Automation</h1>
        <h2>Server Status: ✅ RUNNING</h2>
        <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Webhook URL:</strong> <code>/webhook/vogent</code> (POST only)</p>
        
        <h3>Test Endpoints:</h3>
        <ul>
            <li><strong>Health check:</strong> <a href="/health">/health</a></li>
            <li><strong>Manual fetch:</strong> <code>/test-call/DIAL_ID</code> (replace DIAL_ID with actual ID)</li>
        </ul>
        
        <h3>How to test manually:</h3>
        <p>After making a call, find your Dial ID in Vogent dashboard, then visit:</p>
        <p><code>http://localhost:5000/test-call/YOUR_DIAL_ID_HERE</code></p>
        
        <form action="/test-dial-input" method="post" style="margin-top: 20px; padding: 15px; background: #f5f5f5;">
            <label for="dial_id">Test with Dial ID:</label><br>
            <input type="text" id="dial_id" name="dial_id" placeholder="Enter dial ID here" style="width: 300px; padding: 5px;"><br><br>
            <input type="submit" value="Fetch Transcript" style="padding: 8px 16px;">
        </form>
        
        <h3>Recent Log Entries:</h3>
        <p>Check console output for webhook data and processing logs...</p>
    </body>
    </html>
    """

@app.route('/webhook/vogent', methods=['POST'])
def vogent_webhook():
    """
    Handle incoming webhooks from Vogent
    
    This will log ALL webhook data to help us understand what Vogent sends
    """
    try:
        data = request.get_json()
        
        # Log EVERYTHING we receive
        logger.info("=" * 60)
        logger.info("🔔 WEBHOOK RECEIVED FROM VOGENT")
        logger.info("=" * 60)
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"Raw Data: {json.dumps(data, indent=2)}")
        logger.info("=" * 60)
        
        if not data:
            logger.warning("Received webhook with no JSON data")
            return jsonify({"error": "No JSON data"}), 400
        
        event_type = data.get('event')
        payload = data.get('payload', {})
        
        logger.info(f"Event Type: {event_type}")
        logger.info(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Try to extract dial_id from anywhere in the data
        dial_id = (payload.get('dial_id') or 
                  payload.get('dial_session_id') or 
                  data.get('dial_id') or 
                  data.get('id'))
        
        if dial_id:
            logger.info(f"Found dial_id: {dial_id}")
            
            # For any event with a dial_id, try to fetch transcript
            logger.info(f"Attempting to fetch transcript for dial: {dial_id}")
            
            # Add delay to ensure transcript is ready
            time.sleep(3)
            
            dial_info = vogent_api.wait_for_transcript(dial_id, max_attempts=6, wait_seconds=10)
            
            if dial_info:
                transcript_file = transcript_processor.save_transcript(dial_info)
                json_file = transcript_processor.save_raw_json(dial_info)
                
                if transcript_file:
                    logger.info(f"✅ Successfully saved transcript: {transcript_file}")
                else:
                    logger.warning(f"⚠️ Could not save transcript for {dial_id}")
            else:
                logger.error(f"❌ Failed to fetch dial info for {dial_id}")
        else:
            logger.warning("No dial_id found in webhook data")
        
        return jsonify({"status": "success", "processed": True}), 200
        
    except Exception as e:
        logger.error(f"❌ Error processing webhook: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/webhook/vogent', methods=['GET'])
def vogent_webhook_info():
    """
    Info page for webhook endpoint (for testing/verification)
    """
    return jsonify({
        "message": "Vogent Webhook Endpoint",
        "method": "POST required for webhooks",
        "events": ["dial.inbound", "dial.transcript", "any event with dial_id"],
        "status": "ready",
        "timestamp": datetime.now().isoformat()
    })

# Test endpoint that works with GET requests
@app.route('/test-call/<dial_id>', methods=['GET'])
def test_call_fetch(dial_id: str):
    """
    Test endpoint to manually fetch a transcript via browser
    Just visit: http://localhost:5000/test-call/YOUR_DIAL_ID
    """
    try:
        logger.info(f"🧪 Test fetch for dial: {dial_id}")
        
        dial_info = vogent_api.wait_for_transcript(dial_id, max_attempts=3, wait_seconds=5)
        
        if dial_info:
            transcript_file = transcript_processor.save_transcript(dial_info)
            json_file = transcript_processor.save_raw_json(dial_info)
            
            return f"""
            <html>
            <head><title>Test Fetch Results</title></head>
            <body style="font-family: Arial, sans-serif; margin: 40px;">
                <h2>Test Fetch Results</h2>
                <p><strong>Dial ID:</strong> {dial_id}</p>
                <p><strong>Status:</strong> {'✅ Success' if transcript_file else '❌ Failed'}</p>
                <p><strong>Transcript File:</strong> {transcript_file or 'None'}</p>
                <p><strong>JSON File:</strong> {json_file or 'None'}</p>
                
                <h3>Raw API Response:</h3>
                <pre style="background: #f5f5f5; padding: 15px; overflow: auto;">
{json.dumps(dial_info, indent=2)}
                </pre>
                
                <p><a href="/">← Back to Dashboard</a></p>
            </body>
            </html>
            """
        else:
            return f"""
            <html>
            <body style="font-family: Arial, sans-serif; margin: 40px;">
                <h2>❌ Could not fetch dial info for {dial_id}</h2>
                <p>This could mean:</p>
                <ul>
                    <li>The dial ID doesn't exist</li>
                    <li>The call is still in progress</li>
                    <li>There's an API error</li>
                </ul>
                <p><a href="/">← Back to Dashboard</a></p>
            </body>
            </html>
            """
            
    except Exception as e:
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 40px;">
            <h2>❌ Error: {str(e)}</h2>
            <p><a href="/">← Back to Dashboard</a></p>
        </body>
        </html>
        """

@app.route('/test-dial-input', methods=['POST'])
def test_dial_input():
    """
    Handle form submission for dial ID testing
    """
    dial_id = request.form.get('dial_id', '').strip()
    if not dial_id:
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 40px;">
            <h2>❌ No Dial ID provided</h2>
            <p><a href="/">← Back to Dashboard</a></p>
        </body>
        </html>
        """
    
    # Redirect to the test endpoint
    from flask import redirect, url_for
    return redirect(url_for('test_call_fetch', dial_id=dial_id))

def handle_inbound_call(payload: Dict):
    """
    Handle dial.inbound webhook event
    
    Args:
        payload: Webhook payload containing call information
    """
    dial_id = payload.get('dial_id')
    source_number = payload.get('source_number', 'Unknown')
    agent_id = payload.get('call_agent_id', 'Unknown')
    
    logger.info(f"Inbound call started - Dial ID: {dial_id}, From: {source_number}, Agent: {agent_id}")
    
    # Store call info for later processing if needed
    # For now, we'll wait for the transcript webhook

def handle_transcript_ready(payload: Dict):
    """
    Handle dial.transcript webhook event - transcript is ready
    
    Args:
        payload: Webhook payload containing dial information
    """
    dial_id = payload.get('dial_id')
    
    if not dial_id:
        logger.error("No dial_id in transcript webhook payload")
        return
    
    logger.info(f"Transcript ready for dial: {dial_id}")
    
    # Fetch the complete dial information with transcript
    dial_info = vogent_api.get_dial_info(dial_id)
    
    if not dial_info:
        logger.error(f"Failed to retrieve dial info for {dial_id}")
        return
    
    # Save the transcript
    transcript_file = transcript_processor.save_transcript(dial_info)
    json_file = transcript_processor.save_raw_json(dial_info)
    
    if transcript_file:
        logger.info(f"Successfully processed transcript for dial {dial_id}")
    else:
        logger.error(f"Failed to save transcript for dial {dial_id}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Vogent Transcript Automation",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/manual-fetch/<dial_id>', methods=['POST'])
def manual_fetch(dial_id: str):
    """
    Manual endpoint to fetch a transcript by dial ID
    Useful for testing or recovering missed webhooks
    """
    try:
        logger.info(f"Manual fetch requested for dial: {dial_id}")
        
        # Try to get transcript, with polling if needed
        dial_info = vogent_api.wait_for_transcript(dial_id)
        
        if not dial_info:
            return jsonify({"error": f"Could not retrieve dial info for {dial_id}"}), 404
        
        # Save the transcript
        transcript_file = transcript_processor.save_transcript(dial_info)
        json_file = transcript_processor.save_raw_json(dial_info)
        
        return jsonify({
            "status": "success",
            "dial_id": dial_id,
            "transcript_file": transcript_file,
            "json_file": json_file
        })
        
    except Exception as e:
        logger.error(f"Error in manual fetch for {dial_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Vogent Transcript Automation Server")
    logger.info(f"Transcripts will be saved to: {transcript_processor.output_directory}")
    
    # Run Flask app
    # In production, use a proper WSGI server like gunicorn
    app.run(
        host='0.0.0.0', 
        port=int(os.getenv('PORT', 5000)), 
        debug=os.getenv('DEBUG', 'False').lower() == 'true'
    )