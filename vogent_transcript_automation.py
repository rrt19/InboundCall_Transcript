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
import threading
from datetime import datetime, timedelta
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
    
    def get_recent_dials(self, limit: int = 50, status: str = None) -> Optional[List[Dict]]:
        """
        Retrieve recent dials from the API
        Note: This endpoint may not be available in all Vogent API versions
        
        Args:
            limit: Maximum number of dials to retrieve
            status: Filter by status (e.g., 'completed', 'failed', 'in_progress')
            
        Returns:
            List of dial information or None if failed
        """
        # Try different possible endpoints
        endpoints = [
            f"{self.base_url}/dials",
            f"{self.base_url}/calls", 
            f"{self.base_url}/dial-history",
            f"{self.base_url}/recent-dials"
        ]
        
        params = {'limit': limit}
        if status:
            params['status'] = status
        
        for url in endpoints:
            try:
                logger.debug(f"Trying endpoint: {url}")
                response = requests.get(url, headers=self.headers, params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    dials = data.get('dials', data.get('calls', data)) if isinstance(data, dict) else data
                    if isinstance(dials, list):
                        logger.info(f"Successfully retrieved {len(dials)} recent dials from {url}")
                        return dials
                elif response.status_code != 404 and response.status_code != 405:
                    logger.warning(f"Endpoint {url} returned {response.status_code}: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                logger.debug(f"Network error trying {url}: {str(e)}")
                continue
        
        logger.warning("Could not retrieve recent dials - API endpoint may not be available")
        logger.info("This is normal - the system will rely on webhooks for automation")
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
        self.processed_dials_file = os.path.join(output_directory, "processed_dials.txt")
        self._ensure_output_directory()
        self.processed_dials = self._load_processed_dials()
        self.processing_lock = threading.Lock()  # Add thread safety
    
    def _load_processed_dials(self) -> set:
        """Load previously processed dial IDs from file"""
        try:
            if os.path.exists(self.processed_dials_file):
                with open(self.processed_dials_file, 'r') as f:
                    return set(line.strip() for line in f if line.strip())
            return set()
        except Exception as e:
            logger.warning(f"Could not load processed dials: {e}")
            return set()
    
    def _save_processed_dial(self, dial_id: str):
        """Add dial ID to processed list and save to file"""
        try:
            self.processed_dials.add(dial_id)
            with open(self.processed_dials_file, 'a') as f:
                f.write(f"{dial_id}\n")
        except Exception as e:
            logger.error(f"Could not save processed dial {dial_id}: {e}")
    
    def is_already_processed(self, dial_id: str) -> bool:
        """Check if dial has already been processed"""
        return dial_id in self.processed_dials
    
    def _ensure_output_directory(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
            logger.info(f"Created output directory: {self.output_directory}")
    
    def save_transcript(self, dial_info: Dict) -> Optional[str]:
        """
        Save transcript to a formatted text file (with duplicate prevention)
        
        Args:
            dial_info: Complete dial information from Vogent API
            
        Returns:
            Path to saved file or None if failed
        """
        dial_id = dial_info.get('id', 'unknown')
        
        # Thread-safe duplicate check
        with self.processing_lock:
            if self.is_already_processed(dial_id):
                logger.info(f"Dial {dial_id} already processed, skipping duplicate")
                return None
            
            # Mark as processing immediately to prevent duplicates
            self._save_processed_dial(dial_id)
        
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
            # Already marked as processed above
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

class NotificationService:
    """Handle notifications for processed transcripts"""
    
    def __init__(self):
        self.notifications = []
        self.max_notifications = 50
    
    def add_notification(self, message: str, dial_id: str = None, level: str = "info"):
        """Add a notification"""
        notification = {
            'timestamp': datetime.now(),
            'message': message,
            'dial_id': dial_id,
            'level': level
        }
        
        self.notifications.insert(0, notification)  # Add to beginning
        
        # Keep only recent notifications
        if len(self.notifications) > self.max_notifications:
            self.notifications = self.notifications[:self.max_notifications]
        
        # Log the notification
        if level == "success":
            logger.info(f"✅ {message}")
        elif level == "warning":
            logger.warning(f"⚠️ {message}")
        elif level == "error":
            logger.error(f"❌ {message}")
        else:
            logger.info(f"ℹ️ {message}")
    
    def get_recent_notifications(self, limit: int = 10):
        """Get recent notifications"""
        return self.notifications[:limit]
    
    def clear_notifications(self):
        """Clear all notifications"""
        self.notifications = []

class AutoDiscoveryService:
    """Automatic discovery and processing of new dials"""
    
    def __init__(self, vogent_api: VogentAPI, transcript_processor: TranscriptProcessor, notification_service: NotificationService):
        self.vogent_api = vogent_api
        self.transcript_processor = transcript_processor
        self.notification_service = notification_service
        self.running = False
        self.thread = None
        self.check_interval = 30  # seconds
        self.stats = {
            'last_check': None,
            'total_processed': 0,
            'errors': 0,
            'new_dials_found': 0
        }
    
    def start(self):
        """Start the auto-discovery service"""
        if self.running:
            logger.warning("Auto-discovery service is already running")
            return
        
        # Check if API supports recent dials first
        test_dials = self.vogent_api.get_recent_dials(limit=1)
        if test_dials is None:
            logger.info("Recent dials API not available - running in webhook-only mode")
            self.check_interval = 300  # Check less frequently, mainly for status
        
        self.running = True
        self.thread = threading.Thread(target=self._discovery_loop, daemon=True)
        self.thread.start()
        logger.info(f"Auto-discovery service started (checking every {self.check_interval}s)")
    
    def stop(self):
        """Stop the auto-discovery service"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Auto-discovery service stopped")
    
    def _discovery_loop(self):
        """Main discovery loop that runs in background"""
        while self.running:
            try:
                self.stats['last_check'] = datetime.now()
                self._check_for_new_dials()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in discovery loop: {e}")
                self.stats['errors'] += 1
                time.sleep(self.check_interval)
    
    def _check_for_new_dials(self):
        """Check for new completed dials and process them (if API supports it)"""
        
        # Only attempt API polling if we haven't determined it's unavailable
        if hasattr(self, '_api_unavailable') and self._api_unavailable:
            logger.debug("API polling disabled - running in webhook-only mode")
            return
            
        logger.debug("Checking for new completed dials...")
        
        # Get recent completed dials (may not be available in all API versions)
        recent_dials = self.vogent_api.get_recent_dials(limit=20, status='completed')
        
        if not recent_dials:
            # Mark API as unavailable to avoid repeated failed attempts
            self._api_unavailable = True
            self.check_interval = 300  # Check less frequently
            logger.info("Recent dials API unavailable - switching to webhook-only mode")
            return
        
        new_dials = []
        for dial in recent_dials:
            dial_id = dial.get('id')
            if dial_id and not self.transcript_processor.is_already_processed(dial_id):
                new_dials.append(dial)
        
        if new_dials:
            logger.info(f"Found {len(new_dials)} new completed dials to process")
            self.stats['new_dials_found'] += len(new_dials)
            
            for dial in new_dials:
                try:
                    self._process_dial(dial)
                    self.stats['total_processed'] += 1
                except Exception as e:
                    logger.error(f"Error processing dial {dial.get('id')}: {e}")
                    self.stats['errors'] += 1
        else:
            logger.debug("No new dials to process")
    
    def _process_dial(self, dial: Dict):
        """Process a single dial and save its transcript"""
        dial_id = dial.get('id')
        logger.info(f"Auto-processing dial: {dial_id}")
        
        # Get full dial info with transcript
        dial_info = self.vogent_api.wait_for_transcript(dial_id, max_attempts=3, wait_seconds=5)
        
        if dial_info:
            transcript_file = self.transcript_processor.save_transcript(dial_info)
            # json_file = self.transcript_processor.save_raw_json(dial_info)  # Disabled - only saving .txt files
            
            if transcript_file:
                self.notification_service.add_notification(
                    f"Auto-processed transcript for dial {dial_id[:8]}...", 
                    dial_id, 
                    "success"
                )
            else:
                self.notification_service.add_notification(
                    f"Could not save transcript for dial {dial_id[:8]}...", 
                    dial_id, 
                    "warning"
                )
        else:
            self.notification_service.add_notification(
                f"Failed to fetch dial info for {dial_id[:8]}...", 
                dial_id, 
                "error"
            )

# Initialize Flask app
app = Flask(__name__)

# Initialize components
API_KEY = "elto_DfXARu0I6uEEENntZkWvoCIkQPodVvjA"  # Your Vogent API key

vogent_api = VogentAPI(API_KEY)
transcript_processor = TranscriptProcessor()
notification_service = NotificationService()
auto_discovery = AutoDiscoveryService(vogent_api, transcript_processor, notification_service)

# Add a simple dashboard
@app.route('/', methods=['GET'])
def dashboard():
    """
    Simple dashboard showing server status
    """
    # Get auto-discovery status
    auto_status = "✅ RUNNING" if auto_discovery.running else "⏸️ STOPPED"
    stats = auto_discovery.stats
    last_check = stats['last_check'].strftime('%H:%M:%S') if stats['last_check'] else 'Never'
    
    return f"""
    <html>
    <head>
        <title>Vogent Transcript Automation</title>
        <meta http-equiv="refresh" content="30">
    </head>
    <body style="font-family: Arial, sans-serif; margin: 40px;">
        <h1>🎙️ Vogent Transcript Automation</h1>
        
        <div style="display: flex; gap: 20px;">
            <div style="flex: 1;">
                <h2>Server Status: ✅ RUNNING</h2>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Webhook URL:</strong> <code>/webhook/vogent</code> (POST only)</p>
            </div>
            
            <div style="flex: 1; background: #f0f8ff; padding: 15px; border-radius: 5px;">
                <h3>🤖 Auto-Discovery Service</h3>
                <p><strong>Status:</strong> {auto_status}</p>
                <p><strong>Mode:</strong> {"Webhook-Only" if hasattr(auto_discovery, '_api_unavailable') and auto_discovery._api_unavailable else "API + Webhook"}</p>
                <p><strong>Last Check:</strong> {last_check}</p>
                <p><strong>Processed:</strong> {stats['total_processed']} calls</p>
                <p><strong>New Dials Found:</strong> {stats['new_dials_found']}</p>
                <p><strong>Errors:</strong> {stats['errors']}</p>
                
                <div style="margin-top: 10px;">
                    <a href="/auto-discovery/start" style="background: #4CAF50; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px;">▶️ Start</a>
                    <a href="/auto-discovery/stop" style="background: #f44336; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">⏹️ Stop</a>
                </div>
            </div>
        </div>
        
        <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3>🔧 Important Setup Information</h3>
            <p><strong>For Full Automation:</strong> Configure webhooks in your Vogent dashboard to point to:</p>
            <p><code>http://YOUR_SERVER_IP:5000/webhook/vogent</code></p>
            <p>The system will automatically process transcripts when calls complete via webhooks.</p>
            <p><strong>Manual Processing:</strong> You can always manually fetch transcripts using the form below.</p>
        </div>
        
        <h3>🔗 Quick Actions:</h3>
        <ul>
            <li><strong>Health check:</strong> <a href="/health">/health</a></li>
            <li><strong>Recent dials:</strong> <a href="/recent-dials">/recent-dials</a> (may not work if API doesn't support it)</li>
            <li><strong>Manual fetch:</strong> <code>/test-call/DIAL_ID</code> (replace DIAL_ID with actual ID)</li>
            <li><strong>Force check:</strong> <a href="/check-now">/check-now</a></li>
            <li><strong>Notifications:</strong> <a href="/notifications">/notifications</a></li>
        </ul>
        
        <h3>📞 Manual Testing:</h3>
        <form action="/test-dial-input" method="post" style="margin-top: 20px; padding: 15px; background: #f5f5f5; border-radius: 5px;">
            <label for="dial_id">Test with Dial ID:</label><br>
            <input type="text" id="dial_id" name="dial_id" placeholder="Enter dial ID here" style="width: 300px; padding: 5px; margin: 5px 0;"><br>
            <input type="submit" value="Fetch Transcript" style="padding: 8px 16px; background: #2196F3; color: white; border: none; border-radius: 3px;">
        </form>
        
        <h3>📊 Processing Stats:</h3>
        <p>Processed dials: {len(transcript_processor.processed_dials)}</p>
        <p>Output directory: <code>{transcript_processor.output_directory}</code></p>
        
        <h3>🔔 Recent Notifications:</h3>
        <div style="background: #f9f9f9; padding: 15px; border-radius: 5px; max-height: 200px; overflow-y: auto;">
            {''.join([f'<div style="margin: 5px 0; padding: 5px; background: {"#d4edda" if n["level"]=="success" else "#fff3cd" if n["level"]=="warning" else "#f8d7da" if n["level"]=="error" else "#d1ecf1"}; border-radius: 3px;"><small>{n["timestamp"].strftime("%H:%M:%S")}</small> - {n["message"]}</div>' for n in notification_service.get_recent_notifications(5)])}
        </div>
        
        <p style="margin-top: 30px; color: #666; font-size: 12px;">Auto-refresh every 30 seconds</p>
    </body>
    </html>
    """

@app.route('/webhook/vogent', methods=['POST'])
def vogent_webhook():
    """
    Enhanced webhook handler with better automation and error handling
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
            logger.info(f"Found dial_id: {dial_id} from event: {event_type}")
            
            # Check if already processed to avoid duplicates
            if transcript_processor.is_already_processed(dial_id):
                logger.info(f"Dial {dial_id} already processed, skipping duplicate webhook")
                return jsonify({"status": "already_processed", "dial_id": dial_id}), 200
            
            # Handle different event types
            if event_type == 'call.completed' or event_type == 'dial.completed':
                logger.info(f"Call completed event for dial: {dial_id}")
                # Add small delay for transcript to be ready
                time.sleep(2)
            elif event_type == 'transcript.ready' or event_type == 'dial.transcript':
                logger.info(f"Transcript ready event for dial: {dial_id}")
                # Transcript should be ready immediately
            else:
                logger.info(f"Other event type '{event_type}' for dial: {dial_id}")
                # Add delay to be safe
                time.sleep(3)
            
            # Try to fetch and process transcript
            success = _process_dial_from_webhook(dial_id, event_type)
            
            if success:
                return jsonify({"status": "success", "processed": True, "dial_id": dial_id}), 200
            else:
                return jsonify({"status": "failed", "processed": False, "dial_id": dial_id}), 200
        else:
            logger.warning("No dial_id found in webhook data")
            return jsonify({"status": "no_dial_id", "processed": False}), 200
        
    except Exception as e:
        logger.error(f"❌ Error processing webhook: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Internal server error"}), 500

def _process_dial_from_webhook(dial_id: str, event_type: str = None) -> bool:
    """
    Process a dial ID from webhook with better error handling and retries
    
    Returns:
        True if successfully processed, False otherwise
    """
    try:
        logger.info(f"Processing dial {dial_id} from webhook (event: {event_type})")
        
        # Try to get transcript with retries
        dial_info = vogent_api.wait_for_transcript(dial_id, max_attempts=5, wait_seconds=8)
        
        if dial_info:
            # Check if transcript exists
            transcript_entries = dial_info.get('transcript', [])
            if not transcript_entries:
                logger.warning(f"No transcript entries found for dial {dial_id}, will retry later")
                return False
            
            # Save transcript and raw data
            transcript_file = transcript_processor.save_transcript(dial_info)
            # json_file = transcript_processor.save_raw_json(dial_info)  # Disabled - only saving .txt files
            
            if transcript_file:
                notification_service.add_notification(
                    f"Webhook processed transcript for dial {dial_id[:8]}...", 
                    dial_id, 
                    "success"
                )
                return True
            else:
                notification_service.add_notification(
                    f"Could not save transcript for dial {dial_id[:8]}...", 
                    dial_id, 
                    "error"
                )
                return False
        else:
            logger.error(f"❌ Failed to fetch dial info for {dial_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error processing dial {dial_id} from webhook: {str(e)}")
        return False

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
            # json_file = transcript_processor.save_raw_json(dial_info)  # Disabled - only saving .txt files
            
            return f"""
            <html>
            <head><title>Test Fetch Results</title></head>
            <body style="font-family: Arial, sans-serif; margin: 40px;">
                <h2>Test Fetch Results</h2>
                <p><strong>Dial ID:</strong> {dial_id}</p>
                <p><strong>Status:</strong> {'✅ Success' if transcript_file else '❌ Failed'}</p>
                <p><strong>Transcript File:</strong> {transcript_file or 'None'}</p>
                
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
    # json_file = transcript_processor.save_raw_json(dial_info)  # Disabled - only saving .txt files
    
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

@app.route('/auto-discovery/start', methods=['GET'])
def start_auto_discovery():
    """Start the auto-discovery service"""
    auto_discovery.start()
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; margin: 40px;">
        <h2>✅ Auto-Discovery Service Started</h2>
        <p>The service will now automatically check for new completed calls every {auto_discovery.check_interval} seconds.</p>
        <p><a href="/">← Back to Dashboard</a></p>
    </body>
    </html>
    """

@app.route('/auto-discovery/stop', methods=['GET'])
def stop_auto_discovery():
    """Stop the auto-discovery service"""
    auto_discovery.stop()
    return """
    <html>
    <body style="font-family: Arial, sans-serif; margin: 40px;">
        <h2>⏹️ Auto-Discovery Service Stopped</h2>
        <p>The service has been stopped. No automatic processing will occur.</p>
        <p><a href="/">← Back to Dashboard</a></p>
    </body>
    </html>
    """

@app.route('/check-now', methods=['GET'])
def force_check():
    """Manually trigger a check for new dials"""
    try:
        logger.info("Manual check triggered")
        auto_discovery._check_for_new_dials()
        return """
        <html>
        <body style="font-family: Arial, sans-serif; margin: 40px;">
            <h2>✅ Manual Check Completed</h2>
            <p>Check for new dials has been executed. Check the logs for results.</p>
            <p><a href="/">← Back to Dashboard</a></p>
        </body>
        </html>
        """
    except Exception as e:
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 40px;">
            <h2>❌ Error during manual check</h2>
            <p>Error: {str(e)}</p>
            <p><a href="/">← Back to Dashboard</a></p>
        </body>
        </html>
        """

@app.route('/recent-dials', methods=['GET'])
def show_recent_dials():
    """Show recent dials from the API (if supported)"""
    try:
        dials = vogent_api.get_recent_dials(limit=10)
        if not dials:
            return """
            <html>
            <body style="font-family: Arial, sans-serif; margin: 40px;">
                <h2>📞 Recent Dials API Not Available</h2>
                <div style="background: #d1ecf1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>🔍 This is Normal!</h3>
                    <p>The Vogent API doesn't provide a public endpoint to list recent calls for security reasons.</p>
                    <p><strong>Your system is working correctly in webhook-only mode.</strong></p>
                </div>
                
                <h3>✅ How Full Automation Works:</h3>
                <ol>
                    <li><strong>Webhooks:</strong> When a call completes, Vogent sends a webhook to your server</li>
                    <li><strong>Auto-Processing:</strong> The server automatically fetches and saves the transcript</li>
                    <li><strong>No Manual Work:</strong> Everything happens automatically in the background</li>
                </ol>
                
                <h3>🧪 To Test Right Now:</h3>
                <p>Make a call to your Vogent number, then check the logs or use the manual form on the dashboard.</p>
                
                <p><a href="/" style="background: #007bff; color: white; padding: 8px 16px; text-decoration: none; border-radius: 3px;">← Back to Dashboard</a></p>
            </body>
            </html>
            """
        
        dial_rows = ""
        for dial in dials:
            dial_id = dial.get('id', 'N/A')
            status = dial.get('status', 'N/A')
            created = dial.get('created_at', dial.get('timestamp', 'N/A'))
            processed = '✅' if transcript_processor.is_already_processed(dial_id) else '⏳'
            
            dial_rows += f"""
            <tr>
                <td>{dial_id}</td>
                <td>{status}</td>
                <td>{created}</td>
                <td>{processed}</td>
                <td><a href="/test-call/{dial_id}">Process</a></td>
            </tr>
            """
        
        return f"""
        <html>
        <head><title>Recent Dials</title></head>
        <body style="font-family: Arial, sans-serif; margin: 40px;">
            <h2>📞 Recent Dials</h2>
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr style="background: #f0f0f0;">
                    <th style="padding: 10px;">Dial ID</th>
                    <th style="padding: 10px;">Status</th>
                    <th style="padding: 10px;">Created</th>
                    <th style="padding: 10px;">Processed</th>
                    <th style="padding: 10px;">Action</th>
                </tr>
                {dial_rows}
            </table>
            <p><a href="/">← Back to Dashboard</a></p>
        </body>
        </html>
        """
    except Exception as e:
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 40px;">
            <h2>❌ Error retrieving recent dials</h2>
            <p>Error: {str(e)}</p>
            <p><a href="/">← Back to Dashboard</a></p>
        </body>
        </html>
        """

@app.route('/notifications', methods=['GET'])
def show_notifications():
    """Show all notifications"""
    notifications = notification_service.get_recent_notifications(20)
    
    notification_rows = ""
    for n in notifications:
        color = {
            "success": "#d4edda",
            "warning": "#fff3cd", 
            "error": "#f8d7da",
            "info": "#d1ecf1"
        }.get(n['level'], "#f8f9fa")
        
        notification_rows += f"""
        <tr style="background: {color};">
            <td style="padding: 8px;">{n['timestamp'].strftime('%H:%M:%S')}</td>
            <td style="padding: 8px;">{n['level'].upper()}</td>
            <td style="padding: 8px;">{n['message']}</td>
            <td style="padding: 8px;">{n['dial_id'][:8] + '...' if n['dial_id'] else 'N/A'}</td>
        </tr>
        """
    
    return f"""
    <html>
    <head>
        <title>Notifications</title>
        <meta http-equiv="refresh" content="10">
    </head>
    <body style="font-family: Arial, sans-serif; margin: 40px;">
        <h2>🔔 Notifications</h2>
        <div style="margin: 20px 0;">
            <a href="/" style="background: #007bff; color: white; padding: 8px 16px; text-decoration: none; border-radius: 3px;">← Dashboard</a>
            <a href="/notifications/clear" style="background: #6c757d; color: white; padding: 8px 16px; text-decoration: none; border-radius: 3px; margin-left: 10px;">Clear All</a>
        </div>
        
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr style="background: #f0f0f0;">
                <th style="padding: 10px;">Time</th>
                <th style="padding: 10px;">Level</th>
                <th style="padding: 10px;">Message</th>
                <th style="padding: 10px;">Dial ID</th>
            </tr>
            {notification_rows}
        </table>
        
        <p style="margin-top: 20px; color: #666; font-size: 12px;">Auto-refresh every 10 seconds</p>
    </body>
    </html>
    """

@app.route('/notifications/clear', methods=['GET'])
def clear_notifications():
    """Clear all notifications"""
    notification_service.clear_notifications()
    return """
    <html>
    <body style="font-family: Arial, sans-serif; margin: 40px;">
        <h2>✅ Notifications Cleared</h2>
        <p>All notifications have been cleared.</p>
        <p><a href="/notifications">← Back to Notifications</a></p>
    </body>
    </html>
    """

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
        # json_file = transcript_processor.save_raw_json(dial_info)  # Disabled - only saving .txt files
        
        return jsonify({
            "status": "success",
            "dial_id": dial_id,
            "transcript_file": transcript_file
        })
        
    except Exception as e:
        logger.error(f"Error in manual fetch for {dial_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Vogent Transcript Automation Server")
    logger.info(f"Transcripts will be saved to: {transcript_processor.output_directory}")
    
    # Start auto-discovery service
    auto_discovery.start()
    logger.info("Auto-discovery service started automatically")
    
    try:
        # Run Flask app
        # In production, use a proper WSGI server like gunicorn
        app.run(
            host='0.0.0.0', 
            port=int(os.getenv('PORT', 5000)), 
            debug=os.getenv('DEBUG', 'False').lower() == 'true'
        )
    finally:
        # Clean shutdown
        logger.info("Shutting down...")
        auto_discovery.stop()