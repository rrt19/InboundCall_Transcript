#!/usr/bin/env python3
"""
Transcript Viewer Web Application
================================

A Flask web application to view Vogent call transcripts in a beautiful format.
"""

import os
import json
import re
from datetime import datetime
from flask import Flask, render_template, request, send_file, abort
from pathlib import Path

app = Flask(__name__)

class TranscriptParser:
    """Parse transcript files into structured data"""
    
    def __init__(self, transcripts_dir: str = "transcripts"):
        self.transcripts_dir = transcripts_dir
    
    def get_all_transcripts(self):
        """Get all transcript files with metadata"""
        transcripts = []
        
        if not os.path.exists(self.transcripts_dir):
            return transcripts
        
        for filename in os.listdir(self.transcripts_dir):
            if filename.endswith('.txt') and filename.startswith('transcript_'):
                filepath = os.path.join(self.transcripts_dir, filename)
                try:
                    metadata = self._extract_metadata(filepath)
                    metadata['filename'] = filename
                    metadata['filepath'] = filepath
                    transcripts.append(metadata)
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
        
        # Sort by timestamp (newest first)
        transcripts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return transcripts
    
    def _extract_metadata(self, filepath: str):
        """Extract metadata from transcript file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        metadata = {}
        
        # Extract dial ID from filename or content
        filename = os.path.basename(filepath)
        dial_id_match = re.search(r'transcript_([^_]+)', filename)
        if dial_id_match:
            metadata['dial_id'] = dial_id_match.group(1)
        
        # Extract metadata from content
        lines = content.split('\n')
        for line in lines[:15]:  # Check first 15 lines for metadata
            line = line.strip()
            
            # Handle Vogent format
            if line.startswith('Dial ID:'):
                metadata['dial_id'] = line.split('Dial ID:')[-1].strip()
            elif line.startswith('Generated:'):
                metadata['timestamp'] = line.split('Generated:')[-1].strip()
            elif line.startswith('Call Status:'):
                metadata['status'] = line.split('Call Status:')[-1].strip()
            
            # Handle original format  
            elif line.startswith('Call Transcript - Dial ID:'):
                metadata['dial_id'] = line.split('Dial ID:')[-1].strip()
            elif line.startswith('Timestamp:'):
                metadata['timestamp'] = line.split('Timestamp:')[-1].strip()
            elif line.startswith('Duration:'):
                metadata['duration'] = line.split('Duration:')[-1].strip()
            elif line.startswith('Status:'):
                metadata['status'] = line.split('Status:')[-1].strip()
        
        # Get file modification time as fallback
        if 'timestamp' not in metadata:
            mtime = os.path.getmtime(filepath)
            metadata['timestamp'] = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        # Extract conversation preview
        conversation = self._parse_conversation(content)
        if conversation:
            first_customer_msg = next((msg for msg in conversation if msg['speaker'] == 'Customer'), None)
            if first_customer_msg:
                preview = first_customer_msg['message'][:100]
                metadata['preview'] = preview + '...' if len(first_customer_msg['message']) > 100 else preview
            else:
                metadata['preview'] = "No customer messages found"
        else:
            metadata['preview'] = "No conversation found"
        
        return metadata
    
    def _parse_conversation(self, content: str):
        """Parse conversation from transcript content"""
        conversation = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip metadata and separator lines
            if any(line.startswith(prefix) for prefix in [
                '====', '----', 'VOGENT CALL TRANSCRIPT', 'Dial ID:', 'Generated:', 
                'Call Status:', 'CONVERSATION TRANSCRIPT', 'End of transcript'
            ]):
                continue
                
            # Parse numbered conversation format: [001] HUMAN: or [002] AI:
            numbered_pattern = r'^\[\d{3}\]\s+(HUMAN|AI):\s*(.*)$'
            numbered_match = re.match(numbered_pattern, line)
            if numbered_match:
                speaker_type = numbered_match.group(1)
                message = numbered_match.group(2).strip()
                
                # Skip empty messages or special tokens
                if not message or message in ['<|hangup|>', '<|end|>']:
                    continue
                
                speaker = 'Customer' if speaker_type == 'HUMAN' else 'Agent'
                conversation.append({
                    'speaker': speaker,
                    'message': message,
                    'type': 'human' if speaker_type == 'HUMAN' else 'ai'
                })
                continue
            
            # Fallback: Parse simple format: Agent: or Customer:
            simple_patterns = [
                r'^(Agent|Customer|Caller|Rep|Representative|User|Client):\s*(.*)$',
                r'^\[(Agent|Customer|Caller|Rep|Representative|User|Client)\]:\s*(.*)$'
            ]
            
            for pattern in simple_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    speaker = match.group(1).title()
                    message = match.group(2).strip()
                    
                    if message:  # Only add non-empty messages
                        conversation.append({
                            'speaker': speaker,
                            'message': message,
                            'type': 'ai' if speaker.lower() in ['agent', 'rep', 'representative'] else 'human'
                        })
                    break
        
        return conversation
    
    def get_transcript_details(self, filename: str):
        """Get detailed transcript information"""
        filepath = os.path.join(self.transcripts_dir, filename)
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract metadata
        metadata = self._extract_metadata(filepath)
        
        # Parse conversation
        conversation = self._parse_conversation(content)
        
        # Extract call summary
        summary = ""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('Call Summary:') or line.startswith('CALL SUMMARY:'):
                summary = line.split(':')[-1].strip()
                # Check if summary continues on next lines
                for j in range(i+1, len(lines)):
                    next_line = lines[j].strip()
                    if (next_line and 
                        not next_line.startswith('=') and 
                        not next_line.startswith('-') and
                        not re.match(r'^\[\d{3}\]', next_line) and
                        not any(next_line.startswith(prefix) for prefix in ['Agent:', 'Customer:', 'Call', 'End of'])):
                        summary += " " + next_line
                    else:
                        break
                break
        
        return {
            'metadata': metadata,
            'conversation': conversation,
            'summary': summary,
            'filename': filename,
            'raw_content': content
        }

# Initialize parser
transcript_parser = TranscriptParser()

@app.route('/')
def index():
    """Main page showing all transcripts"""
    search_query = request.args.get('search', '').strip()
    transcripts = transcript_parser.get_all_transcripts()
    
    # Filter transcripts based on search query
    if search_query:
        filtered_transcripts = []
        for transcript in transcripts:
            # Search in dial_id, filename, preview, and timestamp
            searchable_text = ' '.join([
                transcript.get('dial_id', ''),
                transcript.get('filename', ''),
                transcript.get('preview', ''),
                transcript.get('timestamp', ''),
                transcript.get('duration', ''),
                transcript.get('status', '')
            ]).lower()
            
            if search_query.lower() in searchable_text:
                filtered_transcripts.append(transcript)
        
        transcripts = filtered_transcripts
    
    return render_template('index.html', transcripts=transcripts, search_query=search_query)

@app.route('/transcript/<filename>')
def view_transcript(filename: str):
    """View individual transcript"""
    transcript_data = transcript_parser.get_transcript_details(filename)
    
    if not transcript_data:
        abort(404)
    
    return render_template('transcript.html', transcript=transcript_data)

@app.route('/download/<filename>')
def download_transcript(filename: str):
    """Download original transcript file"""
    filepath = os.path.join(transcript_parser.transcripts_dir, filename)
    
    if not os.path.exists(filepath):
        abort(404)
    
    return send_file(filepath, as_attachment=True)

@app.route('/api/transcripts')
def api_transcripts():
    """API endpoint for transcript list"""
    transcripts = transcript_parser.get_all_transcripts()
    return {'transcripts': transcripts}

@app.route('/api/transcript/<filename>')
def api_transcript(filename: str):
    """API endpoint for individual transcript"""
    transcript_data = transcript_parser.get_transcript_details(filename)
    
    if not transcript_data:
        abort(404)
    
    return transcript_data

if __name__ == '__main__':
    print("� Starting Transcript Viewer Web Application")
    print("📁 Transcripts directory:", os.path.abspath(transcript_parser.transcripts_dir))
    print("🌐 Web interface will be available at: http://localhost:5001")
    print("📋 Features:")
    print("   • Browse all transcripts")
    print("   • Search functionality")
    print("   • Beautiful chat-like conversation view")
    print("   • Download original files")
    print("   • Mobile responsive design")
    print("\n🚀 Starting server...")
    
    app.run(debug=True, host='0.0.0.0', port=5001)