import os
import re
from datetime import datetime
from flask import Flask, render_template, abort
from pathlib import Path

app = Flask(__name__)
TRANSCRIPTS_DIR = Path(__file__).parent / 'transcripts'

def parse_transcript_file(filepath):
    messages = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Match patterns like "[001] HUMAN: text" or "[001] AI: text"
            match = re.match(r'^\[\d+\]\s*(HUMAN|AI|PATIENT|ASSISTANT|Patient|Assistant|Human|Ai)(?:\s*\([^)]*\))?\s*:\s*(.+)$', line, re.IGNORECASE)
            if match:
                speaker_raw = match.group(1).upper()
                text = match.group(2).strip()
                
                # Remove ALL occurrences of "AI:", "HUMAN:", "ASSISTANT:", "PATIENT:" prefixes from the text
                # This handles cases like: [011] AI: AI: AI: Understood... (no matter how many times)
                while re.match(r'^(AI|HUMAN|ASSISTANT|PATIENT):\s*', text, flags=re.IGNORECASE):
                    text = re.sub(r'^(AI|HUMAN|ASSISTANT|PATIENT):\s*', '', text, flags=re.IGNORECASE)
                
                # Map HUMAN -> PATIENT and AI -> ASSISTANT
                if speaker_raw in ['HUMAN', 'PATIENT']:
                    speaker = 'patient'
                    display_speaker = 'Patient'
                elif speaker_raw in ['AI', 'ASSISTANT']:
                    speaker = 'assistant'
                    display_speaker = 'Assistant'
                else:
                    speaker = speaker_raw.lower()
                    display_speaker = speaker_raw.title()
                
                messages.append({
                    'speaker': speaker,
                    'display_speaker': display_speaker,
                    'text': text
                })
                continue
            
            # Pattern without brackets: "HUMAN: text" or "AI: text"
            match = re.match(r'^(HUMAN|AI|PATIENT|ASSISTANT|Patient|Assistant|Human|Ai)(?:\s*\([^)]*\))?\s*:\s*(.+)$', line, re.IGNORECASE)
            if match:
                speaker_raw = match.group(1).upper()
                text = match.group(2).strip()
                
                # Remove ALL occurrences of prefixes (loop until none left)
                while re.match(r'^(AI|HUMAN|ASSISTANT|PATIENT):\s*', text, flags=re.IGNORECASE):
                    text = re.sub(r'^(AI|HUMAN|ASSISTANT|PATIENT):\s*', '', text, flags=re.IGNORECASE)
                
                # Map HUMAN -> PATIENT and AI -> ASSISTANT
                if speaker_raw in ['HUMAN', 'PATIENT']:
                    speaker = 'patient'
                    display_speaker = 'Patient'
                elif speaker_raw in ['AI', 'ASSISTANT']:
                    speaker = 'assistant'
                    display_speaker = 'Assistant'
                else:
                    speaker = speaker_raw.lower()
                    display_speaker = speaker_raw.title()
                
                messages.append({
                    'speaker': speaker,
                    'display_speaker': display_speaker,
                    'text': text
                })
                
    except Exception as e:
        print(f"Error parsing transcript: {e}")
    return messages

def get_transcript_metadata(filepath):
    filename = filepath.name
    stats = filepath.stat()
    date_match = re.search(r'_(\d{8})_(\d{6})\.txt$', filename)
    if date_match:
        date_str = date_match.group(1)
        time_str = date_match.group(2)
        try:
            date = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
            formatted_date = date.strftime("%B %d, %Y at %I:%M %p")
        except:
            formatted_date = datetime.fromtimestamp(stats.st_mtime).strftime("%B %d, %Y at %I:%M %p")
    else:
        formatted_date = datetime.fromtimestamp(stats.st_mtime).strftime("%B %d, %Y at %I:%M %p")
    size_bytes = stats.st_size
    if size_bytes < 1024:
        size = f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        size = f"{size_bytes / 1024:.1f} KB"
    else:
        size = f"{size_bytes / (1024 * 1024):.1f} MB"
    display_name = filename.replace('.txt', '')
    display_name = re.sub(r'transcript_([a-f0-9\-]+)_(\d{8})_(\d{6})', r'Session \2 at \3', display_name)
    display_name = re.sub(r'(\d{8})', lambda m: datetime.strptime(m.group(1), '%Y%m%d').strftime('%b %d, %Y'), display_name)
    display_name = re.sub(r'(\d{6})', lambda m: datetime.strptime(m.group(1), '%H%M%S').strftime('%I:%M %p'), display_name)
    return {'filename': filename, 'display_name': display_name, 'date': formatted_date, 'size': size}

@app.route('/')
def index():
    transcripts = []
    if TRANSCRIPTS_DIR.exists():
        txt_files = [f for f in TRANSCRIPTS_DIR.glob('transcript_*.txt')]
        txt_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        for filepath in txt_files:
            metadata = get_transcript_metadata(filepath)
            transcripts.append(metadata)
    return render_template('index.html', transcripts=transcripts)

@app.route('/transcript/<filename>')
def view_transcript(filename):
    if not filename.startswith('transcript_') or not filename.endswith('.txt'):
        abort(404)
    filepath = TRANSCRIPTS_DIR / filename
    if not filepath.exists():
        abort(404)
    messages = parse_transcript_file(filepath)
    metadata = get_transcript_metadata(filepath)
    return render_template('transcript.html', transcript_name=metadata['display_name'], date=metadata['date'], message_count=len(messages), messages=messages)

if __name__ == '__main__':
    TRANSCRIPTS_DIR.mkdir(exist_ok=True)
    print("Kyron Medical - Transcript Viewer")
    print(f"Transcripts: {TRANSCRIPTS_DIR}")
    print("Starting on port 8080...")
    app.run(host='0.0.0.0', port=8080, debug=True)
