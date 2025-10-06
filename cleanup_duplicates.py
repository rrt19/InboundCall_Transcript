#!/usr/bin/env python3
"""
Cleanup script to remove duplicate transcript files
"""
import os
import glob
from collections import defaultdict

def cleanup_duplicate_transcripts():
    """Remove duplicate transcript files, keeping only the first one"""
    
    transcript_dir = "transcripts"
    
    # Group files by dial_id
    dial_files = defaultdict(list)
    
    # Find all transcript files
    for file in glob.glob(os.path.join(transcript_dir, "transcript_*.txt")):
        filename = os.path.basename(file)
        # Extract dial_id from filename (between transcript_ and the timestamp)
        parts = filename.split('_')
        if len(parts) >= 6:  # transcript_[uuid parts]_timestamp.txt
            dial_id = '_'.join(parts[1:5])  # Reconstruct UUID
            dial_files[dial_id].append(file)
    
    # Find and remove duplicates
    removed_count = 0
    for dial_id, files in dial_files.items():
        if len(files) > 1:
            # Sort by filename (timestamp) and keep the first one
            files.sort()
            print(f"Found {len(files)} duplicates for dial {dial_id}")
            
            # Remove all but the first file
            for file_to_remove in files[1:]:
                print(f"  Removing: {file_to_remove}")
                os.remove(file_to_remove)
                removed_count += 1
                
                # Also remove corresponding JSON file
                json_file = file_to_remove.replace("transcript_", "raw_dial_").replace(".txt", ".json")
                if os.path.exists(json_file):
                    print(f"  Removing: {json_file}")
                    os.remove(json_file)
    
    print(f"\nCleanup complete! Removed {removed_count} duplicate transcript files.")
    return removed_count

if __name__ == "__main__":
    cleanup_duplicate_transcripts()